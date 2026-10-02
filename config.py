from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TODO_FILE = BASE_DIR / "todos.txt"
OUTPUT_DIR = BASE_DIR / "generated"
CONFIG_FILE = BASE_DIR / "config.json"

CHECK_INTERVAL = 500
