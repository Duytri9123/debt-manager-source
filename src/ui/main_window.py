# -*- coding: utf-8 -*-
"""
Main Window with sidebar navigation
Mirrors Laravel admin layout
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon

from src.ui.pages.dashboard_page import DashboardPage
from src.ui.pages.customers_page import CustomersPage
from src.ui.pages.products_page import ProductsPage
from src.ui.pages.orders_page import OrdersPage
from src.ui.pages.debts_page import DebtsPage


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        
        self.setWindowTitle("Quản lý Công nợ & Đơn hàng B2B")
        self.setMinimumSize(1400, 900)
        
        # Initialize pages
        self.init_pages()
        
        # Setup UI
        self.setup_ui()
        
    def init_pages(self):
        """Initialize all pages"""
        self.pages = {
            'dashboard': DashboardPage(self.db),
            'customers': CustomersPage(self.db),
            'products': ProductsPage(self.db),
            'orders': OrdersPage(self.db),
            'debts': DebtsPage(self.db),
        }
        
    def setup_ui(self):
        """Setup the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top bar
        top_bar = self.create_top_bar()
        content_layout.addWidget(top_bar)
        
        # Pages stack
        self.stacked_widget = QStackedWidget()
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_widget, 1)
        
        # Default to dashboard
        self.stacked_widget.setCurrentWidget(self.pages['dashboard'])
        
    def create_sidebar(self) -> QWidget:
        """Create sidebar navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-right: 1px solid #334155;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Header
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("background-color: #0F172A;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        logo_label = QLabel("CÔNG NỢ")
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo_label.setStyleSheet("color: #F59E0B;")
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)
        
        subtitle_label = QLabel("Quản lý Kinh Doanh B2B")
        subtitle_label.setFont(QFont("Segoe UI", 8, QFont.Normal, QFont.Italic))
        subtitle_label.setStyleSheet("color: #94A3B8;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Navigation buttons
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1E293B;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 3px;
            }
        """)
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(5)
        
        # Navigation items
        nav_items = [
            ('dashboard', '📊 Dashboard', self.pages['dashboard']),
            ('customers', '👥 Khách hàng', self.pages['customers']),
            ('orders', '📦 Đơn hàng', self.pages['orders']),
            ('debts', '💰 Công nợ', self.pages['debts']),
            ('products', '🛍️ Sản phẩm', self.pages['products']),
        ]
        
        self.nav_buttons = {}
        for key, label, page in nav_items:
            btn = self.create_nav_button(label, key)
            nav_layout.addWidget(btn)
            self.nav_buttons[key] = btn
            
        nav_layout.addStretch()
        
        nav_scroll.setWidget(nav_widget)
        layout.addWidget(nav_scroll)
        
        # Footer
        footer_frame = QFrame()
        footer_frame.setFixedHeight(40)
        footer_frame.setStyleSheet("background-color: #0F172A;")
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 5, 20, 5)
        
        version_label = QLabel("v1.0 | Desktop App")
        version_label.setFont(QFont("Segoe UI", 8, QFont.Normal, QFont.Italic))
        version_label.setStyleSheet("color: #64748B;")
        version_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(version_label)
        
        layout.addWidget(footer_frame)
        
        return sidebar
        
    def create_nav_button(self, text: str, key: str) -> QPushButton:
        """Create navigation button"""
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #0F172A;
                color: #94A3B8;
                border: none;
                border-radius: 5px;
                padding-left: 15px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #E2E8F0;
            }
            QPushButton:checked {
                background-color: #6366F1;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.navigate_to(key))
        return btn
        
    def navigate_to(self, key: str):
        """Navigate to a page"""
        # Update buttons
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)
            
        # Switch page
        if key in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[key])
            
            # Refresh page data
            if hasattr(self.pages[key], 'refresh_data'):
                self.pages[key].refresh_data()
                
    def create_top_bar(self) -> QFrame:
        """Create top bar"""
        top_bar = QFrame()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E2E8F0;
            }
        """)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 5, 20, 5)
        
        title_label = QLabel("Hệ thống Quản lý B2B")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #0F172A;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Add some info
        from datetime import datetime
        date_label = QLabel(datetime.now().strftime('%d/%m/%Y'))
        date_label.setFont(QFont("Segoe UI", 10))
        date_label.setStyleSheet("color: #64748B;")
        layout.addWidget(date_label)
        
        return top_bar
