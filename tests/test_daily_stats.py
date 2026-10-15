"""Daily Stats, through the Posture Monitor with a real SQLite Store on disk."""
from datetime import date, datetime

import pytest
from fakes import FakeClock
from landmarks import leaning_forward, leaning_sideways, upright

from holdup.observation import CameraUnavailable, NoPerson
from holdup.posture_monitor import PostureMonitor
from holdup.store import Store

DAY = date(2026, 1, 5)


def sit(monitor, clock, observation, seconds):
    """The User holds one pose for a while, observed at the watching rate (one frame every 0.4 s)."""
    for _ in range(round(seconds / 0.4)):
        monitor.observe(observation)
        clock.advance(0.4)


def calibrated(clock, store):
    """A calibrated monitor in Good Posture, with every interval up to now already in its Daily Stats."""
    monitor = PostureMonitor(clock=clock, store=store)
    monitor.begin_calibration()
    sit(monitor, clock, upright(), 6)
    monitor.observe(upright())
    return monitor


@pytest.fixture
def store(tmp_path):
    store = Store(tmp_path / "holdup.db")
    yield store
    store.close()


def test_watched_time_is_split_by_kind_of_posture(store):
    clock = FakeClock()
    monitor = calibrated(clock, store)
    before = monitor.today_stats()

    sit(monitor, clock, upright(), 60)
    sit(monitor, clock, leaning_forward(), 20)
    sit(monitor, clock, leaning_sideways("left"), 10)
    monitor.observe(upright())

    today = monitor.today_stats()
    assert today.good_posture - before.good_posture == pytest.approx(60)
    assert today.forward_lean - before.forward_lean == pytest.approx(20)
    assert today.side_lean - before.side_lean == pytest.approx(10)
    assert today.watched_time - before.watched_time == pytest.approx(90)


def test_the_mirror_count_rises_once_each_time_the_mirror_appears(store):
    clock = FakeClock()
    monitor = calibrated(clock, store)

    sit(monitor, clock, leaning_forward(), 20)  # one long appearance
    sit(monitor, clock, upright(), 2)
    sit(monitor, clock, leaning_sideways("right"), 6)
    sit(monitor, clock, upright(), 2)
    sit(monitor, clock, leaning_forward(), 3)  # too short for the Mirror

    assert monitor.today_stats().mirror_count == 2


@pytest.mark.parametrize("unjudged", [NoPerson(), CameraUnavailable()], ids=["absent", "camera unavailable"])
def test_absent_and_camera_unavailable_time_adds_nothing(store, unjudged):
    clock = FakeClock()
    monitor = calibrated(clock, store)
    before = monitor.today_stats()

    sit(monitor, clock, unjudged, 600)
    monitor.observe(unjudged)

    assert monitor.today_stats() == before


def test_paused_time_adds_nothing_although_posture_is_still_seen(store):
    clock = FakeClock()
    monitor = calibrated(clock, store)
    before = monitor.today_stats()

    monitor.pause()
    sit(monitor, clock, leaning_forward(), 600)
    monitor.observe(leaning_forward())

    assert monitor.today_stats() == before


def test_time_before_the_first_calibration_adds_nothing(store):
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock, store=store)

    sit(monitor, clock, upright(), 60)
    monitor.begin_calibration()
    sit(monitor, clock, upright(), 5)

    assert monitor.today_stats().watched_time == 0


def test_a_long_gap_between_frames_such_as_sleep_adds_nothing(store):
    clock = FakeClock()
    monitor = calibrated(clock, store)
    before = monitor.today_stats()

    clock.advance(3600)
    monitor.observe(upright())

    assert monitor.today_stats() == before


def test_time_crossing_local_midnight_is_split_between_the_two_days(store):
    clock = FakeClock(datetime(2026, 1, 5, 23, 59, 0))
    monitor = calibrated(clock, store)  # now 23:59:06
    before = monitor.today_stats()
    sit(monitor, clock, upright(), 53.6)  # last frame at 23:59:59.2

    monitor.observe(upright())  # 23:59:59.6
    clock.advance(1)  # this interval crosses midnight: 0.4 s on the 5th, 0.6 s on the 6th
    monitor.observe(upright())

    stats = monitor.daily_stats(DAY, date(2026, 1, 6))
    assert stats[DAY].good_posture - before.good_posture == pytest.approx(54)
    assert stats[date(2026, 1, 6)].good_posture == pytest.approx(0.6)
    assert monitor.today_stats() == stats[date(2026, 1, 6)]


def test_daily_stats_survive_a_restart(tmp_path):
    clock = FakeClock()
    store = Store(tmp_path / "holdup.db")
    monitor = calibrated(clock, store)
    sit(monitor, clock, leaning_forward(), 10)
    monitor.observe(upright())
    recorded = monitor.today_stats()
    store.close()

    store = Store(tmp_path / "holdup.db")
    restarted = PostureMonitor(clock=clock, store=store)

    assert restarted.today_stats() == recorded
    assert recorded.forward_lean == pytest.approx(10)
    assert recorded.mirror_count == 1
    store.close()


def test_a_range_of_days_holds_only_the_days_with_daily_stats(store):
    clock = FakeClock()
    monitor = calibrated(clock, store)
    clock.advance(2 * 24 * 3600)  # two days later
    sit(monitor, clock, upright(), 10)
    monitor.observe(upright())

    stats = monitor.daily_stats(date(2026, 1, 1), date(2026, 1, 10))

    assert sorted(stats) == [DAY, date(2026, 1, 7)]
    assert stats[date(2026, 1, 7)].good_posture == pytest.approx(10)
