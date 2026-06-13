# -*- coding: utf-8 -*-
"""
Main Window - Native PySide6 admin layout.
Mirrors the Laravel AdminLayout sidebar and header.
"""
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.ui.pages.advances_page import AdvancesPage
from src.ui.pages.customers_page import CustomersPage
from src.ui.pages.dashboard_page import DashboardPage
from src.ui.pages.debts_page import DebtsPage
from src.ui.pages.orders_page import OrdersPage
from src.ui.chat_modal import ChatDialog
from src.services.update_service import UpdateService


class MainWindow(QMainWindow):
    """Main window with the five requested admin tabs."""

    page_changed = Signal(str)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Quản lý Công nợ & Đơn hàng B2B")
        self.setMinimumSize(1120, 700)
        self.chat_dialog = None
        self.chat_button = None

        self.init_pages()
        self.setup_ui()

        # Update service
        self.update_service = UpdateService()
        self.setup_update_connections()

    def init_pages(self):
        """Initialize pages in the same order as the requested sidebar."""
        self.pages = {
            "dashboard": DashboardPage(self.db),
            "customers": CustomersPage(self.db),
            "orders": OrdersPage(self.db),
            "debts": DebtsPage(self.db),
            "advances": AdvancesPage(self.db),
        }

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self.create_sidebar()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        main_layout.addWidget(sidebar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Update notification banner
        self.update_banner = self.create_update_banner()
        content_layout.addWidget(self.update_banner)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("QStackedWidget { background-color: #F9FAFB; }")
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        content_layout.addWidget(self.stacked_widget, 1)

        main_layout.addWidget(content_widget, 1)
        self.navigate_to("dashboard")
        self.create_chat_button()

    def create_chat_button(self):
        self.chat_button = QPushButton("AI", self.centralWidget())
        self.chat_button.setObjectName("floatingChatButton")
        self.chat_button.setFixedSize(58, 58)
        self.chat_button.setToolTip("Mở AI Assistant")
        self.chat_button.setCursor(Qt.PointingHandCursor)
        self.chat_button.clicked.connect(self.open_chat)
        self.position_chat_button()
        self.chat_button.raise_()

    def position_chat_button(self):
        if not self.chat_button:
            return
        margin = 28
        self.chat_button.move(
            max(0, self.centralWidget().width() - self.chat_button.width() - margin),
            max(0, self.centralWidget().height() - self.chat_button.height() - margin),
        )

    def open_chat(self):
        if self.chat_dialog is None:
            self.chat_dialog = ChatDialog(self)
        self.chat_dialog.show()
        self.chat_dialog.raise_()
        self.chat_dialog.activateWindow()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_chat_button()
        if self.chat_button:
            self.chat_button.raise_()

    def create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("sidebarHeader")
        header.setFixedHeight(58)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("Quản lý công nợ")
        title.setObjectName("logoLabel")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        collapse_hint = QLabel("‹")
        collapse_hint.setObjectName("sidebarChevron")
        collapse_hint.setAlignment(Qt.AlignCenter)
        collapse_hint.setFixedWidth(18)
        header_layout.addWidget(collapse_hint)
        layout.addWidget(header)

        nav_scroll = QScrollArea()
        nav_scroll.setObjectName("sidebarScroll")
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.viewport().setObjectName("sidebarViewport")

        nav_widget = QWidget()
        nav_widget.setObjectName("sidebarNav")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(8, 12, 8, 8)
        nav_layout.setSpacing(4)

        nav_items = [
            ("dashboard", "📊  Dashboard", "Tổng quan hệ thống"),
            ("customers", "👥  Khách hàng", "Hồ sơ khách hàng"),
            ("orders", "📦  Theo dõi KD", "Theo dõi đơn hàng kinh doanh"),
            ("debts", "💰  Công nợ", "Quản lý công nợ"),
            ("advances", "💵  Tạm ứng", "Quản lý tạm ứng"),
        ]

        self.nav_buttons = {}
        for key, label, tooltip in nav_items:
            button = self.create_nav_button(label, key, tooltip)
            nav_layout.addWidget(button)
            self.nav_buttons[key] = button

        nav_layout.addStretch()
        nav_scroll.setWidget(nav_widget)
        layout.addWidget(nav_scroll, 1)

        return sidebar

    def create_nav_button(self, text: str, key: str, tooltip: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setFixedHeight(44)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setCheckable(True)
        button.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        button.clicked.connect(lambda: self.navigate_to(key))
        return button

    def navigate_to(self, key: str):
        for page_key, button in self.nav_buttons.items():
            button.setChecked(page_key == key)

        if key in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[key])
            self.page_changed.emit(key)
            if hasattr(self.pages[key], "refresh_data"):
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
