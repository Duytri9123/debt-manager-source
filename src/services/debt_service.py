# -*- coding: utf-8 -*-
"""
Debt Service - Handles debt management and payments
Mirrors: app/Http/Controllers/Admin/DebtController.php
"""
from datetime import datetime, date
from typing import List, Optional, Dict
from src.database import Database


class DebtService:
    """Service for managing debts and payments"""
    
    def __init__(self, db: Database):
        self.db = db
        
    def get_all(self, search: str = "", status: str = "") -> List[Dict]:
        """Get all debts with filtering"""
        query = """
            SELECT d.*, o.order_number, o.order_name, o.grand_total, o.created_at as order_created_at,
                   o.customer_name as order_customer_name,
                   c.name as customer_name
            FROM debts d
            LEFT JOIN orders o ON d.order_id = o.id
            LEFT JOIN customers c ON d.customer_id = c.id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (o.order_number LIKE ? OR o.customer_name LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
            
        if status:
            query += " AND d.status = ?"
            params.append(status)
            
        query += " ORDER BY d.created_at DESC"
        return self.db.fetch_all(query, tuple(params))

    def get_orders_without_debt(self) -> List[Dict]:
        """Get B2B orders that do not have a debt record yet."""
        return self.db.fetch_all(
            """
            SELECT o.id, o.order_number, o.order_name, o.customer_id, o.customer_name, o.grand_total
            FROM orders o
            LEFT JOIN debts d ON d.order_id = o.id
            WHERE o.order_type = 'b2b' AND d.id IS NULL
            ORDER BY o.created_at DESC
            """
        )
        
    def get_by_id(self, debt_id: int) -> Optional[Dict]:
        """Get debt by ID with payments"""
        debt = self.db.fetch_one("""
            SELECT d.*, o.order_number, o.grand_total, o.customer_name as order_customer_name,
                   c.name as customer_name, c.phone, c.email, c.address
            FROM debts d
            LEFT JOIN orders o ON d.order_id = o.id
            LEFT JOIN customers c ON d.customer_id = c.id
            WHERE d.id = ?
        """, (debt_id,))
        
        if debt:
            # Get order items
            order_items = self.db.fetch_all(
                "SELECT * FROM order_items WHERE order_id = ? ORDER BY id",
                (debt['order_id'],)
            )
            debt['order_items'] = order_items
            
            # Get payments
            payments = self.db.fetch_all(
                "SELECT * FROM debt_payments WHERE debt_id = ? ORDER BY paid_at DESC",
                (debt_id,)
            )
            debt['payments'] = payments
            
        return debt
        
    def create(self, data: Dict) -> int:
        """Create new debt from order"""
        query = """
            INSERT INTO debts 
                (order_id, customer_id, original_amount, paid_amount, remaining_amount,
                 status, notes, due_date)
            VALUES (?, ?, ?, 0, ?, ?, ?, ?)
        """
        cursor = self.db.execute(query, (
            data.get('order_id'),
            data.get('customer_id'),
            data.get('original_amount'),
            data.get('original_amount'),  # remaining = original initially
            'pending',
            data.get('notes'),
            data.get('due_date')
        ))
        return cursor.lastrowid
        
    def add_payment(self, debt_id: int, data: Dict) -> int:
        """Add payment to debt"""
        debt = self.db.fetch_one("SELECT * FROM debts WHERE id = ?", (debt_id,))
        if not debt:
            raise ValueError("Debt not found")
            
        remaining = debt['remaining_amount']
        amount = data.get('amount', 0)
        
        if amount > remaining:
            raise ValueError(f"Payment amount cannot exceed remaining amount ({remaining})")
            
        # Create payment
        query = """
            INSERT INTO debt_payments (debt_id, amount, payment_method, notes, paid_at)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(query, (
            debt_id,
            amount,
            data.get('payment_method'),
            data.get('notes'),
            data.get('paid_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ))
        payment_id = cursor.lastrowid
        
        # Recalculate debt
        self.recalculate_debt(debt_id)
        
        # Update order payment status
        self.update_order_payment_status(debt['order_id'])
        
        return payment_id
        
    def update_payment(self, payment_id: int, debt_id: int, data: Dict) -> bool:
        """Update existing payment"""
        self.db.execute("""
            UPDATE debt_payments 
            SET amount=?, payment_method=?, notes=?, paid_at=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (
            data.get('amount'),
            data.get('payment_method'),
            data.get('notes'),
            data.get('paid_at'),
            payment_id
        ))
        
        # Recalculate debt
        self.recalculate_debt(debt_id)
        
        debt = self.db.fetch_one("SELECT order_id FROM debts WHERE id = ?", (debt_id,))
        self.update_order_payment_status(debt['order_id'])
        
        return True
        
    def delete_payment(self, payment_id: int, debt_id: int) -> bool:
        """Delete payment"""
        debt = self.db.fetch_one("SELECT order_id FROM debts WHERE id = ?", (debt_id,))
        
        self.db.execute("DELETE FROM debt_payments WHERE id = ?", (payment_id,))
        
        # Recalculate debt
        self.recalculate_debt(debt_id)
        
        # Update order payment status
        self.update_order_payment_status(debt['order_id'])
        
        return True
        
    def delete(self, debt_id: int) -> bool:
        """Delete debt and its payments, resetting order payment status to unpaid"""
        debt = self.db.fetch_one("SELECT order_id FROM debts WHERE id = ?", (debt_id,))
        if debt:
            order_id = debt['order_id']
            # Delete payments first due to foreign keys
            self.db.execute("DELETE FROM debt_payments WHERE debt_id = ?", (debt_id,))
            self.db.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
            # Reset order payment status to unpaid
            self.db.execute("UPDATE orders SET payment_status = 'unpaid', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (order_id,))
        return True
        
    def recalculate_debt(self, debt_id: int):
        """Recalculate debt amounts (mirrors Laravel Debt::recalculate)"""
        debt = self.db.fetch_one("SELECT * FROM debts WHERE id = ?", (debt_id,))
        if not debt:
            return
            
        paid_amount_result = self.db.fetch_one(
            "SELECT SUM(amount) as total FROM debt_payments WHERE debt_id = ?",
            (debt_id,)
        )
        paid_amount = paid_amount_result['total'] or 0
        
        original_amount = debt['original_amount']
        remaining_amount = max(0, original_amount - paid_amount)
        
        if remaining_amount <= 0:
            status = 'paid'
        elif paid_amount > 0:
            status = 'partial'
        else:
            status = 'pending'
            
        self.db.execute("""
            UPDATE debts 
            SET paid_amount = ?, remaining_amount = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (paid_amount, remaining_amount, status, debt_id))
        
    def update_order_payment_status(self, order_id: int):
        """Update order payment status based on debt"""
        debt = self.db.fetch_one("SELECT * FROM debts WHERE order_id = ?", (order_id,))
        if not debt:
            return
            
        payment_status = {
            'paid': 'paid',
            'partial': 'partial'
        }.get(debt['status'], 'unpaid')
        
        self.db.execute(
            "UPDATE orders SET payment_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (payment_status, order_id)
        )
        
    def get_stats(self) -> Dict:
        """Get debt statistics"""
        debts = self.db.fetch_all("SELECT * FROM debts")
        
        total_original = 0
        total_paid = 0
        total_remaining = 0
        count_overdue = 0
        today = datetime.now().strftime('%Y-%m-%d')
        
        for debt in debts:
            grand_total = debt['original_amount']
            paid = debt['paid_amount']
            remaining = max(0, grand_total - paid)
            
            total_original += grand_total
            total_paid += paid
            total_remaining += remaining
            
            # Check overdue
            if (debt['due_date'] and 
                debt['status'] != 'paid' and 
                remaining > 0 and 
                debt['due_date'] < today):
                count_overdue += 1
                
        # Count by status
        status_counts = self.db.fetch_all("""
            SELECT status, COUNT(*) as count
            FROM debts
            GROUP BY status
        """)
        
        stats = {
            'total_original': total_original,
            'total_paid': total_paid,
            'total_remaining': total_remaining,
            'count_pending': 0,
            'count_partial': 0,
            'count_paid': 0,
            'count_overdue': count_overdue
        }
        
        for row in status_counts:
            if row['status'] == 'pending':
                stats['count_pending'] = row['count']
            elif row['status'] == 'partial':
                stats['count_partial'] = row['count']
            elif row['status'] == 'paid':
                stats['count_paid'] = row['count']
                
        return stats
