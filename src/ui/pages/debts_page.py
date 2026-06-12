# -*- coding: utf-8 -*-
"""Debts page - mirrors Admin/Debts/Index.vue."""
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class DebtsPage(QWidget):
    """Debt list and payment management."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        layout.addLayout(self.create_header())
        layout.addLayout(self.create_stats_cards())
        layout.addWidget(self.create_filters())
        self.table = self.create_table()
        layout.addWidget(self.table, 1)
        self.refresh_data()

    def create_header(self):
        layout = QHBoxLayout()
        text_block = QVBoxLayout()
        title = QLabel("Quản lý Công Nợ")
        title.setObjectName("contentTitle")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        subtitle = QLabel("Theo dõi công nợ đơn hàng và lịch sử thanh toán")
        subtitle.setObjectName("contentSubtitle")
        text_block.addWidget(title)
        text_block.addWidget(subtitle)
        layout.addLayout(text_block)
        layout.addStretch()

        pay_button = QPushButton("Ghi nhận TT")
        pay_button.setObjectName("outlineButton")
        pay_button.setFixedWidth(120)
        pay_button.setFixedHeight(38)
        pay_button.clicked.connect(self.add_payment_for_selected)
        layout.addWidget(pay_button)

        add_button = QPushButton("+  Tạo công nợ")
        add_button.setObjectName("primaryButton")
        add_button.setFixedWidth(138)
        add_button.setFixedHeight(38)
        add_button.clicked.connect(self.create_debt)
        layout.addWidget(add_button)
        return layout

    def create_stats_cards(self):
        layout = QGridLayout()
        layout.setSpacing(12)
        self.stat_total = self.create_stat_card("Tổng nợ gốc", "0đ", "#111827", "statCard")
        self.stat_paid = self.create_stat_card("Đã thu", "0đ", "#047857", "statCardSuccess")
        self.stat_remaining = self.create_stat_card("Còn phải thu", "0đ", "#DC2626", "statCardDanger")
        self.stat_overdue = self.create_stat_card("Quá hạn", "0 đơn", "#6B7280", "statCard")
        layout.addWidget(self.stat_total, 0, 0)
        layout.addWidget(self.stat_paid, 0, 1)
        layout.addWidget(self.stat_remaining, 0, 2)
        layout.addWidget(self.stat_overdue, 0, 3)
        return layout

    def create_stat_card(self, title, value, color, object_name):
        frame = QFrame()
        frame.setObjectName(object_name)
        frame.setMinimumHeight(86)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        title_label = QLabel(title.upper())
        title_label.setObjectName("statTitle")
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setStyleSheet(f"color: {color};")
        frame.value_label = value_label
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return frame

    def create_filters(self):
        frame = QFrame()
        frame.setObjectName("filterBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm mã đơn, tên khách hàng...")
        self.search_input.returnPressed.connect(self.refresh_data)
        layout.addWidget(self.search_input, 1)

        self.status_combo = QComboBox()
        self.status_combo.addItem("Tất cả trạng thái", "")
        self.status_combo.addItem("Chờ thanh toán", "pending")
        self.status_combo.addItem("Thanh toán một phần", "partial")
        self.status_combo.addItem("Đã thanh toán", "paid")
        self.status_combo.currentIndexChanged.connect(self.refresh_data)
        self.status_combo.setFixedWidth(190)
        layout.addWidget(self.status_combo)
        return frame

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Mã đơn hàng", "Khách hàng", "Số tiền gốc",
            "Đã thanh toán", "Còn lại", "Trạng thái", "Ngày tạo đơn",
        ])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.NoFocus)
        table.doubleClicked.connect(self.add_payment_for_selected)
        return table

    def refresh_data(self, *_args):
        try:
            from src.services.debt_service import DebtService

            service = DebtService(self.db)
            debts = service.get_all(
                search=self.search_input.text().strip(),
                status=self.status_combo.currentData() or "",
            )
            stats = service.get_stats()
            self.stat_total.value_label.setText(self.format_currency(stats.get("total_original", 0)))
            self.stat_paid.value_label.setText(self.format_currency(stats.get("total_paid", 0)))
            self.stat_remaining.value_label.setText(self.format_currency(stats.get("total_remaining", 0)))
            self.stat_overdue.value_label.setText(f"{stats.get('count_overdue', 0)} đơn")
            self.render_table(debts)
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải công nợ: {exc}")

    def render_table(self, debts):
        self.table.setRowCount(0)
        if not debts:
            self.table.setRowCount(1)
            item = QTableWidgetItem("Không có công nợ nào")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 7)
            self.table.setRowHeight(0, 80)
            return

        for debt in debts:
            row = self.table.rowCount()
            self.table.insertRow(row)

            order_name = debt.get("order_name") or debt.get("order_number") or f"#{debt.get('order_id')}"
            code_item = QTableWidgetItem(order_name)
            code_item.setData(Qt.UserRole, debt.get("id"))
            code_item.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
            self.table.setItem(row, 0, code_item)

            customer = debt.get("customer_name") or debt.get("order_customer_name") or "—"
            self.table.setItem(row, 1, QTableWidgetItem(customer))
            self.table.setItem(row, 2, self.money_item(debt.get("original_amount") or debt.get("grand_total") or 0))
            self.table.setItem(row, 3, self.money_item(debt.get("paid_amount") or 0, "#059669"))
            remaining = float(debt.get("remaining_amount") or 0)
            self.table.setItem(row, 4, self.money_item(remaining, "#DC2626" if remaining > 0 else "#6B7280"))
            self.table.setCellWidget(row, 5, self.create_status_badge(debt.get("status", "pending")))
            self.table.setItem(row, 6, QTableWidgetItem(self.format_date(debt.get("order_created_at") or debt.get("created_at"))))

    def create_status_badge(self, status):
        labels = {
            "pending": ("Chờ thanh toán", "warning"),
            "partial": ("Thanh toán một phần", "info"),
            "paid": ("Đã thanh toán", "success"),
        }
        text, kind = labels.get(status, (status, "neutral"))
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(4, 0, 4, 0)
        label = QLabel(text)
        label.setObjectName(f"badge{kind.capitalize()}")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return frame

    def create_debt(self):
        dialog = DebtDialog(self.db, self)
        if dialog.has_orders is False:
            QMessageBox.information(self, "Công nợ", "Không có đơn hàng nào chưa tạo công nợ.")
            return
        if dialog.exec():
            try:
                from src.services.debt_service import DebtService

                DebtService(self.db).create(dialog.get_data())
                self.refresh_data()
                QMessageBox.information(self, "Thành công", "Đã tạo công nợ.")
            except Exception as exc:
                QMessageBox.critical(self, "Lỗi", f"Không thể tạo công nợ: {exc}")

    def add_payment_for_selected(self, *_args):
        row = self.table.currentRow()
        if row < 0 or not self.table.item(row, 0):
            QMessageBox.information(self, "Thanh toán", "Vui lòng chọn một dòng công nợ.")
            return
        debt_id = self.table.item(row, 0).data(Qt.UserRole)
        if not debt_id:
            return

        dialog = PaymentDialog(self)
        if dialog.exec():
            try:
                from src.services.debt_service import DebtService

                DebtService(self.db).add_payment(debt_id, dialog.get_data())
                self.refresh_data()
                QMessageBox.information(self, "Thành công", "Đã ghi nhận thanh toán.")
            except Exception as exc:
                QMessageBox.critical(self, "Lỗi", f"Không thể ghi nhận thanh toán: {exc}")

    @staticmethod
    def money_item(value, color=None):
        item = QTableWidgetItem(DebtsPage.format_currency(value))
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        if color:
            item.setForeground(QColor(color))
        return item

    @staticmethod
    def format_currency(value):
        return f"{float(value or 0):,.0f} đ"

    @staticmethod
    def format_date(value):
        return value[:10] if value else "—"


class DebtDialog(QDialog):
    """Create debt from an order."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.has_orders = True
        self.setWindowTitle("Tạo công nợ")
        self.setMinimumWidth(620)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.order_combo = QComboBox()
        self.orders = []
        self.load_orders()
        if not self.orders:
            self.has_orders = False
            return
        self.order_combo.currentIndexChanged.connect(self.apply_order_amount)
        form.addRow("Đơn hàng *", self.order_combo)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(10_000_000_000)
        self.amount_input.setSingleStep(100_000)
        self.amount_input.setSuffix(" đ")
        form.addRow("Số tiền gốc *", self.amount_input)

        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate().addDays(30))
        form.addRow("Hạn thanh toán", self.due_date)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        form.addRow("Ghi chú", self.notes)
        layout.addLayout(form)
        self.apply_order_amount()

        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Hủy")
        cancel.setObjectName("outlineButton")
        cancel.clicked.connect(self.reject)
        actions.addWidget(cancel)
        save = QPushButton("Tạo công nợ")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.accept)
        actions.addWidget(save)
        layout.addLayout(actions)

    def load_orders(self):
        try:
            from src.services.debt_service import DebtService

            self.orders = DebtService(self.db).get_orders_without_debt()
            for order in self.orders:
                label = f"{order.get('order_number')} - {order.get('customer_name')} ({DebtsPage.format_currency(order.get('grand_total'))})"
                self.order_combo.addItem(label, order)
        except Exception:
            self.orders = []

    def apply_order_amount(self):
        order = self.order_combo.currentData()
        if order:
            self.amount_input.setValue(float(order.get("grand_total") or 0))

    def accept(self):
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Số tiền công nợ phải lớn hơn 0.")
            return
        super().accept()

    def get_data(self):
        order = self.order_combo.currentData()
        return {
            "order_id": order.get("id"),
            "customer_id": order.get("customer_id"),
            "original_amount": self.amount_input.value(),
            "due_date": self.due_date.date().toString("yyyy-MM-dd"),
            "notes": self.notes.toPlainText().strip(),
        }


class PaymentDialog(QDialog):
    """Payment entry dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ghi nhận thanh toán")
        self.setMinimumWidth(460)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.amount = QDoubleSpinBox()
        self.amount.setMaximum(10_000_000_000)
        self.amount.setSingleStep(100_000)
        self.amount.setSuffix(" đ")
        form.addRow("Số tiền *", self.amount)

        self.method = QLineEdit()
        self.method.setPlaceholderText("Tiền mặt / chuyển khoản...")
        form.addRow("Phương thức", self.method)

        self.paid_at = QDateEdit()
        self.paid_at.setCalendarPopup(True)
        self.paid_at.setDate(QDate.currentDate())
        form.addRow("Ngày thanh toán", self.paid_at)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        form.addRow("Ghi chú", self.notes)
        layout.addLayout(form)

        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Hủy")
        cancel.setObjectName("outlineButton")
        cancel.clicked.connect(self.reject)
        actions.addWidget(cancel)
        save = QPushButton("Lưu thanh toán")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.accept)
        actions.addWidget(save)
        layout.addLayout(actions)

    def accept(self):
        if self.amount.value() <= 0:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Số tiền thanh toán phải lớn hơn 0.")
            return
        super().accept()

    def get_data(self):
        return {
            "amount": self.amount.value(),
            "payment_method": self.method.text().strip(),
            "paid_at": self.paid_at.date().toString("yyyy-MM-dd"),
            "notes": self.notes.toPlainText().strip(),
        }
