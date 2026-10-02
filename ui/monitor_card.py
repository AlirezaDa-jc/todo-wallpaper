from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)


class MonitorCard(QFrame):
    def __init__(
        self,
        monitor_index,
        width,
        height,
        screen_name,
        parent=None,
    ):
        super().__init__(parent)

        self.monitor_index = monitor_index

        self.setObjectName("monitorCard")

        layout = QVBoxLayout(self)

        title = QLabel(f"Monitor {monitor_index + 1}")

        title.setObjectName("monitorTitle")

        layout.addWidget(title)

        info = QLabel(f"{width} × {height}    •    {screen_name}")

        info.setObjectName("secondaryLabel")

        layout.addWidget(info)

        self.todo_radio = QRadioButton("Use this monitor for Todos")

        self.todo_radio.setObjectName("todoRadio")

        layout.addWidget(self.todo_radio)

        wallpaper_layout = QHBoxLayout()

        self.wallpaper_label = QLabel("No wallpaper selected")

        self.wallpaper_label.setObjectName("secondaryLabel")

        self.wallpaper_label.setWordWrap(True)

        wallpaper_layout.addWidget(self.wallpaper_label)

        self.browse_button = QPushButton("Browse...")

        wallpaper_layout.addWidget(self.browse_button)

        layout.addLayout(wallpaper_layout)

    def set_todo_selected(self, selected):
        self.todo_radio.setChecked(selected)

        self.browse_button.setEnabled(not selected)

        if selected:
            self.wallpaper_label.setText("Generated automatically from todos.txt")

    def set_wallpaper(self, path):
        if path:
            self.wallpaper_label.setText(path)
        else:
            self.wallpaper_label.setText("No wallpaper selected")
