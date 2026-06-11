# -*- coding: utf-8 -*-
"""
Dashboard Page - Native PySide6 with modern design
Matches Vue.js Dashboard.vue with stat cards and charts
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DashboardPage(QWidget):
    """Dashboard page with statistics cards (matches Vue.js Dashboard.vue)"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        
        # Welcome section
        welcome_frame = self.create_welcome_section()
        content_layout.addWidget(welcome_frame)
        
        # Stats grid
        stats_grid = self.create_stats_grid()
        content_layout.addWidget(stats_grid)
        
        # Recent orders and debts
        bottom_layout = self.create_bottom_section()
        content_layout.addLayout(bottom_layout)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Load data
        self.load_data()
        
    def create_welcome_section(self) -> QFrame:
        """Create welcome section"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #6366F1, stop:1 #8B5CF6);
                border-radius: 12px;
                padding: 24px;
            }
        """)
        frame.setMinimumHeight(120)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        
        title = QLabel("👋 Chào mừng đến với Quản lý B2B")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title)
        
        subtitle = QLabel("Theo dõi đơn hàng, công nợ và khách hàng hiệu quả")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet("color: #E0E7FF;")
        layout.addWidget(subtitle)
        
        return frame
        
    def create_stats_grid(self) -> QWidget:
        """Create stats cards grid (matches Vue.js stats cards)"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # All-time stats cards
        self.card_total_orders = self.create_stat_card(
            title="TỔNG ĐƠN HÀNG",
            value="0",
            subtitle="Đơn hàng đã tạo",
            icon="📦",
            color="indigo"
        )
        layout.addWidget(self.card_total_orders, 0, 0)
        
        self.card_total_revenue = self.create_stat_card(
            title="TỔNG DOANH THU",
            value="0đ",
            subtitle="Doanh thu tất cả đơn",
            icon="💰",
            color="emerald"
        )
        layout.addWidget(self.card_total_revenue, 0, 1)
        
        self.card_total_profit = self.create_stat_card(
            title="TỔNG LÃI",
            value="0đ",
            subtitle="Lãi ròng",
            icon="📈",
            color="amber"
        )
        layout.addWidget(self.card_total_profit, 0, 2)
        
        self.card_total_debt = self.create_stat_card(
            title="CÔNG NỢ PHẢI THU",
            value="0đ",
            subtitle="Chưa thanh toán",
            icon="⚠️",
            color="red"
        )
        layout.addWidget(self.card_total_debt, 0, 3)
        
        # Period stats cards
        self.card_period_revenue = self.create_stat_card(
            title="DOANH THU THÁNG NÀY",
            value="0đ",
            subtitle="Tháng hiện tại",
            icon="💵",
            color="blue"
        )
        layout.addWidget(self.card_period_revenue, 1, 0)
        
        self.card_period_orders = self.create_stat_card(
            title="ĐƠN THÁNG NÀY",
            value="0",
            subtitle="Đơn hàng mới",
            icon="📋",
            color="indigo"
        )
        layout.addWidget(self.card_period_orders, 1, 1)
        
        self.card_new_customers = self.create_stat_card(
            title="KHÁCH HÀNG MỚI",
            value="0",
            subtitle="Tháng này",
            icon="👥",
            color="emerald"
        )
        layout.addWidget(self.card_new_customers, 1, 2)
        
        self.card_avg_order = self.create_stat_card(
            title="GIÁ TRỊ TB ĐƠN",
            value="0đ",
            subtitle="Trung bình",
            icon="📊",
            color="amber"
        )
        layout.addWidget(self.card_avg_order, 1, 3)
        
        return widget
        
    def create_stat_card(self, title: str, value: str, subtitle: str, 
                         icon: str, color: str = "indigo") -> QFrame:
        """Create a stat card matching Vue.js design"""
        frame = QFrame()
        frame.setObjectName(f"statCard{color.capitalize()}")
        frame.setMinimumHeight(120)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Icon and title row
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        top_layout.addWidget(title_label)
        
        layout.addLayout(top_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        layout.addWidget(value_label)
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("statSubtitle")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(subtitle_label)
        
        # Store references for updating
        frame.value_label = value_label
        
        return frame
        
    def create_bottom_section(self):
        """Create bottom section with recent orders and debts"""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Recent orders (will be implemented later)
        recent_orders = self.create_info_card("Đơn hàng gần đây", "Chưa có đơn hàng nào")
        layout.addWidget(recent_orders, 1)
        
        # Overdue debts (will be implemented later)
        overdue_debts = self.create_info_card("Công nợ quá hạn", "Không có công nợ quá hạn")
        layout.addWidget(overdue_debts, 1)
        
        return layout
        
    def create_info_card(self, title: str, content: str) -> QFrame:
        """Create info card"""
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setMinimumHeight(200)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)
        
        # Content
        content_label = QLabel(content)
        content_label.setFont(QFont("Segoe UI", 13))
        content_label.setStyleSheet("color: #6B7280;")
        content_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(content_label)
        
        layout.addStretch()
        
        return frame
        
    def format_currency(self, amount: float) -> str:
        """Format currency Vietnamese style"""
        if amount >= 1_000_000_000:
            return f"{amount / 1_000_000_000:,.1f} tỷ"
        elif amount >= 1_000_000:
            return f"{amount / 1_000_000:,.1f}M"
        elif amount >= 1_000:
            return f"{amount / 1_000:,.1f}K"
        else:
            return f"{amount:,.0f}"
        
    def load_data(self):
        """Load dashboard data"""
        try:
            from src.services.order_service import OrderService
            from src.services.debt_service import DebtService
            from src.services.customer_service import CustomerService
            
            order_service = OrderService(self.db)
            debt_service = DebtService(self.db)
            customer_service = CustomerService(self.db)
            
            # Get statistics
            order_stats = order_service.get_stats()
            debt_stats = debt_service.get_stats()
            customer_stats = customer_service.get_stats()
            
            # Update all-time stats
            self.card_total_orders.value_label.setText(
                str(order_stats.get('total_orders', 0))
            )
            
            self.card_total_revenue.value_label.setText(
                self.format_currency(order_stats.get('total_revenue', 0)) + "đ"
            )
            
            self.card_total_profit.value_label.setText(
                self.format_currency(order_stats.get('total_profit', 0)) + "đ"
            )
            
            self.card_total_debt.value_label.setText(
                self.format_currency(debt_stats.get('total_remaining', 0)) + "đ"
            )
            
            # Update period stats
            self.card_period_revenue.value_label.setText(
                self.format_currency(order_stats.get('total_revenue', 0)) + "đ"
            )
            
            self.card_period_orders.value_label.setText(
                str(order_stats.get('total_orders', 0))
            )
            
            self.card_new_customers.value_label.setText(
                str(customer_stats.get('total_customers', 0))
            )
            
            avg_order = order_stats.get('total_revenue', 0) / max(order_stats.get('total_orders', 1), 1)
            self.card_avg_order.value_label.setText(
                self.format_currency(avg_order) + "đ"
            )
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            
    def refresh_data(self):
        """Refresh dashboard data"""
        self.load_data()
