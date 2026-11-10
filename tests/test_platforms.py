"""What differs between Windows, macOS and Linux: where the Store lives, how cameras open, and the copy for
Start at login."""
from pathlib import Path

import cv2

from holdup.camera_source import capture_backend, capture_index
from holdup.store import default_path
from holdup.ui import strings
from holdup.ui.strings import start_at_login_copy, tr


def test_the_store_lives_in_each_os_per_user_data_folder(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\u\AppData\Local")
    assert default_path("win32") == Path(r"C:\Users\u\AppData\Local") / "Holdup" / "holdup.db"
    assert default_path("darwin") == Path.home() / "Library" / "Application Support" / "Holdup" / "holdup.db"

    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    assert default_path("linux") == Path.home() / ".local" / "share" / "holdup" / "holdup.db"
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert default_path("linux") == tmp_path / "holdup" / "holdup.db"


def test_cameras_open_through_each_os_native_backend():
    assert capture_backend("win32") == cv2.CAP_DSHOW
    assert capture_backend("darwin") == cv2.CAP_AVFOUNDATION
    assert capture_backend("linux") == cv2.CAP_V4L2


def test_start_at_login_is_called_start_with_windows_only_on_windows(monkeypatch):
    assert start_at_login_copy("win32")[0] == "Start with Windows"
    assert start_at_login_copy("darwin")[0] == start_at_login_copy("linux")[0] == "Start at login"
    monkeypatch.setattr(strings, "LANG", "pt")
    for platform in ("win32", "darwin", "linux"):
        title, note = start_at_login_copy(platform)
        assert tr(title) != title and tr(note) != note  # translated everywhere


FACETIME, IPHONE = "47B4B64B-7067-4B9C-AD2B-AE273A71F4B5", "108D0874-11D1-471D-A9B1-394200000001"


def test_a_mac_opens_the_camera_qt_names_even_when_opencv_orders_cameras_differently():
    qt_order = [FACETIME, IPHONE]  # Qt lists the built-in camera first; OpenCV 5 sorts by id, iPhone first
    assert capture_index(qt_order, FACETIME, "darwin", opencv_major=5) == 1
    assert capture_index(qt_order, IPHONE, "darwin", opencv_major=5) == 0
    assert capture_index(qt_order, FACETIME, "darwin", opencv_major=4) == 0


def test_linux_opens_the_camera_by_its_dev_video_number():
    assert capture_index(["/dev/video0", "/dev/video2"], "/dev/video2", "linux") == 2


def test_windows_opens_cameras_in_qt_order():
    assert capture_index(["usb-a", "usb-b"], "usb-b", "win32") == 1
