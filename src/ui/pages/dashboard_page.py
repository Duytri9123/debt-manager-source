# -*- coding: utf-8 -*-
"""Dashboard page - mirrors Admin/Dashboard.vue without the product module."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class DashboardPage(QWidget):
    """Dashboard with summary cards and chart placeholders."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)

        layout.addLayout(self.create_header())
        layout.addLayout(self.create_all_time_cards())
        layout.addLayout(self.create_period_cards())
        layout.addLayout(self.create_chart_row())
        layout.addWidget(self.create_comparison_card())
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.refresh_data()

    def create_header(self):
        layout = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("contentTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        subtitle = QLabel("Tổng quan hệ thống")
        subtitle.setObjectName("contentSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        layout.addLayout(title_block)
        layout.addStretch()

        period_bar = QFrame()
        period_bar.setObjectName("segmented")
        period_layout = QHBoxLayout(period_bar)
        period_layout.setContentsMargins(4, 4, 4, 4)
        period_layout.setSpacing(2)
        for label in ["Tuần này", "Tháng này", "Quý này", "Năm này"]:
            button = QPushButton(label)
            button.setObjectName("segmentButton")
            button.setCheckable(True)
            button.setChecked(label == "Tháng này")
            period_layout.addWidget(button)
        layout.addWidget(period_bar)
        return layout

    def create_all_time_cards(self):
        layout = QGridLayout()
        layout.setSpacing(10)
        self.card_users = self.create_stat_card("Người dùng", "0", "#4F46E5")
        self.card_orders = self.create_stat_card("Tổng đơn hàng", "0", "#2563EB")
        self.card_debt = self.create_stat_card("Công nợ chưa TT", "0đ", "#D97706", "statCardWarning")
        self.card_paid = self.create_stat_card("Đã thu", "0đ", "#059669", "statCardSuccess")
        layout.addWidget(self.card_users, 0, 0)
        layout.addWidget(self.card_orders, 0, 1)
        layout.addWidget(self.card_debt, 0, 2)
        layout.addWidget(self.card_paid, 0, 3)
        return layout

    def create_period_cards(self):
        layout = QGridLayout()
        layout.setSpacing(10)
        self.card_revenue = self.create_stat_card("Doanh thu kỳ này", "0đ", "#111827")
        self.card_period_orders = self.create_stat_card("Đơn hàng kỳ này", "0", "#111827")
        self.card_new_customers = self.create_stat_card("Khách mới kỳ này", "0", "#111827")
        self.card_avg_order = self.create_stat_card("Giá trị TB / Đơn", "0đ", "#111827")
        layout.addWidget(self.card_revenue, 0, 0)
        layout.addWidget(self.card_period_orders, 0, 1)
        layout.addWidget(self.card_new_customers, 0, 2)
        layout.addWidget(self.card_avg_order, 0, 3)
        return layout

    def create_stat_card(self, title, value, color, object_name="statCard"):
        frame = QFrame()
        frame.setObjectName(object_name)
        frame.setMinimumHeight(76)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 8)
        layout.setSpacing(4)

        title_label = QLabel(title.upper())
        title_label.setObjectName("statTitle")
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setStyleSheet(f"color: {color};")
        frame.value_label = value_label
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        return frame

    def create_chart_row(self):
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(self.create_chart_card("Doanh thu theo thời gian"), 1)
        layout.addWidget(self.create_chart_card("Số đơn hàng theo thời gian"), 1)
        return layout

    def create_chart_card(self, title):
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setMinimumHeight(205)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        grid = QWidget()
        grid_layout = QVBoxLayout(grid)
        grid_layout.setContentsMargins(0, 8, 0, 0)
        grid_layout.setSpacing(14)
        for _ in range(8):
            line = QFrame()
            line.setObjectName("chartLine")
            line.setFixedHeight(1)
            grid_layout.addWidget(line)
        layout.addWidget(grid, 1)
        return frame

    def create_comparison_card(self):
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setMinimumHeight(120)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        title = QLabel("So sánh 12 tháng gần nhất")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.comparison_label = QLabel("Dữ liệu sẽ được cập nhật theo các đơn hàng hiện có.")
        self.comparison_label.setObjectName("contentSubtitle")
        self.comparison_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.comparison_label, 1)
        return frame

    def refresh_data(self):
        try:
            from src.services.customer_service import CustomerService
            from src.services.debt_service import DebtService
            from src.services.order_service import OrderService

            order_stats = OrderService(self.db).get_stats()
            debt_stats = DebtService(self.db).get_stats()
            customer_stats = CustomerService(self.db).get_stats()

            total_orders = order_stats.get("total_orders", 0)
            total_revenue = order_stats.get("total_revenue", 0)
            avg_order = total_revenue / total_orders if total_orders else 0

            self.card_users.value_label.setText(str(customer_stats.get("total_customers", 0)))
            self.card_orders.value_label.setText(str(total_orders))
            self.card_debt.value_label.setText(self.format_currency(debt_stats.get("total_remaining", 0)))
            self.card_paid.value_label.setText(self.format_currency(debt_stats.get("total_paid", 0)))
            self.card_revenue.value_label.setText(self.format_currency(total_revenue))
            self.card_period_orders.value_label.setText(str(total_orders))
            self.card_new_customers.value_label.setText(str(customer_stats.get("total_customers", 0)))
            self.card_avg_order.value_label.setText(self.format_currency(avg_order))
            self.comparison_label.setText(
                f"{total_orders} đơn hàng · {self.format_currency(total_revenue)} doanh thu"
            )
        except Exception as exc:
            print(f"Error loading dashboard data: {exc}")

    @staticmethod
    def format_currency(value):
        return f"{float(value or 0):,.0f}đ"
