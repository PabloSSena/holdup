"""Tray App: the Qt shell that wires the Camera Source, Pose Detector, Posture Monitor and windows together."""
import os
import sys
from datetime import datetime, timedelta

from PySide6.QtCore import QProcess, QTimer
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from holdup.camera_source import CameraSource, capture_index
from holdup.icons import TRAY_COLORS, app_icon, tray_glyph, tray_icon
from holdup.observation import CameraUnavailable
from holdup.pose_detector import PoseDetector
from holdup.posture_classifier import Sensitivity
from holdup.posture_monitor import PostureMonitor
from holdup.start_at_login import StartAtLogin, app_executable, login_item
from holdup.store import Store, default_path
from holdup.ui.actions import Actions
from holdup.ui.main_window import MainWindow
from holdup.ui import strings
from holdup.ui.strings import LANGUAGE, start_at_login_copy, tr
from holdup.ui.theme import load_fonts
from holdup.windows import MirrorWindow

TICK_MS = 33  # smooth feed while a window shows it; analysis still only runs when the Posture Monitor says it is due


def _device_id(device) -> str:
    return bytes(device.id()).decode(errors="replace")


def _camera_names() -> list[str]:
    """Cameras plugged in right now, the system default first: it is the one used until the User chooses."""
    devices = QMediaDevices.videoInputs()
    default = _device_id(QMediaDevices.defaultVideoInput())
    return [device.description() for device in sorted(devices, key=lambda device: _device_id(device) != default)]


def main() -> int:
    if sys.platform.startswith("linux"):
        # Wayland ignores window positions and always-on-top, which the Mirror needs; XWayland honours both.
        os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(app_icon())
    load_fonts()

    detector = PoseDetector()
    store = Store(default_path())
    strings.LANG = store.get(LANGUAGE, strings.LANG)  # before any window or menu is built, as they read it once
    monitor = PostureMonitor(clock=datetime.now, store=store)

    def locate_camera() -> int | None:
        """The chosen camera's OpenCV index, else the system default's; a saved camera that is missing (or no camera
        at all) gives None, so Camera Unavailable is retried."""
        devices = QMediaDevices.videoInputs()
        ids = [_device_id(device) for device in devices]
        if monitor.camera is None:
            default = _device_id(QMediaDevices.defaultVideoInput())
            wanted = default if default in ids else ids[0] if ids else None
        else:
            wanted = next((_device_id(d) for d in devices if d.description() == monitor.camera), None)
        return None if wanted is None else capture_index(ids, wanted)

    camera = CameraSource(locate_camera)
    mirror = MirrorWindow()
    first_launch = not monitor.calibrated

    def recalibrate() -> None:
        main_window.show_calibration()  # Calibration begins on its Start button

    icons = {glyph: tray_icon(glyph) for glyph in TRAY_COLORS}
    tray = QSystemTrayIcon()
    menu = QMenu()
    menu.addAction(tr("Open Holdup")).triggered.connect(lambda: main_window.present())
    recalibrate_action = QAction(tr("Recalibrate"), menu)
    recalibrate_action.triggered.connect(recalibrate)
    menu.addAction(recalibrate_action)
    sensitivity_menu = menu.addMenu(tr("Sensitivity"))
    sensitivity_group = QActionGroup(sensitivity_menu)  # exclusive: one choice marked at a time
    sensitivity_actions = {}
    for level in Sensitivity:
        action = sensitivity_group.addAction(tr(level.value))
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

    camera_menu = menu.addMenu(tr("Camera"))

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
            camera_menu.addAction(tr("No camera found")).setEnabled(False)
        for name in names:
            action = group.addAction(name)
            action.setCheckable(True)
            action.setChecked(name == current)
            action.triggered.connect(lambda _=False, name=name: choose_camera(name))
            camera_menu.addAction(action)

    camera_menu.aboutToShow.connect(list_cameras)

    pause_actions = []
    for label, duration in (("Pause for 30 minutes", timedelta(minutes=30)), ("Pause for 1 hour", timedelta(hours=1)), ("Pause until resumed", None)):
        action = menu.addAction(tr(label))
        action.triggered.connect(lambda _=False, d=duration: pause(d))
        pause_actions.append(action)
    resume_action = menu.addAction(tr("Resume"))
    resume_action.triggered.connect(resume)
    menu.addSeparator()
    start_at_login = None
    if getattr(sys, "frozen", False):  # from source there is no app to register
        start_at_login = StartAtLogin(store, login_item(), app_executable())
        start_at_login.apply()
        start_action = QAction(tr(start_at_login_copy()[0]), menu, checkable=True, checked=start_at_login.enabled)
        start_action.toggled.connect(start_at_login.set_enabled)
        menu.aboutToShow.connect(lambda: start_action.setChecked(start_at_login.enabled))  # the Settings page may have changed it
        menu.addAction(start_action)
    quit_action = QAction(tr("Quit"), menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)

    def set_language(language: str) -> None:
        """Every window and menu reads the language once when built, so restart rather than rebuild them all."""
        store.set(LANGUAGE, language)
        command = [app_executable()] if getattr(sys, "frozen", False) else [sys.executable, "-m", "holdup"]
        QProcess.startDetached(command[0], command[1:])
        app.quit()

    main_window = MainWindow(monitor, Actions(
        pause=pause, resume=resume, recalibrate=recalibrate, set_sensitivity=set_sensitivity,
        camera_names=_camera_names, choose_camera=choose_camera, start_at_login=start_at_login,
        retry_camera=camera.close, set_language=set_language,
    ))
    calibration = main_window.calibration
    tray.activated.connect(lambda reason: reason == QSystemTrayIcon.Trigger and main_window.present())

    def show_state() -> None:
        paused = monitor.paused
        tray.setIcon(icons[tray_glyph(monitor.state, paused)])
        tray.setToolTip("Holdup: " + tr("Paused" if paused else monitor.state.value))
        for action in pause_actions:
            action.setVisible(not paused)
        resume_action.setVisible(paused)
        if main_window.isVisible():
            main_window.refresh()

    def prompt_recalibration() -> None:
        tray.showMessage(tr("Holdup: camera view changed"),
                         tr("Your Baseline no longer fits. Choose Recalibrate in the tray menu to resume watching."))

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
