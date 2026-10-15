from datetime import timedelta

from fakes import FakeClock
import pytest
from landmarks import leaning_forward, leaning_sideways, tilting_head, upright, upright_points

from holdup.observation import CameraUnavailable, NoPerson, UserSeen
from holdup.posture_classifier import Sensitivity
from holdup.posture_monitor import MonitorState, PostureMonitor
from holdup.store import Store


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


@pytest.mark.parametrize("side", ["left", "right"])
def test_side_lean_to_either_side_shows_the_mirror_after_5_seconds_and_good_posture_hides_it(side):
    clock = FakeClock()
    monitor = calibrated(clock)

    sit(monitor, clock, leaning_sideways(side), 4.8)
    assert monitor.state is MonitorState.SIDE_LEAN
    assert not monitor.mirror_visible
    sit(monitor, clock, leaning_sideways(side), 0.8)
    assert monitor.mirror_visible

    monitor.observe(upright())
    assert monitor.state is MonitorState.GOOD_POSTURE
    assert not monitor.mirror_visible


def test_switching_from_forward_lean_to_side_lean_at_3_seconds_still_shows_the_mirror_at_5_seconds():
    clock = FakeClock()
    monitor = calibrated(clock)

    sit(monitor, clock, leaning_forward(), 3.2)  # lean began at 0 s
    sit(monitor, clock, leaning_sideways("left"), 1.6)
    monitor.observe(leaning_sideways("left"))  # at 4.8 s
    assert not monitor.mirror_visible

    clock.advance(0.2)
    monitor.observe(leaning_sideways("left"))  # at 5 s
    assert monitor.state is MonitorState.SIDE_LEAN
    assert monitor.mirror_visible


def test_switching_from_side_lean_to_forward_lean_keeps_the_mirror_up():
    clock = FakeClock()
    monitor = calibrated(clock)
    sit(monitor, clock, leaning_sideways("right"), 5.6)

    monitor.observe(leaning_forward())

    assert monitor.state is MonitorState.FORWARD_LEAN
    assert monitor.mirror_visible


def test_leaning_forward_and_sideways_at_once_counts_as_forward_lean():
    clock = FakeClock()
    monitor = calibrated(clock)

    monitor.observe(leaning_sideways("left", pose=leaning_forward()))

    assert monitor.state is MonitorState.FORWARD_LEAN


@pytest.mark.parametrize("side", ["left", "right"])
def test_tilting_only_the_head_counts_as_side_lean(side):
    clock = FakeClock()
    monitor = calibrated(clock)

    monitor.observe(tilting_head(side))

    assert monitor.state is MonitorState.SIDE_LEAN


def test_calibration_fails_when_the_user_leans_sideways_during_capture():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)

    monitor.begin_calibration()
    sit(monitor, clock, upright(), 3.2)
    sit(monitor, clock, leaning_sideways("right"), 0.8)
    sit(monitor, clock, upright(), 2)

    assert monitor.calibration_failed


def test_an_unreadable_camera_is_camera_unavailable_not_absent():
    monitor = PostureMonitor(clock=FakeClock())
    monitor.observe(upright())

    monitor.observe(CameraUnavailable())

    assert monitor.state is MonitorState.CAMERA_UNAVAILABLE


def test_camera_unavailable_hides_the_mirror_and_restarts_the_5_second_count():
    clock = FakeClock()
    monitor = calibrated(clock)
    sit(monitor, clock, leaning_forward(), 5.6)

    monitor.observe(CameraUnavailable())
    assert not monitor.mirror_visible

    clock.advance(1)
    sit(monitor, clock, leaning_forward(), 4.8)
    assert not monitor.mirror_visible


def test_watching_resumes_by_itself_when_the_camera_delivers_frames_again():
    clock = FakeClock()
    monitor = calibrated(clock)
    sit(monitor, clock, CameraUnavailable(), 10)

    monitor.observe(leaning_forward())

    assert monitor.state is MonitorState.FORWARD_LEAN


def test_while_the_camera_is_unavailable_it_is_retried_about_once_a_second():
    clock = FakeClock()
    monitor = calibrated(clock)
    monitor.observe(CameraUnavailable())

    clock.advance(0.9)
    assert not monitor.analysis_due()
    clock.advance(0.1)
    assert monitor.analysis_due()


def test_calibration_fails_at_once_when_the_camera_is_unavailable_instead_of_waiting_forever():
    clock = FakeClock()
    monitor = PostureMonitor(clock=clock)
    monitor.begin_calibration()

    monitor.observe(CameraUnavailable())

    assert monitor.state is MonitorState.CAMERA_UNAVAILABLE
    assert monitor.calibration_failed
    assert monitor.calibration_countdown() == 0


def test_a_calibration_lost_to_the_camera_keeps_the_previous_baseline():
    clock = FakeClock()
    monitor = calibrated(clock)
    monitor.begin_calibration()
    sit(monitor, clock, upright(), 3.2)

    monitor.observe(CameraUnavailable())
    monitor.observe(upright())

    assert monitor.state is MonitorState.GOOD_POSTURE


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


SMALL_LEANS = [(leaning_forward(0.1), MonitorState.FORWARD_LEAN), (leaning_sideways("left", degrees=6), MonitorState.SIDE_LEAN)]
MODERATE_LEANS = [(leaning_forward(0.2), MonitorState.FORWARD_LEAN), (leaning_sideways("left", degrees=10), MonitorState.SIDE_LEAN)]


@pytest.mark.parametrize("lean, kind", SMALL_LEANS)
def test_a_small_lean_is_good_posture_at_the_default_medium_and_bad_posture_once_sensitivity_is_high(lean, kind):
    clock = FakeClock()
    monitor = calibrated(clock)
    assert monitor.sensitivity is Sensitivity.MEDIUM

    monitor.observe(lean)
    assert monitor.state is MonitorState.GOOD_POSTURE

    monitor.sensitivity = Sensitivity.HIGH
    monitor.observe(lean)
    assert monitor.state is kind


@pytest.mark.parametrize("lean, kind", MODERATE_LEANS)
def test_a_moderate_lean_is_bad_posture_at_medium_but_good_posture_once_sensitivity_is_low(lean, kind):
    clock = FakeClock()
    monitor = calibrated(clock)

    monitor.observe(lean)
    assert monitor.state is kind

    monitor.sensitivity = Sensitivity.LOW
    monitor.observe(lean)
    assert monitor.state is MonitorState.GOOD_POSTURE


def test_the_chosen_sensitivity_is_remembered_after_a_restart():
    store = Store()
    PostureMonitor(clock=FakeClock(), store=store).sensitivity = Sensitivity.HIGH

    assert PostureMonitor(clock=FakeClock(), store=store).sensitivity is Sensitivity.HIGH


def take_prompts(monitor, clock, observation, seconds):
    """Like sit(), counting the recalibration prompts the Posture Monitor raises meanwhile."""
    prompts = 0
    for _ in range(round(seconds / 0.4)):
        monitor.observe(observation)
        prompts += monitor.take_recalibration_prompt()
        clock.advance(0.4)
    return prompts


moved_back = UserSeen(upright_points(scale=0.6))  # the camera or chair moved: the User looks much smaller
moved_aside = UserSeen(tuple(p._replace(x=p.x + 0.3) for p in upright_points()))  # the camera turned


@pytest.mark.parametrize("view", [moved_back, moved_aside], ids=["smaller", "shifted"])
def test_a_sustained_change_of_camera_view_makes_the_baseline_stale_with_exactly_one_prompt(view):
    clock = FakeClock()
    monitor = calibrated(clock)

    prompts = take_prompts(monitor, clock, view, 120)

    assert monitor.state is MonitorState.STALE_BASELINE
    assert prompts == 1


@pytest.mark.parametrize("lean", [leaning_forward(), leaning_forward(0.6), leaning_sideways("left", 25)], ids=["forward", "far-forward", "sideways"])
def test_a_long_ordinary_lean_is_bad_posture_not_a_stale_baseline(lean):
    clock = FakeClock()
    monitor = calibrated(clock)

    prompts = take_prompts(monitor, clock, lean, 120)

    assert monitor.state in (MonitorState.FORWARD_LEAN, MonitorState.SIDE_LEAN)
    assert monitor.mirror_visible
    assert prompts == 0


def test_a_brief_change_of_view_does_not_make_the_baseline_stale():
    clock = FakeClock()
    monitor = calibrated(clock)

    prompts = take_prompts(monitor, clock, moved_back, 20)
    prompts += take_prompts(monitor, clock, upright(), 1)
    prompts += take_prompts(monitor, clock, moved_back, 20)

    assert monitor.state is MonitorState.GOOD_POSTURE
    assert prompts == 0


def test_a_stale_baseline_hides_the_mirror_and_stops_judging_posture():
    clock = FakeClock()
    monitor = calibrated(clock)
    sit(monitor, clock, leaning_forward(), 6)
    assert monitor.mirror_visible

    sit(monitor, clock, moved_back, 60)
    sit(monitor, clock, leaning_forward(), 30)

    assert monitor.state is MonitorState.STALE_BASELINE
    assert not monitor.mirror_visible


def stale(clock, store=None):
    monitor = PostureMonitor(clock=clock, store=store)
    monitor.begin_calibration()
    sit(monitor, clock, upright(), 6)
    take_prompts(monitor, clock, moved_back, 60)
    return monitor


def test_recalibrating_in_the_new_view_clears_the_stale_baseline_and_resumes_judging():
    clock = FakeClock()
    monitor = stale(clock)

    monitor.begin_calibration()
    prompts = take_prompts(monitor, clock, moved_back, 6)
    assert monitor.state is MonitorState.GOOD_POSTURE

    prompts += take_prompts(monitor, clock, moved_back, 120)
    assert monitor.state is MonitorState.GOOD_POSTURE
    assert prompts == 0
    sit(monitor, clock, UserSeen(upright_points(scale=0.6 * 1.3)), 6)  # leaning toward the moved camera
    assert monitor.state is MonitorState.FORWARD_LEAN
    assert monitor.mirror_visible


def test_a_failed_recalibration_leaves_the_baseline_stale():
    clock = FakeClock()
    monitor = stale(clock)

    monitor.begin_calibration()
    sit(monitor, clock, NoPerson(), 6)
    monitor.observe(moved_back)

    assert monitor.calibration_failed
    assert monitor.state is MonitorState.STALE_BASELINE


def test_a_stale_baseline_stays_stale_after_a_restart_without_a_second_prompt():
    clock = FakeClock()
    store = Store()
    stale(clock, store)

    restarted = PostureMonitor(clock=clock, store=store)
    prompts = take_prompts(restarted, clock, upright(), 10)

    assert restarted.state is MonitorState.STALE_BASELINE
    assert prompts == 0


def test_while_the_baseline_is_stale_frames_are_analysed_about_once_a_second():
    clock = FakeClock()
    monitor = stale(clock)
    monitor.observe(moved_back)

    clock.advance(0.9)
    assert not monitor.analysis_due()
    clock.advance(0.1)
    assert monitor.analysis_due()
