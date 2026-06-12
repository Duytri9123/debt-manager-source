# -*- coding: utf-8 -*-
"""
Customer Service - Handles all customer-related operations
Mirrors: app/Http/Controllers/Admin/CustomerController.php
"""
from datetime import datetime
from typing import List, Optional, Dict
from src.database import Database


class CustomerService:
    """Service for managing customers"""
    
    def __init__(self, db: Database):
        self.db = db
        
    def get_all(self, search: str = "", is_active: bool = True) -> List[Dict]:
        """Get all customers with optional filtering"""
        query = """
            SELECT c.*,
                   (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) as orders_count,
                   (SELECT COALESCE(SUM(o.grand_total), 0) FROM orders o WHERE o.customer_id = c.id) as total_order_value,
                   (SELECT COALESCE(SUM(d.remaining_amount), 0) FROM debts d WHERE d.customer_id = c.id AND d.status IN ('pending', 'partial')) as remaining_debt,
                   0 as purchase_invoices_count
            FROM customers c
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (c.name LIKE ? OR c.phone LIKE ? OR c.email LIKE ? OR c.address LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
            
        if is_active is not None:
            query += " AND c.is_active = ?"
            params.append(1 if is_active else 0)
            
        query += " ORDER BY c.created_at DESC"
        return self.db.fetch_all(query, tuple(params))
        
    def get_by_id(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID"""
        return self.db.fetch_one("SELECT * FROM customers WHERE id = ?", (customer_id,))
        
    def create(self, data: Dict) -> int:
        """Create new customer"""
        query = """
            INSERT INTO customers (name, phone, email, address, tax_code, notes, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(query, (
            data.get('name'),
            data.get('phone'),
            data.get('email'),
            data.get('address'),
            data.get('tax_code'),
            data.get('notes'),
            1 if data.get('is_active', True) else 0
        ))
        return cursor.lastrowid
        
    def update(self, customer_id: int, data: Dict) -> bool:
        """Update customer"""
        query = """
            UPDATE customers 
            SET name=?, phone=?, email=?, address=?, tax_code=?, notes=?, is_active=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """
        self.db.execute(query, (
            data.get('name'),
            data.get('phone'),
            data.get('email'),
            data.get('address'),
            data.get('tax_code'),
            data.get('notes'),
            1 if data.get('is_active', True) else 0,
            customer_id
        ))
        return True
        
    def delete(self, customer_id: int) -> bool:
        """Delete customer (soft delete by setting inactive)"""
        self.db.execute(
            "UPDATE customers SET is_active=0, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (customer_id,)
        )
        return True
        
    def get_stats(self) -> Dict:
        """Get customer statistics"""
        total = self.db.fetch_one("SELECT COUNT(*) as count FROM customers WHERE is_active=1")
        return {
            'total_customers': total['count'] if total else 0
        }
