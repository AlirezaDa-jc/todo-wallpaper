import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.todo_manager import TodoManager
from core.wallpaper import WallpaperManager
from ui.main_window import MainWindow
from ui.theme import apply_theme


def main():
    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon("assets/icon.svg"))
    app.setApplicationName("Todo Wallpaper")
    app.setApplicationDisplayName("Todo Wallpaper")

    apply_theme(app)

    wallpaper_manager = WallpaperManager()
    todo_manager = TodoManager()

    window = MainWindow(
        wallpaper_manager,
        todo_manager,
    )

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
