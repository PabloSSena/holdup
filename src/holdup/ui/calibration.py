"""The Calibration view: covers the main window's content while the User captures a new Baseline."""
import math

import numpy as np
from PySide6.QtCore import QByteArray, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPainterPath, QPen, QPixmap, QRadialGradient
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from holdup.posture_monitor import MonitorState, PostureMonitor
from holdup.ui.theme import THEMES
from holdup.windows import _pixmap

PREVIEW_WIDTH = {False: 480, True: 352}  # by compact; the preview is 4:3

# The design's copy per state: kicker, title, body.
_COPY = {
    "ready": ("Get ready", "Sit up straight, the way you want to sit, facing your screen.",
              "Holdup captures this as your Baseline. It takes about five seconds."),
    "countdown": ("Get ready", "Capturing in {}…", "Sit up straight, the way you want to sit, facing your screen."),
    "hold": ("Capturing", "Hold still…", "Keep looking at your screen for a moment."),
    "success": ("All set", "Your Baseline is captured.", "Holdup is now watching your posture."),
    "fail_view": ("Let’s try again", "Make sure you are in view and hold still",
                  "Your head and shoulders should sit inside the outline."),
    "fail_camera": ("Let’s try again", "The camera can't be read",
                    "Check that it is plugged in, not covered, and not being used by another app."),
}
_BUTTON = {"ready": "Start", "success": "Done", "fail_view": "Retry", "fail_camera": "Retry"}

_CHECK = '<path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
_NO_CAMERA = ('<g fill="none" stroke="#9BA6A1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
              '<rect x="2.5" y="6.5" width="13" height="11" rx="2.5"/><path d="M15.5 10.5l5-3v9l-5-3"/><path d="M3 3l18 18"/></g>')


def _svg(painter: QPainter, body: str, rect: QRectF) -> None:
    QSvgRenderer(QByteArray(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">{body}</svg>'.encode())).render(painter, rect)


class _Preview(QWidget):
    """The 4:3 live preview with the head-and-shoulders outline and what each state draws over the feed."""

    def __init__(self):
        super().__init__()
        self.frame: QPixmap | None = None
        self.state = "ready"
        self.count = 3
        self.progress = 0.0

    def paintEvent(self, event) -> None:
        w, h = self.width(), self.height()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(self.rect()), 14, 14)
        p.setClipPath(clip)
        if self.state == "fail_camera":
            p.fillRect(self.rect(), QColor("#202624"))
            _svg(p, _NO_CAMERA, QRectF(w / 2 - 20, h / 2 - 31, 40, 40))
            p.setPen(QColor("#9BA6A1"))
            p.setFont(_font(13))
            p.drawText(QRectF(0, h / 2 + 19, w, 20), Qt.AlignHCenter | Qt.AlignTop, "No picture")
            return
        gradient = QRadialGradient(w / 2, h * 0.4, math.hypot(w / 2, h * 0.6))
        gradient.setColorAt(0, QColor("#46504B"))
        gradient.setColorAt(0.78, QColor("#1B201E"))
        p.fillRect(self.rect(), gradient)
        if self.frame:
            p.drawPixmap(int((w - self.frame.width()) / 2), int((h - self.frame.height()) / 2), self.frame)

        solid = self.state in ("hold", "success")
        pen = QPen(QColor("#5DBB93" if solid else "#E2A45C" if self.state == "fail_view" else QColor(255, 255, 255, 140)), 2)
        if not solid:
            pen.setDashPattern([3, 3])
        p.setPen(pen)
        p.drawEllipse(QRectF(w * 0.33, h * 0.14, w * 0.34, h * 0.5))  # head
        p.drawArc(QRectF(w * 0.14, h * 0.82, w * 0.72, h * 0.76), 0, 180 * 16)  # shoulders, cut off by the bottom edge

        p.setPen(Qt.NoPen)  # the "Live preview" tag
        p.setFont(_font(12, QFont.DemiBold))
        tag = QRectF(12, 12, 9 + 7 + 6 + p.fontMetrics().horizontalAdvance("Live preview") + 9, 26)
        p.setBrush(QColor(0, 0, 0, 115))
        p.drawRoundedRect(tag, 7, 7)
        p.setBrush(QColor("#3FA36B"))
        p.drawEllipse(QRectF(21, 21.5, 7, 7))
        p.setPen(QColor("#FFFFFF"))
        p.drawText(tag.adjusted(22, 0, 0, 0), Qt.AlignVCenter, "Live preview")

        if self.state == "countdown":
            p.setFont(_font(120, QFont.Bold))
            p.drawText(self.rect(), Qt.AlignCenter, str(self.count))
        elif self.state == "hold":
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 64))
            p.drawRoundedRect(QRectF(16, h - 22, w - 32, 6), 3, 3)
            p.setBrush(QColor("#5DBB93"))
            p.drawRoundedRect(QRectF(16, h - 22, (w - 32) * self.progress, 6), 3, 3)
        elif self.state == "success":
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#2F7D62"))
            p.drawEllipse(QRectF(w / 2 - 36, h / 2 - 36, 72, 72))
            _svg(p, _CHECK, QRectF(w / 2 - 17, h / 2 - 17, 34, 34))


def _font(px: int, weight=QFont.Normal) -> QFont:
    font = QFont("Figtree")
    font.setFamilies(["Figtree", "Segoe UI"])
    font.setPixelSize(px)
    font.setWeight(weight)
    return font


class CalibrationView(QWidget):
    """Ready (Start), countdown, hold, then success (Done) or a failure (Retry). Calibration only begins on Start or
    Retry. Emits finished(True) on Done, finished(False) on Cancel."""

    finished = Signal(bool)

    def __init__(self, monitor: PostureMonitor):
        super().__init__()
        self._monitor = monitor
        self._started = False
        self.setStyleSheet("""
            #heading { font-size: 22px; font-weight: 700; }
            #kicker { font-size: 12px; font-weight: 700; }
            #title { font-size: 24px; font-weight: 700; }
            #body { font-size: 15px; }
            QPushButton { min-height: 40px; max-height: 40px; padding: 0 20px; font-size: 14px; }
            QPushButton#cancel { min-height: 34px; max-height: 34px; padding: 0 14px; font-size: 13px; background: transparent; }
        """)
        heading = QLabel("Calibration", objectName="heading")
        self._cancel = QPushButton("Cancel", objectName="cancel", cursor=Qt.PointingHandCursor)
        self._cancel.clicked.connect(self._cancel_clicked)
        keep_space = self._cancel.sizePolicy()
        keep_space.setRetainSizeWhenHidden(True)  # so the content does not jump when it hides on success
        self._cancel.setSizePolicy(keep_space)
        top = QHBoxLayout()
        top.addWidget(heading, 1)
        top.addWidget(self._cancel)

        self.preview = _Preview()
        self._kicker = QLabel(objectName="kicker")
        kicker_font = self._kicker.font()
        kicker_font.setLetterSpacing(QFont.PercentageSpacing, 108)
        self._kicker.setFont(kicker_font)
        self._title = QLabel(objectName="title", wordWrap=True)
        self._body = QLabel(objectName="body", wordWrap=True)
        self._body.setProperty("role", "muted")
        self._button = QPushButton(cursor=Qt.PointingHandCursor)
        self._button.setProperty("role", "primary")
        self._button.clicked.connect(self._button_clicked)
        text = QVBoxLayout()
        text.setSpacing(10)
        for widget in (self._kicker, self._title, self._body):
            text.addWidget(widget)
        text.addSpacing(12)
        text.addWidget(self._button, 0, Qt.AlignLeft)
        row = QHBoxLayout()
        row.setSpacing(28)
        row.addWidget(self.preview, 0, Qt.AlignVCenter)
        row.addLayout(text, 1)
        row.setAlignment(text, Qt.AlignVCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 22, 30, 26)
        layout.setSpacing(16)
        layout.addLayout(top)
        layout.addLayout(row, 1)
        self.set_compact(False)

    def set_compact(self, compact: bool) -> None:
        width = PREVIEW_WIDTH[compact]
        self.preview.setFixedSize(width, width * 3 // 4)

    def open(self) -> None:
        """Back to Ready; a Calibration still in progress is dropped, as the User starts over."""
        if self._started:
            self._monitor.cancel_calibration()
        self._started = False
        self.preview.frame = None
        self.refresh()

    def show_frame(self, rgb_frame: np.ndarray) -> None:
        self.preview.frame = _pixmap(rgb_frame, self.preview.size(), Qt.KeepAspectRatioByExpanding)
        self.preview.update()

    def state(self) -> str:
        monitor = self._monitor
        if not self._started:
            return "ready"
        if monitor.state is MonitorState.CALIBRATING:
            return "countdown" if monitor.calibration_countdown() else "hold"
        if not monitor.calibration_failed:
            return "success"
        return "fail_camera" if monitor.state is MonitorState.CAMERA_UNAVAILABLE else "fail_view"

    def refresh(self) -> None:
        """Re-read the Posture Monitor. Called on the tray tick while visible, so the countdown and bar stay smooth."""
        state = self.state()
        count = math.ceil(self._monitor.calibration_countdown())
        kicker, title, body = _COPY[state]
        dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
        tokens = THEMES["dark" if dark else "light"]
        self._kicker.setText(kicker.upper())
        self._kicker.setStyleSheet(f"color: {tokens['wni' if state.startswith('fail') else 'ac']}")
        self._title.setText(title.format(count))
        self._body.setText(body)
        self._button.setVisible(state in _BUTTON)
        self._button.setText(_BUTTON.get(state, ""))
        self._cancel.setVisible(state != "success")
        preview = self.preview
        preview.state, preview.count, preview.progress = state, count, self._monitor.calibration_progress()
        preview.update()

    def _button_clicked(self) -> None:
        if self.state() == "success":
            self.finished.emit(True)
            return
        self._monitor.begin_calibration()  # Start and Retry
        self._started = True
        self.refresh()

    def _cancel_clicked(self) -> None:
        if self._started:
            self._monitor.cancel_calibration()
        self.finished.emit(False)

    def hideEvent(self, event) -> None:
        self.preview.frame = None  # the last frame goes with the view
        super().hideEvent(event)
