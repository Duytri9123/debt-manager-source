# -*- coding: utf-8 -*-
"""Advances page - mirrors Admin/Advances/Index.vue."""
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
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


class AdvancesPage(QWidget):
    """List and create advances."""

    def __init__(self, db):
        super().__init__()
        self.db = db
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
        title_block = QVBoxLayout()
        title = QLabel("Tạm ứng")
        title.setObjectName("contentTitle")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        subtitle = QLabel("Quản lý các khoản tạm ứng")
        subtitle.setObjectName("contentSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        layout.addLayout(title_block)
        layout.addStretch()

        add_button = QPushButton("+  Tạo tạm ứng")
        add_button.setObjectName("primaryButton")
        add_button.setFixedWidth(140)
        add_button.setFixedHeight(38)
        add_button.clicked.connect(self.create_advance)
        layout.addWidget(add_button)
        return layout

    def create_filters(self):
        frame = QFrame()
        frame.setObjectName("filterBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm số tạm ứng, mục đích...")
        self.search_input.returnPressed.connect(self.refresh_data)
        layout.addWidget(self.search_input, 1)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Tất cả loại", "")
        self.type_combo.addItem("Nhân viên", "employee")
        self.type_combo.addItem("Khách hàng", "customer")
        self.type_combo.addItem("Nhà cung cấp", "supplier")
        self.type_combo.currentIndexChanged.connect(self.refresh_data)
        self.type_combo.setFixedWidth(140)
        layout.addWidget(self.type_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItem("Tất cả trạng thái", "")
        self.status_combo.addItem("Chờ duyệt", "pending")
        self.status_combo.addItem("Đã duyệt", "approved")
        self.status_combo.addItem("Đã quyết toán", "settled")
        self.status_combo.addItem("Đã hủy", "cancelled")
        self.status_combo.currentIndexChanged.connect(self.refresh_data)
        self.status_combo.setFixedWidth(160)
        layout.addWidget(self.status_combo)
        return frame

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Số tạm ứng", "Loại", "Mục đích", "Ngày",
            "Số tiền", "Đã hoàn", "Còn lại", "Trạng thái",
        ])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.NoFocus)
        return table

    def refresh_data(self, *_args):
        try:
            from src.services.advance_service import AdvanceService

            service = AdvanceService(self.db)
            advances = service.get_all(
                search=self.search_input.text().strip(),
                type_filter=self.type_combo.currentData() or "",
                status=self.status_combo.currentData() or "",
            )
            self.table.setRowCount(0)

            if not advances:
                self.table.setRowCount(1)
                item = QTableWidgetItem("Chưa có tạm ứng nào")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(0, 0, item)
                self.table.setSpan(0, 0, 1, 8)
                self.table.setRowHeight(0, 80)
                return

            for advance in advances:
                row = self.table.rowCount()
                self.table.insertRow(row)
                amount = float(advance.get("amount") or 0)
                returned = float(advance.get("returned_amount") or 0)
                remaining = max(0, amount - returned)
                type_label = service.TYPES.get(advance.get("type"), advance.get("type", ""))

                self.table.setItem(row, 0, QTableWidgetItem(advance.get("advance_number", "")))
                self.table.setItem(row, 1, QTableWidgetItem(type_label))
                self.table.setItem(row, 2, QTableWidgetItem(advance.get("purpose") or "—"))
                self.table.setItem(row, 3, QTableWidgetItem(self.format_date(advance.get("advance_date"))))
                self.table.setItem(row, 4, QTableWidgetItem(self.format_currency(amount)))
                self.table.setItem(row, 5, QTableWidgetItem(self.format_currency(returned)))
                self.table.setItem(row, 6, QTableWidgetItem(self.format_currency(remaining)))
                self.table.setCellWidget(row, 7, self.create_status_badge(advance.get("status", "pending")))
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải tạm ứng: {exc}")

    def create_status_badge(self, status):
        labels = {
            "pending": ("Chờ duyệt", "warning"),
            "approved": ("Đã duyệt", "info"),
            "settled": ("Đã quyết toán", "success"),
            "cancelled": ("Đã hủy", "danger"),
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

    def create_advance(self):
        dialog = AdvanceDialog(self.db, self)
        if dialog.exec():
            try:
                from src.services.advance_service import AdvanceService

                service = AdvanceService(self.db)
                service.create(dialog.get_data())
                self.refresh_data()
                QMessageBox.information(self, "Thành công", "Đã tạo phiếu tạm ứng.")
            except Exception as exc:
                QMessageBox.critical(self, "Lỗi", f"Không thể tạo tạm ứng: {exc}")

    @staticmethod
    def format_currency(value):
        return f"{float(value or 0):,.0f}đ"

    @staticmethod
    def format_date(value):
        return value[:10] if value else "—"


class AdvanceDialog(QDialog):
    """Dialog for creating an advance."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Tạo tạm ứng")
        self.setMinimumWidth(620)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(12)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Tạm ứng nhân viên", "employee")
        self.type_combo.addItem("Đặt cọc khách hàng", "customer")
        self.type_combo.addItem("Tạm ứng nhà cung cấp", "supplier")
        form.addRow("Loại tạm ứng *", self.type_combo)

        self.person_input = QLineEdit()
        self.person_input.setPlaceholderText("Tên nhân viên / nhà cung cấp")
        form.addRow("Người nhận", self.person_input)

        self.customer_combo = QComboBox()
        self.customer_combo.addItem("Không chọn khách hàng", None)
        self.load_customers()
        form.addRow("Khách hàng", self.customer_combo)

        self.advance_date = QDateEdit()
        self.advance_date.setCalendarPopup(True)
        self.advance_date.setDate(QDate.currentDate())
        form.addRow("Ngày tạm ứng *", self.advance_date)

        self.expected_return_date = QDateEdit()
        self.expected_return_date.setCalendarPopup(True)
        self.expected_return_date.setDate(QDate.currentDate())
        form.addRow("Ngày hoàn dự kiến", self.expected_return_date)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(10_000_000_000)
        self.amount_input.setSingleStep(100_000)
        self.amount_input.setSuffix(" đ")
        form.addRow("Số tiền *", self.amount_input)

        self.status_combo = QComboBox()
        self.status_combo.addItem("Chờ duyệt", "pending")
        self.status_combo.addItem("Đã duyệt", "approved")
        self.status_combo.addItem("Đã quyết toán", "settled")
        self.status_combo.addItem("Đã hủy", "cancelled")
        form.addRow("Trạng thái", self.status_combo)

        self.purpose_input = QLineEdit()
        form.addRow("Mục đích", self.purpose_input)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(90)
        form.addRow("Ghi chú", self.notes_input)
        layout.addLayout(form)

        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Hủy")
        cancel.setObjectName("outlineButton")
        cancel.clicked.connect(self.reject)
        actions.addWidget(cancel)
        save = QPushButton("Tạo tạm ứng")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.accept)
        actions.addWidget(save)
        layout.addLayout(actions)

    def load_customers(self):
        try:
            from src.services.customer_service import CustomerService

            for customer in CustomerService(self.db).get_all():
                self.customer_combo.addItem(customer.get("name", ""), customer.get("id"))
        except Exception:
            pass

    def accept(self):
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Số tiền tạm ứng phải lớn hơn 0.")
            return
        super().accept()

    def get_data(self):
        adv_type = self.type_combo.currentData()
        person = self.person_input.text().strip()
        customer_id = self.customer_combo.currentData()
        return {
            "type": adv_type,
            "employee_name": person if adv_type == "employee" else None,
            "supplier_name": person if adv_type == "supplier" else None,
            "customer_id": customer_id if adv_type == "customer" else None,
            "advance_date": self.advance_date.date().toString("yyyy-MM-dd"),
            "expected_return_date": self.expected_return_date.date().toString("yyyy-MM-dd"),
            "amount": self.amount_input.value(),
            "status": self.status_combo.currentData(),
            "purpose": self.purpose_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip(),
        }
