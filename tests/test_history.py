"""What the History page shows for a range of Daily Stats: the table rows, the chart's bars and the average."""
from datetime import date

from holdup.posture_monitor import DailyStats
from holdup.ui.history import Bar, Row, history

TODAY = date(2026, 10, 16)  # a Friday


def test_rows_run_newest_first_with_today_yesterday_then_dates():
    stats = {date(2026, 10, 16): DailyStats(good_posture=11760, forward_lean=3480, side_lean=1320, mirror_count=4)}

    rows = history(stats, TODAY, 7).rows

    assert [row.day for row in rows] == [
        "Today", "Yesterday", "Wed 14 Oct", "Tue 13 Oct", "Mon 12 Oct", "Sun 11 Oct", "Sat 10 Oct",
    ]
    assert rows[0] == Row("Today", "4 h 36 min", ("71%", "21%", "8%", "4"))


def test_a_day_without_watched_time_is_empty_never_zero_percent():
    rows = history({}, TODAY, 7).rows

    assert rows[1] == Row("Yesterday", "", ())


def test_the_7_day_chart_runs_oldest_first_labelled_by_weekday_and_today():
    stats = {date(2026, 10, 16): DailyStats(good_posture=710, forward_lean=290)}

    bars = history(stats, TODAY, 7).bars

    assert bars == (
        Bar("Sat", None), Bar("Sun", None), Bar("Mon", None), Bar("Tue", None), Bar("Wed", None), Bar("Thu", None),
        Bar("Today", 71),
    )


def test_the_30_day_chart_labels_every_5th_day_back_from_today():
    labels = [bar.label for bar in history({}, TODAY, 30).bars]

    assert labels[::-1][::5] == ["Today", "11 Oct", "6 Oct", "1 Oct", "26 Sep", "21 Sep"]
    assert sum(1 for label in labels if label) == 6


def test_the_average_is_over_days_with_watched_time_only():
    stats = {
        date(2026, 10, 16): DailyStats(good_posture=60, forward_lean=40),  # 60%
        date(2026, 10, 14): DailyStats(good_posture=90, side_lean=10),  # 90%
        date(2026, 10, 1): DailyStats(good_posture=10, side_lean=90),  # outside the last 7 days
    }

    view = history(stats, TODAY, 7)

    assert (view.average, view.active_days) == (75, 2)


def test_no_watched_time_in_range_has_no_average():
    view = history({}, TODAY, 7)

    assert (view.average, view.active_days) == (None, 0)
