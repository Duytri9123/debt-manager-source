# -*- coding: utf-8 -*-
"""
Debts Page - Native PySide6 with modern design
Matches Vue.js Debts/Index.vue
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QScrollArea, QMessageBox, QDialog, QFormLayout, QDoubleSpinBox,
    QDateEdit, QTextEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from datetime import datetime


class DebtsPage(QWidget):
    """Debts page (matches Vue.js Debts/Index.vue)"""
    
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
        
        self.refresh_data()
        
    def create_stats_cards(self):
        """Create debt stats cards"""
        layout = QGridLayout()
        layout.setSpacing(16)
        
        self.stat_total_debt = self.create_mini_stat_card("Tổng công nợ", "0đ", "💰", "red")
        layout.addWidget(self.stat_total_debt, 0, 0)
        
        self.stat_paid = self.create_mini_stat_card("Đã thanh toán", "0đ", "✅", "emerald")
        layout.addWidget(self.stat_paid, 0, 1)
        
        self.stat_remaining = self.create_mini_stat_card("Còn phải thu", "0đ", "⚠️", "amber")
        layout.addWidget(self.stat_remaining, 0, 2)
        
        self.stat_overdue = self.create_mini_stat_card("Quá hạn", "0 đơn", "🚨", "red")
        layout.addWidget(self.stat_overdue, 0, 3)
        
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
        """Create filter bar"""
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setFixedHeight(60)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm khách hàng, mã đơn...")
        self.search_input.setFixedWidth(300)
        layout.addWidget(self.search_input)
        
        # Status filter
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Tất cả", "Chưa thanh toán", "Đã thanh toán một phần", "Đã thanh toán"])
        self.status_combo.setFixedWidth(200)
        layout.addWidget(self.status_combo)
        
        layout.addStretch()
        
        # Filter button
        btn_filter = QPushButton("🔍 Lọc")
        btn_filter.setObjectName("successButton")
        btn_filter.setFixedWidth(80)
        btn_filter.clicked.connect(self.refresh_data)
        layout.addWidget(btn_filter)
        
        return frame
        
    def create_table(self) -> QTableWidget:
        """Create debts table"""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Mã đơn", "Khách hàng", "Tổng tiền", "Đã thanh toán", 
            "Còn nợ", "Trạng thái", "Hạn thanh toán"
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
        table.doubleClicked.connect(self.view_debt_detail)
        
        return table
        
    def format_currency(self, amount):
        """Format currency"""
        return f"{amount:,.0f}đ"
        
    def refresh_data(self):
        """Refresh debts data"""
        try:
            from src.services.debt_service import DebtService
            
            debt_service = DebtService(self.db)
            
            search = self.search_input.text()
            status_map = {
                "Tất cả": "",
                "Chưa thanh toán": "unpaid",
                "Đã thanh toán một phần": "partial",
                "Đã thanh toán": "paid",
            }
            status = status_map.get(self.status_combo.currentText(), "")
            
            debts = debt_service.get_all(search=search, status=status)
            stats = debt_service.get_stats()
            
            # Update stats
            self.stat_total_debt.value_label.setText(
                self.format_currency(stats.get('total_original', 0))
            )
            self.stat_paid.value_label.setText(
                self.format_currency(stats.get('total_paid', 0))
            )
            self.stat_remaining.value_label.setText(
                self.format_currency(stats.get('total_remaining', 0))
            )
            self.stat_overdue.value_label.setText(
                f"{stats.get('count_overdue', 0)} đơn"
            )
            
            # Update table
            self.table.setRowCount(0)
            
            for debt in debts:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(debt.get('order_number', '')))
                self.table.setItem(row, 1, QTableWidgetItem(debt.get('customer_name', '')))
                self.table.setItem(row, 2, QTableWidgetItem(self.format_currency(debt.get('original_amount', 0))))
                self.table.setItem(row, 3, QTableWidgetItem(self.format_currency(debt.get('paid_amount', 0))))
                self.table.setItem(row, 4, QTableWidgetItem(self.format_currency(debt.get('remaining_amount', 0))))
                
                # Status badge
                status = debt.get('payment_status', 'unpaid')
                status_badge = self.create_status_badge(status)
                self.table.setCellWidget(row, 5, status_badge)
                
                due_date = debt.get('due_date', '')[:10] if debt.get('due_date') else ''
                self.table.setItem(row, 6, QTableWidgetItem(due_date))
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải công nợ: {str(e)}")
            
    def create_status_badge(self, status):
        """Create status badge widget"""
        frame = QFrame()
        frame.setContentsMargins(4, 2, 4, 2)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)
        
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        if status == 'paid':
            label.setText("✅ Đã thanh toán")
            label.setStyleSheet("color: #065F46; background-color: #D1FAE5; border-radius: 12px; padding: 4px 12px;")
        elif status == 'partial':
            label.setText("⚠️ Một phần")
            label.setStyleSheet("color: #92400E; background-color: #FEF3C7; border-radius: 12px; padding: 4px 12px;")
        else:
            label.setText("❌ Chưa thanh toán")
            label.setStyleSheet("color: #991B1B; background-color: #FEE2E2; border-radius: 12px; padding: 4px 12px;")
            
        layout.addWidget(label)
        return frame
        
    def view_debt_detail(self):
        """View debt detail dialog"""
        row = self.table.currentRow()
        if row < 0:
            return
            
        order_number = self.table.item(row, 0).text()
        QMessageBox.information(self, "Chi tiết công nợ", f"Đơn hàng: {order_number}")
