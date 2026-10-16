"""Settings page logic: when the Baseline was captured, and the Baseline row's text."""
from datetime import datetime

from fakes import FakeClock
from landmarks import upright, upright_points

from holdup.posture_monitor import BASELINE, PostureMonitor
from holdup.store import Store
from holdup.ui.settings import STALE_TEXT, baseline_text


def calibrate(monitor, clock):
    """Hold Good Posture through the countdown and capture, one frame every 0.4 s, until Calibration ends."""
    monitor.begin_calibration()
    for _ in range(14):  # frames at 0.0 .. 5.2 s; the one at 5.2 s ends the 3 s countdown + 2 s capture
        monitor.observe(upright())
        clock.advance(0.4)


def test_calibration_records_when_the_baseline_was_captured_and_a_restart_remembers_it(tmp_path):
    clock = FakeClock()  # 2026-01-05 09:00:00
    store = Store(tmp_path / "holdup.db")
    monitor = PostureMonitor(clock=clock, store=store)
    calibrate(monitor, clock)
    assert monitor.baseline_captured_at == datetime(2026, 1, 5, 9, 0, 5, 200000)
    store.close()

    restarted = PostureMonitor(clock=clock, store=Store(tmp_path / "holdup.db"))

    assert restarted.baseline_captured_at == datetime(2026, 1, 5, 9, 0, 5, 200000)


def test_a_baseline_saved_before_capture_times_were_recorded_has_no_capture_time(tmp_path):
    store = Store(tmp_path / "holdup.db")
    store.set(BASELINE, upright_points())

    monitor = PostureMonitor(clock=FakeClock(), store=store)

    assert monitor.calibrated
    assert monitor.baseline_captured_at is None


NOW = datetime(2026, 10, 16, 15, 30)  # a Friday


def test_baseline_row_shows_the_capture_time_today_or_with_its_date():
    assert baseline_text(datetime(2026, 10, 16, 9, 10), NOW, stale=False, has_camera=True) == "Captured today at 09:10"
    assert baseline_text(datetime(2026, 10, 14, 9, 10), NOW, stale=False, has_camera=True) == "Captured Wed 14 Oct at 09:10"
    assert baseline_text(datetime(2026, 10, 2, 18, 5), NOW, stale=False, has_camera=True) == "Captured Fri 2 Oct at 18:05"


def test_baseline_row_without_a_camera_or_with_a_stale_baseline():
    captured = datetime(2026, 10, 16, 9, 10)
    assert baseline_text(captured, NOW, stale=True, has_camera=False) == "Needs a camera"
    assert baseline_text(captured, NOW, stale=True, has_camera=True) == STALE_TEXT
    assert STALE_TEXT == "Stale — the camera view changed. Recalibrate to resume watching."


def test_baseline_row_for_a_baseline_without_a_capture_time_or_no_baseline_yet():
    assert baseline_text(None, NOW, stale=False, has_camera=True) == "Captured"
    assert baseline_text(None, NOW, stale=False, has_camera=True, calibrated=False) == "Not captured yet"
