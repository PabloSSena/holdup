from datetime import timedelta

from fakes import FakeClock
from landmarks import leaning_forward, upright

from holdup.observation import NoPerson
from holdup.posture_monitor import MonitorState, PostureMonitor


def test_user_sitting_down_is_watched_and_leaving_makes_them_absent():
    monitor = PostureMonitor(clock=FakeClock())

    monitor.observe(upright())
    assert monitor.state is MonitorState.UNCALIBRATED

    monitor.observe(NoPerson())
    assert monitor.state is MonitorState.ABSENT


def test_user_coming_back_after_being_absent_is_watched_again():
    monitor = PostureMonitor(clock=FakeClock())
    monitor.observe(upright())
    monitor.observe(NoPerson())

    monitor.observe(upright())

    assert monitor.state is MonitorState.UNCALIBRATED


def test_nobody_has_been_seen_yet_counts_as_absent():
    assert PostureMonitor(clock=FakeClock()).state is MonitorState.ABSENT


def test_first_frame_is_analysed_straight_away():
    assert PostureMonitor(clock=FakeClock()).analysis_due()


def test_while_the_user_is_present_frames_are_analysed_two_to_three_times_a_second():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)
    monitor.observe(upright())

    clock.advance(0.33)
    assert not monitor.analysis_due()  # no faster than 3 per second
    clock.advance(0.17)
    assert monitor.analysis_due()  # no slower than 2 per second


def test_while_the_user_is_absent_frames_are_analysed_about_once_a_second():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)
    monitor.observe(NoPerson())

    clock.advance(0.9)
    assert not monitor.analysis_due()
    clock.advance(0.1)
    assert monitor.analysis_due()


def test_a_clock_set_backwards_does_not_stall_analysis():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)
    monitor.observe(upright())

    clock.advance(-3600)  # e.g. leaving daylight saving time

    assert monitor.analysis_due()


def test_posture_monitor_stays_free_of_qt_camera_and_mediapipe():
    import subprocess
    import sys

    code = "import sys, holdup.posture_monitor; print(sorted({'PySide6', 'cv2', 'mediapipe'} & set(sys.modules)))"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)

    assert result.stdout.strip() == "[]"


def test_before_the_first_calibration_a_long_forward_lean_is_not_judged_and_shows_no_mirror():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)

    for _ in range(30):
        monitor.observe(leaning_forward())
        clock.advance(0.4)

    assert monitor.state is MonitorState.UNCALIBRATED
    assert not monitor.mirror_visible


def sit(monitor, clock, observation, seconds):
    """The User holds one pose for a while, observed at the watching rate (one frame every 0.4 s)."""
    for _ in range(round(seconds / 0.4)):
        monitor.observe(observation)
        clock.advance(0.4)


def calibrated(clock):
    monitor = PostureMonitor(clock=clock)
    monitor.begin_calibration()
    sit(monitor, clock, upright(), 6)
    return monitor


def test_calibration_counts_down_then_captures_and_good_posture_is_judged_after():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)

    monitor.begin_calibration()
    assert monitor.state is MonitorState.CALIBRATING
    assert monitor.calibration_countdown() == 3

    sit(monitor, clock, upright(), 2)
    assert monitor.state is MonitorState.CALIBRATING
    assert 0 < monitor.calibration_countdown() < 3

    sit(monitor, clock, upright(), 4)
    monitor.observe(upright())

    assert monitor.state is MonitorState.GOOD_POSTURE
    assert not monitor.calibration_failed


def test_calibration_fails_when_nobody_is_seen_during_capture_and_posture_stays_unjudged():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)

    monitor.begin_calibration()
    sit(monitor, clock, upright(), 3.2)
    sit(monitor, clock, NoPerson(), 0.4)
    sit(monitor, clock, upright(), 2)

    assert monitor.calibration_failed
    assert monitor.state is MonitorState.UNCALIBRATED


def test_a_retry_after_a_failed_calibration_can_succeed():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)
    monitor.begin_calibration()
    sit(monitor, clock, NoPerson(), 6)

    monitor.begin_calibration()
    sit(monitor, clock, upright(), 6)

    assert not monitor.calibration_failed
    assert monitor.state is MonitorState.GOOD_POSTURE


def test_calibration_fails_when_the_user_moves_too_much_during_capture():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)

    monitor.begin_calibration()
    sit(monitor, clock, upright(), 3.2)
    sit(monitor, clock, leaning_forward(), 0.8)
    sit(monitor, clock, upright(), 2)

    assert monitor.calibration_failed
    assert monitor.state is MonitorState.UNCALIBRATED


def test_forward_lean_shows_the_mirror_only_after_5_continuous_seconds():
    clock = FakeClock()
    monitor = calibrated(clock)

    monitor.observe(leaning_forward())
    assert monitor.state is MonitorState.FORWARD_LEAN
    clock.advance(4.9)
    monitor.observe(leaning_forward())
    assert not monitor.mirror_visible

    clock.advance(0.1)
    monitor.observe(leaning_forward())
    assert monitor.mirror_visible


def test_good_posture_hides_the_mirror_at_once_and_restarts_the_5_second_count():
    clock = FakeClock()
    monitor = calibrated(clock)
    sit(monitor, clock, leaning_forward(), 5.6)
    assert monitor.mirror_visible

    monitor.observe(upright())
    assert monitor.state is MonitorState.GOOD_POSTURE
    assert not monitor.mirror_visible

    clock.advance(0.4)
    sit(monitor, clock, leaning_forward(), 4.8)
    assert not monitor.mirror_visible


def test_good_posture_at_4_seconds_means_another_5_seconds_of_lean_are_needed():
    clock = FakeClock()
    monitor = calibrated(clock)
    sit(monitor, clock, leaning_forward(), 4)
    sit(monitor, clock, upright(), 0.4)

    sit(monitor, clock, leaning_forward(), 4.8)

    assert not monitor.mirror_visible


def test_becoming_absent_hides_the_mirror_and_restarts_the_5_second_count():
    clock = FakeClock()
    monitor = calibrated(clock)
    sit(monitor, clock, leaning_forward(), 5.6)

    monitor.observe(NoPerson())
    assert monitor.state is MonitorState.ABSENT
    assert not monitor.mirror_visible

    clock.advance(1)
    sit(monitor, clock, leaning_forward(), 4.8)
    assert not monitor.mirror_visible


def test_recalibrating_hides_the_mirror():
    clock = FakeClock()
    monitor = calibrated(clock)
    sit(monitor, clock, leaning_forward(), 5.6)

    monitor.begin_calibration()

    assert not monitor.mirror_visible


def test_pausing_while_the_mirror_is_visible_hides_it_at_once():
    clock = FakeClock()
    monitor = calibrated(clock)
    sit(monitor, clock, leaning_forward(), 5.6)
    assert monitor.mirror_visible

    monitor.pause()

    assert monitor.paused
    assert not monitor.mirror_visible


def test_no_mirror_appears_while_paused_however_long_the_forward_lean_lasts():
    clock = FakeClock()
    monitor = calibrated(clock)
    monitor.pause()

    sit(monitor, clock, leaning_forward(), 120)

    assert monitor.paused
    assert not monitor.mirror_visible


def test_a_30_minute_pause_ends_by_itself_after_30_minutes():
    clock = FakeClock()
    monitor = calibrated(clock)

    monitor.pause(timedelta(minutes=30))
    clock.advance(30 * 60 - 1)
    assert monitor.paused
    clock.advance(1)
    assert not monitor.paused


def test_after_a_pause_ends_the_5_second_count_starts_fresh():
    clock = FakeClock()
    monitor = calibrated(clock)
    monitor.pause(timedelta(hours=1))
    sit(monitor, clock, leaning_forward(), 3600)
    assert not monitor.paused

    monitor.observe(leaning_forward())
    clock.advance(4.9)
    monitor.observe(leaning_forward())
    assert not monitor.mirror_visible
    clock.advance(0.1)
    monitor.observe(leaning_forward())
    assert monitor.mirror_visible


def test_resume_ends_a_pause_early():
    clock = FakeClock()
    monitor = calibrated(clock)
    monitor.pause(timedelta(hours=1))
    clock.advance(60)

    monitor.resume()

    assert not monitor.paused


def test_resume_ends_a_pause_until_resumed():
    clock = FakeClock()
    monitor = calibrated(clock)
    monitor.pause()
    clock.advance(24 * 3600)
    assert monitor.paused

    monitor.resume()

    assert not monitor.paused


def test_while_paused_frames_are_analysed_about_once_a_second():
    clock = FakeClock()
    monitor = calibrated(clock)
    monitor.pause()
    monitor.observe(upright())

    clock.advance(0.9)
    assert not monitor.analysis_due()
    clock.advance(0.1)
    assert monitor.analysis_due()
