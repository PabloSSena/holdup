"""Tray App: the Qt shell that wires the Camera Source, Pose Detector, Posture Monitor and windows together."""
import sys
from datetime import datetime, timedelta

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from holdup.camera_source import CameraSource
from holdup.icons import TRAY_COLORS, app_icon, tray_glyph, tray_icon
from holdup.observation import CameraUnavailable
from holdup.pose_detector import PoseDetector
from holdup.posture_classifier import Sensitivity
from holdup.posture_monitor import PostureMonitor
from holdup.start_with_windows import RunKey, StartWithWindows
from holdup.store import Store, default_path
from holdup.ui.actions import Actions
from holdup.ui.main_window import MainWindow
from holdup.ui.theme import load_fonts
from holdup.windows import MirrorWindow

TICK_MS = 33  # smooth feed while a window shows it; analysis still only runs when the Posture Monitor says it is due


def _camera_names() -> list[str]:
    # shortcut: assumes Qt lists cameras in DirectShow's order (true on typical setups); enumerate DirectShow itself if a wrong camera opens.
    return [device.description() for device in QMediaDevices.videoInputs()]


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(app_icon())
    load_fonts()

    detector = PoseDetector()
    store = Store(default_path())
    monitor = PostureMonitor(clock=datetime.now, store=store)

    def locate_camera() -> int | None:
        """The chosen camera's index; a saved camera that is missing gives None, so Camera Unavailable is retried."""
        names = _camera_names()
        if monitor.camera is None:
            return 0
        return names.index(monitor.camera) if monitor.camera in names else None

    camera = CameraSource(locate_camera)
    mirror = MirrorWindow()
    first_launch = not monitor.calibrated

    def recalibrate() -> None:
        main_window.show_calibration()  # Calibration begins on its Start button

    icons = {glyph: tray_icon(glyph) for glyph in TRAY_COLORS}
    tray = QSystemTrayIcon()
    menu = QMenu()
    menu.addAction("Open Holdup").triggered.connect(lambda: main_window.present())
    recalibrate_action = QAction("Recalibrate", menu)
    recalibrate_action.triggered.connect(recalibrate)
    menu.addAction(recalibrate_action)
    sensitivity_menu = menu.addMenu("Sensitivity")
    sensitivity_group = QActionGroup(sensitivity_menu)  # exclusive: one choice marked at a time
    sensitivity_actions = {}
    for level in Sensitivity:
        action = sensitivity_group.addAction(level.value)
        action.setCheckable(True)
        action.setChecked(level is monitor.sensitivity)
        action.triggered.connect(lambda _=False, level=level: setattr(monitor, "sensitivity", level))
        sensitivity_menu.addAction(action)
        sensitivity_actions[level] = action

    def set_sensitivity(level: Sensitivity) -> None:
        monitor.sensitivity = level
        sensitivity_actions[level].setChecked(True)

    def pause(duration: timedelta | None) -> None:
        monitor.pause(duration)
        mirror.follow(monitor.mirror_visible, monitor.state)
        show_state()

    def resume() -> None:
        monitor.resume()
        show_state()

    camera_menu = menu.addMenu("Camera")

    def choose_camera(name: str) -> None:
        if name == monitor.camera:
            return
        monitor.camera_changed(name)
        camera.close()  # the next tick opens the new camera
        if monitor.take_recalibration_prompt():
            prompt_recalibration()
        show_state()

    def list_cameras() -> None:
        """Rebuilt each time the menu opens, so plugged-in cameras show up."""
        camera_menu.clear()
        group = QActionGroup(camera_menu)
        names = _camera_names()
        current = monitor.camera if monitor.camera is not None else names[0] if names else None
        if not names:
            camera_menu.addAction("No camera found").setEnabled(False)
        for name in names:
            action = group.addAction(name)
            action.setCheckable(True)
            action.setChecked(name == current)
            action.triggered.connect(lambda _=False, name=name: choose_camera(name))
            camera_menu.addAction(action)

    camera_menu.aboutToShow.connect(list_cameras)

    pause_actions = []
    for label, duration in (("Pause for 30 minutes", timedelta(minutes=30)), ("Pause for 1 hour", timedelta(hours=1)), ("Pause until resumed", None)):
        action = menu.addAction(label)
        action.triggered.connect(lambda _=False, d=duration: pause(d))
        pause_actions.append(action)
    resume_action = menu.addAction("Resume")
    resume_action.triggered.connect(resume)
    menu.addSeparator()
    start_with_windows = None
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

    main_window = MainWindow(monitor, Actions(
        pause=pause, resume=resume, recalibrate=recalibrate, set_sensitivity=set_sensitivity,
        camera_names=_camera_names, choose_camera=choose_camera, start_with_windows=start_with_windows,
    ))
    calibration = main_window.calibration
    tray.activated.connect(lambda reason: reason == QSystemTrayIcon.Trigger and main_window.present())

    def show_state() -> None:
        paused = monitor.paused
        tray.setIcon(icons[tray_glyph(monitor.state, paused)])
        tray.setToolTip("Holdup: Paused" if paused else f"Holdup: {monitor.state.value}")
        for action in pause_actions:
            action.setVisible(not paused)
        resume_action.setVisible(paused)
        if main_window.isVisible():
            main_window.refresh()

    def prompt_recalibration() -> None:
        tray.showMessage("Holdup: camera view changed",
                         "Your Baseline no longer fits. Choose Recalibrate in the tray menu to resume watching.")

    def tick() -> None:
        if calibration.isVisible():
            calibration.refresh()
        due = monitor.analysis_due()
        if not (due or mirror.isVisible() or calibration.isVisible()):
            return
        frame = camera.read()
        if due:
            monitor.observe(CameraUnavailable() if frame is None else detector.detect(frame))
            mirror.follow(monitor.mirror_visible, monitor.state)
            show_state()
            if monitor.take_recalibration_prompt():
                prompt_recalibration()
        if frame is None:
            return
        for window in (mirror, calibration):
            if window.isVisible():
                window.show_frame(frame)
        del frame  # frames live in memory only for the length of one tick

    show_state()
    tray.show()
    if first_launch:
        main_window.show_calibration()
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
