# -*- coding: utf-8 -*-
"""Customers page - mirrors Admin/Customers/Index.vue."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
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


class CustomersPage(QWidget):
    """Customer list and creation page."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.customers = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        layout.addLayout(self.create_header())
        layout.addWidget(self.create_filters())
        self.table = self.create_table()
        layout.addWidget(self.table, 1)
        self.refresh_data()

    def create_header(self):
        layout = QHBoxLayout()
        text_block = QVBoxLayout()
        title = QLabel("Hồ sơ Khách hàng")
        title.setObjectName("contentTitle")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.count_label = QLabel("0 khách hàng")
        self.count_label.setObjectName("contentSubtitle")
        text_block.addWidget(title)
        text_block.addWidget(self.count_label)
        layout.addLayout(text_block)
        layout.addStretch()

        add_button = QPushButton("+  Thêm khách hàng")
        add_button.setObjectName("outlineButton")
        add_button.setFixedWidth(168)
        add_button.setFixedHeight(38)
        add_button.clicked.connect(self.add_customer)
        layout.addWidget(add_button)
        return layout

    def create_filters(self):
        frame = QFrame()
        frame.setObjectName("plainBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm tên, SĐT, địa chỉ...")
        self.search_input.returnPressed.connect(self.refresh_data)
        layout.addWidget(self.search_input, 1)

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Sắp xếp: Ngày tạo", "created_at")
        self.sort_combo.addItem("Sắp xếp: Tên", "name")
        self.sort_combo.addItem("Sắp xếp: Đơn hàng", "orders_count")
        self.sort_combo.currentIndexChanged.connect(self.refresh_data)
        self.sort_combo.setFixedWidth(180)
        layout.addWidget(self.sort_combo)

        self.direction_button = QPushButton("↓  Giảm dần")
        self.direction_button.setObjectName("outlineButton")
        self.direction_button.setFixedWidth(120)
        self.direction_button.clicked.connect(self.toggle_direction)
        self.direction = "desc"
        layout.addWidget(self.direction_button)

        clear_button = QPushButton("Xóa bộ lọc")
        clear_button.setObjectName("outlineButton")
        clear_button.setFixedWidth(110)
        clear_button.clicked.connect(self.clear_filters)
        layout.addWidget(clear_button)
        return frame

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Khách hàng", "MST", "Số điện thoại", "Địa chỉ",
            "Đơn hàng", "Nhập", "Tổng ĐH", "Công nợ",
        ])

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.NoFocus)
        table.cellClicked.connect(self.open_customer_detail)
        return table

    def refresh_data(self, *_args):
        try:
            from src.services.customer_service import CustomerService

            service = CustomerService(self.db)
            self.customers = service.get_all(search=self.search_input.text().strip())
            self.apply_sort()
            self.count_label.setText(f"{len(self.customers)} khách hàng")
            self.render_table()
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải khách hàng: {exc}")

    def apply_sort(self):
        key = self.sort_combo.currentData()
        reverse = self.direction == "desc"
        if key == "orders_count":
            self.customers.sort(key=lambda item: item.get("orders_count") or 0, reverse=reverse)
        elif key == "name":
            self.customers.sort(key=lambda item: (item.get("name") or "").lower(), reverse=reverse)
        else:
            self.customers.sort(key=lambda item: item.get("created_at") or "", reverse=reverse)

    def render_table(self):
        self.table.setRowCount(0)
        if not self.customers:
            self.table.setRowCount(1)
            item = QTableWidgetItem("Không có khách hàng nào")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 8)
            self.table.setRowHeight(0, 80)
            return

        for customer in self.customers:
            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(customer.get("name", ""))
            name_item.setData(Qt.UserRole, customer.get("id"))
            name_item.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, QTableWidgetItem(customer.get("tax_code") or ""))
            self.table.setItem(row, 2, QTableWidgetItem(customer.get("phone") or ""))
            self.table.setItem(row, 3, QTableWidgetItem(customer.get("address") or ""))
            self.table.setItem(row, 4, self.numeric_item(customer.get("orders_count") or 0))
            self.table.setItem(row, 5, self.numeric_item(customer.get("purchase_invoices_count") or 0))
            self.table.setItem(row, 6, self.money_item(customer.get("total_order_value") or 0))
            debt_item = self.money_item(customer.get("remaining_debt") or 0)
            if float(customer.get("remaining_debt") or 0) > 0:
                debt_item.setForeground(QColor("#DC2626"))
            self.table.setItem(row, 7, debt_item)

    def toggle_direction(self):
        self.direction = "asc" if self.direction == "desc" else "desc"
        self.direction_button.setText("↑  Tăng dần" if self.direction == "asc" else "↓  Giảm dần")
        self.refresh_data()

    def clear_filters(self):
        self.search_input.clear()
        self.sort_combo.setCurrentIndex(0)
        self.direction = "desc"
        self.direction_button.setText("↓  Giảm dần")
        self.refresh_data()

    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec():
            try:
                from src.services.customer_service import CustomerService

                CustomerService(self.db).create(dialog.get_data())
                self.refresh_data()
                QMessageBox.information(self, "Thành công", "Đã thêm khách hàng.")
            except Exception as exc:
                QMessageBox.critical(self, "Lỗi", f"Không thể thêm khách hàng: {exc}")

    def open_customer_detail(self, row, _column):
        item = self.table.item(row, 0)
        if not item:
            return
        customer_id = item.data(Qt.UserRole)
        if not customer_id:
            return
        dialog = CustomerDetailDialog(self.db, customer_id, self)
        dialog.exec()
        self.refresh_data()

    @staticmethod
    def numeric_item(value):
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item

    @staticmethod
    def money_item(value):
        item = QTableWidgetItem(f"{float(value or 0):,.0f} đ")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item


class CustomerDetailDialog(QDialog):
    """Customer profile view with orders and debt summary."""

    def __init__(self, db, customer_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.customer_id = customer_id
        self.setWindowTitle("Hồ sơ khách hàng")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setMinimumSize(1100, 720)
        self.customer = self.load_customer()
        self.init_ui()

    def load_customer(self):
        from src.services.customer_service import CustomerService

        return CustomerService(self.db).get_by_id(self.customer_id) or {}

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(16)

        back = QLabel("Hồ sơ khách hàng")
        back.setObjectName("dialogTitle")
        back.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(back)

        layout.addWidget(self.create_profile_card())
        layout.addLayout(self.create_stats())

        content = QHBoxLayout()
        content.setSpacing(16)
        content.addWidget(self.create_orders_card(), 3)
        content.addWidget(self.create_debts_card(), 2)
        layout.addLayout(content, 1)

        actions = QHBoxLayout()
        actions.addStretch()
        close = QPushButton("Đóng")
        close.setObjectName("outlineButton")
        close.clicked.connect(self.accept)
        actions.addWidget(close)
        layout.addLayout(actions)

    def create_profile_card(self):
        frame = QFrame()
        frame.setObjectName("formCard")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(16)

        avatar = QLabel((self.customer.get("name") or "?")[:1].upper())
        avatar.setObjectName("topAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(56, 56)
        layout.addWidget(avatar)

        info = QVBoxLayout()
        name = QLabel(self.customer.get("name") or "Khách hàng")
        name.setFont(QFont("Segoe UI", 17, QFont.Bold))
        info.addWidget(name)

        meta = QLabel(
            f"MST: {self.customer.get('tax_code') or '—'}    "
            f"SĐT: {self.customer.get('phone') or '—'}    "
            f"Email: {self.customer.get('email') or '—'}    "
            f"Địa chỉ: {self.customer.get('address') or '—'}"
        )
        meta.setObjectName("contentSubtitle")
        meta.setWordWrap(True)
        info.addWidget(meta)

        created = QLabel(f"Ngày tạo: {self.format_date(self.customer.get('created_at'))}    Hoạt động")
        created.setObjectName("contentSubtitle")
        info.addWidget(created)
        layout.addLayout(info, 1)

        edit = QPushButton("Sửa thông tin")
        edit.setObjectName("outlineButton")
        edit.clicked.connect(self.edit_customer)
        layout.addWidget(edit)
        return frame

    def create_stats(self):
        layout = QGridLayout()
        layout.setSpacing(12)
        summary = self.summary()
        cards = [
            ("Đơn hàng", str(summary["orders_count"]), self.format_money(summary["orders_total"]), "statCard"),
            ("Đã thanh toán", self.format_money(summary["paid_total"]), "", "statCardSuccess"),
            ("Tổng công nợ", self.format_money(summary["debt_total"]), "", "statCardWarning"),
            ("Còn phải thu", self.format_money(summary["remaining_total"]), "", "statCardDanger"),
        ]
        for index, (title, value, sub, object_name) in enumerate(cards):
            frame = QFrame()
            frame.setObjectName(object_name)
            frame.setMinimumHeight(90)
            box = QVBoxLayout(frame)
            box.setContentsMargins(16, 12, 16, 12)
            title_label = QLabel(title)
            title_label.setObjectName("statTitle")
            value_label = QLabel(value)
            value_label.setObjectName("statValue")
            box.addWidget(title_label)
            box.addWidget(value_label)
            if sub:
                sub_label = QLabel(sub)
                sub_label.setObjectName("contentSubtitle")
                box.addWidget(sub_label)
            layout.addWidget(frame, 0, index)
        return layout

    def create_orders_card(self):
        frame = QFrame()
        frame.setObjectName("formCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        header = QHBoxLayout()
        title = QLabel("Đơn hàng bán ra")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()
        add_order = QPushButton("+  Thêm đơn hàng")
        add_order.setObjectName("primaryButton")
        add_order.clicked.connect(self.create_order)
        header.addWidget(add_order)
        layout.addLayout(header)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Mã đơn", "Tên đơn", "Ngày", "Trạng thái", "Tổng"])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.cellClicked.connect(lambda row, column: self.open_order_from_table(table, row, column))
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        orders = self.orders()
        if not orders:
            table.setRowCount(1)
            item = QTableWidgetItem("Chưa có đơn hàng")
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(0, 0, item)
            table.setSpan(0, 0, 1, 5)
            table.setRowHeight(0, 70)
        else:
            for order in orders:
                row = table.rowCount()
                table.insertRow(row)
                code_item = QTableWidgetItem(order.get("order_number") or "")
                code_item.setData(Qt.UserRole, order.get("id"))
                table.setItem(row, 0, code_item)
                table.setItem(row, 1, QTableWidgetItem(order.get("order_name") or "—"))
                table.setItem(row, 2, QTableWidgetItem(self.format_date(order.get("created_at"))))
                table.setItem(row, 3, QTableWidgetItem(self.payment_label(order.get("payment_status"))))
                table.setItem(row, 4, self.money_item(order.get("grand_total") or 0))
        layout.addWidget(table, 1)
        return frame

    def edit_customer(self):
        dialog = CustomerDialog(self, self.customer)
        if dialog.exec():
            try:
                from src.services.customer_service import CustomerService

                CustomerService(self.db).update(self.customer_id, dialog.get_data())
                QMessageBox.information(self, "Thành công", "Đã cập nhật khách hàng.")
                self.accept()
            except Exception as exc:
                QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật khách hàng: {exc}")

    def create_order(self):
        try:
            from src.services.order_service import OrderService
            from src.ui.pages.orders_page import OrderDialog

            dialog = OrderDialog(self, initial_customer=self.customer)
            if dialog.exec():
                OrderService(self.db).create(dialog.get_order_data(), dialog.get_items())
                QMessageBox.information(self, "Thành công", "Đã thêm đơn hàng cho khách hàng.")
                self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm đơn hàng: {exc}")

    def open_order_from_table(self, table, row, _column):
        item = table.item(row, 0)
        if not item:
            return
        order_id = item.data(Qt.UserRole)
        if not order_id:
            return
        from src.ui.pages.orders_page import OrderDetailDialog

        dialog = OrderDetailDialog(self.db, order_id, self)
        dialog.exec()

    def create_debts_card(self):
        frame = QFrame()
        frame.setObjectName("formCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        title = QLabel("Thông tin thanh toán")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Đơn", "Tổng", "Đã TT", "Còn lại"])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for column in range(1, 4):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)

        debts = self.debts()
        if not debts:
            table.setRowCount(1)
            item = QTableWidgetItem("Không có công nợ")
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(0, 0, item)
            table.setSpan(0, 0, 1, 4)
            table.setRowHeight(0, 70)
        else:
            for debt in debts:
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(debt.get("order_name") or debt.get("order_number") or "—"))
                table.setItem(row, 1, self.money_item(debt.get("original_amount") or 0))
                table.setItem(row, 2, self.money_item(debt.get("paid_amount") or 0))
                remain = self.money_item(debt.get("remaining_amount") or 0)
                remain.setForeground(QColor("#DC2626"))
                table.setItem(row, 3, remain)
        layout.addWidget(table, 1)
        return frame

    def summary(self):
        orders = self.orders()
        debts = self.debts()
        return {
            "orders_count": len(orders),
            "orders_total": sum(float(order.get("grand_total") or 0) for order in orders),
            "paid_total": sum(float(debt.get("paid_amount") or 0) for debt in debts),
            "debt_total": sum(float(debt.get("original_amount") or 0) for debt in debts),
            "remaining_total": sum(float(debt.get("remaining_amount") or 0) for debt in debts),
        }

    def orders(self):
        if not hasattr(self, "_orders"):
            self._orders = self.db.fetch_all(
                """
                SELECT *
                FROM orders
                WHERE customer_id = ?
                ORDER BY created_at DESC
                """,
                (self.customer_id,),
            )
        return self._orders

    def debts(self):
        if not hasattr(self, "_debts"):
            self._debts = self.db.fetch_all(
                """
                SELECT d.*, o.order_number, o.order_name
                FROM debts d
                LEFT JOIN orders o ON o.id = d.order_id
                WHERE d.customer_id = ?
                ORDER BY d.created_at DESC
                """,
                (self.customer_id,),
            )
        return self._debts

    @staticmethod
    def payment_label(status):
        return {
            "paid": "Đã TT",
            "partial": "Một phần",
            "unpaid": "Chưa TT",
        }.get(status or "unpaid", "Chưa TT")

    @staticmethod
    def format_date(value):
        return value[:10] if value else "—"

    @staticmethod
    def format_money(value):
        return f"{float(value or 0):,.0f} đ"

    @staticmethod
    def money_item(value):
        item = QTableWidgetItem(CustomerDetailDialog.format_money(value))
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item


class CustomerDialog(QDialog):
    """Dialog for adding or editing a customer."""

    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer or {}
        self.setWindowTitle("Chỉnh sửa khách hàng" if self.customer else "Thêm khách hàng mới")
        self.setMinimumWidth(720)
        self.init_ui()
        if self.customer:
            self.populate_customer()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("Chỉnh sửa khách hàng" if self.customer else "Thêm khách hàng mới")
        title.setObjectName("dialogTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập tên khách hàng")
        form.addRow("Tên khách hàng *", self.name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nhập số điện thoại")
        form.addRow("Số điện thoại", self.phone_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email (tùy chọn)")
        form.addRow("Email", self.email_input)

        self.tax_code_input = QLineEdit()
        self.tax_code_input.setPlaceholderText("Nhập mã số thuế (tùy chọn)")
        form.addRow("Mã số thuế", self.tax_code_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Nhập địa chỉ (tùy chọn)")
        form.addRow("Địa chỉ", self.address_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Nhập ghi chú (tùy chọn)")
        self.notes_input.setMaximumHeight(90)
        form.addRow("Ghi chú", self.notes_input)
        layout.addLayout(form)

        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Hủy")
        cancel.setObjectName("outlineButton")
        cancel.clicked.connect(self.reject)
        actions.addWidget(cancel)

        save = QPushButton("Lưu khách hàng")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.accept)
        actions.addWidget(save)
        layout.addLayout(actions)

    def populate_customer(self):
        self.name_input.setText(self.customer.get("name") or "")
        self.phone_input.setText(self.customer.get("phone") or "")
        self.email_input.setText(self.customer.get("email") or "")
        self.tax_code_input.setText(self.customer.get("tax_code") or "")
        self.address_input.setText(self.customer.get("address") or "")
        self.notes_input.setPlainText(self.customer.get("notes") or "")

    def accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Thiếu dữ liệu", "Tên khách hàng là bắt buộc.")
            return
        super().accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip(),
            "tax_code": self.tax_code_input.text().strip(),
            "address": self.address_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip(),
            "is_active": True,
        }
