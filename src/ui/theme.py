# -*- coding: utf-8 -*-
"""
Modern QSS Theme - Matches Vue.js Tailwind CSS Design
Colors and styling from your Vue.js dashboard
"""

THEME_QSS = """
/* ── Global Styles ───────────────────────────────────────────────────────── */
* {
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

QWidget {
    background-color: #F9FAFB;
    color: #111827;
}

/* ── Main Window ─────────────────────────────────────────────────────────── */
QMainWindow {
    background-color: #F9FAFB;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
QFrame#sidebar {
    background-color: #0F172A;
    border-right: 1px solid #1E293B;
}

QFrame#sidebarHeader {
    background-color: #0F172A;
    border-bottom: 1px solid #1E293B;
}

QLabel#logoLabel {
    color: #F59E0B;
    font-size: 18px;
    font-weight: bold;
}

QLabel#subtitleLabel {
    color: #94A3B8;
    font-size: 11px;
}

/* Navigation Buttons */
QPushButton#navButton {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    padding: 12px 20px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#navButton:hover {
    background-color: #1E293B;
    color: #E2E8F0;
}

QPushButton#navButton:checked {
    background-color: #6366F1;
    color: #FFFFFF;
    font-weight: 600;
}

QPushButton#navButton:pressed {
    background-color: #4F46E5;
}

/* ── Top Bar ─────────────────────────────────────────────────────────────── */
QFrame#topBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
}

QLabel#pageTitle {
    color: #111827;
    font-size: 20px;
    font-weight: bold;
}

QLabel#pageSubtitle {
    color: #6B7280;
    font-size: 13px;
}

/* ── Stat Cards ──────────────────────────────────────────────────────────── */
QFrame#statCard {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 16px;
}

QFrame#statCard:hover {
    border-color: #6366F1;
    background-color: #F9FAFB;
}

QLabel#statTitle {
    color: #6B7280;
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel#statValue {
    color: #111827;
    font-size: 24px;
    font-weight: bold;
}

QLabel#statSubtitle {
    color: #9CA3AF;
    font-size: 12px;
}

/* Stat Card Colors */
QFrame#statCardIndigo {
    background-color: #EEF2FF;
    border: 1px solid #C7D2FE;
}

QFrame#statCardEmerald {
    background-color: #ECFDF5;
    border: 1px solid #A7F3D0;
}

QFrame#statCardAmber {
    background-color: #FFFBEB;
    border: 1px solid #FDE68A;
}

QFrame#statCardRed {
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
}

QFrame#statCardBlue {
    background-color: #EFF6FF;
    border: 1px solid #BFDBFE;
}

/* ── Tables ──────────────────────────────────────────────────────────────── */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    gridline-color: #F3F4F6;
    selection-background-color: #EEF2FF;
    selection-color: #111827;
}

QTableWidget::item {
    padding: 12px 16px;
    border-bottom: 1px solid #F3F4F6;
}

QTableWidget::item:hover {
    background-color: #F9FAFB;
}

QTableWidget::item:selected {
    background-color: #EEF2FF;
    color: #111827;
}

QHeaderView::section {
    background-color: #F9FAFB;
    color: #6B7280;
    padding: 12px 16px;
    border: none;
    border-bottom: 2px solid #E5E7EB;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
QPushButton {
    background-color: #6366F1;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #4F46E5;
}

QPushButton:pressed {
    background-color: #4338CA;
}

QPushButton:disabled {
    background-color: #E5E7EB;
    color: #9CA3AF;
}

/* Button Variants */
QPushButton#primaryButton {
    background-color: #6366F1;
}

QPushButton#primaryButton:hover {
    background-color: #4F46E5;
}

QPushButton#successButton {
    background-color: #10B981;
}

QPushButton#successButton:hover {
    background-color: #059669;
}

QPushButton#warningButton {
    background-color: #F59E0B;
}

QPushButton#warningButton:hover {
    background-color: #D97706;
}

QPushButton#dangerButton {
    background-color: #EF4444;
}

QPushButton#dangerButton:hover {
    background-color: #DC2626;
}

QPushButton#outlineButton {
    background-color: transparent;
    color: #6366F1;
    border: 1px solid #6366F1;
}

QPushButton#outlineButton:hover {
    background-color: #EEF2FF;
}

/* ── Input Fields ────────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    color: #111827;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 2px solid #6366F1;
    outline: none;
}

QLineEdit:hover, QTextEdit:hover {
    border-color: #9CA3AF;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #6B7280;
    margin-right: 10px;
}

/* ── Labels ──────────────────────────────────────────────────────────────── */
QLabel {
    color: #111827;
    font-size: 14px;
}

QLabel#sectionTitle {
    color: #111827;
    font-size: 18px;
    font-weight: bold;
}

QLabel#formLabel {
    color: #374151;
    font-size: 13px;
    font-weight: 500;
}

/* ── Badges ──────────────────────────────────────────────────────────────── */
QLabel#badgeSuccess {
    background-color: #D1FAE5;
    color: #065F46;
    border-radius: 12px;
    padding: 4px 12px;
    font-weight: 600;
    font-size: 12px;
}

QLabel#badgeWarning {
    background-color: #FEF3C7;
    color: #92400E;
    border-radius: 12px;
    padding: 4px 12px;
    font-weight: 600;
    font-size: 12px;
}

QLabel#badgeDanger {
    background-color: #FEE2E2;
    color: #991B1B;
    border-radius: 12px;
    padding: 4px 12px;
    font-weight: 600;
    font-size: 12px;
}

QLabel#badgeInfo {
    background-color: #DBEAFE;
    color: #1E40AF;
    border-radius: 12px;
    padding: 4px 12px;
    font-weight: 600;
    font-size: 12px;
}

QLabel#badgeNeutral {
    background-color: #F3F4F6;
    color: #374151;
    border-radius: 12px;
    padding: 4px 12px;
    font-weight: 600;
    font-size: 12px;
}

/* ── Scroll Bars ─────────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background-color: #F3F4F6;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #D1D5DB;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9CA3AF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #F3F4F6;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #D1D5DB;
    border-radius: 4px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #9CA3AF;
}

/* ── Dialogs ─────────────────────────────────────────────────────────────── */
QDialog {
    background-color: #FFFFFF;
}

QDialog QLabel {
    color: #111827;
}

/* ── ToolBar ─────────────────────────────────────────────────────────────── */
QToolBar {
    background-color: #FFFFFF;
    border: none;
    border-bottom: 1px solid #E5E7EB;
    padding: 8px;
    spacing: 8px;
}

QToolBar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 8px 12px;
    color: #6B7280;
}

QToolBar QToolButton:hover {
    background-color: #F3F4F6;
    border-color: #E5E7EB;
}

QToolBar QToolButton:pressed {
    background-color: #E5E7EB;
}

/* ── Group Box ───────────────────────────────────────────────────────────── */
QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 24px;
    font-weight: 600;
    font-size: 14px;
    color: #111827;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #374151;
}

/* ── Tab Widget ──────────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #F9FAFB;
    color: #6B7280;
    padding: 10px 20px;
    border: 1px solid #E5E7EB;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #6366F1;
    border-bottom: 2px solid #FFFFFF;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #F3F4F6;
}

/* ── Progress Bar ────────────────────────────────────────────────────────── */
QProgressBar {
    background-color: #E5E7EB;
    border: none;
    border-radius: 6px;
    text-align: center;
    height: 8px;
}

QProgressBar::chunk {
    background-color: #6366F1;
    border-radius: 6px;
}

/* ── Check Box ───────────────────────────────────────────────────────────── */
QCheckBox {
    color: #111827;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #D1D5DB;
    border-radius: 4px;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #6366F1;
    border-color: #6366F1;
}

QCheckBox::indicator:hover {
    border-color: #6366F1;
}

/* ── Radio Button ────────────────────────────────────────────────────────── */
QRadioButton {
    color: #111827;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #D1D5DB;
    border-radius: 10px;
    background-color: #FFFFFF;
}

QRadioButton::indicator:checked {
    background-color: #6366F1;
    border-color: #6366F1;
}

/* ── Tool Tips ───────────────────────────────────────────────────────────── */
QToolTip {
    background-color: #1F2937;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}

/* ── Message Box ─────────────────────────────────────────────────────────── */
QMessageBox {
    background-color: #FFFFFF;
}

QMessageBox QLabel {
    color: #111827;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""


def apply_theme(app):
    """Apply theme to QApplication"""
    app.setStyleSheet(THEME_QSS)
