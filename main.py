# -*- coding: utf-8 -*-
"""
Quan ly Cong no & Don hang B2B - Desktop Application
Chuyen doi tu Laravel + VueJS sang Python + PySide6
"""
import sys
import shutil
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

from src.database import Database
from src.core.paths import AppPaths
from src.ui.keyboard import EnterKeyNavigationFilter
from src.ui.native_main_window import MainWindow
from src.ui.theme import apply_theme


def resolve_database_path(app_paths: AppPaths) -> str:
    """Use AppData for persistent installs and migrate a local dev DB once."""
    db_path = Path(app_paths.database_path)
    legacy_db = Path(__file__).resolve().parent / "data" / "b2b_management.db"

    if legacy_db.exists() and not db_path.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy_db, db_path)

    return str(db_path)


def resource_path(relative_path: str) -> Path:
    """Resolve bundled assets in PyInstaller and normal source runs."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def load_app_icon() -> QIcon:
    icon_path = resource_path("src/assets/icon/logo.png")
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()


def main():
    """Application entry point - Native PySide6 with modern QSS theme"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    enter_filter = EnterKeyNavigationFilter(app)
    app.installEventFilter(enter_filter)
    app.enter_key_navigation_filter = enter_filter
    app_icon = load_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    app.setApplicationName("Quan ly Cong no B2B")
    app.setOrganizationName("B2B Management")
    # Apply modern QSS theme first (Fusion palette conflicts with QSS colors)
    apply_theme(app)

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Initialize database
    app_paths = AppPaths()
    db_path = resolve_database_path(app_paths)

    print("Khoi tao database...")
    print(f"Database path: {db_path}")
    db = Database(db_path)
    db.initialize()
    print("Database san sang!")

    # Create and show main window with native PySide6 UI
    print("Khoi dong ung dung...")
    window = MainWindow(db)
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)
    window.show()

    # Check for updates after window is shown
    QTimer.singleShot(2000, window.check_for_updates)

    print("Ung dung da khoi dong thanh cong!")
    print("Giao dien: Native PySide6 + QSS")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
