import sys
import winreg
from pathlib import Path

APP_NAME = "TodoWallpaper"

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_startup_command():
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable)}"'

    python_executable = Path(sys.executable)
    main_script = Path(__file__).resolve().parent.parent / "main.py"

    return f'"{python_executable}" "{main_script}"'


def is_startup_enabled():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_READ,
        ) as key:
            value, _ = winreg.QueryValueEx(
                key,
                APP_NAME,
            )

            return bool(value)

    except FileNotFoundError:
        return False


def set_startup_enabled(enabled):
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        RUN_KEY,
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        if enabled:
            winreg.SetValueEx(
                key,
                APP_NAME,
                0,
                winreg.REG_SZ,
                get_startup_command(),
            )
        else:
            try:
                winreg.DeleteValue(
                    key,
                    APP_NAME,
                )
            except FileNotFoundError:
                pass
