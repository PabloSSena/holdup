"""Observations: what the Posture Monitor learns from one analysed frame."""
from dataclasses import dataclass
from typing import NamedTuple


class Landmark(NamedTuple):
    """One body landmark in normalised image coordinates (MediaPipe's 33-point layout)."""
    x: float
    y: float
    z: float
    visibility: float


@dataclass(frozen=True)
class UserSeen:
    """The User (the person closest to the camera) was seen with these landmarks."""
    landmarks: tuple[Landmark, ...]


@dataclass(frozen=True)
class NoPerson:
    """Nobody was seen in the frame."""


@dataclass(frozen=True)
class CameraUnavailable:
    """The camera could not be read (unplugged, shutter closed, held by another app): the app cannot see."""


Observation = UserSeen | NoPerson | CameraUnavailable


def observation_from(people: list[tuple[Landmark, ...]]) -> Observation:
    """Turn every person detected in a frame into an Observation of the User: the largest one in frame."""
    if not people:
        return NoPerson()
    return UserSeen(max(people, key=_area_in_frame))


def _area_in_frame(landmarks: tuple[Landmark, ...]) -> float:
    # MediaPipe extrapolates off-screen landmarks, so clamp to the frame before measuring.
    xs = [min(max(p.x, 0.0), 1.0) for p in landmarks]
    ys = [min(max(p.y, 0.0), 1.0) for p in landmarks]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))
