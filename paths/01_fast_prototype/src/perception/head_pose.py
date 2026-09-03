from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import cv2
import numpy as np


Point2D = Tuple[int, int]


@dataclass(frozen=True)
class HeadPoseResult:
    """
    Geometric head-pose estimate.

    Angles are expressed in degrees.
    """

    yaw_degrees: float
    pitch_degrees: float
    roll_degrees: float

    rotation_vector: np.ndarray
    translation_vector: np.ndarray


class HeadPoseEstimator:
    """
    Estimate head orientation from 2D facial landmarks using solvePnP.

    The estimator keeps the previous valid pose and uses it as an
    initial guess for the next frame. This improves temporal continuity
    and reduces sudden jumps between alternative PnP solutions.
    """

    REQUIRED_LANDMARKS = (
        "nose_tip",
        "chin",
        "left_eye_outer",
        "right_eye_outer",
        "mouth_left",
        "mouth_right",
    )

    def __init__(
        self,
        max_angle_jump_degrees: float = 75.0,
    ) -> None:
        """
        Initialize the head-pose estimator.

        Args:
            max_angle_jump_degrees:
                Maximum allowed frame-to-frame change for any Euler
                angle before the new pose is treated as implausible.
        """

        if max_angle_jump_degrees <= 0.0:
            raise ValueError(
                "max_angle_jump_degrees must be positive."
            )

        self._max_angle_jump_degrees = (
            max_angle_jump_degrees
        )

        self._model_points = np.array(
            [
                (0.0, 0.0, 0.0),          # Nose tip
                (0.0, -63.6, -12.5),      # Chin
                (-43.3, 32.7, -26.0),     # Left eye outer
                (43.3, 32.7, -26.0),      # Right eye outer
                (-28.9, -28.9, -24.1),    # Left mouth corner
                (28.9, -28.9, -24.1),     # Right mouth corner
            ],
            dtype=np.float64,
        )

        # Coordinate-system correction.
        #
        # Generic face model:
        # +X right
        # +Y up
        #
        # OpenCV camera:
        # +X right
        # +Y down
        # +Z forward
        #
        # This 180-degree X-axis rotation aligns the neutral model
        # with the camera-facing coordinate convention.
        self._model_to_camera_neutral = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, -1.0, 0.0],
                [0.0, 0.0, -1.0],
            ],
            dtype=np.float64,
        )

        self._previous_rotation_vector: Optional[
            np.ndarray
        ] = None

        self._previous_translation_vector: Optional[
            np.ndarray
        ] = None

        self._previous_result: Optional[
            HeadPoseResult
        ] = None

    def estimate(
        self,
        landmarks: Dict[str, Point2D],
        frame_width: int,
        frame_height: int,
    ) -> Optional[HeadPoseResult]:
        """
        Estimate yaw, pitch, and roll from facial landmarks.
        """

        if not self._has_required_landmarks(landmarks):
            return None

        image_points = np.array(
            [
                landmarks["nose_tip"],
                landmarks["chin"],
                landmarks["left_eye_outer"],
                landmarks["right_eye_outer"],
                landmarks["mouth_left"],
                landmarks["mouth_right"],
            ],
            dtype=np.float64,
        )

        camera_matrix = self._build_camera_matrix(
            frame_width=frame_width,
            frame_height=frame_height,
        )

        distortion_coefficients = np.zeros(
            (4, 1),
            dtype=np.float64,
        )

        (
            success,
            rotation_vector,
            translation_vector,
        ) = self._solve_pose(
            image_points=image_points,
            camera_matrix=camera_matrix,
            distortion_coefficients=(
                distortion_coefficients
            ),
        )

        if not success:
            return self._previous_result

        rotation_matrix, _ = cv2.Rodrigues(
            rotation_vector
        )

        relative_rotation = (
            rotation_matrix
            @ self._model_to_camera_neutral
        )

        pitch, yaw, roll = (
            self._rotation_matrix_to_euler_angles(
                relative_rotation
            )
        )

        candidate_result = HeadPoseResult(
            yaw_degrees=yaw,
            pitch_degrees=pitch,
            roll_degrees=roll,
            rotation_vector=rotation_vector.copy(),
            translation_vector=translation_vector.copy(),
        )

        if not self._is_pose_continuous(
            candidate_result
        ):
            return self._previous_result

        self._previous_rotation_vector = (
            rotation_vector.copy()
        )

        self._previous_translation_vector = (
            translation_vector.copy()
        )

        self._previous_result = candidate_result

        return candidate_result

    def reset(self) -> None:
        """
        Reset temporal head-pose state.
        """

        self._previous_rotation_vector = None
        self._previous_translation_vector = None
        self._previous_result = None

    def _solve_pose(
        self,
        image_points: np.ndarray,
        camera_matrix: np.ndarray,
        distortion_coefficients: np.ndarray,
    ) -> tuple[bool, np.ndarray, np.ndarray]:
        """
        Solve the Perspective-n-Point problem.

        After the first valid pose, the previous rotation and
        translation vectors are used as the initial estimate.
        """

        has_previous_pose = (
            self._previous_rotation_vector is not None
            and self._previous_translation_vector is not None
        )

        if has_previous_pose:
            rotation_guess = (
                self._previous_rotation_vector.copy()
            )

            translation_guess = (
                self._previous_translation_vector.copy()
            )

            return cv2.solvePnP(
                self._model_points,
                image_points,
                camera_matrix,
                distortion_coefficients,
                rotation_guess,
                translation_guess,
                True,
                flags=cv2.SOLVEPNP_ITERATIVE,
            )

        return cv2.solvePnP(
            self._model_points,
            image_points,
            camera_matrix,
            distortion_coefficients,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

    def _is_pose_continuous(
        self,
        candidate: HeadPoseResult,
    ) -> bool:
        """
        Reject implausibly large frame-to-frame angular jumps.

        This does not clamp the angles. It rejects a candidate if its
        orientation changes too abruptly compared with the previously
        accepted pose.
        """

        if self._previous_result is None:
            return True

        yaw_change = self._angular_difference(
            candidate.yaw_degrees,
            self._previous_result.yaw_degrees,
        )

        pitch_change = self._angular_difference(
            candidate.pitch_degrees,
            self._previous_result.pitch_degrees,
        )

        roll_change = self._angular_difference(
            candidate.roll_degrees,
            self._previous_result.roll_degrees,
        )

        return (
            yaw_change <= self._max_angle_jump_degrees
            and pitch_change <= self._max_angle_jump_degrees
            and roll_change <= self._max_angle_jump_degrees
        )

    @staticmethod
    def _angular_difference(
        angle_a: float,
        angle_b: float,
    ) -> float:
        """
        Return the smallest absolute angular difference in degrees.

        Example:
            179 degrees and -179 degrees differ by 2 degrees,
            not 358 degrees.
        """

        difference = (
            angle_a
            - angle_b
            + 180.0
        ) % 360.0 - 180.0

        return abs(difference)

    @staticmethod
    def _rotation_matrix_to_euler_angles(
        rotation_matrix: np.ndarray,
    ) -> tuple[float, float, float]:
        """
        Convert a rotation matrix into pitch, yaw, and roll.

        Returns:
            pitch_degrees,
            yaw_degrees,
            roll_degrees
        """

        sy = np.sqrt(
            rotation_matrix[0, 0] ** 2
            + rotation_matrix[1, 0] ** 2
        )

        singular = sy < 1e-6

        if not singular:
            pitch = np.arctan2(
                rotation_matrix[2, 1],
                rotation_matrix[2, 2],
            )

            yaw = np.arctan2(
                -rotation_matrix[2, 0],
                sy,
            )

            roll = np.arctan2(
                rotation_matrix[1, 0],
                rotation_matrix[0, 0],
            )

        else:
            pitch = np.arctan2(
                -rotation_matrix[1, 2],
                rotation_matrix[1, 1],
            )

            yaw = np.arctan2(
                -rotation_matrix[2, 0],
                sy,
            )

            roll = 0.0

        return (
            float(np.degrees(pitch)),
            float(np.degrees(yaw)),
            float(np.degrees(roll)),
        )

    @staticmethod
    def _build_camera_matrix(
        frame_width: int,
        frame_height: int,
    ) -> np.ndarray:
        """
        Build an approximate pinhole-camera intrinsic matrix.
        """

        focal_length = float(frame_width)

        center_x = frame_width / 2.0
        center_y = frame_height / 2.0

        return np.array(
            [
                [
                    focal_length,
                    0.0,
                    center_x,
                ],
                [
                    0.0,
                    focal_length,
                    center_y,
                ],
                [
                    0.0,
                    0.0,
                    1.0,
                ],
            ],
            dtype=np.float64,
        )

    @classmethod
    def _has_required_landmarks(
        cls,
        landmarks: Dict[str, Point2D],
    ) -> bool:
        """
        Verify that every head-pose landmark is available.
        """

        return all(
            name in landmarks
            for name in cls.REQUIRED_LANDMARKS
        )