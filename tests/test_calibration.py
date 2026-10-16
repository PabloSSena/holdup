from fakes import FakeClock
from landmarks import leaning_forward, upright

from holdup.posture_monitor import MonitorState, PostureMonitor
from test_posture_monitor import calibrated, sit, stale


def test_cancelling_calibration_keeps_the_old_baseline_and_judging_resumes():
    clock = FakeClock()
    monitor = calibrated(clock)
    monitor.begin_calibration()
    sit(monitor, clock, upright(), 3.6)  # into the capture

    monitor.cancel_calibration()
    sit(monitor, clock, leaning_forward(), 4)  # long past when the capture would have ended

    assert monitor.state is MonitorState.FORWARD_LEAN  # judged against the old upright Baseline
    assert not monitor.calibration_failed
    assert monitor.calibration_countdown() == 0


def test_cancelling_a_recalibration_leaves_a_stale_baseline_stale():
    clock = FakeClock()
    monitor = stale(clock)
    monitor.begin_calibration()
    sit(monitor, clock, upright(), 1)

    monitor.cancel_calibration()
    sit(monitor, clock, upright(), 6)

    assert monitor.state is MonitorState.STALE_BASELINE


def test_capture_progress_stays_at_zero_through_the_countdown_then_fills_over_the_capture():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)
    assert monitor.calibration_progress() == 0

    monitor.begin_calibration()
    clock.advance(2.5)
    assert monitor.calibration_progress() == 0

    clock.advance(1.5)  # 1 s into the 2 s capture
    assert monitor.calibration_progress() == 0.5

    clock.advance(5)  # no frame has ended it yet
    assert monitor.calibration_progress() == 1

    monitor.observe(upright())
    assert monitor.calibration_progress() == 0  # ended
