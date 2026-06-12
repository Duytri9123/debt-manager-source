# -*- coding: utf-8 -*-
"""
Advance Service - Handles advance requests.
Mirrors: app/Http/Controllers/Admin/AdvanceController.php
"""
from datetime import datetime
from typing import Dict, List, Optional

from src.database import Database


class AdvanceService:
    """Service for managing advances."""

    TYPES = {
        "employee": "Tạm ứng nhân viên",
        "customer": "Đặt cọc khách hàng",
        "supplier": "Tạm ứng nhà cung cấp",
    }

    STATUSES = {
        "pending": "Chờ duyệt",
        "approved": "Đã duyệt",
        "settled": "Đã quyết toán",
        "cancelled": "Đã hủy",
    }

    def __init__(self, db: Database):
        self.db = db

    def generate_advance_number(self) -> str:
        """Generate ADV-YYYYMMDD-0001 style number."""
        today = datetime.now().strftime("%Y-%m-%d")
        result = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM advances WHERE date(created_at) = ?",
            (today,),
        )
        sequence = (result["count"] if result else 0) + 1
        return f"ADV-{today.replace('-', '')}-{sequence:04d}"

    def get_all(self, search: str = "", type_filter: str = "", status: str = "") -> List[Dict]:
        """Get advances with filters."""
        query = """
            SELECT a.*, c.name as customer_name
            FROM advances a
            LEFT JOIN customers c ON a.customer_id = c.id
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (a.advance_number LIKE ? OR a.purpose LIKE ? OR a.employee_name LIKE ? OR a.supplier_name LIKE ? OR c.name LIKE ?)"
            value = f"%{search}%"
            params.extend([value, value, value, value, value])

        if type_filter:
            query += " AND a.type = ?"
            params.append(type_filter)

        if status:
            query += " AND a.status = ?"
            params.append(status)

        query += " ORDER BY a.created_at DESC"
        return self.db.fetch_all(query, tuple(params))

    def get_by_id(self, advance_id: int) -> Optional[Dict]:
        """Get an advance by ID."""
        return self.db.fetch_one(
            """
            SELECT a.*, c.name as customer_name
            FROM advances a
            LEFT JOIN customers c ON a.customer_id = c.id
            WHERE a.id = ?
            """,
            (advance_id,),
        )

    def create(self, data: Dict) -> int:
        """Create an advance."""
        number = self.generate_advance_number()
        query = """
            INSERT INTO advances (
                advance_number, type, created_by, employee_name, customer_id,
                supplier_name, advance_date, expected_return_date, amount,
                returned_amount, status, purpose, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(
            query,
            (
                number,
                data.get("type"),
                data.get("created_by", "Admin"),
                data.get("employee_name"),
                data.get("customer_id"),
                data.get("supplier_name"),
                data.get("advance_date"),
                data.get("expected_return_date"),
                data.get("amount", 0),
                data.get("returned_amount", 0),
                data.get("status", "pending"),
                data.get("purpose"),
                data.get("notes"),
            ),
        )
        return cursor.lastrowid

    def update(self, advance_id: int, data: Dict) -> bool:
        """Update an advance."""
        self.db.execute(
            """
            UPDATE advances
            SET type=?, employee_name=?, customer_id=?, supplier_name=?,
                advance_date=?, expected_return_date=?, amount=?,
                returned_amount=?, status=?, purpose=?, notes=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (
                data.get("type"),
                data.get("employee_name"),
                data.get("customer_id"),
                data.get("supplier_name"),
                data.get("advance_date"),
                data.get("expected_return_date"),
                data.get("amount", 0),
                data.get("returned_amount", 0),
                data.get("status", "pending"),
                data.get("purpose"),
                data.get("notes"),
                advance_id,
            ),
        )
        return True

    def delete(self, advance_id: int) -> bool:
        """Delete an advance."""
        self.db.execute("DELETE FROM advances WHERE id = ?", (advance_id,))
        return True

    def get_stats(self) -> Dict:
        """Get advance statistics."""
        row = self.db.fetch_one(
            """
            SELECT
                COUNT(*) as total_count,
                SUM(amount) as total_amount,
                SUM(returned_amount) as returned_amount,
                SUM(amount - returned_amount) as remaining_amount
            FROM advances
            WHERE status != 'cancelled'
            """
        )
        return {
            "total_count": row["total_count"] or 0,
            "total_amount": row["total_amount"] or 0,
            "returned_amount": row["returned_amount"] or 0,
            "remaining_amount": row["remaining_amount"] or 0,
        }
