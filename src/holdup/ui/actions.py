"""What the pages can ask the app to do. tray.py builds it from the same functions the tray menu uses."""
from dataclasses import dataclass
from datetime import timedelta
from typing import Callable

from holdup.posture_classifier import Sensitivity
from holdup.start_with_windows import StartWithWindows


@dataclass(frozen=True)
class Actions:
    pause: Callable[[timedelta | None], None]  # None pauses until resumed
    resume: Callable[[], None]
    recalibrate: Callable[[], None]  # shows the window with Calibration at Ready
    set_sensitivity: Callable[[Sensitivity], None]  # also keeps the tray menu's mark in step
    camera_names: Callable[[], list[str]]  # cameras plugged in right now
    choose_camera: Callable[[str], None]  # may make the Baseline Stale
    start_with_windows: StartWithWindows | None  # None when run from source: there is no exe to register
    retry_camera: Callable[[], None]  # closes the camera so the next tick reopens it
