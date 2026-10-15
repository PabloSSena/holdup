"""Tray App: the Qt shell that wires the Camera Source, Pose Detector, Posture Monitor and windows together."""
import sys
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from holdup.camera_source import CameraSource
from holdup.pose_detector import PoseDetector
from holdup.posture_monitor import MonitorState, PostureMonitor
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
    monitor = PostureMonitor(clock=datetime.now)
    mirror = MirrorWindow()
    # shortcut: the Baseline lives in memory only, so every launch is a first launch; issue 03 persists it.
    monitor.begin_calibration()
    calibration = CalibrationWindow(monitor)

    icons = {"watching": _dot_icon("#2e9d4f"), "absent": _dot_icon("#8a8a8a")}
    tray = QSystemTrayIcon()
    menu = QMenu()
    quit_action = QAction("Quit", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)

    def show_state() -> None:
        absent = monitor.state is MonitorState.ABSENT
        tray.setIcon(icons["absent" if absent else "watching"])
        tray.setToolTip(f"Holdup: {monitor.state.value}")

    def tick() -> None:
        if calibration.isVisible():
            calibration.refresh()
        due = monitor.analysis_due()
        if not (due or mirror.isVisible() or calibration.isVisible()):
            return
        frame = camera.read()
        if frame is None:
            return  # shortcut: unreadable camera is ignored, issue 07 adds Camera Unavailable
        if due:
            monitor.observe(detector.detect(frame))
            mirror.follow(monitor.mirror_visible)
            show_state()
        for window in (mirror, calibration):
            if window.isVisible():
                window.show_frame(frame)
        del frame  # frames live in memory only for the length of one tick

    show_state()
    tray.show()
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
