# -*- coding: utf-8 -*-
"""
Product Service - Handles all product-related operations
Mirrors: app/Http/Controllers/Admin/ProductController.php
"""
from typing import List, Optional, Dict
from src.database import Database


class ProductService:
    """Service for managing products"""
    
    def __init__(self, db: Database):
        self.db = db
        
    def get_all(self, search: str = "", category_id: int = None, status: str = "") -> List[Dict]:
        """Get all products with filtering"""
        query = """
            SELECT p.*, c.name as category_name, b.name as brand_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN brands b ON p.brand_id = b.id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (p.name LIKE ? OR p.sku LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
            
        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
            
        if status:
            query += " AND p.status = ?"
            params.append(status)
            
        query += " ORDER BY p.created_at DESC"
        return self.db.fetch_all(query, tuple(params))
        
    def get_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID with variants"""
        product = self.db.fetch_one("""
            SELECT p.*, c.name as category_name, b.name as brand_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN brands b ON p.brand_id = b.id
            WHERE p.id = ?
        """, (product_id,))
        
        if product:
            variants = self.db.fetch_all(
                "SELECT * FROM product_variants WHERE product_id = ? ORDER BY is_default DESC",
                (product_id,)
            )
            product['variants'] = variants
            
        return product
        
    def create(self, data: Dict, variants: List[Dict]) -> int:
        """Create new product with variants"""
        # Create product
        query = """
            INSERT INTO products (name, sku, description, short_description, category_id, 
                                 brand_id, origin, tax_code, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(query, (
            data.get('name'),
            data.get('sku'),
            data.get('description'),
            data.get('short_description'),
            data.get('category_id'),
            data.get('brand_id'),
            data.get('origin'),
            data.get('tax_code'),
            'active'
        ))
        product_id = cursor.lastrowid
        
        # Create variants
        for i, variant in enumerate(variants):
            self.db.execute("""
                INSERT INTO product_variants 
                    (product_id, sku, unit, cost_price, selling_price, original_price, quantity, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                variant.get('sku'),
                variant.get('unit'),
                variant.get('cost_price', 0),
                variant.get('selling_price'),
                variant.get('cost_price', 0) or variant.get('selling_price'),
                variant.get('quantity', 0),
                1 if i == 0 or variant.get('is_default') else 0
            ))
            
        return product_id
        
    def update(self, product_id: int, data: Dict, variants: List[Dict] = None) -> bool:
        """Update product"""
        self.db.execute("""
            UPDATE products 
            SET name=?, sku=?, description=?, short_description=?, category_id=?,
                brand_id=?, origin=?, tax_code=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (
            data.get('name'),
            data.get('sku'),
            data.get('description'),
            data.get('short_description'),
            data.get('category_id'),
            data.get('brand_id'),
            data.get('origin'),
            data.get('tax_code'),
            product_id
        ))
        
        # Update variants if provided
        if variants:
            # Delete old variants
            self.db.execute("DELETE FROM product_variants WHERE product_id = ?", (product_id,))
            
            # Insert new variants
            for i, variant in enumerate(variants):
                self.db.execute("""
                    INSERT INTO product_variants 
                        (product_id, sku, unit, cost_price, selling_price, original_price, quantity, is_default)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id,
                    variant.get('sku'),
                    variant.get('unit'),
                    variant.get('cost_price', 0),
                    variant.get('selling_price'),
                    variant.get('original_price', variant.get('selling_price')),
                    variant.get('quantity', 0),
                    1 if i == 0 or variant.get('is_default') else 0
                ))
                
        return True
        
    def delete(self, product_id: int) -> bool:
        """Delete product"""
        self.db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return True
        
    def get_sales_history(self, product_name: str, limit: int = 50) -> List[Dict]:
        """Get sales history for a product"""
        return self.db.fetch_all("""
            SELECT oi.*, o.order_number, o.customer_name, o.created_at as order_date, o.order_type
            FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE oi.product_name LIKE ?
            ORDER BY o.created_at DESC
            LIMIT ?
        """, (f"%{product_name}%", limit))
