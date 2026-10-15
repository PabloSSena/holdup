"""Tray App: the Qt shell that wires the Camera Source, Pose Detector and Posture Monitor together."""
import sys
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from holdup.camera_source import CameraSource
from holdup.pose_detector import PoseDetector
from holdup.posture_monitor import MonitorState, PostureMonitor

TICK_MS = 100  # how often to ask the Posture Monitor whether a frame is due


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
        tray.setToolTip("Holdup: Absent" if absent else "Holdup: watching")

    def tick() -> None:
        if not monitor.analysis_due():
            return
        frame = camera.read()
        if frame is None:
            return  # shortcut: unreadable camera is ignored, issue 07 adds Camera Unavailable
        observation = detector.detect(frame)
        del frame  # frames live in memory only for the length of one detection
        monitor.observe(observation)
        show_state()

    show_state()
    tray.show()
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
