# -*- coding: utf-8 -*-
"""
Main Window - Native PySide6 with modern design
Matches Vue.js AdminLayout with sidebar navigation
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QIcon

from src.ui.pages.dashboard_page import DashboardPage
from src.ui.pages.orders_page import OrdersPage
from src.ui.pages.debts_page import DebtsPage
from src.ui.pages.customers_page import CustomersPage
from src.ui.pages.products_page import ProductsPage


class MainWindow(QMainWindow):
    """Main window with sidebar navigation (matches Vue.js AdminLayout)"""
    
    # Signal for navigation
    page_changed = Signal(str)
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        
        self.setWindowTitle("Quản lý Công nợ & Đơn hàng B2B")
        self.setMinimumSize(1600, 1000)
        
        # Initialize pages
        self.init_pages()
        
        # Setup UI
        self.setup_ui()
        
    def init_pages(self):
        """Initialize all pages"""
        self.pages = {
            'dashboard': DashboardPage(self.db),
            'orders': OrdersPage(self.db),
            'debts': DebtsPage(self.db),
            'customers': CustomersPage(self.db),
            'products': ProductsPage(self.db),
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
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        main_layout.addWidget(sidebar)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top bar
        top_bar = self.create_top_bar()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(64)
        content_layout.addWidget(top_bar)
        
        # Pages stack
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #F9FAFB;")
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_widget, 1)
        
        # Default to dashboard
        self.navigate_to('dashboard')
        
    def create_sidebar(self) -> QFrame:
        """Create sidebar navigation"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Header
        header_frame = QFrame()
        header_frame.setObjectName("sidebarHeader")
        header_frame.setFixedHeight(70)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 16, 24, 16)
        header_layout.setSpacing(4)
        
        logo_label = QLabel("⚡ QUẢN LÝ B2B")
        logo_label.setObjectName("logoLabel")
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_layout.addWidget(logo_label)
        
        subtitle_label = QLabel("Công nợ & Đơn hàng")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Navigation scroll area
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
        nav_layout.setContentsMargins(12, 12, 12, 12)
        nav_layout.setSpacing(6)
        
        # Navigation items
        nav_items = [
            ('dashboard', '📊  Dashboard', 'Dashboard'),
            ('orders', '📦  Đơn hàng B2B', 'Quản lý đơn hàng'),
            ('debts', '💰  Công nợ', 'Quản lý công nợ'),
            ('customers', '👥  Khách hàng', 'Quản lý khách hàng'),
            ('products', '🛍️  Sản phẩm', 'Quản lý sản phẩm'),
        ]
        
        self.nav_buttons = {}
        for key, label, tooltip in nav_items:
            btn = self.create_nav_button(label, key, tooltip)
            nav_layout.addWidget(btn)
            self.nav_buttons[key] = btn
            
        nav_layout.addStretch()
        
        nav_scroll.setWidget(nav_widget)
        layout.addWidget(nav_scroll)
        
        # Footer
        footer_frame = QFrame()
        footer_frame.setObjectName("sidebarHeader")
        footer_frame.setFixedHeight(50)
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(24, 10, 24, 10)
        
        version_label = QLabel("v1.0 | Python + PySide6")
        version_label.setFont(QFont("Segoe UI", 9))
        version_label.setStyleSheet("color: #64748B;")
        version_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(version_label)
        
        layout.addWidget(footer_frame)
        
        return sidebar
        
    def create_nav_button(self, text: str, key: str, tooltip: str) -> QPushButton:
        """Create navigation button"""
        btn = QPushButton(text)
        btn.setObjectName("navButton")
        btn.setFixedHeight(48)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 13, QFont.Normal))
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
            self.page_changed.emit(key)
            
            # Refresh page data
            if hasattr(self.pages[key], 'refresh_data'):
                self.pages[key].refresh_data()
                
    def create_top_bar(self) -> QFrame:
        """Create top bar"""
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(24, 12, 24, 12)
        
        # Page title (will be updated on navigation)
        self.page_title_label = QLabel("Dashboard")
        self.page_title_label.setObjectName("pageTitle")
        self.page_title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        layout.addWidget(self.page_title_label)
        
        layout.addStretch()
        
        # Date label
        from datetime import datetime
        date_label = QLabel(datetime.now().strftime('%d/%m/%Y'))
        date_label.setFont(QFont("Segoe UI", 12))
        date_label.setStyleSheet("color: #6B7280;")
        layout.addWidget(date_label)
        
        # Connect page change signal to update title
        self.page_changed.connect(self.update_page_title)
        
        return top_bar
        
    def update_page_title(self, page_key: str):
        """Update page title in top bar"""
        titles = {
            'dashboard': 'Dashboard',
            'orders': 'Đơn hàng B2B',
            'debts': 'Quản lý Công nợ',
            'customers': 'Khách hàng',
            'products': 'Sản phẩm',
        }
        self.page_title_label.setText(titles.get(page_key, 'Dashboard'))
