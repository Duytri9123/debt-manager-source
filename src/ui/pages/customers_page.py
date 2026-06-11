# -*- coding: utf-8 -*-
"""
Customers Page - Native PySide6 with modern design
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class CustomersPage(QWidget):
    """Customers page"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Top bar with search and add button
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
        self.search_input.setPlaceholderText("🔍 Tìm tên, SĐT, email...")
        self.search_input.setFixedWidth(350)
        layout.addWidget(self.search_input)
        
        layout.addStretch()
        
        # Add customer button
        btn_add = QPushButton("➕ Thêm khách hàng")
        btn_add.setObjectName("primaryButton")
        btn_add.setFixedWidth(170)
        btn_add.clicked.connect(self.add_customer)
        layout.addWidget(btn_add)
        
        # Refresh button
        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setObjectName("outlineButton")
        btn_refresh.setFixedWidth(110)
        btn_refresh.clicked.connect(self.refresh_data)
        layout.addWidget(btn_refresh)
        
        return frame
        
    def create_table(self) -> QTableWidget:
        """Create customers table"""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Mã KH", "Tên khách hàng", "SĐT", "Email", "Địa chỉ", "Trạng thái"
        ])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        
        return table
        
    def refresh_data(self):
        """Refresh customers data"""
        try:
            from src.services.customer_service import CustomerService
            
            customer_service = CustomerService(self.db)
            search = self.search_input.text()
            
            customers = customer_service.get_all(search=search)
            
            # Update table
            self.table.setRowCount(0)
            
            for customer in customers:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(str(customer.get('id', ''))))
                self.table.setItem(row, 1, QTableWidgetItem(customer.get('name', '')))
                self.table.setItem(row, 2, QTableWidgetItem(customer.get('phone', '')))
                self.table.setItem(row, 3, QTableWidgetItem(customer.get('email', '')))
                self.table.setItem(row, 4, QTableWidgetItem(customer.get('address', '')))
                
                # Status badge
                is_active = customer.get('is_active', True)
                status_frame = QFrame()
                status_frame.setContentsMargins(4, 2, 4, 2)
                status_layout = QHBoxLayout(status_frame)
                status_layout.setContentsMargins(8, 4, 8, 4)
                
                status_label = QLabel()
                status_label.setAlignment(Qt.AlignCenter)
                status_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                
                if is_active:
                    status_label.setText("✅ Hoạt động")
                    status_label.setStyleSheet("color: #065F46; background-color: #D1FAE5; border-radius: 12px; padding: 4px 12px;")
                else:
                    status_label.setText("❌ Ngừng hoạt động")
                    status_label.setStyleSheet("color: #991B1B; background-color: #FEE2E2; border-radius: 12px; padding: 4px 12px;")
                    
                status_layout.addWidget(status_label)
                self.table.setCellWidget(row, 5, status_frame)
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải khách hàng: {str(e)}")
            
    def add_customer(self):
        """Add new customer dialog"""
        dialog = CustomerDialog(self)
        if dialog.exec():
            customer_data = dialog.get_data()
            
            try:
                from src.services.customer_service import CustomerService
                customer_service = CustomerService(self.db)
                
                customer_id = customer_service.create(customer_data)
                
                QMessageBox.information(self, "Thành công", f"Đã thêm khách hàng #{customer_id}")
                self.refresh_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể thêm khách hàng: {str(e)}")


class CustomerDialog(QDialog):
    """Dialog for adding/editing customer"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm khách hàng mới")
        self.setMinimumWidth(500)
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
        self.name_input.setPlaceholderText("Nguyễn Văn A")
        form_layout.addRow("Tên khách hàng *:", self.name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("0912345678")
        form_layout.addRow("Số điện thoại:", self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)
        
        self.tax_code_input = QLineEdit()
        self.tax_code_input.setPlaceholderText("0123456789")
        form_layout.addRow("Mã số thuế:", self.tax_code_input)
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        self.address_input.setPlaceholderText("Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành phố")
        form_layout.addRow("Địa chỉ:", self.address_input)
        
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
        """Get customer data from form"""
        return {
            'name': self.name_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'tax_code': self.tax_code_input.text().strip(),
            'address': self.address_input.toPlainText().strip(),
            'is_active': True,
        }
