"""Camera Source: opens the chosen camera and hands out frames in memory only."""
import re
import sys
import time
from typing import Callable

import cv2
import numpy as np

RETRY_INTERVAL = 3.0  # seconds between attempts to reopen a camera that could not be read


def capture_backend(platform: str = sys.platform) -> int:
    """The OS's native capture API."""
    if platform == "win32":
        return cv2.CAP_DSHOW  # the default MSMF backend took ~45 s to open here
    if platform == "darwin":
        return cv2.CAP_AVFOUNDATION
    return cv2.CAP_V4L2


OPENCV_MAJOR = int(cv2.__version__.split(".")[0])


def capture_index(device_ids: list[str], device_id: str, platform: str = sys.platform,
                  opencv_major: int = OPENCV_MAJOR) -> int:
    """The index OpenCV opens the camera with this Qt device id under, given every id in Qt's order.

    macOS: OpenCV 5 sorts AVFoundation cameras by unique id (Qt's id), which is not Qt's order: an iPhone used as a
    Continuity Camera can sort first. Linux: Qt's id is the /dev/videoN path, and N is V4L2's index.
    """
    if platform == "darwin" and opencv_major >= 5:
        return sorted(device_ids).index(device_id)
    if platform.startswith("linux") and (match := re.fullmatch(r"/dev/video(\d+)", device_id)):
        return int(match[1])
    # shortcut: assumes DirectShow (and OpenCV 4's AVFoundation) list cameras in Qt's order, true on typical setups;
    # enumerate the backend itself if a wrong camera opens.
    return device_ids.index(device_id)


class CameraSource:
    def __init__(self, locate: Callable[[], int | None] = lambda: 0):
        """locate gives the camera's index on each open attempt, or None while that camera is missing."""
        self._locate = locate
        self._capture: cv2.VideoCapture | None = None
        self._next_open = 0.0

    def read(self) -> np.ndarray | None:
        """The latest frame as RGB, or None if the camera can't be read (it is reopened every few seconds)."""
        if self._capture is None:
            if time.monotonic() < self._next_open:
                return None
            self._next_open = time.monotonic() + RETRY_INTERVAL
            index = self._locate()
            if index is None:
                return None
            self._capture = cv2.VideoCapture(index, capture_backend())
            # Keep only the newest frame, so a slow analysis rate never sees a stale one.
            self._capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        ok, frame = self._capture.read()
        if not ok:
            self._capture.release()  # an unplugged or taken camera does not come back on the same handle
            self._capture = None
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def close(self) -> None:
        """Release the camera; the next read() opens it again at once (a new choice, or the User's Try again)."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        self._next_open = 0.0
