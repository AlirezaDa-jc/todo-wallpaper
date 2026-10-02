from ctypes import (
    POINTER,
    WINFUNCTYPE,
    Structure,
    byref,
    c_void_p,
    sizeof,
    windll,
)
from ctypes.wintypes import (
    BOOL,
    DWORD,
    HDC,
    LPARAM,
    LPCWSTR,
    LPWSTR,
    RECT,
    UINT,
    WCHAR,
)

import comtypes
from comtypes import COMMETHOD, GUID, HRESULT, IUnknown

CLSID_DesktopWallpaper = GUID("{C2CF3110-460E-4FC1-B9D0-8A1C0C9CC4BD}")

IID_IDesktopWallpaper = GUID("{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}")


class IDesktopWallpaper(IUnknown):
    _iid_ = IID_IDesktopWallpaper

    _methods_ = [
        COMMETHOD(
            [],
            HRESULT,
            "SetWallpaper",
            (["in"], LPCWSTR, "monitorID"),
            (["in"], LPCWSTR, "wallpaper"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetWallpaper",
            (["in"], LPCWSTR, "monitorID"),
            (["out"], POINTER(LPWSTR), "wallpaper"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetMonitorDevicePathAt",
            (["in"], UINT, "monitorIndex"),
            (["out"], POINTER(LPWSTR), "monitorID"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetMonitorDevicePathCount",
            (["out"], POINTER(UINT), "count"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetMonitorRECT",
            (["in"], LPCWSTR, "monitorID"),
            (["out"], POINTER(RECT), "displayRect"),
        ),
    ]

    @classmethod
    def create(cls):
        return comtypes.CoCreateInstance(
            CLSID_DesktopWallpaper,
            interface=cls,
            clsctx=comtypes.CLSCTX_LOCAL_SERVER,
        )

    def get_monitor_count(self):
        count = UINT()

        self.__com_GetMonitorDevicePathCount(byref(count))

        return count.value

    def get_monitor_id(self, monitor_index):
        monitor_id = LPWSTR()

        self.__com_GetMonitorDevicePathAt(
            UINT(monitor_index),
            byref(monitor_id),
        )

        return monitor_id.value

    def get_monitor_rect(self, monitor_id):
        rect = RECT()

        self.__com_GetMonitorRECT(
            LPCWSTR(monitor_id),
            byref(rect),
        )

        return rect

    def set_monitor_wallpaper(
        self,
        monitor_id,
        wallpaper_path,
    ):
        self.__com_SetWallpaper(
            LPCWSTR(monitor_id),
            LPCWSTR(str(wallpaper_path)),
        )


class MONITORINFOEXW(Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", DWORD),
        ("szDevice", WCHAR * 32),
    ]


class WindowsMonitor:
    def __init__(
        self,
        monitor_id,
        device_name,
        left,
        top,
        right,
        bottom,
    ):
        self.monitor_id = monitor_id
        self.device_name = device_name

        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def x(self):
        return self.left

    @property
    def y(self):
        return self.top

    @property
    def geometry(self):
        return (
            self.left,
            self.top,
            self.right,
            self.bottom,
        )

    def __repr__(self):
        return (
            f"WindowsMonitor({self.device_name}, {self.left},{self.top},{self.right},{self.bottom})"
        )


class NativeMonitorEnumerator:
    """
    Enumerates the monitors currently attached to Windows.

    The important information here is the native monitor
    rectangle. We use this rectangle to match a physical
    Windows display to the monitor ID returned by
    IDesktopWallpaper.
    """

    def enumerate(self):
        user32 = windll.user32

        monitors = []

        callback_type = WINFUNCTYPE(
            BOOL,
            c_void_p,
            HDC,
            POINTER(RECT),
            LPARAM,
        )

        def callback(
            hmonitor,
            hdc,
            rect_pointer,
            lparam,
        ):
            info = MONITORINFOEXW()

            info.cbSize = sizeof(MONITORINFOEXW)

            success = user32.GetMonitorInfoW(
                hmonitor,
                byref(info),
            )

            if not success:
                return True

            rect = info.rcMonitor

            monitors.append({
                "device_name": info.szDevice,
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,
            })

            return True

        callback_function = callback_type(callback)

        success = user32.EnumDisplayMonitors(
            None,
            None,
            callback_function,
            0,
        )

        if not success:
            raise OSError("EnumDisplayMonitors failed.")

        return monitors


class WallpaperManager:
    """
    Windows wallpaper manager.

    Application monitor indices are created from the actual
    Windows monitor geometry.

    We never assume that the enumeration order returned by
    IDesktopWallpaper matches the enumeration order returned
    by Windows/Qt.
    """

    def __init__(self):
        self.desktop_wallpaper = IDesktopWallpaper.create()

    def _get_desktop_wallpaper_monitors(self):
        monitors = []

        count = self.desktop_wallpaper.get_monitor_count()

        for index in range(count):
            monitor_id = self.desktop_wallpaper.get_monitor_id(index)

            rect = self.desktop_wallpaper.get_monitor_rect(monitor_id)

            if rect.right <= rect.left or rect.bottom <= rect.top:
                continue

            monitors.append({
                "monitor_id": monitor_id,
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,
            })

        return monitors

    def get_monitors(self):
        """
        Return monitors in Windows' physical display order.

        Each returned monitor has:

            monitor_id
            device_name
            x
            y
            width
            height

        The index in this returned list is the application's
        stable monitor index.
        """

        native_monitors = NativeMonitorEnumerator().enumerate()

        desktop_monitors = self._get_desktop_wallpaper_monitors()

        if not native_monitors:
            raise RuntimeError("Windows did not report any connected monitors.")

        if not desktop_monitors:
            raise RuntimeError("IDesktopWallpaper did not report any connected monitors.")

        result = []

        for native in native_monitors:
            native_rect = (
                native["left"],
                native["top"],
                native["right"],
                native["bottom"],
            )

            match = None

            for desktop in desktop_monitors:
                desktop_rect = (
                    desktop["left"],
                    desktop["top"],
                    desktop["right"],
                    desktop["bottom"],
                )

                if native_rect == desktop_rect:
                    match = desktop
                    break

            if match is None:
                raise RuntimeError(
                    "Could not match monitor "
                    f"{native['device_name']} "
                    f"with rectangle "
                    f"{native_rect} "
                    "to IDesktopWallpaper."
                )

            result.append(
                WindowsMonitor(
                    monitor_id=match["monitor_id"],
                    device_name=native["device_name"],
                    left=native["left"],
                    top=native["top"],
                    right=native["right"],
                    bottom=native["bottom"],
                )
            )

        return result

    def monitor_count(self):
        return len(self.get_monitors())

    def get_monitor(self, monitor_index):
        monitors = self.get_monitors()
        if monitor_index < 0 or monitor_index >= len(monitors):
            raise IndexError(f"Invalid monitor index: {monitor_index}")

        return monitors[monitor_index]

    def get_monitor_id(self, monitor_index):
        monitor = self.get_monitor(monitor_index)

        return monitor.monitor_id

    def set_wallpaper(
        self,
        monitor_index,
        wallpaper_path,
    ):
        """
        Set a wallpaper on the actual Windows monitor
        represented by our application monitor index.
        """

        monitor = self.get_monitor(monitor_index)
        self.desktop_wallpaper.set_monitor_wallpaper(
            monitor.monitor_id,
            wallpaper_path,
        )
