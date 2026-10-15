"""The Mirror and Calibration windows: thin Qt views over the Posture Monitor. Frames are shown, never kept."""
import math

import numpy as np
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from holdup.posture_monitor import MonitorState, PostureMonitor

MIRROR_SIZE = QSize(320, 240)
CALIBRATION_FEED_SIZE = QSize(480, 360)


def _pixmap(rgb_frame: np.ndarray, size: QSize) -> QPixmap:
    height, width, _ = rgb_frame.shape
    # Flipped left-right like a real mirror; mirrored() also copies, so Qt never holds on to the camera buffer.
    image = QImage(rgb_frame.data, width, height, 3 * width, QImage.Format_RGB888).mirrored(True, False)
    return QPixmap.fromImage(image).scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


class MirrorWindow(QLabel):
    """Frameless, always on top, fixed in the bottom-left corner of the primary screen, showing only the live feed."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(MIRROR_SIZE)
        self.setStyleSheet("background: black")
        self.setAlignment(Qt.AlignCenter)

    def follow(self, visible: bool) -> None:
        if visible and not self.isVisible():
            screen = QGuiApplication.primaryScreen().availableGeometry()
            self.move(screen.left(), screen.bottom() - self.height() + 1)
            self.show()
        elif not visible:
            self.hide()

    def show_frame(self, rgb_frame: np.ndarray) -> None:
        self.setPixmap(_pixmap(rgb_frame, MIRROR_SIZE))


class CalibrationWindow(QWidget):
    """Live feed, the "sit up straight" instruction, the countdown, then success or failure with a retry."""

    def __init__(self, monitor: PostureMonitor):
        super().__init__()
        self._monitor = monitor
        self.setWindowTitle("Holdup: Calibration")
        self._feed = QLabel()
        self._feed.setFixedSize(CALIBRATION_FEED_SIZE)
        self._feed.setAlignment(Qt.AlignCenter)
        self._feed.setStyleSheet("background: black")
        instruction = QLabel("Sit up straight, the way you want to sit, facing your screen.")
        self._status = QLabel()
        self._status.setStyleSheet("font-size: 16px")
        self._retry = QPushButton("Retry")
        self._retry.clicked.connect(monitor.begin_calibration)
        self._close = QPushButton("Close")
        self._close.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self._retry)
        buttons.addWidget(self._close)
        layout = QVBoxLayout(self)
        for widget in (self._feed, instruction, self._status):
            layout.addWidget(widget)
        layout.addLayout(buttons)
        self.refresh()

    def show_frame(self, rgb_frame: np.ndarray) -> None:
        self._feed.setPixmap(_pixmap(rgb_frame, CALIBRATION_FEED_SIZE))

    def refresh(self) -> None:
        calibrating = self._monitor.state is MonitorState.CALIBRATING
        failed = not calibrating and self._monitor.calibration_failed
        if calibrating:
            left = self._monitor.calibration_countdown()
            self._status.setText(f"Capturing in {math.ceil(left)}…" if left else "Hold still…")
        elif failed and self._monitor.state is MonitorState.CAMERA_UNAVAILABLE:
            self._status.setText("Calibration failed: the camera can't be read (unplugged, covered or in use by another app).")
        elif failed:
            self._status.setText("Calibration failed: make sure you are in view and hold still, then retry.")
        else:
            self._status.setText("Done: your Baseline is captured. Holdup is now watching your posture.")
        self._retry.setVisible(failed)
        self._close.setVisible(not calibrating)
