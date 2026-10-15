"""The Baseline is remembered in the Store: a real SQLite database in a temporary file."""
from fakes import FakeClock
from landmarks import leaning_forward, upright

from holdup.observation import NoPerson
from holdup.posture_monitor import MonitorState, PostureMonitor
from holdup.store import Store
from test_posture_monitor import sit


def calibrate(monitor, clock, observation=upright()):
    monitor.begin_calibration()
    sit(monitor, clock, observation, 6)


def test_a_calibrated_user_is_watched_straight_after_a_restart(tmp_path):
    clock = FakeClock()
    calibrate(PostureMonitor(clock=clock, store=Store(tmp_path / "holdup.db")), clock)

    restarted = PostureMonitor(clock=clock, store=Store(tmp_path / "holdup.db"))

    assert restarted.calibrated
    restarted.observe(upright())
    assert restarted.state is MonitorState.GOOD_POSTURE
    sit(restarted, clock, leaning_forward(), 5.6)
    assert restarted.mirror_visible


def test_a_failed_recalibration_keeps_the_stored_baseline(tmp_path):
    clock = FakeClock()
    calibrate(PostureMonitor(clock=clock, store=Store(tmp_path / "holdup.db")), clock)
    monitor = PostureMonitor(clock=clock, store=Store(tmp_path / "holdup.db"))

    calibrate(monitor, clock, NoPerson())
    assert monitor.calibration_failed

    restarted = PostureMonitor(clock=clock, store=Store(tmp_path / "holdup.db"))
    restarted.observe(upright())
    assert restarted.state is MonitorState.GOOD_POSTURE


def test_a_successful_recalibration_replaces_the_stored_baseline(tmp_path):
    clock = FakeClock()
    calibrate(PostureMonitor(clock=clock, store=Store(tmp_path / "holdup.db")), clock)
    monitor = PostureMonitor(clock=clock, store=Store(tmp_path / "holdup.db"))

    calibrate(monitor, clock, leaning_forward())  # the User's new setup sits closer to the camera

    restarted = PostureMonitor(clock=clock, store=Store(tmp_path / "holdup.db"))
    restarted.observe(leaning_forward())
    assert restarted.state is MonitorState.GOOD_POSTURE


def test_without_a_stored_baseline_the_user_is_uncalibrated(tmp_path):
    monitor = PostureMonitor(clock=FakeClock(), store=Store(tmp_path / "holdup.db"))

    assert not monitor.calibrated
    monitor.observe(upright())
    assert monitor.state is MonitorState.UNCALIBRATED
