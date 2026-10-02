from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication


def is_dark_mode():
    palette = QApplication.palette()
    window_color = palette.color(QPalette.ColorRole.Window)
    return window_color.lightness() < 128


def apply_theme(app):
    if is_dark_mode():
        app.setStyleSheet(
            """
            QWidget {
                background: #202124;
                color: #e8eaed;
            }

            QMainWindow {
                background: #202124;
            }

            QLabel {
                color: #e8eaed;
            }

            QLabel#secondaryLabel {
                color: #9aa0a6;
            }

            QLabel#monitorTitle {
                color: #e8eaed;
                font-size: 19px;
                font-weight: bold;
                border: none;
            }

            QFrame#monitorCard {
                border: 1px solid #3c4043;
                border-radius: 10px;
                padding: 5px
            }

            QRadioButton {
                color: #e8eaed;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }

            QPushButton {
                background: #303134;
                color: #e8eaed;
                border: 1px solid #5f6368;
                border-radius: 7px;
                padding: 8px 16px;
            }

            QPushButton:hover {
                background: #3c4043;
            }

            QPushButton:pressed {
                background: #202124;
            }

            QPushButton:disabled {
                background: #292a2d;
                color: #777777;
                border-color: #3c4043;
            }

            QScrollArea {
                background: #202124;
                border: none;
            }
            """
        )

    else:
        app.setStyleSheet(
            """
            QWidget {
                background: #f5f5f5;
                color: #202124;
            }

            QMainWindow {
                background: #f5f5f5;
            }

            QLabel {
                color: #202124;
            }

            QLabel#secondaryLabel {
                color: #666666;
            }

            QLabel#monitorTitle {
                color: #202124;
                font-size: 19px;
                font-weight: bold;
                border: none;
            }

            QFrame#monitorCard {
                background: #ffffff;
                border: 1px solid #d5d5d5;
                border-radius: 10px;
            }

            QRadioButton {
                color: #202124;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }

            QPushButton {
                background: #ffffff;
                color: #202124;
                border: 1px solid #c7c7c7;
                border-radius: 7px;
                padding: 8px 16px;
            }

            QPushButton:hover {
                background: #eeeeee;
            }

            QPushButton:pressed {
                background: #e2e2e2;
            }

            QPushButton:disabled {
                background: #eeeeee;
                color: #999999;
                border-color: #dddddd;
            }

            QScrollArea {
                background: #f5f5f5;
                border: none;
            }
            """
        )
