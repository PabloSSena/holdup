"""Posture Classifier: judges the User's landmarks against their Baseline. Internal to the Posture Monitor."""
import math
from enum import Enum
from typing import NamedTuple

from holdup.observation import Landmark

NOSE, LEFT_EYE, RIGHT_EYE, LEFT_SHOULDER, RIGHT_SHOULDER = 0, 2, 5, 11, 12


class Posture(Enum):
    GOOD = "Good Posture"
    FORWARD_LEAN = "Forward Lean"
    SIDE_LEAN = "Side Lean"


class Sensitivity(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Limits(NamedTuple):
    """How far from the Baseline the User may sit before it counts as Bad Posture."""
    closer: float  # growth of the shoulder width (toward the camera), as a share of the Baseline width
    head_drop: float  # sinking of the nose toward the shoulder line, in shoulder widths
    tilt: float  # turn of the shoulder line or of the eye line (head tilt), in degrees


# Every tuning number lives here. Tuned by eye on synthetic poses; expect a hands-on tuning pass.
LOW = Limits(closer=0.25, head_drop=0.25, tilt=13)
MEDIUM = Limits(closer=0.15, head_drop=0.15, tilt=8)
HIGH = Limits(closer=0.08, head_drop=0.08, tilt=5)
LIMITS = {Sensitivity.LOW: LOW, Sensitivity.MEDIUM: MEDIUM, Sensitivity.HIGH: HIGH}


def classify(baseline: tuple[Landmark, ...], landmarks: tuple[Landmark, ...], limits: Limits = MEDIUM) -> Posture:
    """Good Posture, Forward Lean or Side Lean; when both leans apply, Forward Lean wins."""
    base_width, base_head = _shoulder_width_and_head_height(baseline)
    width, head = _shoulder_width_and_head_height(landmarks)
    if width > base_width * (1 + limits.closer) or head < base_head - limits.head_drop:
        return Posture.FORWARD_LEAN
    turns = (_turn(baseline, landmarks, LEFT_SHOULDER, RIGHT_SHOULDER), _turn(baseline, landmarks, LEFT_EYE, RIGHT_EYE))
    if max(turns) > limits.tilt:
        return Posture.SIDE_LEAN
    return Posture.GOOD


def _shoulder_width_and_head_height(landmarks: tuple[Landmark, ...]) -> tuple[float, float]:
    left, right, nose = landmarks[LEFT_SHOULDER], landmarks[RIGHT_SHOULDER], landmarks[NOSE]
    width = math.dist((left.x, left.y), (right.x, right.y))
    # Height of the nose above the shoulder line, in shoulder widths, so it does not change with distance.
    return width, ((left.y + right.y) / 2 - nose.y) / max(width, 1e-6)


def _turn(baseline: tuple[Landmark, ...], landmarks: tuple[Landmark, ...], a: int, b: int) -> float:
    """Degrees the line from landmark a to b has turned since the Baseline, either way."""
    bx, by = baseline[b].x - baseline[a].x, baseline[b].y - baseline[a].y
    x, y = landmarks[b].x - landmarks[a].x, landmarks[b].y - landmarks[a].y
    # Angle between the two lines from cross and dot products, so it never wraps at +-180 degrees.
    return abs(math.degrees(math.atan2(bx * y - by * x, bx * x + by * y)))
