"""What the Mirror's edge and label say for each monitor state."""
from holdup.posture_monitor import MonitorState
from holdup.windows import mirror_lean


def test_each_lean_has_its_edge_colour_and_label():
    assert mirror_lean(MonitorState.FORWARD_LEAN) == ("#E2A45C", "Forward Lean")
    assert mirror_lean(MonitorState.SIDE_LEAN) == ("#A0A7E6", "Side Lean")


def test_states_that_are_not_a_lean_have_no_edge_or_label():
    for state in MonitorState:
        if state not in (MonitorState.FORWARD_LEAN, MonitorState.SIDE_LEAN):
            assert mirror_lean(state) is None
