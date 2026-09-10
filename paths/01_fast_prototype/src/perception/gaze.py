from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

import numpy as np


Point2D = Tuple[int, int]


class GazeDirection(Enum):
    """
    Prototype geometric gaze-direction labels.

    These labels describe normalized iris-position geometry only.
    They are not behavioral classifications such as distraction
    or inattention.
    """

    CENTER = "CENTER"

    LEFT = "LEFT"
    RIGHT = "RIGHT"

    UP = "UP"
    DOWN = "DOWN"

    LEFT_UP = "LEFT_UP"
    LEFT_DOWN = "LEFT_DOWN"

    RIGHT_UP = "RIGHT_UP"
    RIGHT_DOWN = "RIGHT_DOWN"

    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EyeGazeResult:
    """
    Normalized geometric iris position for one eye.

    horizontal_ratio:
        Canonical horizontal iris position.

    vertical_ratio:
        Iris position between upper and lower eyelid landmarks.

    These are image-space geometric features,
    not calibrated gaze angles.
    """

    horizontal_ratio: float
    vertical_ratio: float


@dataclass(frozen=True)
class GazeResult:
    """
    Combined geometric gaze result from both eyes.

    horizontal_ratio:
        Mean canonical horizontal iris position.

    vertical_ratio:
        Mean normalized vertical iris position.

    horizontal_disagreement:
        Absolute disagreement between left and right horizontal values.

    vertical_disagreement:
        Absolute disagreement between left and right vertical values.

    is_consistent:
        Whether the two eyes agree sufficiently according to
        prototype quality thresholds.

    direction:
        Prototype geometric gaze-direction label derived from
        normalized H/V measurements when consistency is acceptable.
    """

    left_eye: EyeGazeResult
    right_eye: EyeGazeResult

    horizontal_ratio: float
    vertical_ratio: float

    horizontal_disagreement: float
    vertical_disagreement: float

    is_consistent: bool

    direction: GazeDirection


class GazeEstimator:
    """
    Estimate normalized iris geometry and prototype gaze direction.

    Milestone 6 baseline:

    - iris-center geometry
    - bilateral horizontal normalization
    - per-eye H/V ratios
    - combined H/V ratios
    - inter-eye disagreement
    - consistency assessment
    - prototype geometric gaze-direction labels

    Current empirical coordinate convention:

        Higher H -> LEFT
        Lower H  -> RIGHT

        Lower V  -> UP
        Higher V -> DOWN

    Direction thresholds were selected from the initial webcam
    validation performed during Milestone 6.

    They are prototype parameters and are not universal,
    calibrated, or safety-validated thresholds.
    """

    REQUIRED_LANDMARKS = (
        "left_eye_outer",
        "left_eye_inner",
        "left_eye_upper",
        "left_eye_lower",
        "left_iris_center",
        "right_eye_outer",
        "right_eye_inner",
        "right_eye_upper",
        "right_eye_lower",
        "right_iris_center",
    )

    def __init__(
        self,
        minimum_eye_width_pixels: float = 1.0,
        minimum_eye_height_pixels: float = 1.0,
        max_horizontal_disagreement: float = 0.15,
        max_vertical_disagreement: float = 0.20,
        right_threshold: float = 0.40,
        left_threshold: float = 0.56,
        up_threshold: float = 0.41,
        down_threshold: float = 0.50,
    ) -> None:
        if minimum_eye_width_pixels <= 0.0:
            raise ValueError(
                "minimum_eye_width_pixels must be positive."
            )

        if minimum_eye_height_pixels <= 0.0:
            raise ValueError(
                "minimum_eye_height_pixels must be positive."
            )

        if max_horizontal_disagreement < 0.0:
            raise ValueError(
                "max_horizontal_disagreement must be non-negative."
            )

        if max_vertical_disagreement < 0.0:
            raise ValueError(
                "max_vertical_disagreement must be non-negative."
            )

        if right_threshold >= left_threshold:
            raise ValueError(
                "right_threshold must be smaller than left_threshold."
            )

        if up_threshold >= down_threshold:
            raise ValueError(
                "up_threshold must be smaller than down_threshold."
            )

        self._minimum_eye_width_pixels = (
            minimum_eye_width_pixels
        )

        self._minimum_eye_height_pixels = (
            minimum_eye_height_pixels
        )

        self._max_horizontal_disagreement = (
            max_horizontal_disagreement
        )

        self._max_vertical_disagreement = (
            max_vertical_disagreement
        )

        self._right_threshold = (
            right_threshold
        )

        self._left_threshold = (
            left_threshold
        )

        self._up_threshold = (
            up_threshold
        )

        self._down_threshold = (
            down_threshold
        )

    def estimate(
        self,
        landmarks: Dict[str, Point2D],
    ) -> Optional[GazeResult]:
        """
        Estimate normalized gaze geometry.

        Returns None when required landmarks are unavailable
        or when either eye geometry is degenerate.
        """

        if not self._has_required_landmarks(
            landmarks
        ):
            return None

        left_eye = self._estimate_eye(
            outer=landmarks["left_eye_outer"],
            inner=landmarks["left_eye_inner"],
            upper=landmarks["left_eye_upper"],
            lower=landmarks["left_eye_lower"],
            iris_center=landmarks["left_iris_center"],
            invert_horizontal=False,
        )

        if left_eye is None:
            return None

        right_eye = self._estimate_eye(
            outer=landmarks["right_eye_outer"],
            inner=landmarks["right_eye_inner"],
            upper=landmarks["right_eye_upper"],
            lower=landmarks["right_eye_lower"],
            iris_center=landmarks["right_iris_center"],
            invert_horizontal=True,
        )

        if right_eye is None:
            return None

        horizontal_ratio = (
            left_eye.horizontal_ratio
            + right_eye.horizontal_ratio
        ) / 2.0

        vertical_ratio = (
            left_eye.vertical_ratio
            + right_eye.vertical_ratio
        ) / 2.0

        horizontal_disagreement = abs(
            left_eye.horizontal_ratio
            - right_eye.horizontal_ratio
        )

        vertical_disagreement = abs(
            left_eye.vertical_ratio
            - right_eye.vertical_ratio
        )

        is_consistent = (
            horizontal_disagreement
            <= self._max_horizontal_disagreement
            and vertical_disagreement
            <= self._max_vertical_disagreement
        )

        direction = self._classify_direction(
            horizontal_ratio=horizontal_ratio,
            vertical_ratio=vertical_ratio,
            is_consistent=is_consistent,
        )

        return GazeResult(
            left_eye=left_eye,
            right_eye=right_eye,
            horizontal_ratio=horizontal_ratio,
            vertical_ratio=vertical_ratio,
            horizontal_disagreement=horizontal_disagreement,
            vertical_disagreement=vertical_disagreement,
            is_consistent=is_consistent,
            direction=direction,
        )

    def _estimate_eye(
        self,
        outer: Point2D,
        inner: Point2D,
        upper: Point2D,
        lower: Point2D,
        iris_center: Point2D,
        invert_horizontal: bool,
    ) -> Optional[EyeGazeResult]:
        """
        Compute normalized iris position for one eye.
        """

        outer_point = np.asarray(
            outer,
            dtype=np.float64,
        )

        inner_point = np.asarray(
            inner,
            dtype=np.float64,
        )

        upper_point = np.asarray(
            upper,
            dtype=np.float64,
        )

        lower_point = np.asarray(
            lower,
            dtype=np.float64,
        )

        iris_point = np.asarray(
            iris_center,
            dtype=np.float64,
        )

        horizontal_axis = (
            inner_point - outer_point
        )

        vertical_axis = (
            lower_point - upper_point
        )

        horizontal_length = float(
            np.linalg.norm(horizontal_axis)
        )

        vertical_length = float(
            np.linalg.norm(vertical_axis)
        )

        if (
            horizontal_length
            < self._minimum_eye_width_pixels
        ):
            return None

        if (
            vertical_length
            < self._minimum_eye_height_pixels
        ):
            return None

        horizontal_ratio = (
            self._normalized_projection(
                point=iris_point,
                start=outer_point,
                axis=horizontal_axis,
            )
        )

        if invert_horizontal:
            horizontal_ratio = (
                1.0 - horizontal_ratio
            )

        vertical_ratio = (
            self._normalized_projection(
                point=iris_point,
                start=upper_point,
                axis=vertical_axis,
            )
        )

        return EyeGazeResult(
            horizontal_ratio=horizontal_ratio,
            vertical_ratio=vertical_ratio,
        )

    def _classify_direction(
        self,
        horizontal_ratio: float,
        vertical_ratio: float,
        is_consistent: bool,
    ) -> GazeDirection:
        """
        Convert normalized H/V geometry into a prototype direction label.

        Horizontal convention:

            H < right_threshold -> RIGHT
            H > left_threshold  -> LEFT
            otherwise           -> horizontal center

        Vertical convention:

            V < up_threshold    -> UP
            V > down_threshold  -> DOWN
            otherwise           -> vertical center

        If inter-eye consistency is low, UNKNOWN is returned.
        """

        if not is_consistent:
            return GazeDirection.UNKNOWN

        horizontal_direction: Optional[str] = None
        vertical_direction: Optional[str] = None

        if horizontal_ratio > self._left_threshold:
            horizontal_direction = "LEFT"

        elif horizontal_ratio < self._right_threshold:
            horizontal_direction = "RIGHT"

        if vertical_ratio < self._up_threshold:
            vertical_direction = "UP"

        elif vertical_ratio > self._down_threshold:
            vertical_direction = "DOWN"

        if (
            horizontal_direction is None
            and vertical_direction is None
        ):
            return GazeDirection.CENTER

        if (
            horizontal_direction == "LEFT"
            and vertical_direction is None
        ):
            return GazeDirection.LEFT

        if (
            horizontal_direction == "RIGHT"
            and vertical_direction is None
        ):
            return GazeDirection.RIGHT

        if (
            horizontal_direction is None
            and vertical_direction == "UP"
        ):
            return GazeDirection.UP

        if (
            horizontal_direction is None
            and vertical_direction == "DOWN"
        ):
            return GazeDirection.DOWN

        if (
            horizontal_direction == "LEFT"
            and vertical_direction == "UP"
        ):
            return GazeDirection.LEFT_UP

        if (
            horizontal_direction == "LEFT"
            and vertical_direction == "DOWN"
        ):
            return GazeDirection.LEFT_DOWN

        if (
            horizontal_direction == "RIGHT"
            and vertical_direction == "UP"
        ):
            return GazeDirection.RIGHT_UP

        if (
            horizontal_direction == "RIGHT"
            and vertical_direction == "DOWN"
        ):
            return GazeDirection.RIGHT_DOWN

        return GazeDirection.UNKNOWN

    @staticmethod
    def _normalized_projection(
        point: np.ndarray,
        start: np.ndarray,
        axis: np.ndarray,
    ) -> float:
        """
        Project a point onto an axis and normalize it.

        Approximate interpretation:

            0.0 -> axis start
            0.5 -> midpoint
            1.0 -> axis end

        Values are intentionally not clamped so abnormal geometry
        remains visible during prototype validation.
        """

        denominator = float(
            np.dot(
                axis,
                axis,
            )
        )

        if denominator < 1e-12:
            return 0.0

        relative_point = (
            point - start
        )

        return float(
            np.dot(
                relative_point,
                axis,
            )
            / denominator
        )

    @classmethod
    def _has_required_landmarks(
        cls,
        landmarks: Dict[str, Point2D],
    ) -> bool:
        return all(
            name in landmarks
            for name in cls.REQUIRED_LANDMARKS
        )