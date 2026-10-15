"""Tray App: the Qt shell that wires the Camera Source, Pose Detector, Posture Monitor and windows together."""
import sys
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from holdup.camera_source import CameraSource
from holdup.observation import CameraUnavailable
from holdup.pose_detector import PoseDetector
from holdup.posture_monitor import MonitorState, PostureMonitor
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

    icons = {"watching": _dot_icon("#2e9d4f"), "absent": _dot_icon("#8a8a8a"), "unavailable": _dot_icon("#d9822b"),
             "stale": _dot_icon("#c62828")}
    tray = QSystemTrayIcon()
    menu = QMenu()
    recalibrate_action = QAction("Recalibrate", menu)
    recalibrate_action.triggered.connect(recalibrate)
    menu.addAction(recalibrate_action)
    quit_action = QAction("Quit", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)

    def show_state() -> None:
        icon = {MonitorState.ABSENT: "absent", MonitorState.CAMERA_UNAVAILABLE: "unavailable",
                MonitorState.STALE_BASELINE: "stale"}.get(monitor.state, "watching")
        tray.setIcon(icons[icon])
        tray.setToolTip(f"Holdup: {monitor.state.value}")

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
