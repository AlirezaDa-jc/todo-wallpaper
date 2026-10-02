import ctypes

from config import TODO_FILE


class TodoManager:
    def __init__(self):
        self.ensure_file()

    def ensure_file(self):
        if not TODO_FILE.exists():
            TODO_FILE.write_text(
                "First task\nSecond task\nThird task\n",
                encoding="utf-8",
            )

    def read(self):
        self.ensure_file()
        text = TODO_FILE.read_text(encoding="utf-8")
        return [line.strip() for line in text.splitlines() if line.strip()]

    def modified_time(self):
        self.ensure_file()
        return TODO_FILE.stat().st_mtime

    def open_file(self):
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "open",
            str(TODO_FILE),
            None,
            None,
            1,
        )
