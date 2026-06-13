# -*- coding: utf-8 -*-
"""
Main Window with sidebar navigation
Mirrors Laravel admin layout
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QScrollArea, QProgressBar
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QIcon

from src.ui.pages.dashboard_page import DashboardPage
from src.ui.pages.customers_page import CustomersPage
from src.ui.pages.products_page import ProductsPage
from src.ui.pages.orders_page import OrdersPage
from src.ui.pages.debts_page import DebtsPage
from src.services.update_service import UpdateService


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation"""

    def __init__(self, db):
        super().__init__()
        self.db = db

        self.setWindowTitle("Quan ly Cong no & Don hang B2B")
        self.setMinimumSize(1400, 900)

        # Initialize pages
        self.init_pages()

        # Setup UI
        self.setup_ui()

        # Update service
        self.update_service = UpdateService()
        self.setup_update_connections()

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

        # Update notification banner
        self.update_banner = self.create_update_banner()
        content_layout.addWidget(self.update_banner)

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

        logo_label = QLabel("Quan ly cong no")
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo_label.setStyleSheet("color: #F59E0B;")
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)

        subtitle_label = QLabel("Quan ly Kinh Doanh B2B")
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
            ('dashboard', 'Dashboard', self.pages['dashboard']),
            ('customers', 'Khach hang', self.pages['customers']),
            ('orders', 'Don hang', self.pages['orders']),
            ('debts', 'Cong no', self.pages['debts']),
            ('products', 'San pham', self.pages['products']),
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
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #0F172A;
                color: #94A3B8;
                border: none;
                border-radius: 5px;
                padding-left: 15px;
                text-align: left;
                font-size: 16px;
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

    # ──────────────────────────────
    # Update notification banner
    # ──────────────────────────────

    def create_update_banner(self) -> QFrame:
        """Create the update notification banner (hidden by default)."""
        banner = QFrame()
        banner.setFixedHeight(48)
        banner.setStyleSheet("""
            QFrame {
                background-color: #1E3A5F;
                border-bottom: 2px solid #3B82F6;
            }
            QLabel {
                color: #E2E8F0;
                font-size: 14px;
            }
        """)
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(20, 5, 20, 5)

        self.update_icon_label = QLabel("\U0001f504")
        layout.addWidget(self.update_icon_label)

        self.update_message_label = QLabel("Dang kiem tra cap nhat...")
        layout.addWidget(self.update_message_label, 1)

        self.update_progress = QProgressBar()
        self.update_progress.setFixedWidth(200)
        self.update_progress.setFixedHeight(20)
        self.update_progress.setVisible(False)
        self.update_progress.setTextVisible(True)
        self.update_progress.setStyleSheet("""
            QProgressBar {
                background-color: #334155;
                border: none;
                border-radius: 10px;
                text-align: center;
                color: white;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.update_progress)

        self.update_action_btn = QPushButton("Cap nhat ngay")
        self.update_action_btn.setFixedHeight(32)
        self.update_action_btn.setCursor(Qt.PointingHandCursor)
        self.update_action_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:disabled {
                background-color: #475569;
                color: #94A3B8;
            }
        """)
        self.update_action_btn.setVisible(False)
        self.update_action_btn.clicked.connect(self.on_update_action_clicked)
        layout.addWidget(self.update_action_btn)

        self.update_dismiss_btn = QPushButton("\u2715")
        self.update_dismiss_btn.setFixedSize(28, 28)
        self.update_dismiss_btn.setCursor(Qt.PointingHandCursor)
        self.update_dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #E2E8F0;
            }
        """)
        self.update_dismiss_btn.setVisible(False)
        self.update_dismiss_btn.clicked.connect(lambda: banner.setVisible(False))
        layout.addWidget(self.update_dismiss_btn)

        banner.setVisible(False)
        return banner

    def setup_update_connections(self):
        """Connect update service signals to UI handlers."""
        svc = self.update_service
        svc.update_available.connect(self.on_update_available)
        svc.no_update.connect(self.on_no_update)
        svc.check_error.connect(self.on_check_error)
        svc.download_progress.connect(self.on_download_progress)
        svc.download_complete.connect(self.on_download_complete)
        svc.download_error.connect(self.on_download_error)

    def check_for_updates(self):
        """Start update check (called after window is shown)."""
        self.update_banner.setVisible(True)
        self.update_icon_label.setText("\U0001f504")
        self.update_message_label.setText("Dang kiem tra cap nhat...")
        self.update_action_btn.setVisible(False)
        self.update_dismiss_btn.setVisible(True)
        self.update_progress.setVisible(False)
        self.update_service.check()

    def on_update_available(self, version_info):
        """Show update banner when new version is found."""
        version = version_info.get("version", "")
        mandatory = version_info.get("mandatory", False)
        self.update_icon_label.setText("\U0001f4e6")
        self.update_message_label.setText(f"Cap nhat moi v{version} da san sang!")
        self.update_action_btn.setText("Cap nhat ngay")
        self.update_action_btn.setEnabled(True)
        self.update_action_btn.setVisible(True)
        self.update_progress.setVisible(False)
        self.update_dismiss_btn.setVisible(not mandatory)
        self.update_banner.setVisible(True)

    def on_no_update(self):
        """Hide banner when app is up to date."""
        self.update_banner.setVisible(False)

    def on_check_error(self, error_msg):
        """Show error briefly then hide."""
        self.update_icon_label.setText("\u26a0\ufe0f")
        self.update_message_label.setText("Khong the kiem tra cap nhat")
        self.update_action_btn.setVisible(False)
        self.update_dismiss_btn.setVisible(True)
        QTimer.singleShot(8000, lambda: self.update_banner.setVisible(False))

    def on_update_action_clicked(self):
        """Handle update button click."""
        self.update_action_btn.setEnabled(False)
        self.update_action_btn.setText("Dang tai...")
        self.update_progress.setVisible(True)
        self.update_progress.setValue(0)
        self.update_service.download_update()

    def on_download_progress(self, percent: int):
        """Update progress bar during download."""
        self.update_progress.setValue(percent)
        self.update_message_label.setText(f"Dang tai ban cap nhat... {percent}%")

    def on_download_complete(self, installer_path: str):
        """Download finished - start installation."""
        self.update_progress.setVisible(False)
        self.update_icon_label.setText("\u2705")
        self.update_message_label.setText("Da tai xong! Dang cai dat...")
        self.update_action_btn.setVisible(False)
        self.update_dismiss_btn.setVisible(False)
        UpdateService.install_update(installer_path)
        QTimer.singleShot(2000, self.close)

    def on_download_error(self, error_msg):
        """Show download error."""
        self.update_progress.setVisible(False)
        self.update_icon_label.setText("\u274c")
        self.update_message_label.setText(f"Tai that bai: {error_msg[:50]}")
        self.update_action_btn.setText("Thu lai")
        self.update_action_btn.setEnabled(True)
        self.update_action_btn.setVisible(True)
            # Refresh page data
            if hasattr(self.pages[key], 'refresh_data'):
                self.pages[key].refresh_data()
                
        # Switch page
        if key in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[key])
            
            # Refresh page data
            if hasattr(self.pages[key], 'refresh_data'):
                self.pages[key].refresh_data()

    # ──────────────────────────────
    # Update notification banner
    # ──────────────────────────────

    def create_update_banner(self) -> QFrame:
        """Create the update notification banner (hidden by default)."""
        banner = QFrame()
        banner.setFixedHeight(48)
        banner.setStyleSheet("""
            QFrame {
                background-color: #1E3A5F;
                border-bottom: 2px solid #3B82F6;
            }
            QLabel {
                color: #E2E8F0;
                font-size: 14px;
            }
        """)
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(20, 5, 20, 5)

        self.update_icon_label = QLabel("🔄")
        layout.addWidget(self.update_icon_label)

        self.update_message_label = QLabel("Đang kiểm tra cập nhật...")
        layout.addWidget(self.update_message_label, 1)

        self.update_progress = QProgressBar()
        self.update_progress.setFixedWidth(200)
        self.update_progress.setFixedHeight(20)
        self.update_progress.setVisible(False)
        self.update_progress.setTextVisible(True)
        self.update_progress.setStyleSheet("""
            QProgressBar {
                background-color: #334155;
                border: none;
                border-radius: 10px;
                text-align: center;
                color: white;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.update_progress)

        self.update_action_btn = QPushButton("Cập nhật ngay")
        self.update_action_btn.setFixedHeight(32)
        self.update_action_btn.setCursor(Qt.PointingHandCursor)
        self.update_action_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:disabled {
                background-color: #475569;
                color: #94A3B8;
            }
        """)
        self.update_action_btn.setVisible(False)
        self.update_action_btn.clicked.connect(self.on_update_action_clicked)
        layout.addWidget(self.update_action_btn)

        self.update_dismiss_btn = QPushButton("✕")
        self.update_dismiss_btn.setFixedSize(28, 28)
        self.update_dismiss_btn.setCursor(Qt.PointingHandCursor)
        self.update_dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #E2E8F0;
            }
        """)
        self.update_dismiss_btn.setVisible(False)
        self.update_dismiss_btn.clicked.connect(lambda: banner.setVisible(False))
        layout.addWidget(self.update_dismiss_btn)

        banner.setVisible(False)
        return banner

    def setup_update_connections(self):
        """Connect update service signals to UI handlers."""
        svc = self.update_service
        svc.update_available.connect(self.on_update_available)
        svc.no_update.connect(self.on_no_update)
        svc.check_error.connect(self.on_check_error)
        svc.download_progress.connect(self.on_download_progress)
        svc.download_complete.connect(self.on_download_complete)
        svc.download_error.connect(self.on_download_error)

    def check_for_updates(self):
        """Start update check (called after window is shown)."""
        self.update_banner.setVisible(True)
        self.update_icon_label.setText("🔄")
        self.update_message_label.setText("Đang kiểm tra cập nhật...")
        self.update_action_btn.setVisible(False)
        self.update_dismiss_btn.setVisible(True)
        self.update_progress.setVisible(False)
        self.update_service.check()

    def on_update_available(self, version_info):
        """Show update banner when new version is found."""
        version = version_info.get("version", "")
        mandatory = version_info.get("mandatory", False)
        self.update_icon_label.setText("📦")
        self.update_message_label.setText(f"Cập nhật mới v{version} đã sẵn sàng!")
        self.update_action_btn.setText("Cập nhật ngay")
        self.update_action_btn.setEnabled(True)
        self.update_action_btn.setVisible(True)
        self.update_progress.setVisible(False)
        self.update_dismiss_btn.setVisible(not mandatory)
        self.update_banner.setVisible(True)

    def on_no_update(self):
        """Hide banner when app is up to date."""
        self.update_banner.setVisible(False)

    def on_check_error(self, error_msg):
        """Show error briefly then hide."""
        self.update_icon_label.setText("⚠️")
        self.update_message_label.setText("Không thể kiểm tra cập nhật")
        self.update_action_btn.setVisible(False)
        self.update_dismiss_btn.setVisible(True)
        # Auto-hide after 8 seconds
        QTimer.singleShot(8000, lambda: self.update_banner.setVisible(False))

    def on_update_action_clicked(self):
        """Handle update button click."""
        self.update_action_btn.setEnabled(False)
        self.update_action_btn.setText("Đang tải...")
        self.update_progress.setVisible(True)
        self.update_progress.setValue(0)
        self.update_service.download_update()

    def on_download_progress(self, percent: int):
        """Update progress bar during download."""
        self.update_progress.setValue(percent)
        self.update_message_label.setText(f"Đang tải bản cập nhật... {percent}%")

    def on_download_complete(self, installer_path: str):
        """Download finished - start installation."""
        self.update_progress.setVisible(False)
        self.update_icon_label.setText("✅")
        self.update_message_label.setText("Đã tải xong! Đang cài đặt...")
        self.update_action_btn.setVisible(False)
        self.update_dismiss_btn.setVisible(False)
        # Start installer
        UpdateService.install_update(installer_path)
        # Wait a moment then close app
        QTimer.singleShot(2000, self.close)

    def on_download_error(self, error_msg):
        """Show download error."""
        self.update_progress.setVisible(False)
        self.update_icon_label.setText("❌")
        self.update_message_label.setText(f"Tải thất bại: {error_msg[:50]}")
        self.update_action_btn.setText("Thử lại")
        self.update_action_btn.setEnabled(True)
        self.update_action_btn.setVisible(True)
                
