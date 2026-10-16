"""The Settings page: Sensitivity, camera, Baseline, Start with Windows and the privacy promise."""
from datetime import datetime

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QButtonGroup, QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from holdup.posture_classifier import Sensitivity
from holdup.posture_monitor import MonitorState, PostureMonitor
from holdup.ui.actions import Actions
from holdup.ui.strings import short_date, tr
from holdup.ui.theme import CARD_MARGINS, PAGE_MARGINS, THEMES

STALE_TEXT = "Stale — the camera view changed. Recalibrate to resume watching."
_SENSITIVITY = {  # description, and the Baseline zone's share of the bar in %
    Sensitivity.LOW: ("You can move quite a bit away from your Baseline before it counts as Bad Posture.", 78),
    Sensitivity.MEDIUM: ("A balanced margin around your Baseline. Good for most people.", 50),
    Sensitivity.HIGH: ("Only small shifts away from your Baseline are allowed. Good if you want a firm nudge.", 26),
}
_INFO_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6.5" fill="none" '
             'stroke="INK" stroke-width="1.3"/><path d="M8 7v4M8 4.8v.1" stroke="INK" stroke-width="1.5" '
             'stroke-linecap="round"/></svg>')
_LOCK_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="4.5" y="10.5" width="15" height="10" '
             'rx="2.5" fill="none" stroke="INK" stroke-width="1.8"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" fill="none" '
             'stroke="INK" stroke-width="1.8"/></svg>')
_CHEVRON_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12"><path d="M2.5 4.5L6 8l3.5-3.5" fill="none" '
                'stroke="INK" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def baseline_text(captured_at: datetime | None, now: datetime, stale: bool, has_camera: bool, calibrated: bool = True) -> str:
    """The Baseline row's text, e.g. "Captured today at 09:10" or "Captured Wed 14 Oct at 09:10"."""
    if not has_camera:
        return tr("Needs a camera")
    if stale:
        return tr(STALE_TEXT)
    if not calibrated:
        return tr("Not captured yet")
    if captured_at is None:  # a Baseline saved before capture times were recorded
        return tr("Captured")
    if captured_at.date() == now.date():
        return tr("Captured today at {}").format(f"{captured_at:%H:%M}")
    return tr("Captured {} at {}").format(short_date(captured_at), f"{captured_at:%H:%M}")


def _label(text: str, role: str | None = None) -> QLabel:
    label = QLabel(text, wordWrap=True)
    if role:
        label.setProperty("role", role)
    return label


def _card(role: str = "card") -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setProperty("role", role)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(*CARD_MARGINS)
    return card, layout


def _set_role(widget: QWidget, role: str) -> None:
    """Change a widget's role after the stylesheet has been applied."""
    if widget.property("role") != role:
        widget.setProperty("role", role)
        widget.style().unpolish(widget)
        widget.style().polish(widget)


class _CameraBox(QComboBox):
    """Re-lists the cameras each time it opens, so a camera plugged in meanwhile shows up."""

    def __init__(self, relist):
        super().__init__()
        self._relist = relist
        self.chevron = QSvgWidget(fixedSize=QSize(12, 12))  # the design's arrow; Qt's own ignores the theme
        self.chevron.setAttribute(Qt.WA_TransparentForMouseEvents)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 12, 0)
        row.addStretch()
        row.addWidget(self.chevron)

    def showPopup(self) -> None:
        self._relist()
        super().showPopup()


class SettingsPage(QWidget):
    def __init__(self, monitor: PostureMonitor, actions: Actions):
        super().__init__()
        self._monitor = monitor
        self._actions = actions
        self._cameras: list[str] = []
        self._ink: str | None = None  # the theme the icons were drawn for
        outer = QVBoxLayout(self)
        outer.setContentsMargins(*PAGE_MARGINS)
        column = QWidget(maximumWidth=680)
        outer.addWidget(column)
        outer.addStretch()
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(_label(tr("Settings"), "title"))

        card, box = _card()
        box.setSpacing(14)
        heading = QVBoxLayout()
        heading.setSpacing(4)
        heading.addWidget(_label(tr("Sensitivity"), "heading"))
        heading.addWidget(_label(tr("How far from your Baseline you may sit before it counts as Bad Posture."), "muted"))
        box.addLayout(heading)
        segments = QFrame(objectName="segments")
        row = QHBoxLayout(segments)
        row.setContentsMargins(3, 3, 3, 3)
        row.setSpacing(2)
        self._levels = QButtonGroup(self)
        for level in Sensitivity:
            button = QPushButton(tr(level.value), checkable=True, cursor=Qt.PointingHandCursor)
            button.clicked.connect(lambda _=False, level=level: self._set_sensitivity(level))
            self._levels.addButton(button)
            row.addWidget(button)
        box.addWidget(segments, 0, Qt.AlignLeft)
        self._track = QFrame(fixedHeight=28)
        self._track.setProperty("role", "track")
        bar = QHBoxLayout(self._track)
        bar.setContentsMargins(0, 0, 0, 0)
        bar.setSpacing(0)
        zone = QFrame()
        zone.setProperty("role", "zone")
        inside = QHBoxLayout(zone)
        inside.setContentsMargins(0, 4, 0, 4)  # the Baseline mark stops 5 px from the bar's edges, less its border
        marker = QFrame(fixedWidth=2)
        marker.setProperty("role", "marker")
        inside.addStretch()
        inside.addWidget(marker)
        inside.addStretch()
        bar.addStretch()
        bar.addWidget(zone)
        bar.addStretch()
        scale = QHBoxLayout()
        scale.addWidget(_label(tr("Bad Posture"), "caption"))
        scale.addStretch()
        scale.addWidget(_label(tr("Baseline"), "caption-strong"))
        scale.addStretch()
        scale.addWidget(_label(tr("Bad Posture"), "caption"))
        zone_box = QVBoxLayout()
        zone_box.setSpacing(8)
        zone_box.addWidget(self._track)
        zone_box.addLayout(scale)
        box.addLayout(zone_box)
        self._description = _label("")
        box.addWidget(self._description)
        layout.addWidget(card)

        card, box = _card()
        box.setSpacing(12)
        box.addWidget(_label(tr("Camera"), "heading"))
        self._camera = _CameraBox(self._list_cameras)
        self._camera.setMaximumWidth(380)
        self._camera.setCursor(Qt.PointingHandCursor)
        self._camera.setPlaceholderText(tr("Choose a camera"))
        self._camera.activated.connect(lambda index: self._choose_camera(self._camera.itemText(index)))
        box.addWidget(self._camera)
        self._no_camera = _label(tr("Plug in a camera and it shows up here."), "muted")
        box.addWidget(self._no_camera)
        note = QHBoxLayout()
        note.setSpacing(8)
        self._info = QSvgWidget(fixedSize=QSize(16, 16))
        note.addWidget(self._info, 0, Qt.AlignTop)
        note.addWidget(_label(tr("Switching camera makes your Baseline Stale. You'll be asked to Recalibrate "
                                 "before watching resumes."), "note"), 1)
        box.addLayout(note)
        rule = QFrame(fixedHeight=1)
        rule.setProperty("role", "rule")
        box.addWidget(rule)
        baseline = QHBoxLayout()
        baseline.setSpacing(12)
        text = QVBoxLayout()
        text.setSpacing(2)
        text.addWidget(_label(tr("Baseline"), "strong"))
        self._baseline = _label("", "note")
        text.addWidget(self._baseline)
        baseline.addLayout(text, 1)
        recalibrate = QPushButton(tr("Recalibrate"), cursor=Qt.PointingHandCursor)
        recalibrate.setProperty("role", "small")
        recalibrate.clicked.connect(actions.recalibrate)
        baseline.addWidget(recalibrate)
        box.addLayout(baseline)
        layout.addWidget(card)

        self._start = None
        if actions.start_with_windows is not None:  # None when run from source, like the tray menu
            card, box = _card()
            box.setContentsMargins(22, 18, 22, 18)
            row = QHBoxLayout()
            row.setSpacing(16)
            text = QVBoxLayout()
            text.setSpacing(2)
            text.addWidget(_label(tr("Start with Windows"), "heading"))
            text.addWidget(_label(tr("Holdup starts in the tray when you sign in."), "note"))
            row.addLayout(text, 1)
            self._start = QPushButton(checkable=True, cursor=Qt.PointingHandCursor)
            self._start.setProperty("role", "switch")
            knob_row = QHBoxLayout(self._start)
            knob_row.setContentsMargins(3, 3, 3, 3)
            self._knob = QFrame(fixedSize=QSize(18, 18))
            self._knob.setProperty("role", "knob")
            knob_row.addWidget(self._knob)
            self._start.toggled.connect(self._toggle_start)
            row.addWidget(self._start)
            box.addLayout(row)
            layout.addWidget(card)

        card, box = _card("privacy")
        box.setContentsMargins(22, 18, 22, 18)
        row = QHBoxLayout()
        row.setSpacing(14)
        self._lock = QSvgWidget(fixedSize=QSize(22, 22))
        row.addWidget(self._lock, 0, Qt.AlignTop)
        text = QVBoxLayout()
        text.setSpacing(3)
        text.addWidget(_label(tr("Your camera picture stays with you"), "heading"))
        text.addWidget(_label(tr("Frames never leave this computer and are never saved. Holdup keeps only numbers, "
                                 "like how many minutes you sat in Good Posture.")))
        row.addLayout(text, 1)
        box.addLayout(row)
        layout.addWidget(card)

    def showEvent(self, event) -> None:
        self._list_cameras()  # once per showing, not on every tick
        self.refresh()
        super().showEvent(event)

    def refresh(self) -> None:
        """Re-read the Posture Monitor. Called on show and on the tray tick while this page is showing."""
        monitor = self._monitor
        self._levels.buttons()[list(Sensitivity).index(monitor.sensitivity)].setChecked(True)
        description, zone = _SENSITIVITY[monitor.sensitivity]
        self._description.setText(tr(description))
        bar = self._track.layout()
        for index, stretch in enumerate((100 - zone, 2 * zone, 100 - zone)):
            bar.setStretch(index, stretch)
        stale = monitor.state is MonitorState.STALE_BASELINE
        self._baseline.setText(baseline_text(monitor.baseline_captured_at, datetime.now(), stale, bool(self._cameras),
                                             monitor.calibrated))
        _set_role(self._baseline, "warning" if stale and self._cameras else "note")
        if not self._camera.view().isVisible():  # don't change the list under an open dropdown
            self._show_current_camera()
        if self._start is not None:
            self._start.setChecked(self._actions.start_with_windows.enabled)
        dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
        tokens = THEMES["dark" if dark else "light"]
        if tokens["mu"] != self._ink:
            self._ink = tokens["mu"]
            self._info.load(QByteArray(_INFO_SVG.replace("INK", tokens["mu"]).encode()))
            self._lock.load(QByteArray(_LOCK_SVG.replace("INK", tokens["ac"]).encode()))
            self._camera.chevron.load(QByteArray(_CHEVRON_SVG.replace("INK", tokens["ink"]).encode()))

    def _set_sensitivity(self, level: Sensitivity) -> None:
        self._actions.set_sensitivity(level)
        self.refresh()

    def _list_cameras(self) -> None:
        self._cameras = self._actions.camera_names()
        self._camera.clear()
        self._camera.addItems(self._cameras or [tr("No camera found")])
        self._camera.setEnabled(bool(self._cameras))
        self._no_camera.setVisible(not self._cameras)
        self._show_current_camera()

    def _show_current_camera(self) -> None:
        if not self._cameras:
            self._camera.setCurrentIndex(0)  # "No camera found"
            return
        chosen = self._monitor.camera
        # None is the Windows default camera, listed first; a chosen camera that is unplugged shows the placeholder.
        self._camera.setCurrentIndex(0 if chosen is None else self._cameras.index(chosen) if chosen in self._cameras else -1)

    def _choose_camera(self, name: str) -> None:
        self._actions.choose_camera(name)
        self.refresh()

    def _toggle_start(self, on: bool) -> None:
        self._knob.parentWidget().layout().setAlignment(self._knob, Qt.AlignRight if on else Qt.AlignLeft)
        if on != self._actions.start_with_windows.enabled:
            self._actions.start_with_windows.set_enabled(on)
