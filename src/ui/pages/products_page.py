# -*- coding: utf-8 -*-
"""
Products Page - Native PySide6 with modern design
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QDoubleSpinBox, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ProductsPage(QWidget):
    """Products page"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Table
        self.table = self.create_table()
        main_layout.addWidget(self.table, 1)
        
        self.refresh_data()
        
    def create_top_bar(self) -> QFrame:
        """Create top bar"""
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setFixedHeight(60)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm tên, mã sản phẩm...")
        self.search_input.setFixedWidth(300)
        layout.addWidget(self.search_input)
        
        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Tất cả danh mục"])
        self.category_combo.setFixedWidth(200)
        layout.addWidget(self.category_combo)
        
        layout.addStretch()
        
        # Add product button
        btn_add = QPushButton("➕ Thêm sản phẩm")
        btn_add.setObjectName("primaryButton")
        btn_add.setFixedWidth(150)
        btn_add.clicked.connect(self.add_product)
        layout.addWidget(btn_add)
        
        # Refresh button
        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setObjectName("outlineButton")
        btn_refresh.setFixedWidth(110)
        btn_refresh.clicked.connect(self.refresh_data)
        layout.addWidget(btn_refresh)
        
        return frame
        
    def create_table(self) -> QTableWidget:
        """Create products table"""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Mã SP", "Tên sản phẩm", "Danh mục", "Giá nhập", "Giá bán", "Tồn kho", "Trạng thái"
        ])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        
        return table
        
    def format_currency(self, amount):
        """Format currency"""
        return f"{amount:,.0f}đ"
        
    def refresh_data(self):
        """Refresh products data"""
        try:
            from src.services.product_service import ProductService
            
            product_service = ProductService(self.db)
            search = self.search_input.text()
            
            products = product_service.get_all(search=search)
            
            # Update table
            self.table.setRowCount(0)
            
            for product in products:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(product.get('sku', '')))
                self.table.setItem(row, 1, QTableWidgetItem(product.get('name', '')))
                self.table.setItem(row, 2, QTableWidgetItem(product.get('category_name', '')))
                self.table.setItem(row, 3, QTableWidgetItem(self.format_currency(product.get('purchase_price', 0))))
                self.table.setItem(row, 4, QTableWidgetItem(self.format_currency(product.get('sale_price', 0))))
                self.table.setItem(row, 5, QTableWidgetItem(str(product.get('stock', 0))))
                
                # Status badge
                is_active = product.get('is_active', True)
                stock = product.get('stock', 0)
                
                status_frame = QFrame()
                status_frame.setContentsMargins(4, 2, 4, 2)
                status_layout = QHBoxLayout(status_frame)
                status_layout.setContentsMargins(8, 4, 8, 4)
                
                status_label = QLabel()
                status_label.setAlignment(Qt.AlignCenter)
                status_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                
                if not is_active:
                    status_label.setText("❌ Ngừng bán")
                    status_label.setStyleSheet("color: #991B1B; background-color: #FEE2E2; border-radius: 12px; padding: 4px 12px;")
                elif stock <= 0:
                    status_label.setText("⚠️ Hết hàng")
                    status_label.setStyleSheet("color: #92400E; background-color: #FEF3C7; border-radius: 12px; padding: 4px 12px;")
                elif stock < 10:
                    status_label.setText("📉 Sắp hết")
                    status_label.setStyleSheet("color: #92400E; background-color: #FEF3C7; border-radius: 12px; padding: 4px 12px;")
                else:
                    status_label.setText("✅ Còn hàng")
                    status_label.setStyleSheet("color: #065F46; background-color: #D1FAE5; border-radius: 12px; padding: 4px 12px;")
                    
                status_layout.addWidget(status_label)
                self.table.setCellWidget(row, 6, status_frame)
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải sản phẩm: {str(e)}")
            
    def add_product(self):
        """Add new product dialog"""
        dialog = ProductDialog(self)
        if dialog.exec():
            product_data = dialog.get_data()
            
            try:
                from src.services.product_service import ProductService
                product_service = ProductService(self.db)
                
                product_id = product_service.create(product_data)
                
                QMessageBox.information(self, "Thành công", f"Đã thêm sản phẩm #{product_id}")
                self.refresh_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể thêm sản phẩm: {str(e)}")


class ProductDialog(QDialog):
    """Dialog for adding/editing product"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm sản phẩm mới")
        self.setMinimumWidth(600)
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Sản phẩm ABC")
        form_layout.addRow("Tên sản phẩm *:", self.name_input)
        
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("PRD-001")
        form_layout.addRow("Mã sản phẩm:", self.sku_input)
        
        self.category_input = QComboBox()
        self.category_input.addItems(["Chưa phân loại", "Danh mục 1", "Danh mục 2"])
        form_layout.addRow("Danh mục:", self.category_input)
        
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setMaximum(1000000000)
        self.purchase_price_input.setSuffix(" đ")
        form_layout.addRow("Giá nhập:", self.purchase_price_input)
        
        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setMaximum(1000000000)
        self.sale_price_input.setSuffix(" đ")
        form_layout.addRow("Giá bán:", self.sale_price_input)
        
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(1000000)
        form_layout.addRow("Tồn kho:", self.stock_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_cancel = QPushButton("❌ Hủy")
        btn_cancel.setObjectName("outlineButton")
        btn_cancel.setFixedWidth(100)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("💾 Lưu")
        btn_save.setObjectName("successButton")
        btn_save.setFixedWidth(100)
        btn_save.clicked.connect(self.accept)
        button_layout.addWidget(btn_save)
        
        layout.addLayout(button_layout)
        
    def get_data(self):
        """Get product data from form"""
        return {
            'name': self.name_input.text().strip(),
            'sku': self.sku_input.text().strip(),
            'purchase_price': self.purchase_price_input.value(),
            'sale_price': self.sale_price_input.value(),
            'stock': self.stock_input.value(),
            'is_active': True,
        }
