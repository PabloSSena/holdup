"""Synthetic landmark builders: numbers shaped like MediaPipe's 33-point pose."""
from holdup.observation import Landmark, UserSeen

# A User sitting up straight, roughly centred, head and shoulders filling the upper frame.
_UPRIGHT = {
    0: (0.50, 0.30),  # nose
    2: (0.47, 0.27), 5: (0.53, 0.27),  # eyes
    7: (0.43, 0.29), 8: (0.57, 0.29),  # ears
    9: (0.48, 0.34), 10: (0.52, 0.34),  # mouth
    11: (0.38, 0.50), 12: (0.62, 0.50),  # shoulders
    13: (0.33, 0.70), 14: (0.67, 0.70),  # elbows
    23: (0.42, 0.95), 24: (0.58, 0.95),  # hips
}


def upright_points(scale: float = 1.0) -> tuple[Landmark, ...]:
    """33 landmarks of an upright User; scale < 1 shrinks the body around the frame centre."""
    return tuple(
        Landmark(0.5 + (x - 0.5) * scale, 0.5 + (y - 0.5) * scale, 0.0, 0.99)
        for x, y in (_UPRIGHT.get(i, (0.5, 0.6)) for i in range(33))
    )


def upright() -> UserSeen:
    return UserSeen(upright_points())
