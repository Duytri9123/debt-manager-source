# -*- coding: utf-8 -*-
"""
Modern QSS Theme - Clean, Professional B2B Management UI
Inspired by Linear, Vercel, and modern SaaS dashboards
"""

THEME_QSS = """
/* ═══════════════════════════════════════════════════════════════════════════
   GLOBAL STYLES
   ═══════════════════════════════════════════════════════════════════════════ */
* {
    font-family: 'Segoe UI', 'Inter', 'SF Pro Display', sans-serif;
}

QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-size: 13px;
}

QMainWindow {
    background-color: #f8fafc;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR — Sleek dark with gradient feel
   ═══════════════════════════════════════════════════════════════════════════ */
QFrame#sidebar {
    background-color: #0f172a;
    border-right: none;
}

QFrame#sidebar QWidget,
QWidget#sidebarNav,
QWidget#sidebarViewport,
QScrollArea#sidebarScroll {
    background-color: #0f172a;
}

QFrame#sidebar QLabel {
    background-color: transparent;
}

QFrame#sidebarHeader {
    background-color: #0f172a;
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

QLabel#logoLabel {
    color: #ffffff;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 1px;
}

QLabel#subtitleLabel {
    color: #94a3b8;
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 0.8px;
}

QLabel#sidebarChevron {
    color: #64748b;
    font-size: 22px;
}

QFrame#sidebarFooter {
    background-color: #0f172a;
    border-top: 1px solid rgba(148, 163, 184, 0.08);
}

/* Avatar */
QLabel#avatar, QLabel#topAvatar {
    background-color: #312e81;
    color: #c7d2fe;
    border-radius: 16px;
    font-weight: 700;
    font-size: 13px;
}

QLabel#sidebarUserName {
    color: #f1f5f9;
    font-size: 13px;
    font-weight: 700;
}

QLabel#sidebarUserEmail {
    color: #818cf8;
    font-size: 11px;
}

QLabel#topUserName {
    color: #475569;
    font-weight: 600;
}

/* Navigation Buttons */
QPushButton#navButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}

QPushButton#navButton:hover {
    background-color: rgba(99, 102, 241, 0.12);
    color: #e2e8f0;
}

QPushButton#navButton:checked {
    background-color: #6366f1;
    color: #ffffff;
    font-weight: 700;
}

QPushButton#navButton:pressed {
    background-color: #4f46e5;
}

QPushButton#logoutButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: left;
    font-size: 12px;
    font-weight: 500;
}

QPushButton#logoutButton:hover {
    background-color: rgba(239, 68, 68, 0.12);
    color: #f87171;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TOP BAR
   ═══════════════════════════════════════════════════════════════════════════ */
QFrame#topBar {
    background-color: #ffffff;
    border-bottom: 1px solid #f1f5f9;
}

QLabel#pageTitle {
    color: #0f172a;
    font-size: 20px;
    font-weight: 800;
}

QLabel#pageSubtitle {
    color: #64748b;
    font-size: 13px;
}

QLabel#contentTitle {
    color: #0f172a;
    font-size: 22px;
    font-weight: 800;
}

QLabel#contentSubtitle {
    color: #64748b;
    font-size: 13px;
}

QLabel#dialogTitle {
    color: #0f172a;
    font-size: 18px;
    font-weight: 800;
}

/* Filter & Form Cards */
QFrame#filterBar {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

QFrame#formCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
}

QWidget#transparentBlock {
    background-color: transparent;
}

QFrame#plainBar {
    background-color: transparent;
    border: none;
}

QFrame#segmented {
    background-color: #f1f5f9;
    border: none;
    border-radius: 12px;
    padding: 4px;
}

QPushButton#segmentButton {
    background-color: transparent;
    color: #64748b;
    border: none;
    border-radius: 9px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#segmentButton:checked {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #e2e8f0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   STAT CARDS — Modern card design with subtle depth
   ═══════════════════════════════════════════════════════════════════════════ */
QFrame#statCard {
    background-color: #ffffff;
    border: 1px solid #f1f5f9;
    border-radius: 14px;
    padding: 10px;
}

QFrame#statCard:hover {
    border-color: #e2e8f0;
    background-color: #fafbfc;
}

QLabel#statTitle {
    color: #94a3b8;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}

QLabel#statValue {
    color: #0f172a;
    font-size: 24px;
    font-weight: 800;
}

QLabel#statSubtitle {
    color: #94a3b8;
    font-size: 12px;
}

/* Stat Card Color Variants */
QFrame#statCardIndigo {
    background-color: #eef2ff;
    border: 1px solid #e0e7ff;
    border-radius: 14px;
}
QFrame#statCardIndigo:hover { border-color: #c7d2fe; }

QFrame#statCardEmerald {
    background-color: #ecfdf5;
    border: 1px solid #d1fae5;
    border-radius: 14px;
}
QFrame#statCardEmerald:hover { border-color: #a7f3d0; }

QFrame#statCardAmber {
    background-color: #fffbeb;
    border: 1px solid #fef3c7;
    border-radius: 14px;
}
QFrame#statCardAmber:hover { border-color: #fde68a; }

QFrame#statCardRed {
    background-color: #fef2f2;
    border: 1px solid #fee2e2;
    border-radius: 14px;
}
QFrame#statCardRed:hover { border-color: #fecaca; }

QFrame#statCardBlue {
    background-color: #eff6ff;
    border: 1px solid #dbeafe;
    border-radius: 14px;
}
QFrame#statCardBlue:hover { border-color: #bfdbfe; }

QFrame#statCardSuccess {
    background-color: #ecfdf5;
    border: 1px solid #d1fae5;
    border-radius: 14px;
}

QFrame#statCardDanger {
    background-color: #fef2f2;
    border: 1px solid #fee2e2;
    border-radius: 14px;
}

QFrame#statCardWarning {
    background-color: #fffbeb;
    border: 1px solid #fef3c7;
    border-radius: 14px;
}

QFrame#chartLine {
    background-color: #f1f5f9;
    border: none;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TABLES — Clean, airy data tables
   ═══════════════════════════════════════════════════════════════════════════ */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #f1f5f9;
    border-radius: 14px;
    gridline-color: transparent;
    selection-background-color: #eef2ff;
    selection-color: #1e293b;
    outline: none;
}

QTableWidget::item {
    padding: 10px 14px;
    border-bottom: 1px solid #f8fafc;
}

QTableWidget::item:hover {
    background-color: #f8fafc;
}

QTableWidget::item:selected {
    background-color: #eef2ff;
    color: #1e293b;
}

QHeaderView::section {
    background-color: #fafbfc;
    color: #94a3b8;
    padding: 12px 14px;
    border: none;
    border-bottom: 2px solid #f1f5f9;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   BUTTONS — Clear hierarchy with smooth interactions
   ═══════════════════════════════════════════════════════════════════════════ */
QPushButton {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #4f46e5;
}

QPushButton:pressed {
    background-color: #4338ca;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
}

/* Primary Button */
QPushButton#primaryButton {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    min-height: 24px;
    font-size: 13px;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background-color: #4f46e5;
}

QPushButton#primaryButton:pressed {
    background-color: #4338ca;
}

QPushButton#primaryButton:disabled {
    background-color: #eef2ff;
    color: #a5b4fc;
}

/* Button Variants */
QPushButton#successButton {
    background-color: #10b981;
    color: #ffffff;
    border-radius: 10px;
    font-weight: 700;
}

QPushButton#successButton:hover {
    background-color: #059669;
}

QPushButton#successButton:pressed {
    background-color: #047857;
}

QPushButton#warningButton {
    background-color: #f59e0b;
    color: #ffffff;
    border-radius: 10px;
    font-weight: 700;
}

QPushButton#warningButton:hover {
    background-color: #d97706;
}

QPushButton#warningButton:pressed {
    background-color: #b45309;
}

QPushButton#dangerButton {
    background-color: #ef4444;
    color: #ffffff;
    border-radius: 10px;
    font-weight: 700;
}

QPushButton#dangerButton:hover {
    background-color: #dc2626;
}

QPushButton#dangerButton:pressed {
    background-color: #b91c1c;
}

/* Outline Button */
QPushButton#outlineButton {
    background-color: #ffffff;
    color: #6366f1;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 20px;
    min-height: 24px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#outlineButton:enabled {
    background-color: #ffffff;
    color: #6366f1;
    border: 1.5px solid #e2e8f0;
}

QPushButton#outlineButton:hover {
    background-color: #f8fafc;
    color: #4f46e5;
    border-color: #6366f1;
}

QPushButton#outlineButton:pressed {
    background-color: #eef2ff;
    color: #4338ca;
}

QPushButton#outlineButton:disabled {
    background-color: #f8fafc;
    color: #cbd5e1;
    border: 1.5px solid #f1f5f9;
}

/* ═══════════════════════════════════════════════════════════════════════════
   INPUT FIELDS — Modern, approachable form controls
   ═══════════════════════════════════════════════════════════════════════════ */
QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: #1e293b;
    selection-background-color: #eef2ff;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 2px solid #6366f1;
    outline: none;
    background-color: #ffffff;
}

QLineEdit:hover, QTextEdit:hover {
    border-color: #cbd5e1;
}

QLineEdit::placeholder, QTextEdit::placeholder {
    color: #94a3b8;
}

QComboBox {
    padding: 10px 14px;
    min-height: 20px;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
    padding-right: 8px;
}

QComboBox::down-arrow {
    image: none;
    width: 0px;
    height: 0px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    selection-background-color: #eef2ff;
    selection-color: #1e293b;
    outline: none;
    padding: 6px;
}

QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 6px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #f8fafc;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #eef2ff;
}

QDateEdit {
    padding: 10px 14px;
}

QDateEdit::drop-down {
    border: none;
    width: 28px;
}

QSpinBox, QDoubleSpinBox {
    padding: 10px 14px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   LABELS
   ═══════════════════════════════════════════════════════════════════════════ */
QLabel {
    color: #1e293b;
    font-size: 13px;
    background-color: transparent;
}

QLabel#sectionTitle {
    color: #0f172a;
    font-size: 15px;
    font-weight: 700;
}

QLabel#formLabel {
    color: #475569;
    font-size: 12px;
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════════════════════
   BADGES — Pill-shaped status indicators
   ═══════════════════════════════════════════════════════════════════════════ */
QLabel#badgeSuccess {
    background-color: #d1fae5;
    color: #065f46;
    border-radius: 12px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#badgeWarning {
    background-color: #fef3c7;
    color: #92400e;
    border-radius: 12px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#badgeDanger {
    background-color: #fee2e2;
    color: #991b1b;
    border-radius: 12px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#badgeInfo {
    background-color: #dbeafe;
    color: #1e40af;
    border-radius: 12px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#badgeNeutral {
    background-color: #f1f5f9;
    color: #475569;
    border-radius: 12px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 11px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SCROLL BARS — Minimal, elegant
   ═══════════════════════════════════════════════════════════════════════════ */
QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 6px;
    margin: 2px 4px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    border-radius: 3px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   DIALOGS
   ═══════════════════════════════════════════════════════════════════════════ */
QDialog {
    background-color: #ffffff;
    border-radius: 16px;
}

QDialog QLabel {
    color: #1e293b;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TOOLBAR
   ═══════════════════════════════════════════════════════════════════════════ */
QToolBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 1px solid #f1f5f9;
    padding: 8px;
    spacing: 8px;
}

QToolBar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 8px 14px;
    color: #64748b;
}

QToolBar QToolButton:hover {
    background-color: #f8fafc;
    border-color: #e2e8f0;
}

QToolBar QToolButton:pressed {
    background-color: #f1f5f9;
}

/* ═══════════════════════════════════════════════════════════════════════════
   GROUP BOX
   ═══════════════════════════════════════════════════════════════════════════ */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    margin-top: 16px;
    padding-top: 28px;
    font-weight: 700;
    font-size: 14px;
    color: #0f172a;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 18px;
    padding: 0 10px;
    color: #475569;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TAB WIDGET
   ═══════════════════════════════════════════════════════════════════════════ */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f8fafc;
    color: #64748b;
    padding: 12px 24px;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 4px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #6366f1;
    border-bottom: 2px solid #ffffff;
    font-weight: 700;
}

QTabBar::tab:hover:!selected {
    background-color: #f1f5f9;
}

/* ═══════════════════════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════════════════════ */
QProgressBar {
    background-color: #f1f5f9;
    border: none;
    border-radius: 8px;
    text-align: center;
    height: 8px;
    font-size: 0px;
}

QProgressBar::chunk {
    background-color: #6366f1;
    border-radius: 8px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CHECK BOX
   ═══════════════════════════════════════════════════════════════════════════ */
QCheckBox {
    color: #1e293b;
    spacing: 10px;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #cbd5e1;
    border-radius: 6px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
}

QCheckBox::indicator:hover {
    border-color: #6366f1;
}

QCheckBox::indicator:checked:hover {
    background-color: #4f46e5;
}

/* ═══════════════════════════════════════════════════════════════════════════
   RADIO BUTTON
   ═══════════════════════════════════════════════════════════════════════════ */
QRadioButton {
    color: #1e293b;
    spacing: 10px;
    font-size: 13px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #cbd5e1;
    border-radius: 10px;
    background-color: #ffffff;
}

QRadioButton::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
}

QRadioButton::indicator:hover {
    border-color: #6366f1;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TOOL TIPS
   ═══════════════════════════════════════════════════════════════════════════ */
QToolTip {
    background-color: #0f172a;
    color: #f1f5f9;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   MESSAGE BOX
   ═══════════════════════════════════════════════════════════════════════════ */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #1e293b;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 90px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   ORDER LINE ITEMS (forms inside tables)
   ═══════════════════════════════════════════════════════════════════════════ */
QLineEdit#lineItemInput, QDoubleSpinBox#lineItemSpin {
    padding: 8px 12px;
    border-radius: 8px;
    min-height: 22px;
    font-size: 13px;
    border: 1.5px solid #e2e8f0;
}

QLineEdit#lineItemInput:focus, QDoubleSpinBox#lineItemSpin:focus {
    border: 2px solid #6366f1;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FLOATING CHAT BUTTON
   ═══════════════════════════════════════════════════════════════════════════ */
QPushButton#floatingChatButton {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    border-radius: 29px;
    font-size: 15px;
    font-weight: 800;
}

QPushButton#floatingChatButton:hover {
    background-color: #4f46e5;
}

QPushButton#floatingChatButton:pressed {
    background-color: #4338ca;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CHAT MODAL
   ═══════════════════════════════════════════════════════════════════════════ */
QFrame#chatHeader {
    background-color: #6366f1;
    border-top-left-radius: 14px;
    border-top-right-radius: 14px;
}

QLabel#chatTitle {
    color: #ffffff;
    background-color: transparent;
    font-weight: 700;
}

QPushButton#chatHeaderButton {
    background-color: rgba(255, 255, 255, 0.15);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#chatHeaderButton:hover {
    background-color: rgba(255, 255, 255, 0.25);
}

QTextEdit#chatHistory {
    background-color: #ffffff;
    border: none;
    border-radius: 0px;
    padding: 16px;
}

QPushButton#quickChatButton {
    background-color: #eef2ff;
    color: #4f46e5;
    border: 1px solid #e0e7ff;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#quickChatButton:hover {
    background-color: #e0e7ff;
    border-color: #c7d2fe;
}

/* ═══════════════════════════════════════════════════════════════════════════
   OVERRIDES — Force primary & outline button styles in all contexts
   ═══════════════════════════════════════════════════════════════════════════ */
QWidget QPushButton#primaryButton {
    background: #6366f1;
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    border-radius: 10px;
}

QWidget QPushButton#primaryButton:enabled {
    background: #6366f1;
    background-color: #6366f1;
    color: #ffffff;
    border: none;
}

QWidget QPushButton#primaryButton:hover {
    background: #4f46e5;
    background-color: #4f46e5;
    color: #ffffff;
}

QWidget QPushButton#primaryButton:pressed {
    background: #4338ca;
    background-color: #4338ca;
}

QWidget QPushButton#primaryButton:disabled {
    background: #eef2ff;
    background-color: #eef2ff;
    color: #a5b4fc;
    border: none;
}

QWidget QPushButton#outlineButton {
    background-color: #ffffff;
    color: #6366f1;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
}

QWidget QPushButton#outlineButton:hover {
    background-color: #f8fafc;
    color: #4f46e5;
    border-color: #6366f1;
}

QWidget QPushButton#outlineButton:pressed {
    background-color: #eef2ff;
    color: #4338ca;
}

QWidget QPushButton#outlineButton:disabled {
    background-color: #f8fafc;
    color: #cbd5e1;
    border: 1.5px solid #f1f5f9;
}

/* ═══════════════════════════════════════════════════════════════════════════
   ABSTRACT ITEM VIEW (dropdown lists, combo boxes)
   ═══════════════════════════════════════════════════════════════════════════ */
QAbstractItemView {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    selection-background-color: #eef2ff;
    selection-color: #1e293b;
    outline: none;
    padding: 4px;
}

QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 6px;
}

QAbstractItemView::item:hover {
    background-color: #f8fafc;
}

QAbstractItemView::item:selected {
    background-color: #eef2ff;
}
"""


def apply_theme(app):
    """Apply the modern theme to QApplication."""
    app.setStyleSheet(THEME_QSS)
