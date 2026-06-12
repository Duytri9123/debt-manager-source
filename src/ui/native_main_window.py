# -*- coding: utf-8 -*-
"""
Main Window - Native PySide6 admin layout.
Mirrors the Laravel AdminLayout sidebar and header.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
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

        top_bar = self.create_top_bar()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(52)
        content_layout.addWidget(top_bar)

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

        title = QLabel("Admin Panel")
        title.setObjectName("logoLabel")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
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

        footer = QFrame()
        footer.setObjectName("sidebarFooter")
        footer.setFixedHeight(104)
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(12, 10, 12, 12)
        footer_layout.setSpacing(8)

        user_row = QHBoxLayout()
        avatar = QLabel("A")
        avatar.setObjectName("avatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(32, 32)
        user_row.addWidget(avatar)

        user_text = QVBoxLayout()
        name = QLabel("Admin")
        name.setObjectName("sidebarUserName")
        email = QLabel("Admin@dtshop.com")
        email.setObjectName("sidebarUserEmail")
        user_text.addWidget(name)
        user_text.addWidget(email)
        user_row.addLayout(user_text, 1)
        footer_layout.addLayout(user_row)

        logout = QPushButton("Đăng xuất")
        logout.setObjectName("logoutButton")
        logout.setCursor(Qt.PointingHandCursor)
        footer_layout.addWidget(logout)
        layout.addWidget(footer)

        return sidebar

    def create_nav_button(self, text: str, key: str, tooltip: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setFixedHeight(40)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setCheckable(True)
        button.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        button.clicked.connect(lambda: self.navigate_to(key))
        return button

    def create_top_bar(self) -> QFrame:
        top_bar = QFrame()
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.addStretch()

        avatar = QLabel("A")
        avatar.setObjectName("topAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(32, 32)
        layout.addWidget(avatar)

        name = QLabel("Admin")
        name.setObjectName("topUserName")
        name.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        layout.addWidget(name)
        return top_bar

    def navigate_to(self, key: str):
        for page_key, button in self.nav_buttons.items():
            button.setChecked(page_key == key)

        if key in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[key])
            self.page_changed.emit(key)
            if hasattr(self.pages[key], "refresh_data"):
                self.pages[key].refresh_data()
