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
            SELECT o.*, c.name as customer_full_name,
                   COUNT(oi.id) as items_count,
                   d.paid_amount as debt_paid_amount,
                   d.remaining_amount as debt_remaining_amount,
                   d.status as debt_status
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_items oi ON oi.order_id = o.id
            LEFT JOIN debts d ON d.order_id = o.id
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
            
        query += " GROUP BY o.id ORDER BY o.created_at DESC"
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
        customer_id = data.get('customer_id')
        if not customer_id and data.get('customer_name'):
            customer_id = self.upsert_customer(
                data.get('customer_name'),
                data.get('customer_phone'),
                data.get('customer_email'),
                data.get('customer_address') or data.get('shipping_address')
            )

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
            customer_id,
            data.get('customer_name'),
            data.get('customer_phone'),
            data.get('customer_email'),
            data.get('shipping_address') or data.get('customer_address'),
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
            data.get('payment_status', 'unpaid'),
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

        initial_payment = min(float(data.get('initial_payment') or 0), grand_total)
        payment_status = data.get('payment_status', 'unpaid')
        if data.get('create_debt') or initial_payment > 0 or payment_status != 'unpaid':
            self.create_or_update_debt(
                order_id, customer_id, grand_total, initial_payment,
                due_date=data.get('delivery_date'), notes=data.get('notes'),
                payment_status=payment_status
            )

        return order_id
        
    def update(self, order_id: int, data: Dict, items: List[Dict]) -> bool:
        """Update order and items"""
        customer_id = data.get('customer_id')
        if not customer_id and data.get('customer_name'):
            customer_id = self.upsert_customer(
                data.get('customer_name'),
                data.get('customer_phone'),
                data.get('customer_email'),
                data.get('customer_address') or data.get('shipping_address')
            )

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
        
        # Update payment status based on existing debt or create a new one
        payment_status = data.get('payment_status', 'unpaid')
        self.create_or_update_debt(
            order_id, customer_id, grand_total,
            due_date=data.get('delivery_date'), notes=data.get('notes'),
            payment_status=payment_status
        )
        
        # Read the calculated status back from the debt record
        debt = self.db.fetch_one("SELECT * FROM debts WHERE order_id = ?", (order_id,))
        if debt:
            payment_status = {'paid': 'paid', 'partial': 'partial'}.get(debt['status'], 'unpaid')
        
        # Update order
        self.db.execute("""
            UPDATE orders 
            SET order_name=?, customer_id=?, customer_name=?, customer_phone=?, notes=?,
                created_at=?, delivery_date=?,
                subtotal=?, total_before_tax=?, tax_amount=?, grand_total=?, total_profit=?,
                payment_status=?, status=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (
            data.get('order_name'),
            customer_id,
            data.get('customer_name'),
            data.get('customer_phone'),
            data.get('notes'),
            data.get('order_date'),
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
            WHERE order_type = 'b2b' AND status != 'cancelled'
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

    def upsert_customer(self, name: str, phone: str = None, email: str = None, address: str = None) -> Optional[int]:
        """Find or create a customer by name/phone, matching the Laravel flow."""
        if not name:
            return None

        customer = None
        if phone:
            customer = self.db.fetch_one("SELECT * FROM customers WHERE phone = ?", (phone,))
        if not customer:
            customer = self.db.fetch_one("SELECT * FROM customers WHERE name = ?", (name,))

        if customer:
            updates = {}
            if phone and not customer.get('phone'):
                updates['phone'] = phone
            if email and not customer.get('email'):
                updates['email'] = email
            if address and not customer.get('address'):
                updates['address'] = address

            if updates:
                fields = ", ".join(f"{key}=?" for key in updates)
                values = list(updates.values())
                values.append(customer['id'])
                self.db.execute(
                    f"UPDATE customers SET {fields}, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    tuple(values)
                )
            return customer['id']

        cursor = self.db.execute(
            """
            INSERT INTO customers (name, phone, email, address, is_active)
            VALUES (?, ?, ?, ?, 1)
            """,
            (name, phone, email, address),
        )
        return cursor.lastrowid

    def create_or_update_debt(
        self,
        order_id: int,
        customer_id: Optional[int],
        original_amount: float,
        paid_amount: float = 0,
        due_date: str = None,
        notes: str = None,
        payment_status: str = 'unpaid',
    ) -> int:
        """Create a debt record and optional first payment for an order."""
        if payment_status == 'paid':
            paid_amount = original_amount
        elif payment_status == 'unpaid':
            paid_amount = 0

        existing = self.db.fetch_one("SELECT * FROM debts WHERE order_id = ?", (order_id,))
        if existing:
            debt_id = existing['id']
            if payment_status == 'paid' and existing['remaining_amount'] > 0:
                self.db.execute(
                    """
                    INSERT INTO debt_payments (debt_id, amount, payment_method, notes, paid_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        debt_id,
                        existing['remaining_amount'],
                        'Tien mat',
                        'Cap nhat thanh toan',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    ),
                )
            elif payment_status == 'unpaid' and existing['paid_amount'] > 0:
                self.db.execute("DELETE FROM debt_payments WHERE debt_id = ?", (debt_id,))
                
            self.db.execute(
                """
                UPDATE debts
                SET original_amount=?, customer_id=?, due_date=COALESCE(?, due_date),
                    notes=COALESCE(?, notes), updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """,
                (original_amount, customer_id, due_date, notes, debt_id),
            )
        else:
            remaining = max(0, original_amount - paid_amount)
            status = 'paid' if remaining <= 0 else ('partial' if paid_amount > 0 else 'pending')
            cursor = self.db.execute(
                """
                INSERT INTO debts
                    (order_id, customer_id, original_amount, paid_amount, remaining_amount, status, due_date, notes)
                VALUES (?, ?, ?, 0, ?, ?, ?, ?)
                """,
                (order_id, customer_id, original_amount, original_amount, status, due_date, notes),
            )
            debt_id = cursor.lastrowid

            if paid_amount > 0:
                self.db.execute(
                    """
                    INSERT INTO debt_payments (debt_id, amount, payment_method, notes, paid_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        debt_id,
                        paid_amount,
                        'Tien mat',
                        'Thanh toan ban dau',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    ),
                )

        self.recalculate_debt(debt_id)
        debt = self.db.fetch_one("SELECT * FROM debts WHERE id = ?", (debt_id,))
        payment_status_db = {'paid': 'paid', 'partial': 'partial'}.get(debt['status'], 'unpaid')
        self.db.execute(
            "UPDATE orders SET payment_status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (payment_status_db, order_id),
        )
        return debt_id
        
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
