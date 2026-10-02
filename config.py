import os
from pathlib import Path


APP_NAME = "TodoWallpaper"

APP_DATA_DIR = (
    Path(os.environ["APPDATA"])
    / APP_NAME
)

TODO_FILE = APP_DATA_DIR / "todos.txt"
OUTPUT_DIR = APP_DATA_DIR / "generated"
CONFIG_FILE = APP_DATA_DIR / "config.json"

CHECK_INTERVAL = 500