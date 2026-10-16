"""Which tray icon each state shows."""
from holdup.icons import TRAY_COLORS, tray_glyph
from holdup.posture_monitor import MonitorState


def test_every_state_maps_to_its_own_tray_icon():
    assert {state: tray_glyph(state, paused=False) for state in MonitorState} == {
        MonitorState.UNCALIBRATED: "calibrating",
        MonitorState.CALIBRATING: "calibrating",
        MonitorState.GOOD_POSTURE: "watching",
        MonitorState.FORWARD_LEAN: "watching",
        MonitorState.SIDE_LEAN: "watching",
        MonitorState.ABSENT: "absent",
        MonitorState.CAMERA_UNAVAILABLE: "unavailable",
        MonitorState.STALE_BASELINE: "stale",
    }


def test_paused_shows_the_pause_icon_whatever_the_state():
    assert {tray_glyph(state, paused=True) for state in MonitorState} == {"paused"}


def test_every_tray_icon_has_its_design_colour():
    assert TRAY_COLORS == {
        "watching": "#3FA36B", "absent": "#8C948F", "unavailable": "#E07A2E",
        "stale": "#D9534F", "paused": "#E3B53B", "calibrating": "#4C8BD6",
    }
