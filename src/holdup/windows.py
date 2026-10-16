"""The Mirror, Calibration and Stats windows: thin Qt views over the Posture Monitor. Frames are shown, never kept."""
import math
from datetime import date, timedelta

import numpy as np
from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from holdup.posture_monitor import DailyStats, MonitorState, PostureMonitor

MIRROR_SIZE = QSize(320, 240)
CALIBRATION_FEED_SIZE = QSize(480, 360)


def _pixmap(rgb_frame: np.ndarray, size: QSize) -> QPixmap:
    height, width, _ = rgb_frame.shape
    # Flipped left-right like a real mirror; mirrored() also copies, so Qt never holds on to the camera buffer.
    image = QImage(rgb_frame.data, width, height, 3 * width, QImage.Format_RGB888).mirrored(True, False)
    return QPixmap.fromImage(image).scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


_LEAN_EDGE = {MonitorState.FORWARD_LEAN: "#E2A45C", MonitorState.SIDE_LEAN: "#A0A7E6"}
_LABEL_INK = {"#E2A45C": "#241808", "#A0A7E6": "#16183A"}  # label text on each edge colour
MIRROR_EDGE = 3


def mirror_lean(state: MonitorState) -> tuple[str, str] | None:
    """The Mirror's edge colour and label for a lean; None for any state that is not a lean."""
    return (_LEAN_EDGE[state], state.value) if state in _LEAN_EDGE else None


class MirrorWindow(QLabel):
    """Frameless, always on top, fixed in the bottom-left corner of the primary screen, showing only the live feed,
    with an inner edge and a label in the colour of the current lean."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(MIRROR_SIZE)
        self.setStyleSheet("background: black")
        self.setAlignment(Qt.AlignCenter)
        self._edge: str | None = None
        self._label = QLabel(self)
        self._label.hide()

    def follow(self, visible: bool, state: MonitorState) -> None:
        self._set_lean(mirror_lean(state))
        if visible and not self.isVisible():
            screen = QGuiApplication.primaryScreen().availableGeometry()
            self.move(screen.left(), screen.bottom() - self.height() + 1)
            self.show()
        elif not visible:
            self.hide()

    def _set_lean(self, lean: tuple[str, str] | None) -> None:
        self._edge = lean and lean[0]
        self._label.setVisible(lean is not None)
        if lean:
            self._label.setText(lean[1])
            self._label.setStyleSheet(
                f"background: {lean[0]}; color: {_LABEL_INK[lean[0]]}; font-size: 12px; font-weight: 700;"
                " padding: 4px 8px; border-radius: 6px"
            )
            self._label.adjustSize()
            self._label.move(10, self.height() - 10 - self._label.height())
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self._edge:
            painter = QPainter(self)
            pen = QPen(QColor(self._edge), MIRROR_EDGE)
            pen.setJoinStyle(Qt.MiterJoin)
            painter.setPen(pen)
            half = MIRROR_EDGE / 2  # the pen is centred on the line: inset by half keeps all 3 px inside
            painter.drawRect(QRectF(self.rect()).adjusted(half, half, -half, -half))
            painter.end()

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


STATS_COLUMNS = ("Good Posture", "Forward Lean", "Side Lean", "Mirror")
STATS_DAYS = 8  # today and the last 7 days


def stats_cells(stats: DailyStats | None) -> list[str]:
    """One day's row: shares of Watched Time and the Mirror count; a day without Watched Time is empty, not 0%."""
    if not stats or not stats.watched_time:
        return [""] * len(STATS_COLUMNS)
    shares = (stats.good_posture, stats.forward_lean, stats.side_lean)
    return [f"{round(100 * seconds / stats.watched_time)}%" for seconds in shares] + [str(stats.mirror_count)]


class StatsWindow(QWidget):
    """Today and the last 7 days of Daily Stats, and the Clear statistics button. Re-read on every show."""

    def __init__(self, monitor: PostureMonitor):
        super().__init__()
        self._monitor = monitor
        self.setWindowTitle("Holdup: Stats")
        self._table = QTableWidget(STATS_DAYS, len(STATS_COLUMNS))
        self._table.setHorizontalHeaderLabels(STATS_COLUMNS)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.NoSelection)
        clear = QPushButton("Clear statistics")
        clear.clicked.connect(self._clear)
        close = QPushButton("Close")
        close.clicked.connect(self.close)

        buttons = QHBoxLayout()
        buttons.addWidget(clear)
        buttons.addStretch()
        buttons.addWidget(close)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Share of Watched Time in each posture, and how many times the Mirror appeared."))
        layout.addWidget(self._table)
        layout.addLayout(buttons)
        self.refresh()

    def showEvent(self, event) -> None:
        self.refresh()
        super().showEvent(event)

    def refresh(self) -> None:
        last = date.today()  # the tray's monitor clock is datetime.now, so this is the same local day
        days = [last - timedelta(days=n) for n in range(STATS_DAYS)]
        stats = self._monitor.daily_stats(days[-1], last)
        self._table.setVerticalHeaderLabels(["Today"] + [day.strftime("%a %d %b") for day in days[1:]])
        for row, day in enumerate(days):
            for column, text in enumerate(stats_cells(stats.get(day))):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._table.setItem(row, column, item)
        self._table.resizeColumnsToContents()
        frame = 2 * self._table.frameWidth()  # fit all rows and columns, no scrolling
        self._table.setFixedSize(
            self._table.verticalHeader().width() + self._table.horizontalHeader().length() + frame,
            self._table.horizontalHeader().height() + self._table.verticalHeader().length() + frame,
        )

    def _clear(self) -> None:
        answer = QMessageBox.question(
            self, "Clear statistics", "Delete all Daily Stats? Your Baseline and settings are kept.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self._monitor.clear_stats()
            self.refresh()
