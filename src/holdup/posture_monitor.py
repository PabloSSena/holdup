"""The Posture Monitor: pure logic, no Qt, camera or MediaPipe. Time comes from an injected clock."""
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

from holdup.observation import CameraUnavailable, Landmark, NoPerson, Observation, UserSeen
from holdup.posture_classifier import LIMITS, Posture, Sensitivity, classify
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


class MonitorState(Enum):
    UNCALIBRATED = "Uncalibrated"
    CALIBRATING = "Calibrating"
    GOOD_POSTURE = "Good Posture"
    FORWARD_LEAN = "Forward Lean"
    SIDE_LEAN = "Side Lean"
    ABSENT = "Absent"
    CAMERA_UNAVAILABLE = "Camera Unavailable"


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
        if isinstance(observation, CameraUnavailable):
            self.state = MonitorState.CAMERA_UNAVAILABLE
        elif isinstance(observation, NoPerson):
            self.state = MonitorState.ABSENT
        elif self._baseline is None:
            self.state = MonitorState.UNCALIBRATED
        else:
            self.state = MonitorState(classify(self._baseline, observation.landmarks, LIMITS[self._sensitivity]).value)
        bad = self.state in (MonitorState.FORWARD_LEAN, MonitorState.SIDE_LEAN) and not self.paused
        self._bad_since = (self._bad_since or now) if bad else None
        self.mirror_visible = bad and now - self._bad_since >= BAD_POSTURE_DELAY

    def _end_calibration(self, succeeded: bool) -> None:
        if succeeded:
            self._baseline = _average(self._captured)
            self._store.set(BASELINE, self._baseline)
        self.calibration_failed = not succeeded
        self._calibration_started = None
        self._captured = []

    def analysis_due(self) -> bool:
        """Whether the next camera frame should be analysed and passed to observe()."""
        if self._last_observed is None:
            return True
        idle = self.state in (MonitorState.ABSENT, MonitorState.CAMERA_UNAVAILABLE) or self.paused
        interval = IDLE_INTERVAL if idle else WATCHING_INTERVAL
        elapsed = self._clock() - self._last_observed
        return not timedelta(0) <= elapsed < interval


def _average(poses: list[tuple[Landmark, ...]]) -> tuple[Landmark, ...]:
    return tuple(Landmark(*(sum(values) / len(poses) for values in zip(*points))) for points in zip(*poses))


def _steady(poses: list[tuple[Landmark, ...]]) -> bool:
    """Whether the User held still: no captured pose is as far from the first as a Bad Posture would be."""
    first = poses[0]
    return all(classify(first, pose) is classify(pose, first) is Posture.GOOD for pose in poses)
