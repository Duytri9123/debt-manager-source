# -*- coding: utf-8 -*-
"""
Database layer - SQLite
Mirrors Laravel Eloquent models with SQLAlchemy-like pattern
"""
import sqlite3
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import json


class Database:
    """Database manager for SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def initialize(self):
        """Create all tables"""
        self.connect()
        cursor = self.conn.cursor()
        
        # Categories
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        """)
        
        # Brands
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Customers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                tax_code TEXT,
                is_active BOOLEAN DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Products
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT,
                description TEXT,
                short_description TEXT,
                category_id INTEGER,
                brand_id INTEGER,
                origin TEXT,
                tax_code TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (brand_id) REFERENCES brands(id)
            )
        """)
        
        # Product Variants
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                sku TEXT NOT NULL,
                unit TEXT,
                cost_price REAL DEFAULT 0,
                selling_price REAL NOT NULL,
                original_price REAL,
                quantity INTEGER DEFAULT 0,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        
        # Orders (B2B Orders)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                order_name TEXT,
                customer_id INTEGER,
                customer_name TEXT NOT NULL,
                customer_phone TEXT,
                customer_email TEXT,
                shipping_address TEXT,
                delivery_date DATE,
                notes TEXT,
                subtotal REAL DEFAULT 0,
                total_before_tax REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                tax_rate REAL DEFAULT 10,
                shipping_fee REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                grand_total REAL DEFAULT 0,
                total_profit REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                payment_status TEXT DEFAULT 'unpaid',
                order_type TEXT DEFAULT 'b2b',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        # Order Items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_variant_id INTEGER,
                product_name TEXT NOT NULL,
                variant_sku TEXT,
                origin TEXT,
                unit TEXT,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                cost_price REAL,
                selling_price REAL,
                business_pct REAL,
                profit_per_kg REAL,
                weight_kg REAL,
                total_profit REAL,
                line_total REAL,
                variant_attributes TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )
        """)
        
        # Debts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL UNIQUE,
                customer_id INTEGER,
                original_amount REAL NOT NULL,
                paid_amount REAL DEFAULT 0,
                remaining_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                due_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        # Debt Payments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debt_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT,
                notes TEXT,
                paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debt_id) REFERENCES debts(id) ON DELETE CASCADE
            )
        """)
        
        # Site Settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS site_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON orders(payment_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_debts_order ON debts(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_debts_status ON debts(status)")
        
        # Insert default settings
        cursor.execute("""
            INSERT OR IGNORE INTO site_settings (key, value) VALUES 
            ('tax_rate', '10'),
            ('tax_enabled', '1'),
            ('currency', 'VND')
        """)
        
        self.conn.commit()
        
    def execute(self, query: str, params: tuple = ()):
        """Execute a query"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
        
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one row"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
        
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows"""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    def commit(self):
        """Commit transaction"""
        self.conn.commit()
        
    def rollback(self):
        """Rollback transaction"""
        self.conn.rollback()
