from fakes import FakeClock
from landmarks import upright

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
