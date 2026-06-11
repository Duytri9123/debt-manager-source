# -*- coding: utf-8 -*-
"""
Main Window with PySide6 QWebEngineView
Loads Vue.js UI from Flask server
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

import threading
import time


class MainWindow(QMainWindow):
    """Main window with WebView for Vue.js UI"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        
        self.setWindowTitle("Quản lý Công nợ & Đơn hàng B2B")
        self.setMinimumSize(1600, 1000)
        
        # Start Flask server in background thread
        self.server_thread = None
        self.start_flask_server()
        
        # Setup UI
        self.setup_ui()
        
    def start_flask_server(self):
        """Start Flask server in background thread"""
        from src.api_server import create_api_server
        
        app, port = create_api_server(self.db)
        
        def run_server():
            app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        print(f"✅ Flask server started on http://127.0.0.1:{port}")
        
    def setup_ui(self):
        """Setup the main UI with sidebar and WebView"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar navigation
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # WebView container
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        
        # Load initial page (Dashboard)
        QTimer.singleShot(3000, lambda: self.web_view.load(QUrl("http://127.0.0.1:5000/")))
        
        # Loading indicator
        loading_label = QLabel("Đang tải giao diện...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setFont(QFont("Inter", 14))
        loading_label.setStyleSheet("color: #6B7280;")
        
        # Create stacked widget for loading/webview
        self.stack = QStackedWidget()
        self.stack.addWidget(loading_label)
        self.stack.addWidget(self.web_view)
        self.stack.setCurrentIndex(0)
        
        # Switch to webview when loaded
        self.web_view.loadFinished.connect(lambda: self.stack.setCurrentIndex(1))
        
        main_layout.addWidget(self.stack, 1)
        
    def create_sidebar(self) -> QFrame:
        """Create sidebar navigation matching Vue.js AdminLayout"""
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-right: 1px solid #1E293B;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Header
        header_frame = QFrame()
        header_frame.setFixedHeight(70)
        header_frame.setStyleSheet("background-color: #0F172A; border-bottom: 1px solid #1E293B;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        logo_label = QLabel("⚡ QUẢN LÝ B2B")
        logo_label.setFont(QFont("Inter", 16, QFont.Bold))
        logo_label.setStyleSheet("color: #F59E0B;")
        header_layout.addWidget(logo_label)
        
        subtitle_label = QLabel("Công nợ & Đơn hàng")
        subtitle_label.setFont(QFont("Inter", 10))
        subtitle_label.setStyleSheet("color: #94A3B8;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Navigation buttons
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(12, 12, 12, 12)
        nav_layout.setSpacing(6)
        
        nav_items = [
            ('📊 Dashboard', 'http://127.0.0.1:5000/'),
            ('📦 Đơn hàng B2B', 'http://127.0.0.1:5000/b2b-orders'),
            ('💰 Công nợ', 'http://127.0.0.1:5000/debts'),
            ('👥 Khách hàng', 'http://127.0.0.1:5000/customers'),
            ('🛍️ Sản phẩm', 'http://127.0.0.1:5000/products'),
        ]
        
        for label, url in nav_items:
            btn = self.create_nav_button(label, url)
            nav_layout.addWidget(btn)
            
        nav_layout.addStretch()
        layout.addLayout(nav_layout)
        
        # Footer
        footer_frame = QFrame()
        footer_frame.setFixedHeight(50)
        footer_frame.setStyleSheet("""
            background-color: #0F172A; 
            border-top: 1px solid #1E293B;
        """)
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        version_label = QLabel("v1.0 | Python + Vue.js")
        version_label.setFont(QFont("Inter", 9))
        version_label.setStyleSheet("color: #64748B;")
        version_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(version_label)
        
        layout.addWidget(footer_frame)
        
        return sidebar
        
    def create_nav_button(self, text: str, url: str) -> QPushButton:
        """Create navigation button"""
        btn = QPushButton(text)
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Inter", 13))
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 8px;
                padding-left: 20px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #E2E8F0;
            }
            QPushButton:pressed {
                background-color: #334155;
                color: #FFFFFF;
            }
        """)
        btn.clicked.connect(lambda: self.web_view.load(QUrl(url)))
        return btn
        
    def closeEvent(self, event):
        """Handle window close"""
        print("👋 Đóng ứng dụng...")
        event.accept()
