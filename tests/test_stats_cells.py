"""What one day's row in the Stats window says."""
from holdup.posture_monitor import DailyStats
from holdup.windows import stats_cells


def test_a_day_shows_shares_of_watched_time_and_the_mirror_count():
    day = DailyStats(good_posture=1800, forward_lean=900, side_lean=900, mirror_count=4)

    assert stats_cells(day) == ["50%", "25%", "25%", "4"]


def test_a_day_without_watched_time_is_empty_not_zero_percent():
    assert stats_cells(None) == ["", "", "", ""]
    assert stats_cells(DailyStats()) == ["", "", "", ""]
