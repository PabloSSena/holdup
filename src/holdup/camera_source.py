"""Camera Source: opens the Windows default camera and hands out frames in memory only."""
import cv2
import numpy as np


class CameraSource:
    def __init__(self, index: int = 0):
        self._capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # default MSMF backend took ~45 s to open here
        # Keep only the newest frame, so a slow analysis rate never sees a stale one.
        self._capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def read(self) -> np.ndarray | None:
        """The latest frame as RGB, or None if the camera can't be read."""
        ok, frame = self._capture.read()
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if ok else None

    def close(self) -> None:
        self._capture.release()
