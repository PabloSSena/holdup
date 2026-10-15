"""Pose Detector: wraps MediaPipe and turns a frame into an Observation. Frames are never kept."""
from pathlib import Path

import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

from holdup.observation import Landmark, Observation, observation_from

MODEL = Path(__file__).parent / "models" / "pose_landmarker_lite.task"
MAX_PEOPLE = 3  # enough to find the User among a few passers-by


class PoseDetector:
    def __init__(self):
        options = vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_buffer=MODEL.read_bytes()),
            num_poses=MAX_PEOPLE,
        )
        self._landmarker = vision.PoseLandmarker.create_from_options(options)

    def detect(self, rgb_frame: np.ndarray) -> Observation:
        result = self._landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame))
        return observation_from([
            tuple(Landmark(p.x, p.y, p.z, p.visibility or 0.0) for p in pose)
            for pose in result.pose_landmarks
        ])

    def close(self) -> None:
        self._landmarker.close()
