"""Camera Source: opens the chosen camera and hands out frames in memory only."""
import time
from typing import Callable

import cv2
import numpy as np

RETRY_INTERVAL = 3.0  # seconds between attempts to reopen a camera that could not be read


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
            self._capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # default MSMF backend took ~45 s to open here
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
