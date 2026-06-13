# -*- coding: utf-8 -*-
"""B2B orders page - mirrors Admin/B2BOrders/Index.vue."""
from PySide6.QtCore import QDate, QStringListModel, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QCompleter,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

DRAG_COLUMN = 0
INDEX_COLUMN = 1
DESCRIPTION_COLUMN = 2
SKU_COLUMN = 3
ORIGIN_COLUMN = 4
UNIT_COLUMN = 5
QUANTITY_COLUMN = 6
PRICE_COLUMN = 7
TOTAL_COLUMN = 8
NOTE_COLUMN = 9
ACTION_COLUMN = 10
ITEM_TABLE_COLUMNS = 11
DRAG_HANDLE_TEXT = "☰"
ITEM_NAV_COLUMNS = (
    DESCRIPTION_COLUMN,
    SKU_COLUMN,
    ORIGIN_COLUMN,
    UNIT_COLUMN,
    QUANTITY_COLUMN,
    PRICE_COLUMN,
    NOTE_COLUMN,
)


class OrdersPage(QWidget):
    """B2B order tracking page."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.orders = []
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
        title = QLabel("Theo dõi Đơn hàng KD")
        title.setObjectName("contentTitle")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        subtitle = QLabel("Quản lý đơn hàng kinh doanh B2B - thay thế Excel")
        subtitle.setObjectName("contentSubtitle")
        text_block.addWidget(title)
        text_block.addWidget(subtitle)
        layout.addLayout(text_block)
        layout.addStretch()

        import_button = QPushButton("Import Excel")
        import_button.setObjectName("outlineButton")
        import_button.setFixedWidth(132)
        import_button.setFixedHeight(38)
        import_button.clicked.connect(self.import_excel)
        layout.addWidget(import_button)

        add_button = QPushButton("+  Tạo đơn hàng")
        add_button.setObjectName("primaryButton")
        add_button.setFixedWidth(142)
        add_button.setFixedHeight(38)
        add_button.clicked.connect(self.create_order)
        layout.addWidget(add_button)
        return layout

    def create_stats_cards(self):
        layout = QGridLayout()
        layout.setSpacing(12)
        self.stat_total_orders = self.create_stat_card("Tổng đơn", "0", "#4F46E5")
        self.stat_customers = self.create_stat_card("Khách hàng", "0", "#2563EB")
        self.stat_revenue = self.create_stat_card("Doanh thu", "0đ", "#059669")
        layout.addWidget(self.stat_total_orders, 0, 0)
        layout.addWidget(self.stat_customers, 0, 1)
        layout.addWidget(self.stat_revenue, 0, 2)
        return layout

    def create_stat_card(self, title, value, color):
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setMinimumHeight(86)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        label = QLabel(title.upper())
        label.setObjectName("statTitle")
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setStyleSheet(f"color: {color};")
        frame.value_label = value_label
        layout.addWidget(label)
        layout.addWidget(value_label)
        return frame

    def create_filters(self):
        frame = QFrame()
        frame.setObjectName("filterBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm mã đơn, tên khách...")
        self.search_input.returnPressed.connect(self.refresh_data)
        layout.addWidget(self.search_input, 1)

        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("dd/MM/yyyy")
        self.from_date.setDate(QDate.currentDate().addMonths(-12))
        self.from_date.setFixedHeight(38)
        self.from_date.setFixedWidth(160)
        layout.addWidget(self.from_date)

        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat("dd/MM/yyyy")
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setFixedHeight(38)
        self.to_date.setFixedWidth(160)
        layout.addWidget(self.to_date)

        filter_button = QPushButton("Lọc")
        filter_button.setObjectName("outlineButton")
        filter_button.setFixedWidth(70)
        filter_button.clicked.connect(self.refresh_data)
        layout.addWidget(filter_button)

        reset_button = QPushButton("Reset")
        reset_button.setObjectName("outlineButton")
        reset_button.setFixedWidth(80)
        reset_button.clicked.connect(self.reset_filters)
        layout.addWidget(reset_button)
        return frame

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "Mã đơn", "Khách hàng", "Tên đơn hàng", "Ngày đặt",
            "Ngày xuất", "Trạng thái", "Số SP", "Tổng sau thuế", "",
        ])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.Interactive)
        header.setSectionResizeMode(6, QHeaderView.Interactive)
        header.setSectionResizeMode(7, QHeaderView.Interactive)
        header.setSectionResizeMode(8, QHeaderView.Interactive)
        table.setColumnWidth(0, 160) # Mã đơn
        table.setColumnWidth(1, 180) # Khách hàng
        table.setColumnWidth(3, 110) # Ngày đặt
        table.setColumnWidth(4, 110) # Ngày xuất
        table.setColumnWidth(5, 120) # Trạng thái
        table.setColumnWidth(6, 90)  # Số SP
        table.setColumnWidth(7, 130) # Tổng sau thuế
        table.setColumnWidth(8, 50)  # Action column
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.NoFocus)
        table.cellClicked.connect(self.open_order_detail)
        return table

    def refresh_data(self):
        try:
            from src.services.order_service import OrderService

            service = OrderService(self.db)
            self.orders = service.get_all(
                search=self.search_input.text().strip(),
                from_date=self.from_date.date().toString("yyyy-MM-dd"),
                to_date=self.to_date.date().toString("yyyy-MM-dd"),
            )
            stats = service.get_stats()

            self.stat_total_orders.value_label.setText(str(stats.get("total_orders", 0)))
            self.stat_customers.value_label.setText(str(stats.get("total_customers", 0)))
            self.stat_revenue.value_label.setText(self.format_currency(stats.get("total_revenue", 0)))
            self.render_table(self.orders)
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải đơn hàng: {exc}")

    def render_table(self, orders):
        self.table.setRowCount(0)
        if not orders:
            self.table.setRowCount(1)
            item = QTableWidgetItem("Chưa có đơn hàng nào")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 9)
            self.table.setRowHeight(0, 80)
            return

        for order in orders:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 44)

            code_item = QTableWidgetItem(order.get("order_number", ""))
            code_item.setData(Qt.UserRole, order.get("id"))
            code_item.setForeground(QColor("#4F46E5"))
            code_item.setFont(QFont("Consolas", 9, QFont.DemiBold))
            self.table.setItem(row, 0, code_item)
            self.table.setItem(row, 1, QTableWidgetItem(order.get("customer_full_name") or order.get("customer_name") or ""))
            self.table.setItem(row, 2, QTableWidgetItem(order.get("order_name") or "—"))
            self.table.setItem(row, 3, QTableWidgetItem(self.format_date(order.get("created_at"))))
            self.table.setItem(row, 4, QTableWidgetItem(self.format_date(order.get("delivery_date"))))
            self.table.setCellWidget(row, 5, self.create_payment_badge(order))
            self.table.setItem(row, 6, self.center_item(order.get("items_count") or 0))
            self.table.setItem(row, 7, self.money_item(order.get("grand_total") or 0))
            self.table.setCellWidget(row, 8, self.create_action_button(order))

    def create_payment_badge(self, order):
        status = order.get("payment_status") or "unpaid"
        if order.get("debt_status"):
            status = {"paid": "paid", "partial": "partial"}.get(order.get("debt_status"), "unpaid")
        labels = {
            "paid": ("Đã TT", "success"),
            "partial": ("Một phần", "warning"),
            "unpaid": ("Chưa TT", "danger"),
        }
        text, kind = labels.get(status, ("Chưa TT", "danger"))
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(text)
        label.setObjectName(f"badge{kind.capitalize()}")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(24)
        label.setFixedWidth(78)
        layout.addWidget(label)
        return frame

    def reset_filters(self):
        self.search_input.clear()
        self.from_date.setDate(QDate.currentDate().addMonths(-12))
        self.to_date.setDate(QDate.currentDate())
        self.refresh_data()

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        try:
            from src.services.excel_service import ExcelService
            from src.services.order_service import OrderService

            parser = ExcelService()
            result = parser.import_orders_from_excel(file_path)
            service = OrderService(self.db)

            imported = 0
            failed = 0
            for block in result.get("orders", []):
                try:
                    order_id = service.create(
                        {
                            "customer_name": block.get("customer"),
                            "order_date": block.get("date"),
                            "status": "delivered",
                            "tax_rate": 10,
                        },
                        block.get("items", []),
                    )
                    self.db.execute(
                        "UPDATE orders SET payment_status='paid' WHERE id=?",
                        (order_id,),
                    )
                    imported += 1
                except Exception:
                    failed += 1

            self.refresh_data()
            QMessageBox.information(
                self,
                "Import Excel",
                f"Import thành công {imported} đơn" + (f", lỗi {failed} đơn." if failed else "."),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi", f"Import thất bại: {exc}")

    def create_order(self):
        dialog = OrderDialog(self)
        if dialog.exec():
            try:
                from src.services.order_service import OrderService

                service = OrderService(self.db)
                service.create(dialog.get_order_data(), dialog.get_items())
                self.refresh_data()
                QMessageBox.information(self, "Thành công", "Đã tạo đơn hàng.")
            except Exception as exc:
                QMessageBox.critical(self, "Lỗi", f"Không thể tạo đơn hàng: {exc}")

    def open_order_detail(self, row, column):
        if column == 8:
            return
        item = self.table.item(row, 0)
        if not item:
            return
        order_id = item.data(Qt.UserRole)
        if not order_id:
            return
        dialog = OrderDetailDialog(self.db, order_id, self)
        dialog.exec()
        self.refresh_data()

    def create_action_button(self, order):
        btn = QPushButton("⋮")
        btn.setObjectName("actionMenuButton")
        btn.setFixedSize(30, 30)
        btn.setStyleSheet("""
            QPushButton#actionMenuButton {
                border: none;
                background: transparent;
                font-weight: bold;
                font-size: 16px;
                color: #64748B;
                border-radius: 4px;
            }
            QPushButton#actionMenuButton:hover {
                background-color: #E2E8F0;
                color: #1E293B;
            }
        """)
        btn.setToolTip("Xóa, chỉnh sửa, xem chi tiết")
        btn.clicked.connect(lambda: self.show_row_action_menu(btn, order))
        return btn

    def show_row_action_menu(self, btn, order):
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 6px 20px;
                color: #334155;
            }
            QMenu::item:selected {
                background-color: #F1F5F9;
                color: #0F172A;
            }
        """)
        
        view_action = QAction("Xem chi tiết", self)
        edit_action = QAction("Chỉnh sửa", self)
        delete_action = QAction("Xóa", self)
        
        view_action.triggered.connect(lambda: self.open_order_detail_by_id(order.get("id")))
        edit_action.triggered.connect(lambda: self.edit_order_by_id(order))
        delete_action.triggered.connect(lambda: self.delete_order_by_id(order))
        
        menu.addAction(view_action)
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        
        menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    def open_order_detail_by_id(self, order_id):
        if not order_id:
            return
        dialog = OrderDetailDialog(self.db, order_id, self)
        dialog.exec()
        self.refresh_data()

    def edit_order_by_id(self, order):
        order_id = order.get("id")
        if not order_id:
            return
        try:
            from src.services.order_service import OrderService
            full_order = OrderService(self.db).get_by_id(order_id)
            if not full_order:
                return
            dialog = OrderDialog(self, full_order)
            if dialog.exec():
                OrderService(self.db).update(order_id, dialog.get_order_data(), dialog.get_items())
                self.refresh_data()
                QMessageBox.information(self, "Thành công", "Đã cập nhật đơn hàng.")
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật đơn hàng: {exc}")

    def delete_order_by_id(self, order):
        order_id = order.get("id")
        order_number = order.get("order_number") or ""
        if not order_id:
            return
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa đơn hàng {order_number} không?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                from src.services.order_service import OrderService
                OrderService(self.db).delete(order_id)
                self.refresh_data()
                QMessageBox.information(self, "Thành công", "Đã xóa đơn hàng.")
            except Exception as exc:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa đơn hàng: {exc}")

    @staticmethod
    def center_item(value):
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        return item

    @staticmethod
    def money_item(value):
        item = QTableWidgetItem(OrdersPage.format_currency(value))
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        return item

    @staticmethod
    def format_currency(value):
        return f"{float(value or 0):,.0f}đ"

    @staticmethod
    def format_date(value):
        return value[:10] if value else "—"


class OrderDetailDialog(QDialog):
    """Read-only order detail with edit action."""

    def __init__(self, db, order_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.order_id = order_id
        self.setWindowTitle("Chi tiết đơn hàng")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setMinimumSize(1100, 720)
        self.init_ui()

    def load_order(self):
        from src.services.order_service import OrderService

        return OrderService(self.db).get_by_id(self.order_id) or {}

    def init_ui(self):
        self.order = self.load_order()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel(self.order.get("order_name") or self.order.get("order_number") or "Chi tiết đơn hàng")
        title.setObjectName("dialogTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        edit = QPushButton("Chỉnh sửa")
        edit.setObjectName("warningButton")
        edit.clicked.connect(self.edit_order)
        header.addWidget(edit)

        close = QPushButton("Đóng")
        close.setObjectName("outlineButton")
        close.clicked.connect(self.accept)
        header.addWidget(close)
        layout.addLayout(header)

        info = QFrame()
        info.setObjectName("formCard")
        info_layout = QGridLayout(info)
        info_layout.setContentsMargins(16, 14, 16, 14)
        info_layout.setHorizontalSpacing(24)
        info_layout.setVerticalSpacing(10)

        rows = [
            ("Mã đơn", self.order.get("order_number") or "—"),
            ("Khách hàng", self.order.get("customer_full_name") or self.order.get("customer_name") or "—"),
            ("Số điện thoại", self.order.get("customer_phone") or "—"),
            ("Ngày đặt", self.format_date(self.order.get("created_at"))),
            ("Ngày xuất", self.format_date(self.order.get("delivery_date"))),
            ("Trạng thái", self.status_label(self.order.get("status"))),
            ("Thanh toán", self.payment_label(self.order.get("payment_status"))),
            ("Tổng sau thuế", self.format_money(self.order.get("grand_total") or 0)),
        ]
        for index, (label, value) in enumerate(rows):
            box = QVBoxLayout()
            label_widget = QLabel(label)
            label_widget.setObjectName("statTitle")
            value_widget = QLabel(str(value))
            value_widget.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            box.addWidget(label_widget)
            box.addWidget(value_widget)
            info_layout.addLayout(box, index // 4, index % 4)
        layout.addWidget(info)

        notes = self.order.get("notes")
        if notes:
            note_label = QLabel(f"Ghi chú: {notes}")
            note_label.setWordWrap(True)
            note_label.setObjectName("contentSubtitle")
            layout.addWidget(note_label)

        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Mô tả chi tiết", "Mã hàng", "Xuất xứ", "Đơn vị",
            "Số lượng", "Đơn giá", "Thành tiền", "Ghi chú",
        ])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        header_view = table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)
        for column in range(1, 8):
            header_view.setSectionResizeMode(column, QHeaderView.ResizeToContents)

        items = self.order.get("items") or []
        table.setRowCount(len(items) if items else 1)
        if not items:
            item = QTableWidgetItem("Chưa có dòng sản phẩm")
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(0, 0, item)
            table.setSpan(0, 0, 1, 8)
        else:
            import json
            for row, line in enumerate(items):
                attrs_str = line.get("variant_attributes")
                is_cat = False
                if attrs_str:
                    try:
                        attrs = json.loads(attrs_str) if isinstance(attrs_str, str) else attrs_str
                        if attrs.get("type") == "category":
                            is_cat = True
                    except Exception:
                        pass
                
                if is_cat:
                    # Tính tổng phụ của danh mục này cho đến danh mục tiếp theo
                    cat_total = 0
                    for j in range(row + 1, len(items)):
                        next_line = items[j]
                        next_attrs_str = next_line.get("variant_attributes")
                        next_is_cat = False
                        if next_attrs_str:
                            try:
                                next_attrs = json.loads(next_attrs_str) if isinstance(next_attrs_str, str) else next_attrs_str
                                if next_attrs.get("type") == "category":
                                    next_is_cat = True
                            except Exception:
                                pass
                        if next_is_cat:
                            break
                        cat_total += float(next_line.get("line_total") or 0)
                    
                    cat_item = QTableWidgetItem(f"📁  {line.get('product_name') or ''}")
                    cat_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                    cat_item.setBackground(QColor("#FFFBEB"))
                    cat_item.setForeground(QColor("#B45309"))
                    table.setItem(row, 0, cat_item)
                    table.setSpan(row, 0, 1, 6)
                    
                    # Style merged cells backgrounds
                    for col in range(1, 6):
                        empty_item = QTableWidgetItem("")
                        empty_item.setBackground(QColor("#FFFBEB"))
                        table.setItem(row, col, empty_item)
                    
                    total_item = QTableWidgetItem(self.format_money(cat_total))
                    total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    total_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                    total_item.setForeground(QColor("#B45309"))
                    total_item.setBackground(QColor("#FFFBEB"))
                    table.setItem(row, 6, total_item)
                    
                    note_item = QTableWidgetItem("")
                    note_item.setBackground(QColor("#FFFBEB"))
                    table.setItem(row, 7, note_item)
                else:
                    table.setItem(row, 0, QTableWidgetItem(line.get("product_name") or ""))
                    table.setItem(row, 1, QTableWidgetItem(line.get("variant_sku") or ""))
                    table.setItem(row, 2, QTableWidgetItem(line.get("origin") or ""))
                    table.setItem(row, 3, QTableWidgetItem(line.get("unit") or ""))
                    table.setItem(row, 4, self.center_item(line.get("quantity") or 0))
                    table.setItem(row, 5, self.money_item(line.get("price") or 0))
                    table.setItem(row, 6, self.money_item(line.get("line_total") or 0))
                    table.setItem(row, 7, QTableWidgetItem(line.get("note") or ""))
        layout.addWidget(table, 1)

    def edit_order(self):
        dialog = OrderDialog(self, self.order)
        if dialog.exec():
            try:
                from src.services.order_service import OrderService

                OrderService(self.db).update(self.order_id, dialog.get_order_data(), dialog.get_items())
                QMessageBox.information(self, "Thành công", "Đã cập nhật đơn hàng.")
                self.accept()
            except Exception as exc:
                QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật đơn hàng: {exc}")

    @staticmethod
    def format_date(value):
        return value[:10] if value else "—"

    @staticmethod
    def format_money(value):
        return f"{float(value or 0):,.0f}đ"

    @staticmethod
    def status_label(status):
        return {
            "pending": "Chờ xử lý",
            "processing": "Đang xử lý",
            "delivered": "Đã giao",
            "cancelled": "Đã hủy",
        }.get(status or "pending", "Chờ xử lý")

    @staticmethod
    def payment_label(status):
        return {
            "paid": "Đã TT",
            "partial": "Một phần",
            "unpaid": "Chưa TT",
        }.get(status or "unpaid", "Chưa TT")

    @staticmethod
    def center_item(value):
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        return item

    @staticmethod
    def money_item(value):
        item = QTableWidgetItem(OrderDetailDialog.format_money(value))
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item


class DragDropTableWidget(QTableWidget):
    """Table widget supporting drag-and-drop row reordering."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.dragged_row = -1
        self.parent_dialog = None

    def mousePressEvent(self, event):
        col = self.columnAt(event.position().x())
        if col == DRAG_COLUMN:
            row = self.rowAt(event.position().y())
            if row >= 0:
                self.dragged_row = row
                self.setCurrentCell(row, DRAG_COLUMN)
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.source() == self and self.dragged_row >= 0:
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.source() == self and self.dragged_row >= 0:
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.source() == self and self.dragged_row >= 0:
            model_index = self.indexAt(event.position().toPoint())
            target_row = model_index.row()
            if target_row < 0:
                target_row = self.rowCount() - 1

            source_row = self.dragged_row
            if source_row >= 0 and target_row >= 0 and source_row != target_row:
                event.acceptProposedAction()
                if self.parent_dialog and hasattr(self.parent_dialog, "move_row"):
                    self.parent_dialog.move_row(source_row, target_row)
            self.dragged_row = -1
        else:
            super().dropEvent(event)


class OrderDialog(QDialog):
    """Dialog for creating a B2B order with line items."""

    def __init__(self, parent=None, order=None, initial_customer=None):
        super().__init__(parent)
        self.order = order or {}
        self.initial_customer = initial_customer or {}
        self.customer_lookup = []
        self.customer_completer = None
        self.setWindowTitle("Chỉnh sửa đơn hàng" if self.order else "Tạo đơn hàng mới")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setMinimumSize(900, 620)
        self.resize(1180, 740)
        self.init_ui()
        if self.order:
            self.populate_order()
        elif self.initial_customer:
            self.populate_customer()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        title = QLabel("Chỉnh sửa đơn hàng" if self.order else "Tạo đơn hàng mới")
        title.setObjectName("dialogTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.full_button = QPushButton("Hiển thị full")
        self.full_button.setObjectName("outlineButton")
        self.full_button.setFixedWidth(124)
        self.full_button.setFocusPolicy(Qt.NoFocus)
        self.full_button.clicked.connect(self.toggle_fullscreen)
        header_layout.addWidget(self.full_button)
        layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("dialogScroll")
        content = QWidget()
        content.setObjectName("dialogContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        customer_card = QFrame()
        customer_card.setObjectName("formCard")
        customer_layout = QVBoxLayout(customer_card)
        customer_layout.setContentsMargins(14, 10, 14, 12)
        customer_layout.setSpacing(8)

        # Title Layout with toggle button
        title_layout = QHBoxLayout()
        card_title = QLabel("Thông tin khách hàng")
        card_title.setObjectName("sectionTitle")
        title_layout.addWidget(card_title)
        title_layout.addStretch()
        
        self.toggle_customer_btn = QPushButton("Thu gọn  ▲")
        self.toggle_customer_btn.setObjectName("outlineButton")
        self.toggle_customer_btn.setFixedWidth(100)
        self.toggle_customer_btn.setFixedHeight(28)
        self.toggle_customer_btn.setFocusPolicy(Qt.NoFocus)
        self.toggle_customer_btn.clicked.connect(self.toggle_customer_info)
        title_layout.addWidget(self.toggle_customer_btn)
        customer_layout.addLayout(title_layout)

        # Collapsible Fields Container
        self.customer_fields_container = QWidget()
        self.customer_fields_container.setObjectName("transparentBlock")
        customer_fields_layout = QVBoxLayout(self.customer_fields_container)
        customer_fields_layout.setContentsMargins(0, 0, 0, 0)
        customer_fields_layout.setSpacing(8)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)

        self.customer_name = self.create_field("Tên khách hàng")
        self.setup_customer_completer()
        grid.addWidget(self.create_field_block("Tên khách hàng *", self.customer_name), 0, 0)

        self.customer_phone = self.create_field("Số điện thoại")
        grid.addWidget(self.create_field_block("Số điện thoại", self.customer_phone), 0, 1)

        self.order_date = QDateEdit()
        self.order_date.setCalendarPopup(True)
        self.order_date.setDisplayFormat("dd/MM/yyyy")
        self.order_date.setDate(QDate.currentDate())
        self.order_date.setFixedHeight(38)
        grid.addWidget(self.create_field_block("Ngày đặt *", self.order_date), 1, 0)

        self.delivery_date = QDateEdit()
        self.delivery_date.setCalendarPopup(True)
        self.delivery_date.setDisplayFormat("dd/MM/yyyy")
        self.delivery_date.setDate(QDate.currentDate())
        self.delivery_date.setFixedHeight(38)
        grid.addWidget(self.create_field_block("Ngày xuất", self.delivery_date), 1, 1)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(70)
        self.notes.setPlaceholderText("Ghi chú...")
        grid.addWidget(self.create_field_block("Ghi chú đơn hàng", self.notes), 2, 0, 1, 2)

        for column in range(2):
            grid.setColumnStretch(column, 1)
        customer_fields_layout.addLayout(grid)
        customer_layout.addWidget(self.customer_fields_container)
        content_layout.addWidget(customer_card)

        order_card = QFrame()
        order_card.setObjectName("formCard")
        order_layout = QVBoxLayout(order_card)
        order_layout.setContentsMargins(14, 10, 14, 12)
        order_layout.setSpacing(8)

        order_grid = QGridLayout()
        order_grid.setHorizontalSpacing(12)
        order_grid.setVerticalSpacing(8)

        self.order_name = self.create_field("VD: Đơn tháng 5, Dự án ABC...")
        order_grid.addWidget(self.create_field_block("Tên đơn hàng", self.order_name), 0, 0, 1, 2)

        self.status_combo = QComboBox()
        self.status_combo.addItem("Chờ xử lý", "pending")
        self.status_combo.addItem("Đang xử lý", "processing")
        self.status_combo.addItem("Đã giao", "delivered")
        self.status_combo.addItem("Đã hủy", "cancelled")
        self.status_combo.setFixedHeight(38)
        order_grid.addWidget(self.create_field_block("Trạng thái", self.status_combo), 1, 0)

        self.payment_status_combo = QComboBox()
        self.payment_status_combo.addItem("Chưa thanh toán", "unpaid")
        self.payment_status_combo.addItem("Thanh toán một phần", "partial")
        self.payment_status_combo.addItem("Đã thanh toán", "paid")
        self.payment_status_combo.setFixedHeight(38)
        order_grid.addWidget(self.create_field_block("Trạng thái thanh toán", self.payment_status_combo), 1, 1)

        order_grid.setColumnStretch(0, 1)
        order_grid.setColumnStretch(1, 1)
        order_layout.addLayout(order_grid)

        line_header = QHBoxLayout()
        line_title = QLabel("Chi tiết sản phẩm")
        line_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        line_header.addWidget(line_title)
        line_header.addStretch()
        
        # Bổ sung nút Thêm danh mục
        add_cat = QPushButton("📂  Thêm danh mục")
        add_cat.setObjectName("outlineButton")
        add_cat.clicked.connect(self.add_category_row)
        line_header.addWidget(add_cat)

        add_row = QPushButton("+  Thêm dòng")
        add_row.setObjectName("outlineButton")
        add_row.clicked.connect(self.add_item_row)
        line_header.addWidget(add_row)
        
        remove_row = QPushButton("Xóa dòng")
        remove_row.setObjectName("outlineButton")
        remove_row.clicked.connect(self.remove_selected_row)
        line_header.addWidget(remove_row)
        order_layout.addLayout(line_header)

        # Sử dụng DragDropTableWidget thay vì QTableWidget
        self.items_table = DragDropTableWidget()
        self.items_table.parent_dialog = self
        self.items_table.setColumnCount(ITEM_TABLE_COLUMNS)
        self.items_table.setHorizontalHeaderLabels([
            "Kéo", "TT", "Mô tả chi tiết *", "Mã hàng", "Xuất xứ", "Đơn vị",
            "Số lượng", "Đơn giá", "Thành tiền", "Ghi chú", "",
        ])
        header = self.items_table.horizontalHeader()
        header.setStretchLastSection(False)
        for column in range(ITEM_TABLE_COLUMNS):
            header.setSectionResizeMode(column, QHeaderView.Interactive)
        header.setSectionResizeMode(DESCRIPTION_COLUMN, QHeaderView.Stretch)
        self.items_table.setColumnWidth(DRAG_COLUMN, 42)        # Kéo
        self.items_table.setColumnWidth(INDEX_COLUMN, 42)       # TT
        self.items_table.setColumnWidth(DESCRIPTION_COLUMN, 360) # Mô tả chi tiết *
        self.items_table.setColumnWidth(SKU_COLUMN, 120)        # Mã hàng
        self.items_table.setColumnWidth(ORIGIN_COLUMN, 90)      # Xuất xứ
        self.items_table.setColumnWidth(UNIT_COLUMN, 90)        # Đơn vị
        self.items_table.setColumnWidth(QUANTITY_COLUMN, 100)   # Số lượng
        self.items_table.setColumnWidth(PRICE_COLUMN, 120)      # Đơn giá
        self.items_table.setColumnWidth(TOTAL_COLUMN, 130)      # Thành tiền
        self.items_table.setColumnWidth(NOTE_COLUMN, 150)       # Ghi chú
        self.items_table.setColumnWidth(ACTION_COLUMN, 48)      # Xóa
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setShowGrid(False)
        self.items_table.setMinimumHeight(260)
        self.items_table.setMinimumWidth(1100)
        self.items_table.setFocusPolicy(Qt.NoFocus)
        self.items_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        order_layout.addWidget(self.items_table, 1)
        self.add_item_row()
        content_layout.addWidget(order_card)
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Hủy")
        cancel.setObjectName("outlineButton")
        cancel.clicked.connect(self.reject)
        actions.addWidget(cancel)
        save = QPushButton("Lưu đơn hàng" if self.order else "Tạo đơn hàng")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.accept)
        actions.addWidget(save)
        layout.addLayout(actions)

    def toggle_fullscreen(self):
        if self.isMaximized():
            self.showNormal()
            self.full_button.setText("Hiển thị full")
        else:
            self.showMaximized()
            self.full_button.setText("Thu nhỏ")

    def toggle_customer_info(self):
        is_visible = self.customer_fields_container.isVisible()
        self.customer_fields_container.setVisible(not is_visible)
        if is_visible:
            self.toggle_customer_btn.setText("Mở rộng  ▼")
        else:
            self.toggle_customer_btn.setText("Thu gọn  ▲")

    def handle_enter_navigation(self, widget: QWidget, backward: bool = False) -> bool:
        position = self.find_item_widget_position(widget)
        if position is None:
            return False

        next_position = (
            self.previous_item_field_position(*position)
            if backward
            else self.next_item_field_position(*position)
        )
        if next_position is None:
            return False

        return self.focus_item_field(*next_position)

    def find_item_widget_position(self, widget: QWidget):
        for row in range(self.items_table.rowCount()):
            for column in ITEM_NAV_COLUMNS:
                cell_widget = self.items_table.cellWidget(row, column)
                if cell_widget is None:
                    continue
                if cell_widget == widget or cell_widget.isAncestorOf(widget):
                    return row, column
        return None

    def next_item_field_position(self, row: int, column: int):
        if self.get_row_type(row) == "item" and column in ITEM_NAV_COLUMNS:
            index = ITEM_NAV_COLUMNS.index(column)
            if index + 1 < len(ITEM_NAV_COLUMNS):
                return row, ITEM_NAV_COLUMNS[index + 1]

        return self.first_item_field_after(row, column)

    def previous_item_field_position(self, row: int, column: int):
        if self.get_row_type(row) == "item" and column in ITEM_NAV_COLUMNS:
            index = ITEM_NAV_COLUMNS.index(column)
            if index > 0:
                return row, ITEM_NAV_COLUMNS[index - 1]

        for candidate in range(row - 1, -1, -1):
            if self.get_row_type(candidate) == "category":
                return candidate, DESCRIPTION_COLUMN
            return candidate, NOTE_COLUMN
        return None

    def first_item_field_after(self, row: int, column: int):
        for candidate in range(row + 1, self.items_table.rowCount()):
            return candidate, DESCRIPTION_COLUMN

        self.items_table.setCurrentCell(row, column)
        self.add_item_row()
        return self.items_table.currentRow(), DESCRIPTION_COLUMN

    def focus_item_field(self, row: int, column: int) -> bool:
        target = self.items_table.cellWidget(row, column)
        if target is None:
            return False

        self.items_table.setCurrentCell(row, column)
        target.setFocus()
        if hasattr(target, "selectAll"):
            target.selectAll()
        return True

    def create_field(self, placeholder: str) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(38)
        return field

    def create_field_block(self, label: str, widget: QWidget) -> QWidget:
        block = QWidget()
        block.setObjectName("transparentBlock")
        layout = QVBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label_widget = QLabel(label)
        label_widget.setObjectName("formLabel")
        layout.addWidget(label_widget)
        layout.addWidget(widget)
        return block

    def setup_customer_completer(self):
        try:
            from src.services.customer_service import CustomerService

            root = self.parent()
            db = None
            while root is not None and db is None:
                db = getattr(root, "db", None)
                root = root.parent()
            if db is None:
                return

            self.customer_lookup = CustomerService(db).get_all(is_active=True)
            labels = []
            for customer in self.customer_lookup:
                name = customer.get("name") or ""
                phone = customer.get("phone") or ""
                address = customer.get("address") or ""
                label = name
                if phone:
                    label += f" | {phone}"
                if address:
                    label += f" | {address}"
                labels.append(label)

            model = QStringListModel(labels)
            completer = QCompleter(model, self)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.activated[str].connect(self.apply_customer_suggestion)
            self.customer_name.setCompleter(completer)
            self.customer_name.textEdited.connect(self.on_customer_text_edited)
            self.customer_completer = completer
        except Exception:
            self.customer_lookup = []

    def on_customer_text_edited(self, text: str):
        typed = text.strip().lower()
        if not typed:
            return
        for customer in self.customer_lookup:
            name = (customer.get("name") or "").strip().lower()
            phone = (customer.get("phone") or "").strip().lower()
            if typed == name or (phone and typed == phone):
                self.fill_customer(customer)
                break

    def apply_customer_suggestion(self, label: str):
        selected_name = label.split("|", 1)[0].strip()
        for customer in self.customer_lookup:
            if (customer.get("name") or "").strip() == selected_name:
                self.fill_customer(customer)
                return
        self.customer_name.setText(selected_name)

    def fill_customer(self, customer):
        self.customer_name.setText(customer.get("name") or "")
        self.customer_phone.setText(customer.get("phone") or "")
        self.initial_customer = customer

    def populate_customer(self):
        self.customer_name.setText(self.initial_customer.get("name") or "")
        self.customer_phone.setText(self.initial_customer.get("phone") or "")

    def populate_order(self):
        self.customer_name.setText(self.order.get("customer_name") or "")
        self.customer_phone.setText(self.order.get("customer_phone") or "")
        self.order_name.setText(self.order.get("order_name") or "")
        self.notes.setPlainText(self.order.get("notes") or "")

        status = self.order.get("status") or "pending"
        index = self.status_combo.findData(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

        payment_status = self.order.get("payment_status") or "unpaid"
        index_pay = self.payment_status_combo.findData(payment_status)
        if index_pay >= 0:
            self.payment_status_combo.setCurrentIndex(index_pay)

        created_at = self.order.get("created_at") or ""
        if created_at:
            self.order_date.setDate(QDate.fromString(created_at[:10], "yyyy-MM-dd"))
        delivery_date = self.order.get("delivery_date") or ""
        if delivery_date:
            self.delivery_date.setDate(QDate.fromString(delivery_date[:10], "yyyy-MM-dd"))

        self.items_table.setRowCount(0)
        items = self.order.get("items") or []
        if not items:
            self.add_item_row()
            return

        import json
        for line in items:
            attrs_str = line.get("variant_attributes")
            is_cat = False
            if attrs_str:
                try:
                    attrs = json.loads(attrs_str) if isinstance(attrs_str, str) else attrs_str
                    if attrs.get("type") == "category":
                        is_cat = True
                except Exception:
                    pass
            
            if is_cat:
                self.add_category_row()
                row = self.items_table.rowCount() - 1
                desc_widget = self.items_table.cellWidget(row, DESCRIPTION_COLUMN)
                if desc_widget:
                    desc_widget.setText(line.get("product_name") or "")
            else:
                self.add_item_row()
                row = self.items_table.rowCount() - 1
                desc_widget = self.items_table.cellWidget(row, DESCRIPTION_COLUMN)
                if desc_widget:
                    desc_widget.setText(line.get("product_name") or "")
                
                sku_widget = self.items_table.cellWidget(row, SKU_COLUMN)
                if sku_widget:
                    sku_widget.setText(line.get("variant_sku") or "")
                
                origin_widget = self.items_table.cellWidget(row, ORIGIN_COLUMN)
                if origin_widget:
                    origin_widget.setText(line.get("origin") or "")
                
                unit_widget = self.items_table.cellWidget(row, UNIT_COLUMN)
                if unit_widget:
                    unit_widget.setText(line.get("unit") or "")
                
                qty_widget = self.items_table.cellWidget(row, QUANTITY_COLUMN)
                if qty_widget:
                    qty_widget.setValue(float(line.get("quantity") or 0))
                
                price_widget = self.items_table.cellWidget(row, PRICE_COLUMN)
                if price_widget:
                    price_widget.setValue(float(line.get("price") or 0))
                
                note_widget = self.items_table.cellWidget(row, NOTE_COLUMN)
                if note_widget:
                    note_widget.setText(line.get("note") or "")
                
                self.update_line_total(row)
                
        self.update_sequence_numbers()

    def get_insert_index(self):
        row = self.items_table.currentRow()
        if row >= 0:
            return row + 1
        return self.items_table.rowCount()

    def create_drag_item(self, row_type: str) -> QTableWidgetItem:
        item = QTableWidgetItem(DRAG_HANDLE_TEXT)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(QFont("Segoe UI Symbol", 13, QFont.Bold))
        item.setForeground(QColor("#D97706" if row_type == "category" else "#94A3B8"))
        item.setData(Qt.UserRole, row_type)
        return item

    def set_row_type(self, row, row_type):
        item = self.items_table.item(row, DRAG_COLUMN)
        if not item:
            item = self.create_drag_item(row_type)
            self.items_table.setItem(row, DRAG_COLUMN, item)
        item.setData(Qt.UserRole, row_type)

    def get_row_type(self, row):
        item = self.items_table.item(row, DRAG_COLUMN)
        if item:
            val = item.data(Qt.UserRole)
            if val:
                return val
        return "item"

    def clear_row_spans(self, row):
        for column in range(ITEM_TABLE_COLUMNS):
            self.items_table.setSpan(row, column, 1, 1)

    def create_delete_button(self) -> QPushButton:
        button = QPushButton()
        button.setObjectName("rowDeleteButton")
        button.setFixedSize(28, 28)
        button.setToolTip("Xóa dòng")
        try:
            button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        except Exception:
            button.setText("×")
        button.setStyleSheet("""
            QPushButton#rowDeleteButton {
                border: 1px solid transparent;
                border-radius: 6px;
                color: #EF4444;
                background: transparent;
            }
            QPushButton#rowDeleteButton:hover:enabled {
                background: #FEF2F2;
                border-color: #FECACA;
            }
            QPushButton#rowDeleteButton:disabled {
                color: #CBD5E1;
            }
        """)
        button.clicked.connect(lambda _checked=False, btn=button: self.remove_row_for_button(btn))
        return button

    def set_delete_button(self, row):
        self.items_table.setCellWidget(row, ACTION_COLUMN, self.create_delete_button())

    def update_delete_buttons(self):
        can_delete = self.items_table.rowCount() > 1
        for row in range(self.items_table.rowCount()):
            button = self.items_table.cellWidget(row, ACTION_COLUMN)
            if button:
                button.setEnabled(can_delete)

    def remove_row_for_button(self, button=None):
        button = button or self.sender()
        for row in range(self.items_table.rowCount()):
            if self.items_table.cellWidget(row, ACTION_COLUMN) == button:
                self.remove_row(row)
                return

    def add_category_row(self):
        insert_idx = self.get_insert_index()
        self.items_table.insertRow(insert_idx)
        self.items_table.setRowHeight(insert_idx, 48)
        self.clear_row_spans(insert_idx)
        self.items_table.setItem(insert_idx, DRAG_COLUMN, self.create_drag_item("category"))
        
        folder_item = QTableWidgetItem("📁")
        folder_item.setTextAlignment(Qt.AlignCenter)
        self.items_table.setItem(insert_idx, INDEX_COLUMN, folder_item)
        
        cat_input = QLineEdit()
        cat_input.setObjectName("categoryInput")
        cat_input.setPlaceholderText("Tên danh mục (VD: Tủ điện 1, Thiết bị chính...)")
        cat_input.setFont(QFont("Segoe UI", 10, QFont.Bold))
        cat_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFBEB;
                border: 1px solid #FDE68A;
                border-radius: 6px;
                padding: 6px 10px;
                color: #78350F;
            }
            QLineEdit:focus {
                border: 1px solid #D97706;
            }
        """)
        cat_input.textChanged.connect(self.update_sequence_numbers)
        self.items_table.setCellWidget(insert_idx, DESCRIPTION_COLUMN, cat_input)
        
        self.items_table.setSpan(insert_idx, DESCRIPTION_COLUMN, 1, 6)
        
        total_item = QTableWidgetItem("0đ")
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
        total_item.setForeground(QColor("#B45309"))
        self.items_table.setItem(insert_idx, TOTAL_COLUMN, total_item)
        
        self.items_table.setItem(insert_idx, NOTE_COLUMN, QTableWidgetItem(""))
        self.set_delete_button(insert_idx)
        
        self.items_table.setCurrentCell(insert_idx, DESCRIPTION_COLUMN)
        self.update_sequence_numbers()

    def add_item_row(self):
        insert_idx = self.get_insert_index()
        self.items_table.insertRow(insert_idx)
        self.items_table.setRowHeight(insert_idx, 62)
        self.clear_row_spans(insert_idx)
        self.items_table.setItem(insert_idx, DRAG_COLUMN, self.create_drag_item("item"))
        
        stt_item = QTableWidgetItem("")
        stt_item.setTextAlignment(Qt.AlignCenter)
        self.items_table.setItem(insert_idx, INDEX_COLUMN, stt_item)
        
        self.items_table.setCellWidget(insert_idx, DESCRIPTION_COLUMN, self.table_line_edit("Mô tả sản phẩm..."))
        self.items_table.setCellWidget(insert_idx, SKU_COLUMN, self.table_line_edit("Mã SP"))
        self.items_table.setCellWidget(insert_idx, ORIGIN_COLUMN, self.table_line_edit("VN"))
        self.items_table.setCellWidget(insert_idx, UNIT_COLUMN, self.table_line_edit("Cái"))
        
        quantity = QDoubleSpinBox()
        quantity.setObjectName("lineItemSpin")
        quantity.setButtonSymbols(QAbstractSpinBox.NoButtons)
        quantity.setMaximum(1_000_000)
        quantity.setValue(1)
        quantity.setFixedHeight(38)
        quantity.valueChanged.connect(self.on_line_value_changed)
        self.items_table.setCellWidget(insert_idx, QUANTITY_COLUMN, quantity)
        
        price = QDoubleSpinBox()
        price.setObjectName("lineItemSpin")
        price.setButtonSymbols(QAbstractSpinBox.NoButtons)
        price.setMaximum(10_000_000_000)
        price.setSingleStep(100_000)
        price.setFixedHeight(38)
        price.valueChanged.connect(self.on_line_value_changed)
        self.items_table.setCellWidget(insert_idx, PRICE_COLUMN, price)
        
        total = QTableWidgetItem("0đ")
        total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.items_table.setItem(insert_idx, TOTAL_COLUMN, total)
        
        self.items_table.setCellWidget(insert_idx, NOTE_COLUMN, self.table_line_edit("Ghi chú"))
        self.set_delete_button(insert_idx)
        
        self.items_table.setCurrentCell(insert_idx, DESCRIPTION_COLUMN)
        self.update_sequence_numbers()

    def table_line_edit(self, text: str) -> QLineEdit:
        field = QLineEdit()
        field.setObjectName("lineItemInput")
        field.setPlaceholderText(text)
        if text and text not in {"Mô tả sản phẩm...", "Mã SP", "Ghi chú"}:
            field.setText(text)
        field.setFixedHeight(38)
        return field

    def remove_selected_row(self):
        row = self.items_table.currentRow()
        self.remove_row(row)

    def remove_row(self, row):
        if row >= 0 and self.items_table.rowCount() > 1:
            self.items_table.removeRow(row)
            self.update_all_totals()

    def on_line_value_changed(self):
        widget = self.sender()
        if not widget:
            return
        for row in range(self.items_table.rowCount()):
            if (self.items_table.cellWidget(row, QUANTITY_COLUMN) == widget or
                self.items_table.cellWidget(row, PRICE_COLUMN) == widget):
                self.update_line_total(row)
                break

    def update_line_total(self, row):
        row_type = self.get_row_type(row)
        if row_type == "category":
            self.update_category_total(row)
            return
            
        qty_widget = self.items_table.cellWidget(row, QUANTITY_COLUMN)
        price_widget = self.items_table.cellWidget(row, PRICE_COLUMN)
        if not qty_widget or not price_widget:
            return
            
        quantity = qty_widget.value()
        price = price_widget.value()
        total = quantity * price
        
        item = self.items_table.item(row, TOTAL_COLUMN) or QTableWidgetItem()
        item.setText(f"{total:,.0f}đ")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.items_table.setItem(row, TOTAL_COLUMN, item)
        
        self.update_all_totals()

    def update_category_total(self, cat_row):
        total = 0
        for row in range(cat_row + 1, self.items_table.rowCount()):
            if self.get_row_type(row) == "category":
                break
            qty_widget = self.items_table.cellWidget(row, QUANTITY_COLUMN)
            price_widget = self.items_table.cellWidget(row, PRICE_COLUMN)
            if qty_widget and price_widget:
                total += qty_widget.value() * price_widget.value()
                
        item = self.items_table.item(cat_row, TOTAL_COLUMN)
        if not item:
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            item.setForeground(QColor("#B45309"))
            self.items_table.setItem(cat_row, TOTAL_COLUMN, item)
        item.setText(f"{total:,.0f}đ")

    def update_all_totals(self):
        for row in range(self.items_table.rowCount()):
            if self.get_row_type(row) == "category":
                self.update_category_total(row)
        self.update_sequence_numbers()

    def update_sequence_numbers(self):
        num = 0
        for row in range(self.items_table.rowCount()):
            row_type = self.get_row_type(row)
            if row_type == "category":
                num = 0
                folder_item = self.items_table.item(row, INDEX_COLUMN)
                if not folder_item:
                    folder_item = QTableWidgetItem("📁")
                    folder_item.setTextAlignment(Qt.AlignCenter)
                    self.items_table.setItem(row, INDEX_COLUMN, folder_item)
            else:
                num += 1
                item = self.items_table.item(row, INDEX_COLUMN)
                if not item:
                    item = QTableWidgetItem()
                    item.setTextAlignment(Qt.AlignCenter)
                    self.items_table.setItem(row, INDEX_COLUMN, item)
                item.setText(str(num))
        self.update_delete_buttons()

    def move_row(self, from_row, to_row):
        if from_row == to_row or from_row < 0 or to_row < 0 or from_row >= self.items_table.rowCount() or to_row >= self.items_table.rowCount():
            return
            
        row_type = self.get_row_type(from_row)
        
        if row_type == "category":
            desc_widget = self.items_table.cellWidget(from_row, DESCRIPTION_COLUMN)
            desc_text = desc_widget.text() if desc_widget else ""
            total_item = self.items_table.item(from_row, TOTAL_COLUMN)
            total_text = total_item.text() if total_item else "0đ"
            
            self.items_table.removeRow(from_row)
            self.items_table.insertRow(to_row)
            self.items_table.setRowHeight(to_row, 48)
            self.clear_row_spans(to_row)
            self.items_table.setItem(to_row, DRAG_COLUMN, self.create_drag_item("category"))
            
            folder_item = QTableWidgetItem("📁")
            folder_item.setTextAlignment(Qt.AlignCenter)
            self.items_table.setItem(to_row, INDEX_COLUMN, folder_item)
            
            cat_input = QLineEdit()
            cat_input.setObjectName("categoryInput")
            cat_input.setPlaceholderText("Tên danh mục (VD: Tủ điện 1, Thiết bị chính...)")
            cat_input.setFont(QFont("Segoe UI", 10, QFont.Bold))
            cat_input.setStyleSheet("""
                QLineEdit {
                    background-color: #FFFBEB;
                    border: 1px solid #FDE68A;
                    border-radius: 6px;
                    padding: 6px 10px;
                    color: #78350F;
                }
                QLineEdit:focus {
                    border: 1px solid #D97706;
                }
            """)
            cat_input.setText(desc_text)
            cat_input.textChanged.connect(self.update_sequence_numbers)
            self.items_table.setCellWidget(to_row, DESCRIPTION_COLUMN, cat_input)
            self.items_table.setSpan(to_row, DESCRIPTION_COLUMN, 1, 6)
            
            total_item_new = QTableWidgetItem(total_text)
            total_item_new.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item_new.setFont(QFont("Segoe UI", 10, QFont.Bold))
            total_item_new.setForeground(QColor("#B45309"))
            self.items_table.setItem(to_row, TOTAL_COLUMN, total_item_new)
            self.items_table.setItem(to_row, NOTE_COLUMN, QTableWidgetItem(""))
            self.set_delete_button(to_row)
        else:
            desc_widget = self.items_table.cellWidget(from_row, DESCRIPTION_COLUMN)
            sku_widget = self.items_table.cellWidget(from_row, SKU_COLUMN)
            origin_widget = self.items_table.cellWidget(from_row, ORIGIN_COLUMN)
            unit_widget = self.items_table.cellWidget(from_row, UNIT_COLUMN)
            qty_widget = self.items_table.cellWidget(from_row, QUANTITY_COLUMN)
            price_widget = self.items_table.cellWidget(from_row, PRICE_COLUMN)
            total_item = self.items_table.item(from_row, TOTAL_COLUMN)
            note_widget = self.items_table.cellWidget(from_row, NOTE_COLUMN)
            
            desc_text = desc_widget.text() if desc_widget else ""
            sku_text = sku_widget.text() if sku_widget else ""
            origin_text = origin_widget.text() if origin_widget else ""
            unit_text = unit_widget.text() if unit_widget else ""
            qty_val = qty_widget.value() if qty_widget else 1.0
            price_val = price_widget.value() if price_widget else 0.0
            total_text = total_item.text() if total_item else "0đ"
            note_text = note_widget.text() if note_widget else ""
            
            self.items_table.removeRow(from_row)
            self.items_table.insertRow(to_row)
            self.items_table.setRowHeight(to_row, 62)
            self.clear_row_spans(to_row)
            self.items_table.setItem(to_row, DRAG_COLUMN, self.create_drag_item("item"))
            
            stt_item = QTableWidgetItem("")
            stt_item.setTextAlignment(Qt.AlignCenter)
            self.items_table.setItem(to_row, INDEX_COLUMN, stt_item)
            
            self.items_table.setCellWidget(to_row, DESCRIPTION_COLUMN, self.table_line_edit("Mô tả sản phẩm..."))
            self.items_table.cellWidget(to_row, DESCRIPTION_COLUMN).setText(desc_text)
            
            self.items_table.setCellWidget(to_row, SKU_COLUMN, self.table_line_edit("Mã SP"))
            self.items_table.cellWidget(to_row, SKU_COLUMN).setText(sku_text)
            
            self.items_table.setCellWidget(to_row, ORIGIN_COLUMN, self.table_line_edit("VN"))
            self.items_table.cellWidget(to_row, ORIGIN_COLUMN).setText(origin_text)
            
            self.items_table.setCellWidget(to_row, UNIT_COLUMN, self.table_line_edit("Cái"))
            self.items_table.cellWidget(to_row, UNIT_COLUMN).setText(unit_text)
            
            quantity = QDoubleSpinBox()
            quantity.setObjectName("lineItemSpin")
            quantity.setButtonSymbols(QAbstractSpinBox.NoButtons)
            quantity.setMaximum(1_000_000)
            quantity.setValue(qty_val)
            quantity.setFixedHeight(38)
            quantity.valueChanged.connect(self.on_line_value_changed)
            self.items_table.setCellWidget(to_row, QUANTITY_COLUMN, quantity)
            
            price = QDoubleSpinBox()
            price.setObjectName("lineItemSpin")
            price.setButtonSymbols(QAbstractSpinBox.NoButtons)
            price.setMaximum(10_000_000_000)
            price.setSingleStep(100_000)
            price.setValue(price_val)
            price.setFixedHeight(38)
            price.valueChanged.connect(self.on_line_value_changed)
            self.items_table.setCellWidget(to_row, PRICE_COLUMN, price)
            
            total = QTableWidgetItem(total_text)
            total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items_table.setItem(to_row, TOTAL_COLUMN, total)
            
            self.items_table.setCellWidget(to_row, NOTE_COLUMN, self.table_line_edit("Ghi chú"))
            self.items_table.cellWidget(to_row, NOTE_COLUMN).setText(note_text)
            self.set_delete_button(to_row)
            
        self.items_table.setCurrentCell(to_row, DRAG_COLUMN)
        self.update_all_totals()

    def accept(self):
        if not self.customer_name.text().strip():
            QMessageBox.warning(self, "Thiếu dữ liệu", "Tên khách hàng là bắt buộc.")
            return
        if not self.get_items():
            QMessageBox.warning(self, "Thiếu dữ liệu", "Cần ít nhất một dòng chi tiết sản phẩm.")
            return
        super().accept()

    def get_order_data(self):
        current_name = self.customer_name.text().strip()
        cust_id = None
        if self.initial_customer and self.initial_customer.get("name") == current_name:
            cust_id = self.initial_customer.get("id")
        elif self.order and self.order.get("customer_name") == current_name:
            cust_id = self.order.get("customer_id")

        return {
            "customer_name": current_name,
            "customer_phone": self.customer_phone.text().strip(),
            "customer_id": cust_id,
            "order_name": self.order_name.text().strip(),
            "status": self.status_combo.currentData(),
            "payment_status": self.payment_status_combo.currentData(),
            "order_date": self.order_date.date().toString("yyyy-MM-dd"),
            "delivery_date": self.delivery_date.date().toString("yyyy-MM-dd"),
            "notes": self.notes.toPlainText().strip(),
            "tax_rate": 10,
            "create_debt": True,
        }

    def get_items(self):
        items = []
        for row in range(self.items_table.rowCount()):
            row_type = self.get_row_type(row)
            if row_type == "category":
                desc_widget = self.items_table.cellWidget(row, DESCRIPTION_COLUMN)
                description = desc_widget.text().strip() if desc_widget else ""
                items.append({
                    "type": "category",
                    "description": description,
                })
            else:
                desc_widget = self.items_table.cellWidget(row, DESCRIPTION_COLUMN)
                description = desc_widget.text().strip() if desc_widget else ""
                if not description:
                    continue
                    
                code_widget = self.items_table.cellWidget(row, SKU_COLUMN)
                origin_widget = self.items_table.cellWidget(row, ORIGIN_COLUMN)
                unit_widget = self.items_table.cellWidget(row, UNIT_COLUMN)
                qty_widget = self.items_table.cellWidget(row, QUANTITY_COLUMN)
                price_widget = self.items_table.cellWidget(row, PRICE_COLUMN)
                note_widget = self.items_table.cellWidget(row, NOTE_COLUMN)
                
                quantity = qty_widget.value() if qty_widget else 0.0
                unit_price = price_widget.value() if price_widget else 0.0
                
                items.append({
                    "type": "item",
                    "description": description,
                    "product_code": code_widget.text().strip() if code_widget else "",
                    "origin": origin_widget.text().strip() if origin_widget else "",
                    "unit": unit_widget.text().strip() if unit_widget else "",
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": quantity * unit_price,
                    "note": note_widget.text().strip() if note_widget else "",
                })
        return items
