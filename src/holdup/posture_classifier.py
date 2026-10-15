"""Posture Classifier: judges the User's landmarks against their Baseline. Internal to the Posture Monitor."""
import math
from typing import NamedTuple

from holdup.observation import Landmark

NOSE, LEFT_SHOULDER, RIGHT_SHOULDER = 0, 11, 12


class Limits(NamedTuple):
    """How far from the Baseline the User may sit before it counts as Bad Posture."""
    closer: float  # growth of the shoulder width (toward the camera), as a share of the Baseline width
    head_drop: float  # sinking of the nose toward the shoulder line, in shoulder widths


# Every tuning number lives here. Tuned by eye on synthetic poses; expect a hands-on tuning pass (issue 05 adds Low/High).
MEDIUM = Limits(closer=0.15, head_drop=0.15)


def leans_forward(baseline: tuple[Landmark, ...], landmarks: tuple[Landmark, ...], limits: Limits = MEDIUM) -> bool:
    base_width, base_head = _shoulder_width_and_head_height(baseline)
    width, head = _shoulder_width_and_head_height(landmarks)
    return width > base_width * (1 + limits.closer) or head < base_head - limits.head_drop


def _shoulder_width_and_head_height(landmarks: tuple[Landmark, ...]) -> tuple[float, float]:
    left, right, nose = landmarks[LEFT_SHOULDER], landmarks[RIGHT_SHOULDER], landmarks[NOSE]
    width = math.dist((left.x, left.y), (right.x, right.y))
    # Height of the nose above the shoulder line, in shoulder widths, so it does not change with distance.
    return width, ((left.y + right.y) / 2 - nose.y) / max(width, 1e-6)
