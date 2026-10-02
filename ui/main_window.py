import json
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config import CONFIG_FILE
from core.todo_manager import TodoManager
from core.todo_renderer import (
    cleanup_old_wallpapers,
    create_wallpaper,
    save_wallpaper,
)
from core.wallpaper import WallpaperManager
from ui.monitor_card import MonitorCard


class MainWindow(QMainWindow):
    def __init__(
        self,
        wallpaper_manager,
        todo_manager,
    ):
        super().__init__()
        self.setWindowTitle("Todo Wallpaper")
        self.resize(
            850,
            750,
        )
        self.wallpaper_manager = wallpaper_manager
        self.todo_manager = todo_manager
        self.monitor_cards = {}
        self.wallpapers = {}
        self.todo_monitor = 0
        self.last_modified = None
        self.load_config()
        self.build_ui()
        self.start_watcher()

    def load_config(self):
        if not CONFIG_FILE.exists():
            return

        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            self.todo_monitor = data.get(
                "todo_monitor",
                0,
            )
            self.wallpapers = data.get(
                "wallpapers",
                {},
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):
            self.todo_monitor = 0
            self.wallpapers = {}

    def save_config(self):
        data = {
            "todo_monitor": self.todo_monitor,
            "wallpapers": self.wallpapers,
        }

        CONFIG_FILE.write_text(
            json.dumps(
                data,
                indent=4,
            ),
            encoding="utf-8",
        )

    def build_ui(self):
        central = QWidget()

        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        main_layout.setContentsMargins(
            30,
            25,
            30,
            25,
        )

        title = QLabel("Todo Wallpaper")
        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(title)

        subtitle = QLabel("Choose one monitor for your todo list and wallpapers for the others.")
        subtitle.setStyleSheet(
            """
            color: #888888;
            margin-bottom: 15px;
            """
        )

        main_layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        container = QWidget()

        monitor_layout = QVBoxLayout(container)

        monitor_layout.setSpacing(15)

        screens = self.screen_list()

        for index, screen in enumerate(screens):
            geometry = screen.geometry()

            card = MonitorCard(
                index,
                geometry.width(),
                geometry.height(),
                screen.name(),
            )

            card.todo_radio.toggled.connect(
                lambda checked, i=index: self.todo_monitor_changed(
                    i,
                    checked,
                )
            )

            card.browse_button.clicked.connect(
                lambda checked=False, i=index: self.browse_wallpaper(i)
            )

            self.monitor_cards[index] = card

            monitor_layout.addWidget(card)

        monitor_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        bottom_layout = QHBoxLayout()

        self.status_label = QLabel("Ready")

        bottom_layout.addWidget(self.status_label)

        bottom_layout.addStretch()

        open_button = QPushButton("Open todos.txt")
        open_button.clicked.connect(self.todo_manager.open_file)

        bottom_layout.addWidget(open_button)

        apply_button = QPushButton("Apply")
        apply_button.setMinimumWidth(120)
        apply_button.clicked.connect(self.apply_settings)

        bottom_layout.addWidget(apply_button)

        main_layout.addLayout(bottom_layout)

        self.refresh_cards()

    def screen_list(self):
        from PySide6.QtWidgets import QApplication

        return QApplication.screens()

    def todo_monitor_changed(
        self,
        monitor_index,
        checked,
    ):
        if not checked:
            return

        self.todo_monitor = monitor_index

        self.refresh_cards()

    def refresh_cards(self):
        for index, card in self.monitor_cards.items():
            card.set_todo_selected(index == self.todo_monitor)

            if index != self.todo_monitor:
                card.set_wallpaper(
                    self.wallpapers.get(
                        str(index),
                        "",
                    )
                )

    def browse_wallpaper(
        self,
        monitor_index,
    ):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select wallpaper",
            "",
            ("Images (*.jpg *.jpeg *.png *.bmp *.webp);;All files (*.*)"),
        )

        if not path:
            return

        self.wallpapers[str(monitor_index)] = path
        self.refresh_cards()

    def apply_settings(self):
        try:
            self.status_label.setText("Applying...")

            todos = self.todo_manager.read()

            screen = self.screen_list()[self.todo_monitor]

            geometry = screen.geometry()

            image = create_wallpaper(
                todos,
                geometry.width(),
                geometry.height(),
            )

            todo_wallpaper = save_wallpaper(image)

            self.wallpaper_manager.set_wallpaper(
                self.todo_monitor,
                todo_wallpaper,
            )

            for index in range(len(self.monitor_cards)):
                if index == self.todo_monitor:
                    continue

                path = self.wallpapers.get(
                    str(index),
                    "",
                )

                if not path:
                    continue

                wallpaper_path = Path(path)

                if not wallpaper_path.exists():
                    raise FileNotFoundError(
                        f"Wallpaper for Monitor {index + 1} does not exist:\n{path}"
                    )

                self.wallpaper_manager.set_wallpaper(
                    index,
                    wallpaper_path,
                )

            self.save_config()

            cleanup_old_wallpapers()

            self.last_modified = self.todo_manager.modified_time()

            self.status_label.setText("Applied successfully")

        except Exception as error:
            self.status_label.setText("Failed")

            QMessageBox.critical(
                self,
                "Failed to apply wallpapers",
                str(error),
            )

    def start_watcher(self):
        self.last_modified = self.todo_manager.modified_time()

        self.timer = QTimer(self)

        self.timer.timeout.connect(self.check_todos)

        self.timer.start(500)

    def check_todos(self):
        try:
            modified = self.todo_manager.modified_time()

        except OSError:
            return

        if modified == self.last_modified:
            return

        self.last_modified = modified

        self.update_todo_wallpaper()

    def update_todo_wallpaper(self):
        try:
            screen = self.screen_list()[self.todo_monitor]

            geometry = screen.geometry()

            todos = self.todo_manager.read()

            image = create_wallpaper(
                todos,
                geometry.width(),
                geometry.height(),
            )

            wallpaper_path = save_wallpaper(image)

            self.wallpaper_manager.set_wallpaper(
                self.todo_monitor,
                wallpaper_path,
            )

            cleanup_old_wallpapers()

            self.status_label.setText("Todo wallpaper updated")

        except Exception as error:
            self.status_label.setText(f"Update failed: {error}")
