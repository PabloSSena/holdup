"""What the main window's status pill says for each Posture Monitor state."""
from holdup.posture_monitor import MonitorState
from holdup.ui.theme import status


def test_judging_states_all_read_as_watching():
    for state in (MonitorState.GOOD_POSTURE, MonitorState.FORWARD_LEAN, MonitorState.SIDE_LEAN):
        assert status(state, paused=False) == ("Watching", "#3FA36B")


def test_states_that_stop_watching_have_their_own_label_and_colour():
    assert status(MonitorState.ABSENT, paused=False) == ("Absent", "#8C948F")
    assert status(MonitorState.CAMERA_UNAVAILABLE, paused=False) == ("Camera Unavailable", "#E07A2E")
    assert status(MonitorState.STALE_BASELINE, paused=False) == ("Stale Baseline", "#D9534F")
    assert status(MonitorState.CALIBRATING, paused=False) == ("Calibrating", "#4C8BD6")


def test_without_a_baseline_the_pill_reads_as_calibrating_like_the_tray_icon():
    assert status(MonitorState.UNCALIBRATED, paused=False) == ("Calibrating", "#4C8BD6")


def test_paused_wins_over_any_state():
    for state in MonitorState:
        assert status(state, paused=True) == ("Paused", "#E3B53B")
