"""The Posture Monitor: pure logic, no Qt, camera or MediaPipe. Time comes from an injected clock."""
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

from holdup.observation import NoPerson, Observation

Clock = Callable[[], datetime]

# Frame pacing (ADR 0002): analyse little to save CPU and battery.
WATCHING_INTERVAL = timedelta(seconds=0.4)
IDLE_INTERVAL = timedelta(seconds=1.0)


class MonitorState(Enum):
    UNCALIBRATED = "Uncalibrated"
    ABSENT = "Absent"


class PostureMonitor:
    def __init__(self, clock: Clock):
        self._clock = clock
        self.state = MonitorState.ABSENT
        self._last_observed: datetime | None = None

    def observe(self, observation: Observation) -> None:
        self._last_observed = self._clock()
        self.state = MonitorState.ABSENT if isinstance(observation, NoPerson) else MonitorState.UNCALIBRATED

    def analysis_due(self) -> bool:
        """Whether the next camera frame should be analysed and passed to observe()."""
        if self._last_observed is None:
            return True
        interval = IDLE_INTERVAL if self.state is MonitorState.ABSENT else WATCHING_INTERVAL
        elapsed = self._clock() - self._last_observed
        return not timedelta(0) <= elapsed < interval
