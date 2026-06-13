# -*- coding: utf-8 -*-
"""Shared keyboard behavior for data-entry screens."""
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractSpinBox,
    QComboBox,
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QWidget,
)


class EnterKeyNavigationFilter(QObject):
    """Make Enter behave like Tab in forms while preserving multiline edits."""

    def eventFilter(self, watched, event):
        if event.type() != QEvent.KeyPress:
            return False

        if event.key() not in (Qt.Key_Return, Qt.Key_Enter):
            return False

        modifiers = event.modifiers()
        if modifiers & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier):
            return False

        widget = watched if isinstance(watched, QWidget) else None
        if widget is None:
            return False

        if self._keeps_default_enter(widget):
            return False

        if isinstance(widget, (QTextEdit, QPlainTextEdit)):
            return False

        if self._completion_popup_is_open(widget):
            return False

        backward = bool(modifiers & Qt.ShiftModifier)

        if self._dispatch_custom_navigation(widget, backward):
            event.accept()
            return True

        if self._is_form_control(widget):
            self._commit_spinbox_text(widget)
            self._move_focus(widget, backward)
            event.accept()
            return True

        return False

    def _keeps_default_enter(self, widget: QWidget) -> bool:
        current = widget
        while current is not None:
            if current.property("enterKeepsDefault"):
                return True
            current = current.parentWidget()
        return False

    def _completion_popup_is_open(self, widget: QWidget) -> bool:
        if isinstance(widget, QLineEdit):
            completer = widget.completer()
            popup = completer.popup() if completer else None
            if popup is not None and popup.isVisible():
                return True

        combo = self._ancestor(widget, QComboBox)
        if combo is not None:
            view = combo.view()
            if view is not None and view.isVisible():
                return True

        return False

    def _dispatch_custom_navigation(self, widget: QWidget, backward: bool) -> bool:
        current = widget
        while current is not None:
            handler = getattr(current, "handle_enter_navigation", None)
            if callable(handler) and handler(widget, backward):
                return True
            current = current.parentWidget()
        return False

    def _is_form_control(self, widget: QWidget) -> bool:
        if isinstance(widget, (QLineEdit, QAbstractSpinBox, QComboBox, QAbstractButton)):
            return True
        return self._ancestor(widget, QAbstractSpinBox) is not None

    def _commit_spinbox_text(self, widget: QWidget) -> None:
        spinbox = self._ancestor(widget, QAbstractSpinBox)
        if spinbox is not None:
            spinbox.interpretText()

    def _move_focus(self, widget: QWidget, backward: bool) -> None:
        if backward:
            widget.focusPreviousChild()
        else:
            widget.focusNextChild()

    def _ancestor(self, widget: QWidget, cls):
        current = widget
        while current is not None:
            if isinstance(current, cls):
                return current
            current = current.parentWidget()
        return None
