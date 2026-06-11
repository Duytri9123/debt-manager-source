# -*- coding: utf-8 -*-
"""
Quản lý Công nợ & Đơn hàng B2B - Desktop Application
Chuyển đổi từ Laravel + VueJS sang Python + PySide6
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

from src.database import Database
from src.ui.native_main_window import MainWindow
from src.ui.theme import apply_theme


def main():
    """Application entry point - Native PySide6 with modern QSS theme"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Quản lý Công nợ B2B")
    app.setOrganizationName("B2B Management")
    app.setStyle("Fusion")
    
    # Apply modern QSS theme (matches Vue.js Tailwind design)
    apply_theme(app)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), "data", "b2b_management.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print("🗄️  Khởi tạo database...")
    db = Database(db_path)
    db.initialize()
    print("✅ Database sẵn sàng!")
    
    # Create and show main window with native PySide6 UI
    print("🚀 Khởi động ứng dụng...")
    window = MainWindow(db)
    window.show()
    
    print("✨ Ứng dụng đã khởi động thành công!")
    print("💡 Giao diện: Native PySide6 + QSS (giống Vue.js Tailwind)")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
