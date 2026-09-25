from dataclasses import dataclass
from enum import Enum
import math
from statistics import median
from typing import Dict, Optional, Tuple


Point2D = Tuple[int, int]
Point2DFloat = Tuple[float, float]


SELECTED_BODY_LANDMARKS = {
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_hip": 23,
    "right_hip": 24,
}


@dataclass(frozen=True)
class BodyLandmark:
    pixel: Point2D

    normalized_x: float
    normalized_y: float
    normalized_z: float

    visibility: float


@dataclass(frozen=True)
class BodyPoseResult:
    landmarks: Dict[str, BodyLandmark]

    pose_detected: bool

    all_required_landmarks_visible: bool


@dataclass(frozen=True)
class BodyGeometryResult:
    shoulder_midpoint: Point2DFloat
    hip_midpoint: Point2DFloat

    shoulder_angle_degrees: float
    hip_angle_degrees: float

    torso_lateral_angle_degrees: float

    shoulder_depth: float
    hip_depth: float
    torso_depth_delta: float

    shoulder_width_pixels: float
    hip_width_pixels: float
    torso_length_pixels: float

    normalized_torso_length: float

    geometry_valid: bool


class LateralPostureState(Enum):
    """
    Prototype lateral posture state.
    """

    UPRIGHT = "UPRIGHT"
    LEAN_LEFT = "LEAN_LEFT"
    LEAN_RIGHT = "LEAN_RIGHT"
    UNKNOWN = "UNKNOWN"


class SagittalPostureState(Enum):
    """
    Prototype sagittal posture state.

    Current implementation detects only forward lean.
    Backward/reclined posture is not yet classified.
    """
    NOT_CALIBRATED = "NOT_CALIBRATED"
    CALIBRATING = "CALIBRATING"
    NEUTRAL = "NEUTRAL"
    FORWARD_LEAN = "FORWARD_LEAN"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class BodyPostureResult:
    """
    Two-axis prototype posture interpretation.

    lateral_state:
        UPRIGHT / LEAN_LEFT / LEAN_RIGHT / UNKNOWN

    sagittal_state:
        NOT_CALIBRATED / CALIBRATING / NEUTRAL / FORWARD_LEAN / UNKNOWN

    Both outputs remain geometric prototype states.
    They are not behavioral or safety classifications.
    """

    lateral_state: LateralPostureState
    sagittal_state: SagittalPostureState

    torso_lateral_angle_degrees: float
    torso_depth_delta: float
    neutral_torso_depth_delta: Optional[float]
    torso_depth_change: Optional[float]

    geometry_valid: bool


class BodyPoseDetector:
    """
    MediaPipe Pose wrapper for selected shoulders and hips.
    """

    def __init__(
        self,
        static_image_mode: bool = False,
        model_complexity: int = 1,
        smooth_landmarks: bool = True,
        enable_segmentation: bool = False,
        smooth_segmentation: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        minimum_landmark_visibility: float = 0.5,
    ) -> None:

        if model_complexity not in (0, 1, 2):
            raise ValueError(
                "model_complexity must be 0, 1, or 2."
            )

        if not 0.0 <= min_detection_confidence <= 1.0:
            raise ValueError(
                "min_detection_confidence must be between 0 and 1."
            )

        if not 0.0 <= min_tracking_confidence <= 1.0:
            raise ValueError(
                "min_tracking_confidence must be between 0 and 1."
            )

        if not 0.0 <= minimum_landmark_visibility <= 1.0:
            raise ValueError(
                "minimum_landmark_visibility must be between 0 and 1."
            )

        self._minimum_landmark_visibility = (
            minimum_landmark_visibility
        )

        # Load native inference dependencies only when a detector is created.
        # Geometry/calibration unit tests need neither MediaPipe nor OpenCV.
        import mediapipe as mp

        self._mp_pose = mp.solutions.pose

        self._pose = self._mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            enable_segmentation=enable_segmentation,
            smooth_segmentation=smooth_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def detect(
        self,
        frame,
    ) -> Optional[BodyPoseResult]:

        if frame is None:
            return None

        if frame.size == 0:
            return None

        frame_height, frame_width = frame.shape[:2]

        if frame_width <= 0 or frame_height <= 0:
            return None

        import cv2

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        results = self._pose.process(
            rgb_frame
        )

        if results.pose_landmarks is None:
            return None

        pose_landmarks = (
            results.pose_landmarks.landmark
        )

        selected_landmarks: Dict[str, BodyLandmark] = {}

        all_required_landmarks_visible = True

        for (
            landmark_name,
            landmark_index,
        ) in SELECTED_BODY_LANDMARKS.items():

            landmark = pose_landmarks[
                landmark_index
            ]

            pixel_x = int(
                round(
                    landmark.x
                    * frame_width
                )
            )

            pixel_y = int(
                round(
                    landmark.y
                    * frame_height
                )
            )

            pixel_x = max(
                0,
                min(
                    pixel_x,
                    frame_width - 1,
                ),
            )

            pixel_y = max(
                0,
                min(
                    pixel_y,
                    frame_height - 1,
                ),
            )

            visibility = float(
                landmark.visibility
            )

            selected_landmarks[
                landmark_name
            ] = BodyLandmark(
                pixel=(
                    pixel_x,
                    pixel_y,
                ),
                normalized_x=float(
                    landmark.x
                ),
                normalized_y=float(
                    landmark.y
                ),
                normalized_z=float(
                    landmark.z
                ),
                visibility=visibility,
            )

            if (
                visibility
                < self._minimum_landmark_visibility
            ):
                all_required_landmarks_visible = False

        return BodyPoseResult(
            landmarks=selected_landmarks,
            pose_detected=True,
            all_required_landmarks_visible=(
                all_required_landmarks_visible
            ),
        )

    def detect_selected_landmarks(
        self,
        frame,
    ) -> Optional[Dict[str, Point2D]]:

        result = self.detect(
            frame
        )

        if result is None:
            return None

        return {
            name: landmark.pixel
            for name, landmark
            in result.landmarks.items()
        }

    def close(
        self,
    ) -> None:

        self._pose.close()

    def __enter__(
        self,
    ):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        self.close()


class BodyGeometryExtractor:
    """
    Extract continuous upper-body geometry.
    """

    REQUIRED_LANDMARKS = (
        "left_shoulder",
        "right_shoulder",
        "left_hip",
        "right_hip",
    )

    def __init__(
        self,
        minimum_shoulder_width_pixels: float = 10.0,
        minimum_torso_length_pixels: float = 10.0,
    ) -> None:

        if minimum_shoulder_width_pixels <= 0.0:
            raise ValueError(
                "minimum_shoulder_width_pixels must be positive."
            )

        if minimum_torso_length_pixels <= 0.0:
            raise ValueError(
                "minimum_torso_length_pixels must be positive."
            )

        self._minimum_shoulder_width_pixels = (
            minimum_shoulder_width_pixels
        )

        self._minimum_torso_length_pixels = (
            minimum_torso_length_pixels
        )

    def compute_features(
        self,
        body_pose: Optional[BodyPoseResult],
    ) -> Optional[BodyGeometryResult]:

        if body_pose is None:
            return None

        if not self._has_required_landmarks(
            body_pose.landmarks
        ):
            return None

        left_shoulder_landmark = body_pose.landmarks[
            "left_shoulder"
        ]

        right_shoulder_landmark = body_pose.landmarks[
            "right_shoulder"
        ]

        left_hip_landmark = body_pose.landmarks[
            "left_hip"
        ]

        right_hip_landmark = body_pose.landmarks[
            "right_hip"
        ]

        left_shoulder = left_shoulder_landmark.pixel
        right_shoulder = right_shoulder_landmark.pixel

        left_hip = left_hip_landmark.pixel
        right_hip = right_hip_landmark.pixel

        shoulder_midpoint = self._midpoint(
            left_shoulder,
            right_shoulder,
        )

        hip_midpoint = self._midpoint(
            left_hip,
            right_hip,
        )

        shoulder_width = self._distance(
            left_shoulder,
            right_shoulder,
        )

        hip_width = self._distance(
            left_hip,
            right_hip,
        )

        torso_length = self._distance_float(
            shoulder_midpoint,
            hip_midpoint,
        )

        shoulder_angle = self._line_angle_degrees(
            start=right_shoulder,
            end=left_shoulder,
        )

        hip_angle = self._line_angle_degrees(
            start=right_hip,
            end=left_hip,
        )

        torso_lateral_angle = (
            self._torso_lateral_angle_degrees(
                shoulder_midpoint=shoulder_midpoint,
                hip_midpoint=hip_midpoint,
            )
        )

        shoulder_depth = (
            left_shoulder_landmark.normalized_z
            + right_shoulder_landmark.normalized_z
        ) / 2.0

        hip_depth = (
            left_hip_landmark.normalized_z
            + right_hip_landmark.normalized_z
        ) / 2.0

        torso_depth_delta = (
            shoulder_depth
            - hip_depth
        )

        if (
            shoulder_width
            >= self._minimum_shoulder_width_pixels
        ):
            normalized_torso_length = (
                torso_length
                / shoulder_width
            )
        else:
            normalized_torso_length = 0.0

        geometry_valid = (
            body_pose.all_required_landmarks_visible
            and shoulder_width
            >= self._minimum_shoulder_width_pixels
            and torso_length
            >= self._minimum_torso_length_pixels
        )

        return BodyGeometryResult(
            shoulder_midpoint=shoulder_midpoint,
            hip_midpoint=hip_midpoint,
            shoulder_angle_degrees=shoulder_angle,
            hip_angle_degrees=hip_angle,
            torso_lateral_angle_degrees=(
                torso_lateral_angle
            ),
            shoulder_depth=shoulder_depth,
            hip_depth=hip_depth,
            torso_depth_delta=torso_depth_delta,
            shoulder_width_pixels=shoulder_width,
            hip_width_pixels=hip_width,
            torso_length_pixels=torso_length,
            normalized_torso_length=(
                normalized_torso_length
            ),
            geometry_valid=geometry_valid,
        )

    @staticmethod
    def _midpoint(
        point_a: Point2D,
        point_b: Point2D,
    ) -> Point2DFloat:

        return (
            (
                point_a[0]
                + point_b[0]
            )
            / 2.0,
            (
                point_a[1]
                + point_b[1]
            )
            / 2.0,
        )

    @staticmethod
    def _distance(
        point_a: Point2D,
        point_b: Point2D,
    ) -> float:

        return math.hypot(
            point_b[0] - point_a[0],
            point_b[1] - point_a[1],
        )

    @staticmethod
    def _distance_float(
        point_a: Point2DFloat,
        point_b: Point2DFloat,
    ) -> float:

        return math.hypot(
            point_b[0] - point_a[0],
            point_b[1] - point_a[1],
        )

    @staticmethod
    def _line_angle_degrees(
        start: Point2D,
        end: Point2D,
    ) -> float:

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        return math.degrees(
            math.atan2(
                dy,
                dx,
            )
        )

    @staticmethod
    def _torso_lateral_angle_degrees(
        shoulder_midpoint: Point2DFloat,
        hip_midpoint: Point2DFloat,
    ) -> float:

        dx = (
            shoulder_midpoint[0]
            - hip_midpoint[0]
        )

        upward_distance = (
            hip_midpoint[1]
            - shoulder_midpoint[1]
        )

        return math.degrees(
            math.atan2(
                dx,
                upward_distance,
            )
        )

    @classmethod
    def _has_required_landmarks(
        cls,
        landmarks: Dict[str, BodyLandmark],
    ) -> bool:

        return all(
            name in landmarks
            for name in cls.REQUIRED_LANDMARKS
        )


class BodyPostureEstimator:
    """Two-axis experimental posture estimator with neutral median calibration.

    C begins collection of 30 valid *successive observed* neutral frames.
    Invalid/non-neutral frames are skipped, not included. The completed sample
    window is rejected if its dZ range is above the configurable stability
    tolerance. All values and thresholds are prototype parameters, not metric
    distances or safety decisions.
    """

    def __init__(
        self,
        lateral_lean_threshold_degrees: float = 6.0,
        forward_lean_relative_depth_threshold: float = -0.08,
        calibration_target_frames: int = 30,
        calibration_max_attempts: int = 150,
        calibration_max_depth_spread: float = 0.12,
    ) -> None:
        if not math.isfinite(lateral_lean_threshold_degrees) or lateral_lean_threshold_degrees <= 0:
            raise ValueError("lateral_lean_threshold_degrees must be finite and positive")
        if not math.isfinite(forward_lean_relative_depth_threshold) or forward_lean_relative_depth_threshold >= 0:
            raise ValueError("forward_lean_relative_depth_threshold must be finite and negative")
        if calibration_target_frames < 2:
            raise ValueError("calibration_target_frames must be >= 2")
        if calibration_max_attempts < calibration_target_frames:
            raise ValueError("calibration_max_attempts must be >= calibration_target_frames")
        if not math.isfinite(calibration_max_depth_spread) or calibration_max_depth_spread <= 0:
            raise ValueError("calibration_max_depth_spread must be finite and positive")

        self._lateral_lean_threshold_degrees = lateral_lean_threshold_degrees
        self._forward_lean_relative_depth_threshold = forward_lean_relative_depth_threshold
        self._calibration_target_frames = calibration_target_frames
        self._calibration_max_attempts = calibration_max_attempts
        self._calibration_max_depth_spread = calibration_max_depth_spread
        self._neutral_torso_depth_delta: Optional[float] = None
        self._calibrating = False
        self._calibration_samples: list[float] = []
        self._calibration_attempts = 0
        self._calibration_message = "Press C while seated neutral."
        self._last_calibration_spread: Optional[float] = None

    @property
    def is_calibrated(self) -> bool:
        return self._neutral_torso_depth_delta is not None

    @property
    def is_calibrating(self) -> bool:
        return self._calibrating

    @property
    def neutral_torso_depth_delta(self) -> Optional[float]:
        return self._neutral_torso_depth_delta

    @property
    def calibration_progress(self) -> tuple[int, int]:
        return len(self._calibration_samples), self._calibration_target_frames

    @property
    def calibration_message(self) -> str:
        return self._calibration_message

    @property
    def last_calibration_spread(self) -> Optional[float]:
        return self._last_calibration_spread

    def begin_calibration(self) -> None:
        """Start or restart one automatic 30-valid-frame calibration run."""
        self._neutral_torso_depth_delta = None
        self._calibration_samples.clear()
        self._calibration_attempts = 0
        self._last_calibration_spread = None
        self._calibrating = True
        self._calibration_message = "Collecting neutral frames: sit still and face the camera."

    def update_calibration(self, geometry: Optional[BodyGeometryResult]) -> bool:
        """Feed exactly one *new* frame. Return True only upon completion.

        This method is deliberately separate from estimate(): a caller must
        explicitly feed each acquired frame, avoiding accidental repeated
        sampling of a paused frame or repeated estimate() calls.
        """
        if not self._calibrating:
            return False

        self._calibration_attempts += 1
        if (
            geometry is not None
            and geometry.geometry_valid
            and math.isfinite(geometry.torso_depth_delta)
            and math.isfinite(geometry.torso_lateral_angle_degrees)
            and abs(geometry.torso_lateral_angle_degrees) <= self._lateral_lean_threshold_degrees
        ):
            self._calibration_samples.append(geometry.torso_depth_delta)
            self._calibration_message = "Collecting neutral frames: keep still."
        else:
            self._calibration_message = "Skipped frame: pose invalid or leaning sideways."

        if len(self._calibration_samples) >= self._calibration_target_frames:
            samples = self._calibration_samples
            spread = max(samples) - min(samples)
            self._last_calibration_spread = spread
            self._calibrating = False
            if spread > self._calibration_max_depth_spread:
                self._calibration_message = (
                    f"Calibration rejected: depth range {spread:.4f} > "
                    f"{self._calibration_max_depth_spread:.4f}. Press C and stay still."
                )
                self._calibration_samples.clear()
                return False
            self._neutral_torso_depth_delta = float(median(samples))
            self._calibration_message = (
                f"Calibrated from {len(samples)} valid frames "
                f"(range {spread:.4f})."
            )
            return True

        if self._calibration_attempts >= self._calibration_max_attempts:
            self._calibrating = False
            self._calibration_samples.clear()
            self._calibration_message = (
                "Calibration timed out: insufficient valid neutral frames. "
                "Check visibility and press C again."
            )
        return False

    def reset_calibration(self) -> None:
        self._neutral_torso_depth_delta = None
        self._calibrating = False
        self._calibration_samples.clear()
        self._calibration_attempts = 0
        self._last_calibration_spread = None
        self._calibration_message = "Calibration reset. Sit neutral and press C."

    def estimate(self, geometry: Optional[BodyGeometryResult]) -> BodyPostureResult:
        baseline = self._neutral_torso_depth_delta
        if geometry is None or not geometry.geometry_valid or not (
            math.isfinite(geometry.torso_lateral_angle_degrees)
            and math.isfinite(geometry.torso_depth_delta)
        ):
            return BodyPostureResult(
                lateral_state=LateralPostureState.UNKNOWN,
                sagittal_state=SagittalPostureState.UNKNOWN,
                torso_lateral_angle_degrees=(
                    geometry.torso_lateral_angle_degrees if geometry is not None else 0.0
                ),
                torso_depth_delta=(geometry.torso_depth_delta if geometry is not None else 0.0),
                neutral_torso_depth_delta=baseline,
                torso_depth_change=None,
                geometry_valid=False,
            )

        angle = geometry.torso_lateral_angle_degrees
        if angle > self._lateral_lean_threshold_degrees:
            lateral = LateralPostureState.LEAN_LEFT
        elif angle < -self._lateral_lean_threshold_degrees:
            lateral = LateralPostureState.LEAN_RIGHT
        else:
            lateral = LateralPostureState.UPRIGHT

        change: Optional[float] = None
        if self._calibrating:
            sagittal = SagittalPostureState.CALIBRATING
        elif baseline is None:
            sagittal = SagittalPostureState.NOT_CALIBRATED
        else:
            change = geometry.torso_depth_delta - baseline
            sagittal = (
                SagittalPostureState.FORWARD_LEAN
                if change < self._forward_lean_relative_depth_threshold
                else SagittalPostureState.NEUTRAL
            )

        return BodyPostureResult(
            lateral_state=lateral,
            sagittal_state=sagittal,
            torso_lateral_angle_degrees=angle,
            torso_depth_delta=geometry.torso_depth_delta,
            neutral_torso_depth_delta=baseline,
            torso_depth_change=change,
            geometry_valid=True,
        )
