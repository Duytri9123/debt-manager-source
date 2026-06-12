# -*- coding: utf-8 -*-
"""Floating AI chat modal."""
import threading

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from src.services.chat_service import ChatService


class ChatDialog(QDialog):
    """Modal-style assistant chat window using DeepSeek's OpenAI-compatible API."""

    response_ready = Signal(str)
    error_ready = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Assistant")
        self.setMinimumSize(520, 620)
        self.resize(560, 680)
        self.service = ChatService()
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là AI Assistant cho ứng dụng quản lý công nợ và đơn hàng B2B. "
                    "Trả lời ngắn gọn, rõ ràng bằng tiếng Việt."
                ),
            }
        ]
        self.response_ready.connect(self.on_response)
        self.error_ready.connect(self.on_error)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("chatHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 12, 12)
        header_layout.setSpacing(8)

        title = QLabel("AI Assistant")
        title.setObjectName("chatTitle")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.full_button = QPushButton("Hiển thị full")
        self.full_button.setObjectName("chatHeaderButton")
        self.full_button.setCursor(Qt.PointingHandCursor)
        self.full_button.clicked.connect(self.toggle_fullscreen)
        header_layout.addWidget(self.full_button)

        close_button = QPushButton("X")
        close_button.setObjectName("chatHeaderButton")
        close_button.setFixedWidth(34)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.hide)
        header_layout.addWidget(close_button)
        layout.addWidget(header)

        self.history = QTextEdit()
        self.history.setObjectName("chatHistory")
        self.history.setReadOnly(True)
        self.history.setText(
            "Xin chào! Tôi là AI Assistant.\n\n"
            "Tôi có thể giúp bạn tìm dữ liệu, phân tích công nợ, gợi ý thao tác "
            "và thống kê tổng quan.\n"
        )
        layout.addWidget(self.history, 1)

        quick = QHBoxLayout()
        quick.setContentsMargins(14, 10, 14, 4)
        quick.setSpacing(8)
        for text in ("Tìm khách hàng", "Xem công nợ", "Thống kê"):
            button = QPushButton(text)
            button.setObjectName("quickChatButton")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _=False, prompt=text: self.quick_prompt(prompt))
            quick.addWidget(button)
        quick.addStretch()
        layout.addLayout(quick)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(14, 8, 14, 14)
        input_row.setSpacing(8)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Nhập tin nhắn...")
        self.input.returnPressed.connect(self.send_message)
        input_row.addWidget(self.input, 1)

        self.send_button = QPushButton("Gửi")
        self.send_button.setObjectName("primaryButton")
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.clicked.connect(self.send_message)
        input_row.addWidget(self.send_button)
        layout.addLayout(input_row)

    def quick_prompt(self, text: str):
        prompts = {
            "Tìm khách hàng": "Hướng dẫn tôi tìm khách hàng trong hệ thống.",
            "Xem công nợ": "Hướng dẫn tôi xem và ghi nhận công nợ.",
            "Thống kê": "Gợi ý các thống kê quan trọng cần xem hôm nay.",
        }
        self.input.setText(prompts.get(text, text))
        self.send_message()

    def send_message(self):
        text = self.input.text().strip()
        if not text:
            return

        self.input.clear()
        self.append_message("Bạn", text)
        self.messages.append({"role": "user", "content": text})
        self.send_button.setEnabled(False)
        self.send_button.setText("Đang gửi...")
        threading.Thread(target=self._send_worker, daemon=True).start()

    def _send_worker(self):
        try:
            reply = self.service.send(self.messages[-12:])
            self.response_ready.emit(reply)
        except Exception as exc:
            self.error_ready.emit(str(exc))

    def on_response(self, reply: str):
        self.messages.append({"role": "assistant", "content": reply})
        self.append_message("AI", reply)
        self.send_button.setEnabled(True)
        self.send_button.setText("Gửi")

    def on_error(self, error: str):
        self.append_message("Lỗi", error)
        self.send_button.setEnabled(True)
        self.send_button.setText("Gửi")

    def append_message(self, who: str, text: str):
        self.history.append(f"\n{who}: {text}")
        self.history.verticalScrollBar().setValue(self.history.verticalScrollBar().maximum())

    def toggle_fullscreen(self):
        if self.isMaximized():
            self.showNormal()
            self.full_button.setText("Hiển thị full")
        else:
            self.showMaximized()
            self.full_button.setText("Thu nhỏ")
