"""Tray App: the Qt shell that wires the Camera Source, Pose Detector, Posture Monitor and windows together."""
import sys
from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from holdup.camera_source import CameraSource
from holdup.observation import CameraUnavailable
from holdup.pose_detector import PoseDetector
from holdup.posture_classifier import Sensitivity
from holdup.posture_monitor import MonitorState, PostureMonitor
from holdup.start_with_windows import RunKey, StartWithWindows
from holdup.store import Store, default_path
from holdup.windows import CalibrationWindow, MirrorWindow

TICK_MS = 33  # smooth feed while a window shows it; analysis still only runs when the Posture Monitor says it is due


def _dot_icon(color: str) -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(6, 6, 52, 52)
    painter.end()
    return QIcon(pixmap)


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    camera = CameraSource()
    detector = PoseDetector()
    store = Store(default_path())
    monitor = PostureMonitor(clock=datetime.now, store=store)
    mirror = MirrorWindow()
    first_launch = not monitor.calibrated
    if first_launch:
        monitor.begin_calibration()
    calibration = CalibrationWindow(monitor)

    def recalibrate() -> None:
        monitor.begin_calibration()
        calibration.show()
        calibration.raise_()
        calibration.activateWindow()

    icons = {
        "watching": _dot_icon("#2e9d4f"),
        "absent": _dot_icon("#8a8a8a"),
        "unavailable": _dot_icon("#d9822b"),
        "stale": _dot_icon("#c62828"),
        "paused": _dot_icon("#e0a020"),
    }
    tray = QSystemTrayIcon()
    menu = QMenu()
    recalibrate_action = QAction("Recalibrate", menu)
    recalibrate_action.triggered.connect(recalibrate)
    menu.addAction(recalibrate_action)
    sensitivity_menu = menu.addMenu("Sensitivity")
    sensitivity_group = QActionGroup(sensitivity_menu)  # exclusive: one choice marked at a time
    for level in Sensitivity:
        action = sensitivity_group.addAction(level.value)
        action.setCheckable(True)
        action.setChecked(level is monitor.sensitivity)
        action.triggered.connect(lambda _=False, level=level: setattr(monitor, "sensitivity", level))
        sensitivity_menu.addAction(action)

    def pause(duration: timedelta | None) -> None:
        monitor.pause(duration)
        mirror.follow(monitor.mirror_visible)
        show_state()

    def resume() -> None:
        monitor.resume()
        show_state()

    pause_actions = []
    for label, duration in (("Pause for 30 minutes", timedelta(minutes=30)), ("Pause for 1 hour", timedelta(hours=1)), ("Pause until resumed", None)):
        action = menu.addAction(label)
        action.triggered.connect(lambda _=False, d=duration: pause(d))
        pause_actions.append(action)
    resume_action = menu.addAction("Resume")
    resume_action.triggered.connect(resume)
    menu.addSeparator()
    if getattr(sys, "frozen", False):  # from source there is no exe to register
        start_with_windows = StartWithWindows(store, RunKey(), sys.executable)
        start_with_windows.apply()
        start_action = QAction("Start with Windows", menu, checkable=True, checked=start_with_windows.enabled)
        start_action.toggled.connect(start_with_windows.set_enabled)
        menu.addAction(start_action)
    quit_action = QAction("Quit", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)

    def show_state() -> None:
        paused = monitor.paused
        icon = {MonitorState.ABSENT: "absent", MonitorState.CAMERA_UNAVAILABLE: "unavailable",
                MonitorState.STALE_BASELINE: "stale"}.get(monitor.state, "watching")
        tray.setIcon(icons["paused" if paused else icon])
        tray.setToolTip("Holdup: Paused" if paused else f"Holdup: {monitor.state.value}")
        for action in pause_actions:
            action.setVisible(not paused)
        resume_action.setVisible(paused)

    def tick() -> None:
        if calibration.isVisible():
            calibration.refresh()
        due = monitor.analysis_due()
        if not (due or mirror.isVisible() or calibration.isVisible()):
            return
        frame = camera.read()
        if due:
            monitor.observe(CameraUnavailable() if frame is None else detector.detect(frame))
            mirror.follow(monitor.mirror_visible)
            show_state()
            if monitor.take_recalibration_prompt():
                tray.showMessage("Holdup: camera view changed",
                                 "Your Baseline no longer fits. Choose Recalibrate in the tray menu to resume watching.")
        if frame is None:
            return
        for window in (mirror, calibration):
            if window.isVisible():
                window.show_frame(frame)
        del frame  # frames live in memory only for the length of one tick

    show_state()
    tray.show()
    if first_launch:
        calibration.show()
    # shortcut: camera read and detection run on the Qt thread (~tens of ms at 1-3 fps); move to a worker if the tray stutters.
    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(TICK_MS)

    try:
        return app.exec()
    finally:
        timer.stop()
        detector.close()
        camera.close()
        store.close()
