"""The Posture Monitor: pure logic, no Qt, camera or MediaPipe. Time comes from an injected clock."""
import math
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

from holdup.observation import CameraUnavailable, Landmark, NoPerson, Observation, UserSeen
from holdup.posture_classifier import LEFT_SHOULDER, RIGHT_SHOULDER, Posture, classify
from holdup.store import Store

Clock = Callable[[], datetime]

# Frame pacing (ADR 0002): analyse little to save CPU and battery.
WATCHING_INTERVAL = timedelta(seconds=0.4)
IDLE_INTERVAL = timedelta(seconds=1.0)

BAD_POSTURE_DELAY = timedelta(seconds=5)  # Bad Posture must last this long before the Mirror appears
CALIBRATION_COUNTDOWN = timedelta(seconds=3)
CALIBRATION_CAPTURE = timedelta(seconds=2)

BASELINE = "baseline"  # Store name of the Baseline landmarks
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
        self._stale: bool = self._store.get(STALE, False)
        self._view_changed_since: datetime | None = None
        self._prompt = False

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
        now = self._last_observed = self._clock()
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
        changed = isinstance(observation, UserSeen) and self._baseline is not None and not self._stale             and _view_changed(self._baseline, observation.landmarks)
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
            self.state = MonitorState(classify(self._baseline, observation.landmarks).value)
        bad = self.state in (MonitorState.FORWARD_LEAN, MonitorState.SIDE_LEAN)
        self._bad_since = (self._bad_since or now) if bad else None
        self.mirror_visible = bad and now - self._bad_since >= BAD_POSTURE_DELAY

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
        idle = self.state in (MonitorState.ABSENT, MonitorState.CAMERA_UNAVAILABLE, MonitorState.STALE_BASELINE)
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
