# -*- coding: utf-8 -*-
"""
Orders Page - Native PySide6 with modern design
Matches Vue.js B2BOrders/Index.vue
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QLineEdit, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QScrollArea, QMessageBox, QDialog, QFormLayout, QComboBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

import os


class OrdersPage(QWidget):
    """B2B Orders page (matches Vue.js B2BOrders/Index.vue)"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Stats cards
        stats_layout = self.create_stats_cards()
        main_layout.addLayout(stats_layout)
        
        # Filter bar
        filter_bar = self.create_filter_bar()
        main_layout.addWidget(filter_bar)
        
        # Table
        self.table = self.create_table()
        main_layout.addWidget(self.table, 1)
        
        # Load data
        self.refresh_data()
        
    def create_stats_cards(self):
        """Create stats cards row"""
        layout = QGridLayout()
        layout.setSpacing(16)
        
        self.stat_total_orders = self.create_mini_stat_card("Tổng đơn", "0", "📦", "indigo")
        layout.addWidget(self.stat_total_orders, 0, 0)
        
        self.stat_customers = self.create_mini_stat_card("Khách hàng", "0", "👥", "blue")
        layout.addWidget(self.stat_customers, 0, 1)
        
        self.stat_revenue = self.create_mini_stat_card("Doanh thu", "0đ", "💰", "emerald")
        layout.addWidget(self.stat_revenue, 0, 2)
        
        self.stat_profit = self.create_mini_stat_card("Tổng lãi", "0đ", "📈", "amber")
        layout.addWidget(self.stat_profit, 0, 3)
        
        return layout
        
    def create_mini_stat_card(self, title, value, icon, color):
        """Create mini stat card"""
        frame = QFrame()
        frame.setObjectName(f"statCard{color.capitalize()}")
        frame.setMinimumHeight(80)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        title_label = QLabel(f"{icon} {title}")
        title_label.setObjectName("statTitle")
        title_label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        layout.addWidget(value_label)
        
        frame.value_label = value_label
        return frame
        
    def create_filter_bar(self) -> QFrame:
        """Create filter bar (search + dates + buttons)"""
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setFixedHeight(60)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm mã đơn, tên khách...")
        self.search_input.setFixedWidth(300)
        layout.addWidget(self.search_input)
        
        # Date filters
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setFixedWidth(130)
        layout.addWidget(self.from_date)
        
        label_to = QLabel("→")
        label_to.setStyleSheet("color: #6B7280;")
        layout.addWidget(label_to)
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setFixedWidth(130)
        layout.addWidget(self.to_date)
        
        layout.addStretch()
        
        # Import Excel button
        btn_import = QPushButton("📥 Import Excel")
        btn_import.setObjectName("outlineButton")
        btn_import.setFixedWidth(130)
        btn_import.clicked.connect(self.import_excel)
        layout.addWidget(btn_import)
        
        # Add order button
        btn_add = QPushButton("➕ Tạo đơn hàng")
        btn_add.setObjectName("primaryButton")
        btn_add.setFixedWidth(140)
        btn_add.clicked.connect(self.create_order)
        layout.addWidget(btn_add)
        
        # Apply filter button
        btn_filter = QPushButton("🔍 Lọc")
        btn_filter.setObjectName("successButton")
        btn_filter.setFixedWidth(80)
        btn_filter.clicked.connect(self.refresh_data)
        layout.addWidget(btn_filter)
        
        return frame
        
    def create_table(self) -> QTableWidget:
        """Create orders table"""
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Mã đơn", "Khách hàng", "Ngày đặt", "Số SP", 
            "Trước thuế", "Thuế 10%", "Tổng sau thuế", "Tiền lãi"
        ])
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        
        return table
        
    def format_currency(self, amount):
        """Format currency"""
        return f"{amount:,.0f}đ"
        
    def refresh_data(self):
        """Refresh orders data"""
        try:
            from src.services.order_service import OrderService
            
            order_service = OrderService(self.db)
            
            # Get filter values
            search = self.search_input.text()
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # Get orders
            orders = order_service.get_all(search=search, from_date=from_date, to_date=to_date)
            stats = order_service.get_stats()
            
            # Update stats
            self.stat_total_orders.value_label.setText(str(stats.get('total_orders', 0)))
            self.stat_customers.value_label.setText(str(stats.get('total_customers', 0)))
            self.stat_revenue.value_label.setText(self.format_currency(stats.get('total_revenue', 0)))
            self.stat_profit.value_label.setText(self.format_currency(stats.get('total_profit', 0)))
            
            # Update table
            self.table.setRowCount(0)
            
            for order in orders:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(order.get('order_number', '')))
                self.table.setItem(row, 1, QTableWidgetItem(order.get('customer_name', '')))
                
                date_str = order.get('created_at', '')[:10] if order.get('created_at') else ''
                self.table.setItem(row, 2, QTableWidgetItem(date_str))
                
                items_count = len(order.get('items', []))
                self.table.setItem(row, 3, QTableWidgetItem(str(items_count)))
                
                self.table.setItem(row, 4, QTableWidgetItem(self.format_currency(order.get('total_before_tax', 0))))
                self.table.setItem(row, 5, QTableWidgetItem(self.format_currency(order.get('tax_amount', 0))))
                self.table.setItem(row, 6, QTableWidgetItem(self.format_currency(order.get('grand_total', 0))))
                self.table.setItem(row, 7, QTableWidgetItem(self.format_currency(order.get('total_profit', 0))))
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải đơn hàng: {str(e)}")
            
    def import_excel(self):
        """Import orders from Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if not file_path:
            return
            
        try:
            from src.services.excel_service import ExcelService
            from src.services.order_service import OrderService
            
            excel_service = ExcelService()
            order_service = OrderService(self.db)
            
            result = excel_service.import_orders_from_excel(file_path, order_service)
            
            QMessageBox.information(
                self, "Import thành công",
                f"Đã import {result.get('total', 0)} đơn hàng\n"
                f"Thành công: {result.get('success', 0)}\n"
                f"Lỗi: {result.get('failed', 0)}"
            )
            
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Import thất bại: {str(e)}")
            
    def create_order(self):
        """Create new order dialog"""
        QMessageBox.information(self, "Thông báo", "Tính năng đang được phát triển")
