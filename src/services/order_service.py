# -*- coding: utf-8 -*-
"""
Order Service - Handles B2B orders
Mirrors: app/Http/Controllers/Admin/B2BOrderController.php
"""
import random
import string
from datetime import datetime, date
from typing import List, Optional, Dict
from src.database import Database


class OrderService:
    """Service for managing B2B orders"""
    
    def __init__(self, db: Database):
        self.db = db
        
    def generate_order_number(self, order_date: str = None) -> str:
        """Generate unique order number like ORD-20240115-ABCDE"""
        if order_date:
            date_str = order_date.replace('-', '')
        else:
            date_str = datetime.now().strftime('%Y%m%d')
        
        random_str = ''.join(random.choices(string.ascii_uppercase, k=5))
        return f"ORD-{date_str}-{random_str}"
        
    def get_all(self, search: str = "", from_date: str = "", to_date: str = "") -> List[Dict]:
        """Get all B2B orders"""
        query = """
            SELECT o.*, c.name as customer_full_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE o.order_type = 'b2b'
        """
        params = []
        
        if search:
            query += " AND (o.order_number LIKE ? OR o.customer_name LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
            
        if from_date:
            query += " AND o.created_at >= ?"
            params.append(from_date)
            
        if to_date:
            query += " AND o.created_at <= ?"
            params.append(to_date)
            
        query += " ORDER BY o.created_at DESC"
        return self.db.fetch_all(query, tuple(params))
        
    def get_by_id(self, order_id: int) -> Optional[Dict]:
        """Get order by ID with items"""
        order = self.db.fetch_one("""
            SELECT o.*, c.name as customer_full_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE o.id = ?
        """, (order_id,))
        
        if order:
            items = self.db.fetch_all(
                "SELECT * FROM order_items WHERE order_id = ? ORDER BY id",
                (order_id,)
            )
            order['items'] = items
            
            # Get debt info
            debt = self.db.fetch_one("SELECT * FROM debts WHERE order_id = ?", (order_id,))
            if debt:
                payments = self.db.fetch_all(
                    "SELECT * FROM debt_payments WHERE debt_id = ? ORDER BY paid_at DESC",
                    (debt['id'],)
                )
                debt['payments'] = payments
                order['debt'] = debt
                
        return order
        
    def create(self, data: Dict, items: List[Dict]) -> int:
        """Create new B2B order with items"""
        # Calculate totals
        subtotal = sum(
            item.get('line_total', 0) or (item.get('unit_price', 0) * item.get('quantity', 0))
            for item in items
            if item.get('type') != 'category'
        )
        
        tax_rate = data.get('tax_rate', 10)
        tax_amount = round(subtotal * tax_rate / 100, 2) if tax_rate > 0 else 0
        grand_total = subtotal + tax_amount
        total_profit = sum(item.get('total_profit', 0) for item in items)
        
        # Generate order number
        order_number = self.generate_order_number(data.get('order_date'))
        
        # Create order
        query = """
            INSERT INTO orders 
                (order_number, order_name, customer_id, customer_name, customer_phone,
                 customer_email, shipping_address, delivery_date, notes, subtotal,
                 total_before_tax, tax_amount, tax_rate, shipping_fee, discount_amount,
                 grand_total, total_profit, status, payment_status, order_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(query, (
            order_number,
            data.get('order_name'),
            data.get('customer_id'),
            data.get('customer_name'),
            data.get('customer_phone'),
            data.get('customer_email'),
            data.get('shipping_address'),
            data.get('delivery_date'),
            data.get('notes'),
            subtotal,
            subtotal,
            tax_amount,
            tax_rate,
            0,
            0,
            grand_total,
            total_profit,
            data.get('status', 'pending'),
            'unpaid',
            'b2b',
            data.get('order_date', datetime.now().strftime('%Y-%m-%d'))
        ))
        order_id = cursor.lastrowid
        
        # Create order items
        for item in items:
            if item.get('type') == 'category':
                # Category header row
                self.db.execute("""
                    INSERT INTO order_items 
                        (order_id, product_name, variant_sku, price, quantity, variant_attributes)
                    VALUES (?, ?, '', 0, 0, ?)
                """, (order_id, item.get('description'), '{"type": "category"}'))
            else:
                self.db.execute("""
                    INSERT INTO order_items 
                        (order_id, product_name, variant_sku, origin, unit, price, quantity,
                         cost_price, selling_price, business_pct, profit_per_kg, weight_kg,
                         total_profit, line_total, variant_attributes, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_id,
                    item.get('description'),
                    item.get('product_code', self.generate_sku()),
                    item.get('origin'),
                    item.get('unit'),
                    item.get('unit_price', 0),
                    item.get('quantity', 0),
                    item.get('cost_price'),
                    item.get('selling_price'),
                    item.get('business_pct'),
                    item.get('profit_per_kg'),
                    item.get('weight_kg'),
                    item.get('total_profit', 0),
                    item.get('line_total', 0),
                    '{"note": "' + (item.get('note', '') or '') + '"}',
                    item.get('note')
                ))
                
        return order_id
        
    def update(self, order_id: int, data: Dict, items: List[Dict]) -> bool:
        """Update order and items"""
        # Recalculate totals
        subtotal = sum(
            item.get('line_total', 0) or (item.get('unit_price', 0) * item.get('quantity', 0))
            for item in items
            if item.get('type') != 'category'
        )
        
        tax_rate = data.get('tax_rate', 10)
        tax_amount = round(subtotal * tax_rate / 100, 2) if tax_rate > 0 else 0
        grand_total = subtotal + tax_amount
        total_profit = sum(item.get('total_profit', 0) for item in items)
        
        # Update payment status based on existing debt
        debt = self.db.fetch_one("SELECT * FROM debts WHERE order_id = ?", (order_id,))
        payment_status = 'unpaid'
        
        if debt:
            paid_amount = debt['paid_amount']
            if paid_amount <= 0:
                payment_status = 'unpaid'
            elif paid_amount >= grand_total:
                payment_status = 'paid'
            else:
                payment_status = 'partial'
                
            # Update debt original amount
            self.db.execute(
                "UPDATE debts SET original_amount = ?, updated_at = CURRENT_TIMESTAMP WHERE order_id = ?",
                (grand_total, order_id)
            )
            self.recalculate_debt(debt['id'])
            
            # Read updated debt status
            debt_updated = self.db.fetch_one("SELECT * FROM debts WHERE id = ?", (debt['id'],))
            payment_status = {
                'paid': 'paid',
                'partial': 'partial'
            }.get(debt_updated['status'], 'unpaid')
        
        # Update order
        self.db.execute("""
            UPDATE orders 
            SET order_name=?, customer_name=?, customer_phone=?, notes=?, delivery_date=?,
                subtotal=?, total_before_tax=?, tax_amount=?, grand_total=?, total_profit=?,
                payment_status=?, status=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (
            data.get('order_name'),
            data.get('customer_name'),
            data.get('customer_phone'),
            data.get('notes'),
            data.get('delivery_date'),
            subtotal,
            subtotal,
            tax_amount,
            grand_total,
            total_profit,
            payment_status,
            data.get('status'),
            order_id
        ))
        
        # Delete old items and create new ones
        self.db.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        
        for item in items:
            if item.get('type') == 'category':
                self.db.execute("""
                    INSERT INTO order_items 
                        (order_id, product_name, variant_sku, price, quantity, variant_attributes)
                    VALUES (?, ?, '', 0, 0, ?)
                """, (order_id, item.get('description'), '{"type": "category"}'))
            else:
                self.db.execute("""
                    INSERT INTO order_items 
                        (order_id, product_name, variant_sku, origin, unit, price, quantity,
                         cost_price, selling_price, business_pct, profit_per_kg, weight_kg,
                         total_profit, line_total, variant_attributes, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_id,
                    item.get('description'),
                    item.get('product_code', self.generate_sku()),
                    item.get('origin'),
                    item.get('unit'),
                    item.get('unit_price', 0),
                    item.get('quantity', 0),
                    item.get('cost_price'),
                    item.get('selling_price'),
                    item.get('business_pct'),
                    item.get('profit_per_kg'),
                    item.get('weight_kg'),
                    item.get('total_profit', 0),
                    item.get('line_total', 0),
                    '{"note": "' + (item.get('note', '') or '') + '"}',
                    item.get('note')
                ))
                
        return True
        
    def update_status(self, order_id: int, status: str) -> bool:
        """Update order status"""
        self.db.execute(
            "UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, order_id)
        )
        return True
        
    def delete(self, order_id: int) -> bool:
        """Delete order"""
        self.db.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        return True
        
    def get_stats(self) -> Dict:
        """Get order statistics"""
        stats = self.db.fetch_one("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(grand_total) as total_revenue,
                SUM(total_profit) as total_profit,
                COUNT(DISTINCT customer_name) as total_customers
            FROM orders
            WHERE order_type = 'b2b'
        """)
        
        return {
            'total_orders': stats['total_orders'] or 0,
            'total_revenue': stats['total_revenue'] or 0,
            'total_profit': stats['total_profit'] or 0,
            'total_customers': stats['total_customers'] or 0
        }
        
    def generate_sku(self) -> str:
        """Generate random SKU"""
        return ''.join(random.choices(string.ascii_uppercase, k=8))
        
    def recalculate_debt(self, debt_id: int):
        """Recalculate debt amounts based on payments (mirrors Laravel Debt::recalculate)"""
        debt = self.db.fetch_one("SELECT * FROM debts WHERE id = ?", (debt_id,))
        if not debt:
            return
            
        paid_amount = self.db.fetch_one(
            "SELECT SUM(amount) as total FROM debt_payments WHERE debt_id = ?",
            (debt_id,)
        )['total'] or 0
        
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
