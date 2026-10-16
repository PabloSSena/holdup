"""The Today page: live status with Pause / Resume / Recalibrate, today's Watched Time and Mirror count, and banners."""
from datetime import datetime, timedelta

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPainter, QPainterPath, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from holdup.posture_monitor import MonitorState, PostureMonitor
from holdup.ui.actions import Actions
from holdup.ui.theme import CARD_MARGINS, PAGE_MARGINS, THEMES, status

_EXPLANATIONS = {
    "Watching": "You are sitting well. Holdup is quietly keeping an eye on your posture.",
    "Absent": "Nobody is in front of the camera. Watching picks up again when you are back.",
    "Camera Unavailable": "Watching is on hold until the camera can be read.",
    "Stale Baseline": "Watching is on hold until you Recalibrate.",
    "Paused": "Holdup is not watching right now. Your Watched Time is not counting.",
    "Calibrating": "Capturing your Baseline. Hold still for a moment.",
}
_SHOWS_SINCE = ("Watching", "Absent", "Camera Unavailable")  # as in the design; the others say when they end or nothing
_PAUSES = (("Pause for 30 minutes", timedelta(minutes=30)), ("Pause for 1 hour", timedelta(hours=1)),
           ("Pause until resumed", None))

# the design's icons; INK becomes the colour they are drawn in
_CAMERA_OFF = ('<rect x="2.5" y="6.5" width="13" height="11" rx="2.5" fill="none" stroke="INK" stroke-width="1.7"/>'
               '<path d="M15.5 10.5l5-3v9l-5-3" fill="none" stroke="INK" stroke-width="1.7" stroke-linejoin="round"/>'
               '<path d="M3 3l18 18" stroke="INK" stroke-width="1.7" stroke-linecap="round"/>')
_REDO = ('<path d="M20 12a8 8 0 1 1-2.6-5.9" fill="none" stroke="INK" stroke-width="W" stroke-linecap="round"/>'
         '<path d="M18 2.5v4h-4" fill="none" stroke="INK" stroke-width="W" stroke-linecap="round" stroke-linejoin="round"/>')
_PLAY = '<path d="M3 1.5l7 4.5-7 4.5z" fill="INK"/>'


def format_duration(seconds: float) -> str:
    """Watched Time as "3 h 16 min" or "58 min" (whole minutes, rounded down)."""
    hours, minutes = divmod(int(seconds // 60), 60)
    return f"{hours} h {minutes} min" if hours else f"{minutes} min"


def headline(state: MonitorState, paused: bool, paused_until: datetime | None) -> tuple[str, str]:
    """The status card's title and one-line explanation."""
    label, _ = status(state, paused)
    title = (f"Paused until {paused_until:%H:%M}" if paused_until else "Paused until resumed") if paused else label
    return title, _EXPLANATIONS[label]


def _pixmap(body: str, view: int, size: int, ink: str) -> QPixmap:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view} {view}">{body.replace("INK", ink)}</svg>'
    pixmap = QPixmap(size * 3, size * 3)  # 3x, so it stays sharp on high-DPI screens
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(svg.encode())).render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(3)
    return pixmap


def _stylesheet(t: dict[str, str]) -> str:
    """Roles local to this page, on top of the main window's stylesheet."""
    return f"""
    QPushButton {{ font-size: 13px; }}
    *[role="status"] {{ font-size: 24px; font-weight: 700; }}
    *[role="small"] {{ font-size: 13px; color: {t['mu']}; }}
    *[role="heading"] {{ font-size: 15px; font-weight: 700; }}
    *[role="total"] {{ font-size: 22px; font-weight: 700; }}
    *[role="count"] {{ font-size: 44px; font-weight: 700; }}
    *[role="kind"] {{ font-weight: 600; }}
    *[role="share"] {{ font-weight: 700; }}
    *[role="rule"] {{ background: {t['ln']}; border: none; }}
    QPushButton[role="pause"], QPushButton[role="ghost"] {{ padding: 0 14px; background: transparent; }}
    QPushButton[role="pause-on"] {{ padding: 0 14px; background: {t['acs']}; border-color: {t['ac']}; }}
    *[role="banner"] {{ background: {t['wn']}; border-radius: 14px; }}
    *[role="banner"] QLabel {{ color: {t['wni']}; background: transparent; }}
    *[role="banner"] QLabel[role="heading"] {{ font-size: 15px; font-weight: 700; }}
    *[role="banner"] QPushButton {{ min-height: 34px; max-height: 34px; padding: 0 14px; border-radius: 9px;
        color: {t['wni']}; background: transparent; border: 1px solid {t['wni']}; }}
    *[role="banner"] QPushButton[role="primary"] {{ color: {t['wn']}; background: {t['wni']}; border: none; }}
    """


class _Bar(QWidget):
    """Today's Watched Time split as one 12 px stacked bar; an empty track when nothing was watched."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(12)
        self.parts: list[tuple[float, str]] = []  # (seconds, colour)
        self.track = "#E3DED4"

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(self.rect()), 6, 6)
        painter.setClipPath(clip)
        parts = [(seconds, colour) for seconds, colour in self.parts if seconds > 0]
        if not parts:
            painter.fillRect(self.rect(), QColor(self.track))
            return
        total = sum(seconds for seconds, _ in parts)
        width = self.width() - 2 * (len(parts) - 1)  # 2 px gaps, as in the design
        x = 0.0
        for seconds, colour in parts:
            painter.fillRect(QRectF(x, 0, width * seconds / total, 12), QColor(colour))
            x += width * seconds / total + 2


def _label(text: str = "", role: str | None = None) -> QLabel:
    label = QLabel(text, wordWrap=True)
    if role:
        label.setProperty("role", role)
    return label


def _card() -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setProperty("role", "card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(*CARD_MARGINS)
    return card, layout


class TodayPage(QWidget):
    def __init__(self, monitor: PostureMonitor, actions: Actions):
        super().__init__()
        self._monitor = monitor
        self._actions = actions
        self._tokens: dict[str, str] | None = None
        self._since: tuple[str, datetime] | None = None  # the status label shown and when it last changed
        self._chosen: tuple[int, datetime | None] | None = None  # pause button clicked here and the end it set
        self.setMaximumWidth(820 + PAGE_MARGINS[0] + PAGE_MARGINS[2])
        page = QVBoxLayout(self)
        page.setContentsMargins(*PAGE_MARGINS)
        page.setSpacing(16)

        header = QHBoxLayout()
        title = _label("Today", "title")
        title.setWordWrap(False)
        self._date = _label(role="muted")
        self._date.setWordWrap(False)
        header.addWidget(title, 1, Qt.AlignBottom)
        header.addWidget(self._date, 0, Qt.AlignBottom)
        page.addLayout(header)

        self._camera_banner, self._camera_icon = self._banner(
            "Holdup can't read your camera",
            "It may be unplugged, covered, or in use by another app such as a video call. Holdup keeps trying on its "
            "own and starts watching again when the camera is free.",
            [("Try again", actions.retry_camera), ("Choose another camera", lambda: self.window().show_page("Settings"))])
        self._stale_banner, self._stale_icon = self._banner(
            "Your camera view has changed",
            "Your Baseline no longer matches what the camera sees, so Holdup has stopped watching for now. "
            "Recalibrate and it picks up right away.",
            [("Recalibrate", actions.recalibrate)])
        page.addWidget(self._camera_banner)
        page.addWidget(self._stale_banner)

        card, layout = _card()
        layout.setSpacing(18)
        top = QHBoxLayout()
        top.setSpacing(16)
        self._halo = QFrame()
        self._halo.setFixedSize(52, 52)
        self._dot = QFrame(self._halo)
        self._dot.setGeometry(17, 17, 18, 18)
        top.addWidget(self._halo)
        text = QVBoxLayout()
        text.setSpacing(2)
        line = QHBoxLayout()
        line.setSpacing(10)
        self._title = _label(role="status")
        self._since_label = _label(role="small")
        line.addWidget(self._title)
        line.addWidget(self._since_label, 1, Qt.AlignBaseline)
        text.addLayout(line)
        self._explanation = _label(role="muted")
        text.addWidget(self._explanation)
        top.addLayout(text, 1)
        layout.addLayout(top)
        rule = QFrame()
        rule.setFixedHeight(1)
        rule.setProperty("role", "rule")
        layout.addWidget(rule)
        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self._resume = QPushButton("Resume")
        self._resume.setProperty("role", "primary")
        self._resume.clicked.connect(actions.resume)
        buttons.addWidget(self._resume)
        self._pause_buttons = []
        for index, (text_, duration) in enumerate(_PAUSES):
            button = QPushButton(text_)
            button.clicked.connect(lambda _=False, i=index, d=duration: self._pause(i, d))
            buttons.addWidget(button)
            self._pause_buttons.append(button)
        buttons.addStretch()
        self._recalibrate = QPushButton("Recalibrate")
        self._recalibrate.setProperty("role", "ghost")
        self._recalibrate.clicked.connect(actions.recalibrate)
        buttons.addWidget(self._recalibrate)
        for button in (self._resume, *self._pause_buttons, self._recalibrate):
            button.setCursor(Qt.PointingHandCursor)
        self._buttons, self._wrapped = buttons, QHBoxLayout()  # Recalibrate wraps to the second row when narrow
        rows = QVBoxLayout()
        rows.setSpacing(8)
        rows.addLayout(buttons)
        rows.addLayout(self._wrapped)
        layout.addLayout(rows)
        page.addWidget(card)

        row = QHBoxLayout()
        row.setSpacing(16)
        watched, layout = _card()
        layout.setSpacing(16)
        head = QHBoxLayout()
        head.addWidget(_label("Watched Time", "heading"), 1, Qt.AlignBaseline)
        self._total = _label(role="total")
        self._total.setWordWrap(False)
        head.addWidget(self._total, 0, Qt.AlignBaseline)
        layout.addLayout(head)
        self._bar = _Bar()
        layout.addWidget(self._bar)
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(1, 1)
        grid.setColumnMinimumWidth(2, 48)
        grid.setColumnMinimumWidth(3, 84)
        self._rows = []
        for r, kind in enumerate(("Good Posture", "Forward Lean", "Side Lean")):
            swatch = QFrame()
            swatch.setFixedSize(12, 12)
            share, time = _label(role="share"), _label(role="muted")
            share.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            grid.addWidget(swatch, r, 0)
            grid.addWidget(_label(kind, "kind"), r, 1)
            grid.addWidget(share, r, 2)
            grid.addWidget(time, r, 3)
            self._rows.append((swatch, share, time))
        layout.addLayout(grid)
        row.addWidget(watched, 2)

        mirror, layout = _card()
        layout.setSpacing(8)
        layout.addWidget(_label("Mirror", "heading"))
        count = QHBoxLayout()
        count.setSpacing(8)
        self._mirror_count = _label(role="count")
        self._mirror_count.setWordWrap(False)
        count.addWidget(self._mirror_count, 0, Qt.AlignBaseline)
        count.addWidget(_label("times today", "muted"), 1, Qt.AlignBaseline)
        layout.addSpacing(6)
        layout.addLayout(count)
        layout.addStretch()
        layout.addWidget(_label("The Mirror shows you your camera picture when Bad Posture lasts too long.", "small"))
        row.addWidget(mirror, 1)
        page.addLayout(row)
        page.addStretch()

    def _banner(self, title: str, body: str, buttons) -> tuple[QFrame, QLabel]:
        banner = QFrame()
        banner.setProperty("role", "banner")
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)
        icon = QLabel()
        icon.setFixedSize(22, 22)
        layout.addWidget(icon, 0, Qt.AlignTop)
        text = QVBoxLayout()
        text.setSpacing(4)
        text.addWidget(_label(title, "heading"))
        text.addWidget(_label(body))
        row = QHBoxLayout()
        row.setSpacing(8)
        for index, (label, slot) in enumerate(buttons):
            button = QPushButton(label)
            button.setCursor(Qt.PointingHandCursor)
            if index == 0:
                button.setProperty("role", "primary")
            button.clicked.connect(slot)
            row.addWidget(button)
        row.addStretch()
        text.addSpacing(8)
        text.addLayout(row)
        layout.addLayout(text, 1)
        return banner, icon

    def resizeEvent(self, event) -> None:
        self._wrap_recalibrate()
        super().resizeEvent(event)

    def _wrap_recalibrate(self) -> None:
        """Like the design's wrapping button row: Recalibrate moves under the others when they do not fit in one."""
        width = self.width() - PAGE_MARGINS[0] - PAGE_MARGINS[2] - CARD_MARGINS[0] - CARD_MARGINS[2] - 2
        shown = [b for b in (self._resume, *self._pause_buttons, self._recalibrate) if not b.isHidden()]
        target = self._buttons if sum(b.sizeHint().width() + 8 for b in shown) - 8 <= width else self._wrapped
        if target.indexOf(self._recalibrate) < 0:
            (self._wrapped if target is self._buttons else self._buttons).removeWidget(self._recalibrate)
            target.addWidget(self._recalibrate, 0, Qt.AlignLeft)

    def _pause(self, index: int, duration: timedelta | None) -> None:
        self._actions.pause(duration)
        self._chosen = index, self._monitor.paused_until
        self.refresh()

    def _apply_theme(self) -> dict[str, str]:
        dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
        t = THEMES["dark" if dark else "light"]
        if t is not self._tokens:
            self._tokens = t
            self.setStyleSheet(_stylesheet(t))
            self._camera_icon.setPixmap(_pixmap(_CAMERA_OFF, 24, 22, t["wni"]))
            self._stale_icon.setPixmap(_pixmap(_REDO.replace("W", "1.7"), 24, 22, t["wni"]))
            self._resume.setIcon(QIcon(_pixmap(_PLAY, 12, 12, t["aci"])))
            self._recalibrate.setIcon(QIcon(_pixmap(_REDO.replace("W", "2.2"), 24, 14, t["ink"])))
            self._bar.track = t["ln"]
            for (swatch, _, _), token in zip(self._rows, ("ac", "fw", "sd")):
                swatch.setStyleSheet(f"background: {t[token]}; border-radius: 4px;")
        return t

    def refresh(self) -> None:
        """Re-read the Posture Monitor. Called on show and on the tray tick while this page is showing."""
        t = self._apply_theme()
        monitor, now = self._monitor, datetime.now()
        paused, until = monitor.paused, monitor.paused_until
        label, colour = status(monitor.state, paused)
        if self._since is None or self._since[0] != label:
            self._since = label, now
        title, explanation = headline(monitor.state, paused, until)
        self._date.setText(f"{now:%A}, {now.day} {now:%B}")
        self._title.setText(title)
        self._since_label.setText(f"since {self._since[1]:%H:%M}" if label in _SHOWS_SINCE else "")
        self._explanation.setText(explanation)
        soft = QColor(colour)  # the design's colour + "2E" alpha; Qt reads 8-digit hex as #AARRGGBB, so use rgba
        self._halo.setStyleSheet(f"background: rgba({soft.red()},{soft.green()},{soft.blue()},46); border-radius: 26px;")
        self._dot.setStyleSheet(f"background: {colour}; border-radius: 9px;")
        self._camera_banner.setVisible(label == "Camera Unavailable")
        self._stale_banner.setVisible(label == "Stale Baseline")

        self._resume.setVisible(paused)
        self._wrap_recalibrate()
        for index, button in enumerate(self._pause_buttons):
            # until-resumed is always known; a timed one only when it was chosen here (the tray menu does not say which)
            on = paused and (until is None if _PAUSES[index][1] is None else self._chosen == (index, until))
            role = "pause-on" if on else "pause"
            if button.property("role") != role:
                button.setProperty("role", role)
                button.style().polish(button)

        stats = monitor.today_stats()
        total = stats.watched_time
        self._total.setText(format_duration(total))
        parts = (stats.good_posture, stats.forward_lean, stats.side_lean)
        self._bar.parts = list(zip(parts, (t["ac"], t["fw"], t["sd"])))
        self._bar.update()
        for (_, share, time), seconds in zip(self._rows, parts):
            share.setText(f"{round(100 * seconds / total) if total else 0}%")
            time.setText(format_duration(seconds))
        self._mirror_count.setText(str(stats.mirror_count))
