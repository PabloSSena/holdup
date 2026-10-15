"""The Posture Monitor: pure logic, no Qt, camera or MediaPipe. Time comes from an injected clock."""
import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Callable

from holdup.observation import CameraUnavailable, Landmark, NoPerson, Observation, UserSeen
from holdup.posture_classifier import LEFT_SHOULDER, LIMITS, RIGHT_SHOULDER, Posture, Sensitivity, classify
from holdup.store import Store

Clock = Callable[[], datetime]

# Frame pacing (ADR 0002): analyse little to save CPU and battery.
WATCHING_INTERVAL = timedelta(seconds=0.4)
IDLE_INTERVAL = timedelta(seconds=1.0)

BAD_POSTURE_DELAY = timedelta(seconds=5)  # Bad Posture must last this long before the Mirror appears
CALIBRATION_COUNTDOWN = timedelta(seconds=3)
CALIBRATION_CAPTURE = timedelta(seconds=2)

BASELINE = "baseline"  # Store name of the Baseline landmarks
SENSITIVITY = "sensitivity"  # Store name of the User's Sensitivity ("Low", "Medium" or "High")

# Watched Time between two frames goes to the earlier frame's posture; a longer gap (sleep, hibernate) adds nothing.
STATS_MAX_GAP = timedelta(seconds=5)
STALE = "baseline_stale"  # Store name of the Stale flag, so a restart does not judge against a Stale Baseline

# Stale Baseline detection: every tuning number lives here. Guesses on synthetic poses, like the Sensitivity limits.
STALE_AFTER = timedelta(seconds=30)  # the camera view must stay changed this long
STALE_SCALE = (0.7, 1.8)  # shoulder width outside this share of the Baseline width; Forward Lean only grows it a little
STALE_SHIFT = 0.25  # shoulder midpoint moved this far, in frame widths/heights; a strong Side Lean moves it ~0.12


class MonitorState(Enum):
    UNCALIBRATED = "Uncalibrated"
    CALIBRATING = "Calibrating"
    GOOD_POSTURE = "Good Posture"
    FORWARD_LEAN = "Forward Lean"
    SIDE_LEAN = "Side Lean"
    ABSENT = "Absent"
    CAMERA_UNAVAILABLE = "Camera Unavailable"
    STALE_BASELINE = "Stale Baseline"


# The judging states, by Daily Stats column. Any other state (Absent, Stale, ...) is not Watched Time.
_STATS_COLUMN = {
    MonitorState.GOOD_POSTURE: "good_posture",
    MonitorState.FORWARD_LEAN: "forward_lean",
    MonitorState.SIDE_LEAN: "side_lean",
}


@dataclass(frozen=True)
class DailyStats:
    """One local day: seconds of Watched Time per kind of posture, and how many times the Mirror appeared."""

    good_posture: float = 0.0
    forward_lean: float = 0.0
    side_lean: float = 0.0
    mirror_count: int = 0

    @property
    def watched_time(self) -> float:
        return self.good_posture + self.forward_lean + self.side_lean


class PostureMonitor:
    def __init__(self, clock: Clock, store: Store | None = None):
        self._clock = clock
        self._store = store or Store()  # in memory: nothing outlives the monitor
        self.state = MonitorState.ABSENT
        self._last_observed: datetime | None = None
        self.mirror_visible = False
        self.calibration_failed = False
        stored = self._store.get(BASELINE)
        self._baseline: tuple[Landmark, ...] | None = stored and tuple(Landmark(*point) for point in stored)
        self._calibration_started: datetime | None = None
        self._captured: list[tuple[Landmark, ...]] = []
        self._bad_since: datetime | None = None
        self._paused_until: datetime | None = None
        saved = self._store.get(SENSITIVITY)
        self._sensitivity = Sensitivity(saved) if saved in {s.value for s in Sensitivity} else Sensitivity.MEDIUM
        self._judged_as: str | None = None  # Daily Stats column of the last frame, None when it was not judged
        self._stale: bool = self._store.get(STALE, False)
        self._view_changed_since: datetime | None = None
        self._prompt = False

    def pause(self, duration: timedelta | None = None) -> None:
        """Pause watching for a duration, or until resume() when None. Hides the Mirror at once."""
        self._paused_until = self._clock() + duration if duration else datetime.max
        self.mirror_visible = False
        self._bad_since = None

    def resume(self) -> None:
        self._paused_until = None

    @property
    def paused(self) -> bool:
        return self._paused_until is not None and self._clock() < self._paused_until

    def begin_calibration(self) -> None:
        self._calibration_started = self._clock()
        self._captured = []
        self.calibration_failed = False
        self.state = MonitorState.CALIBRATING
        self.mirror_visible = False
        self._bad_since = None
        self._view_changed_since = None

    def take_recalibration_prompt(self) -> bool:
        """True once per Stale Baseline episode: the moment to ask the User to recalibrate."""
        prompt, self._prompt = self._prompt, False
        return prompt

    def _make_stale(self) -> None:
        self._stale = True
        self._store.set(STALE, True)
        self._prompt = True
        self.mirror_visible = False
        self._bad_since = None

    @property
    def sensitivity(self) -> Sensitivity:
        return self._sensitivity

    @sensitivity.setter
    def sensitivity(self, sensitivity: Sensitivity) -> None:
        self._sensitivity = sensitivity
        self._store.set(SENSITIVITY, sensitivity.value)

    @property
    def calibrated(self) -> bool:
        """Whether a Baseline exists, from this run or remembered in the Store."""
        return self._baseline is not None

    def calibration_countdown(self) -> float:
        """Seconds left before the Baseline capture starts (0 while capturing or not calibrating)."""
        if self._calibration_started is None:
            return 0.0
        left = self._calibration_started + CALIBRATION_COUNTDOWN - self._clock()
        return max(left.total_seconds(), 0.0)

    def observe(self, observation: Observation) -> None:
        previous = self._last_observed
        now = self._last_observed = self._clock()
        if self._judged_as and timedelta(0) < now - previous <= STATS_MAX_GAP:
            self._add_watched_time(previous, now, self._judged_as)
        self._judged_as = None
        if self._calibration_started is not None and isinstance(observation, CameraUnavailable):
            self._end_calibration(succeeded=False)  # without frames the countdown would never end
        if self._calibration_started is not None:
            capture_from = self._calibration_started + CALIBRATION_COUNTDOWN
            if now < capture_from:
                return
            capturing = now < capture_from + CALIBRATION_CAPTURE
            if capturing and isinstance(observation, UserSeen):
                self._captured.append(observation.landmarks)
                return
            self._end_calibration(succeeded=not capturing and bool(self._captured) and _steady(self._captured))
        changed = isinstance(observation, UserSeen) and self._baseline is not None and not self._stale and _view_changed(self._baseline, observation.landmarks)
        self._view_changed_since = (self._view_changed_since or now) if changed else None
        if changed and now - self._view_changed_since >= STALE_AFTER:
            self._make_stale()
        if self._stale:
            self.state = MonitorState.STALE_BASELINE
        elif isinstance(observation, CameraUnavailable):
            self.state = MonitorState.CAMERA_UNAVAILABLE
        elif isinstance(observation, NoPerson):
            self.state = MonitorState.ABSENT
        elif self._baseline is None:
            self.state = MonitorState.UNCALIBRATED
        else:
            self.state = MonitorState(classify(self._baseline, observation.landmarks, LIMITS[self._sensitivity]).value)
        bad = self.state in (MonitorState.FORWARD_LEAN, MonitorState.SIDE_LEAN) and not self.paused
        self._bad_since = (self._bad_since or now) if bad else None
        was_visible = self.mirror_visible
        self.mirror_visible = bad and now - self._bad_since >= BAD_POSTURE_DELAY
        if self.mirror_visible and not was_visible:
            self._store.add_daily_stats(now.date(), "mirror_count", 1)
        self._judged_as = None if self.paused else _STATS_COLUMN.get(self.state)

    def _add_watched_time(self, start: datetime, end: datetime, column: str) -> None:
        """Add start..end to the Daily Stats, split at each local midnight."""
        # shortcut: one SQLite commit per judged frame (~2.5/s); batch in memory if disk wake-ups show in battery use.
        while start.date() < end.date():
            midnight = datetime.combine(start.date() + timedelta(days=1), time())
            self._store.add_daily_stats(start.date(), column, (midnight - start).total_seconds())
            start = midnight
        self._store.add_daily_stats(end.date(), column, (end - start).total_seconds())

    def daily_stats(self, first: date, last: date) -> dict[date, DailyStats]:
        """Daily Stats of each local day from first to last (inclusive); days without Watched Time are left out."""
        return {day: DailyStats(*values) for day, values in self._store.daily_stats(first, last).items()}

    def today_stats(self) -> DailyStats:
        today = self._clock().date()
        return self.daily_stats(today, today).get(today, DailyStats())

    def clear_stats(self) -> None:
        """Clear statistics: all Daily Stats go; the Baseline and settings stay."""
        self._store.clear_daily_stats()

    def _end_calibration(self, succeeded: bool) -> None:
        if succeeded:
            self._baseline = _average(self._captured)
            self._store.set(BASELINE, self._baseline)
            if self._stale:
                self._stale = False
                self._store.set(STALE, False)
        self.calibration_failed = not succeeded
        self._calibration_started = None
        self._captured = []

    def analysis_due(self) -> bool:
        """Whether the next camera frame should be analysed and passed to observe()."""
        if self._last_observed is None:
            return True
        idle = self.state in (MonitorState.ABSENT, MonitorState.CAMERA_UNAVAILABLE, MonitorState.STALE_BASELINE) or self.paused
        interval = IDLE_INTERVAL if idle else WATCHING_INTERVAL
        elapsed = self._clock() - self._last_observed
        return not timedelta(0) <= elapsed < interval


def _view_changed(baseline: tuple[Landmark, ...], landmarks: tuple[Landmark, ...]) -> bool:
    """Whether the User's overall scale or position in the frame is further from the Baseline than any lean explains."""
    (base_width, base_x, base_y), (width, x, y) = _shoulders(baseline), _shoulders(landmarks)
    low, high = STALE_SCALE
    return not low <= width / max(base_width, 1e-6) <= high or max(abs(x - base_x), abs(y - base_y)) > STALE_SHIFT


def _shoulders(landmarks: tuple[Landmark, ...]) -> tuple[float, float, float]:
    left, right = landmarks[LEFT_SHOULDER], landmarks[RIGHT_SHOULDER]
    return math.dist((left.x, left.y), (right.x, right.y)), (left.x + right.x) / 2, (left.y + right.y) / 2


def _average(poses: list[tuple[Landmark, ...]]) -> tuple[Landmark, ...]:
    return tuple(Landmark(*(sum(values) / len(poses) for values in zip(*points))) for points in zip(*poses))


def _steady(poses: list[tuple[Landmark, ...]]) -> bool:
    """Whether the User held still: no captured pose is as far from the first as a Bad Posture would be."""
    first = poses[0]
    return all(classify(first, pose) is classify(pose, first) is Posture.GOOD for pose in poses)
