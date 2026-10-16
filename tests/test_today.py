"""The Today page's pure parts: when a Pause ends, the status card's wording and the Watched Time durations."""
from datetime import datetime, timedelta

from fakes import FakeClock

from holdup.posture_monitor import MonitorState, PostureMonitor
from holdup.ui.today import format_duration, headline


def test_a_timed_pause_ends_at_the_time_it_was_started_plus_its_duration():
    clock = FakeClock(datetime(2026, 10, 16, 14, 0))
    monitor = PostureMonitor(clock=clock)

    monitor.pause(timedelta(minutes=30))

    assert monitor.paused_until == datetime(2026, 10, 16, 14, 30)


def test_a_pause_until_resumed_has_no_end_time():
    monitor = PostureMonitor(clock=FakeClock())

    monitor.pause()

    assert monitor.paused and monitor.paused_until is None


def test_durations_read_as_hours_and_minutes_or_minutes_alone():
    assert format_duration(3 * 3600 + 16 * 60) == "3 h 16 min"
    assert format_duration(58 * 60 + 59) == "58 min"
    assert format_duration(0) == "0 min"


def test_the_status_card_explains_each_state():
    assert headline(MonitorState.GOOD_POSTURE, False, None) == (
        "Watching", "You are sitting well. Holdup is quietly keeping an eye on your posture.")
    assert headline(MonitorState.FORWARD_LEAN, False, None)[0] == "Watching"
    assert headline(MonitorState.ABSENT, False, None) == (
        "Absent", "Nobody is in front of the camera. Watching picks up again when you are back.")
    assert headline(MonitorState.CAMERA_UNAVAILABLE, False, None) == (
        "Camera Unavailable", "Watching is on hold until the camera can be read.")
    assert headline(MonitorState.STALE_BASELINE, False, None) == (
        "Stale Baseline", "Watching is on hold until you Recalibrate.")
    assert headline(MonitorState.CALIBRATING, False, None) == (
        "Calibrating", "Capturing your Baseline. Hold still for a moment.")


def test_a_paused_status_card_says_when_watching_starts_again():
    paused = "Holdup is not watching right now. Your Watched Time is not counting."
    assert headline(MonitorState.GOOD_POSTURE, True, datetime(2026, 10, 16, 14, 30)) == ("Paused until 14:30", paused)
    assert headline(MonitorState.ABSENT, True, None) == ("Paused until resumed", paused)
