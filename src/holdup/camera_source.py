"""Camera Source: opens the Windows default camera and hands out frames in memory only."""
import time

import cv2
import numpy as np

RETRY_INTERVAL = 3.0  # seconds between attempts to reopen a camera that could not be read


class CameraSource:
    def __init__(self, index: int = 0):
        self._index = index
        self._capture: cv2.VideoCapture | None = None
        self._next_open = 0.0

    def read(self) -> np.ndarray | None:
        """The latest frame as RGB, or None if the camera can't be read (it is reopened every few seconds)."""
        if self._capture is None:
            if time.monotonic() < self._next_open:
                return None
            self._next_open = time.monotonic() + RETRY_INTERVAL
            self._capture = cv2.VideoCapture(self._index, cv2.CAP_DSHOW)  # default MSMF backend took ~45 s to open here
            # Keep only the newest frame, so a slow analysis rate never sees a stale one.
            self._capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        ok, frame = self._capture.read()
        if not ok:
            self.close()  # an unplugged or taken camera does not come back on the same handle
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
