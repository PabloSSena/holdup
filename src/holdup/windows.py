"""The Mirror window: a thin Qt view over the Posture Monitor. Frames are shown, never kept."""
import numpy as np
from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel

from holdup.posture_monitor import DailyStats, MonitorState

MIRROR_SIZE = QSize(320, 240)


def _pixmap(rgb_frame: np.ndarray, size: QSize, mode=Qt.KeepAspectRatio) -> QPixmap:
    height, width, _ = rgb_frame.shape
    # Flipped left-right like a real mirror; mirrored() also copies, so Qt never holds on to the camera buffer.
    image = QImage(rgb_frame.data, width, height, 3 * width, QImage.Format_RGB888).mirrored(True, False)
    return QPixmap.fromImage(image).scaled(size, mode, Qt.SmoothTransformation)


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


STATS_COLUMNS = ("Good Posture", "Forward Lean", "Side Lean", "Mirror")


def stats_cells(stats: DailyStats | None) -> list[str]:
    """One day's row: shares of Watched Time and the Mirror count; a day without Watched Time is empty, not 0%."""
    if not stats or not stats.watched_time:
        return [""] * len(STATS_COLUMNS)
    shares = (stats.good_posture, stats.forward_lean, stats.side_lean)
    return [f"{round(100 * seconds / stats.watched_time)}%" for seconds in shares] + [str(stats.mirror_count)]

