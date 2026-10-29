from dataclasses import dataclass
from enum import Enum
import math
from typing import Dict, List, Optional, Tuple


Point2D = Tuple[int, int]
Point2DFloat = Tuple[float, float]


SELECTED_HAND_LANDMARKS = {
    "wrist": 0,
    "thumb_tip": 4,
    "index_mcp": 5,
    "index_tip": 8,
    "middle_mcp": 9,
    "middle_tip": 12,
    "ring_mcp": 13,
    "ring_tip": 16,
    "pinky_mcp": 17,
    "pinky_tip": 20,
}


class HandVisibilityState(Enum):
    """
    Prototype hand visibility state.

    These states describe only whether hand landmarks are
    currently observed by the detector.
    """

    NOT_DETECTED = "NOT_DETECTED"
    SINGLE_HAND = "SINGLE_HAND"
    TWO_HANDS = "TWO_HANDS"


class HandOpenState(Enum):
    """
    Coarse geometric hand-shape state.

    This is based only on normalized fingertip extension.
    It is not a gesture, intent, or safety classification.
    """

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    INTERMEDIATE = "INTERMEDIATE"
    UNKNOWN = "UNKNOWN"


class HandSpatialState(Enum):
    """
    Prototype image-space hand location.

    These are geometric regions only.

    They must not be interpreted directly as:
    - phone use
    - steering-wheel contact
    - distraction
    - driver engagement
    - safety state
    """

    NEAR_FACE = "NEAR_FACE"
    TORSO_REGION = "TORSO_REGION"
    LOWER_REGION = "LOWER_REGION"
    OUTSIDE_BODY_REGION = "OUTSIDE_BODY_REGION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class HandLandmark:
    pixel: Point2D

    normalized_x: float
    normalized_y: float
    normalized_z: float


@dataclass(frozen=True)
class DetectedHand:
    """
    One detected hand.

    model_handedness_label is MediaPipe's handedness estimate.

    It is deliberately not called anatomical_left/right because
    interpretation depends on camera orientation and mirroring.
    """

    landmarks: Dict[str, HandLandmark]

    model_handedness_label: Optional[str]
    model_handedness_score: Optional[float]

    all_required_landmarks_available: bool


@dataclass(frozen=True)
class HandDetectionResult:
    hands: Tuple[DetectedHand, ...]

    hand_count: int

    visibility_state: HandVisibilityState


@dataclass(frozen=True)
class HandGeometryResult:
    """
    Geometric description of one detected hand.
    """

    wrist: Point2DFloat
    palm_center: Point2DFloat

    palm_width_pixels: float
    palm_length_pixels: float

    wrist_to_index_tip_pixels: float
    wrist_to_middle_tip_pixels: float
    wrist_to_ring_tip_pixels: float
    wrist_to_pinky_tip_pixels: float

    normalized_index_extension: float
    normalized_middle_extension: float
    normalized_ring_extension: float
    normalized_pinky_extension: float

    open_state: HandOpenState

    geometry_valid: bool


@dataclass(frozen=True)
class HandSpatialResult:
    """
    Relative hand location with respect to face and torso geometry.
    """

    state: HandSpatialState

    palm_center: Point2DFloat

    face_center: Optional[Point2DFloat]
    face_scale_pixels: Optional[float]

    distance_to_face_pixels: Optional[float]
    normalized_distance_to_face: Optional[float]

    shoulder_midpoint: Optional[Point2DFloat]
    hip_midpoint: Optional[Point2DFloat]

    shoulder_width_pixels: Optional[float]
    torso_length_pixels: Optional[float]

    spatial_geometry_valid: bool


def _euclidean_distance(
    point_a: Point2DFloat,
    point_b: Point2DFloat,
) -> float:
    return math.hypot(
        point_a[0] - point_b[0],
        point_a[1] - point_b[1],
    )


def _mean_point(
    points: Tuple[Point2DFloat, ...],
) -> Point2DFloat:

    if not points:
        return 0.0, 0.0

    return (
        sum(point[0] for point in points)
        / len(points),

        sum(point[1] for point in points)
        / len(points),
    )


class HandGeometryExtractor:
    """
    Compute deterministic geometric hand features.

    This class does not depend on MediaPipe internally,
    which makes the geometric logic independently testable.
    """

    REQUIRED_LANDMARKS = (
        "wrist",
        "index_mcp",
        "middle_mcp",
        "ring_mcp",
        "pinky_mcp",
        "index_tip",
        "middle_tip",
        "ring_tip",
        "pinky_tip",
    )

    def __init__(
        self,
        closed_threshold: float = 1.45,
        open_threshold: float = 2.05,
        minimum_palm_size_pixels: float = 5.0,
    ) -> None:

        if closed_threshold <= 0.0:
            raise ValueError(
                "closed_threshold must be greater than 0."
            )

        if open_threshold <= closed_threshold:
            raise ValueError(
                "open_threshold must be greater than "
                "closed_threshold."
            )

        if minimum_palm_size_pixels <= 0.0:
            raise ValueError(
                "minimum_palm_size_pixels must be greater than 0."
            )

        self._closed_threshold = (
            closed_threshold
        )

        self._open_threshold = (
            open_threshold
        )

        self._minimum_palm_size_pixels = (
            minimum_palm_size_pixels
        )

    def compute_geometry(
        self,
        hand: DetectedHand,
    ) -> HandGeometryResult:

        landmarks = hand.landmarks

        if not all(
            name in landmarks
            for name in self.REQUIRED_LANDMARKS
        ):
            return self._invalid_result()

        wrist = self._pixel_float(
            landmarks["wrist"]
        )

        index_mcp = self._pixel_float(
            landmarks["index_mcp"]
        )

        middle_mcp = self._pixel_float(
            landmarks["middle_mcp"]
        )

        ring_mcp = self._pixel_float(
            landmarks["ring_mcp"]
        )

        pinky_mcp = self._pixel_float(
            landmarks["pinky_mcp"]
        )

        index_tip = self._pixel_float(
            landmarks["index_tip"]
        )

        middle_tip = self._pixel_float(
            landmarks["middle_tip"]
        )

        ring_tip = self._pixel_float(
            landmarks["ring_tip"]
        )

        pinky_tip = self._pixel_float(
            landmarks["pinky_tip"]
        )

        palm_center = _mean_point(
            (
                index_mcp,
                middle_mcp,
                ring_mcp,
                pinky_mcp,
            )
        )

        palm_width_pixels = (
            _euclidean_distance(
                index_mcp,
                pinky_mcp,
            )
        )

        palm_length_pixels = (
            _euclidean_distance(
                wrist,
                middle_mcp,
            )
        )

        palm_scale = max(
            palm_width_pixels,
            palm_length_pixels,
        )

        if (
            not math.isfinite(
                palm_scale
            )
            or palm_scale
            < self._minimum_palm_size_pixels
        ):
            return self._invalid_result(
                wrist=wrist,
                palm_center=palm_center,
                palm_width_pixels=(
                    palm_width_pixels
                ),
                palm_length_pixels=(
                    palm_length_pixels
                ),
            )

        wrist_to_index_tip_pixels = (
            _euclidean_distance(
                wrist,
                index_tip,
            )
        )

        wrist_to_middle_tip_pixels = (
            _euclidean_distance(
                wrist,
                middle_tip,
            )
        )

        wrist_to_ring_tip_pixels = (
            _euclidean_distance(
                wrist,
                ring_tip,
            )
        )

        wrist_to_pinky_tip_pixels = (
            _euclidean_distance(
                wrist,
                pinky_tip,
            )
        )

        normalized_index_extension = (
            wrist_to_index_tip_pixels
            / palm_scale
        )

        normalized_middle_extension = (
            wrist_to_middle_tip_pixels
            / palm_scale
        )

        normalized_ring_extension = (
            wrist_to_ring_tip_pixels
            / palm_scale
        )

        normalized_pinky_extension = (
            wrist_to_pinky_tip_pixels
            / palm_scale
        )

        normalized_extensions = (
            normalized_index_extension,
            normalized_middle_extension,
            normalized_ring_extension,
            normalized_pinky_extension,
        )

        if not all(
            math.isfinite(value)
            for value in normalized_extensions
        ):
            return self._invalid_result(
                wrist=wrist,
                palm_center=palm_center,
                palm_width_pixels=(
                    palm_width_pixels
                ),
                palm_length_pixels=(
                    palm_length_pixels
                ),
            )

        mean_extension = (
            sum(
                normalized_extensions
            )
            / len(
                normalized_extensions
            )
        )

        if (
            mean_extension
            <= self._closed_threshold
        ):
            open_state = (
                HandOpenState.CLOSED
            )

        elif (
            mean_extension
            >= self._open_threshold
        ):
            open_state = (
                HandOpenState.OPEN
            )

        else:
            open_state = (
                HandOpenState.INTERMEDIATE
            )

        return HandGeometryResult(
            wrist=wrist,

            palm_center=palm_center,

            palm_width_pixels=(
                palm_width_pixels
            ),

            palm_length_pixels=(
                palm_length_pixels
            ),

            wrist_to_index_tip_pixels=(
                wrist_to_index_tip_pixels
            ),

            wrist_to_middle_tip_pixels=(
                wrist_to_middle_tip_pixels
            ),

            wrist_to_ring_tip_pixels=(
                wrist_to_ring_tip_pixels
            ),

            wrist_to_pinky_tip_pixels=(
                wrist_to_pinky_tip_pixels
            ),

            normalized_index_extension=(
                normalized_index_extension
            ),

            normalized_middle_extension=(
                normalized_middle_extension
            ),

            normalized_ring_extension=(
                normalized_ring_extension
            ),

            normalized_pinky_extension=(
                normalized_pinky_extension
            ),

            open_state=open_state,

            geometry_valid=True,
        )

    @staticmethod
    def _pixel_float(
        landmark: HandLandmark,
    ) -> Point2DFloat:

        return (
            float(
                landmark.pixel[0]
            ),

            float(
                landmark.pixel[1]
            ),
        )

    @staticmethod
    def _invalid_result(
        wrist: Point2DFloat = (
            0.0,
            0.0,
        ),
        palm_center: Point2DFloat = (
            0.0,
            0.0,
        ),
        palm_width_pixels: float = 0.0,
        palm_length_pixels: float = 0.0,
    ) -> HandGeometryResult:

        return HandGeometryResult(
            wrist=wrist,

            palm_center=palm_center,

            palm_width_pixels=(
                palm_width_pixels
            ),

            palm_length_pixels=(
                palm_length_pixels
            ),

            wrist_to_index_tip_pixels=0.0,

            wrist_to_middle_tip_pixels=0.0,

            wrist_to_ring_tip_pixels=0.0,

            wrist_to_pinky_tip_pixels=0.0,

            normalized_index_extension=0.0,

            normalized_middle_extension=0.0,

            normalized_ring_extension=0.0,

            normalized_pinky_extension=0.0,

            open_state=(
                HandOpenState.UNKNOWN
            ),

            geometry_valid=False,
        )


class HandSpatialEstimator:
    """
    Estimate coarse image-space hand location.

    Inputs:
    - hand palm center
    - existing face landmarks
    - existing M7 body geometry

    Output:
    - NEAR_FACE
    - TORSO_REGION
    - LOWER_REGION
    - OUTSIDE_BODY_REGION
    - UNKNOWN

    This remains geometric only.
    """

    REQUIRED_FACE_LANDMARKS = (
        "forehead",
        "chin",
    )

    def __init__(
        self,
        near_face_threshold: float = 1.10,
        torso_lateral_margin_ratio: float = 0.65,
        lower_region_start_ratio: float = 0.65,
        lower_region_extension_ratio: float = 0.80,
    ) -> None:

        if near_face_threshold <= 0.0:
            raise ValueError(
                "near_face_threshold must be positive."
            )

        if torso_lateral_margin_ratio < 0.0:
            raise ValueError(
                "torso_lateral_margin_ratio must be "
                "non-negative."
            )

        if not (
            0.0
            < lower_region_start_ratio
            < 1.0
        ):
            raise ValueError(
                "lower_region_start_ratio must be "
                "between 0 and 1."
            )

        if lower_region_extension_ratio <= 0.0:
            raise ValueError(
                "lower_region_extension_ratio must "
                "be positive."
            )

        self._near_face_threshold = (
            near_face_threshold
        )

        self._torso_lateral_margin_ratio = (
            torso_lateral_margin_ratio
        )

        self._lower_region_start_ratio = (
            lower_region_start_ratio
        )

        self._lower_region_extension_ratio = (
            lower_region_extension_ratio
        )

    def estimate(
        self,
        hand_geometry: Optional[
            HandGeometryResult
        ],
        face_landmarks: Optional[
            Dict[str, Point2D]
        ],
        body_geometry,
    ) -> HandSpatialResult:

        if (
            hand_geometry is None
            or not hand_geometry.geometry_valid
        ):
            return (
                self._unknown_result()
            )

        palm_center = (
            hand_geometry.palm_center
        )

        face_center = None
        face_scale_pixels = None

        distance_to_face_pixels = None

        normalized_distance_to_face = (
            None
        )

        # -----------------------------------------------------
        # Face-relative geometry
        # -----------------------------------------------------

        if self._valid_face_landmarks(
            face_landmarks
        ):

            forehead = self._to_float(
                face_landmarks[
                    "forehead"
                ]
            )

            chin = self._to_float(
                face_landmarks[
                    "chin"
                ]
            )

            face_center = (
                (
                    forehead[0]
                    + chin[0]
                )
                / 2.0,

                (
                    forehead[1]
                    + chin[1]
                )
                / 2.0,
            )

            face_scale_pixels = (
                _euclidean_distance(
                    forehead,
                    chin,
                )
            )

            if (
                math.isfinite(
                    face_scale_pixels
                )
                and face_scale_pixels
                > 1.0
            ):
                distance_to_face_pixels = (
                    _euclidean_distance(
                        palm_center,
                        face_center,
                    )
                )

                normalized_distance_to_face = (
                    distance_to_face_pixels
                    / face_scale_pixels
                )

                if (
                    normalized_distance_to_face
                    <= self._near_face_threshold
                ):
                    return (
                        HandSpatialResult(
                            state=(
                                HandSpatialState.NEAR_FACE
                            ),

                            palm_center=(
                                palm_center
                            ),

                            face_center=(
                                face_center
                            ),

                            face_scale_pixels=(
                                face_scale_pixels
                            ),

                            distance_to_face_pixels=(
                                distance_to_face_pixels
                            ),

                            normalized_distance_to_face=(
                                normalized_distance_to_face
                            ),

                            shoulder_midpoint=(
                                self._optional_body_attr(
                                    body_geometry,
                                    "shoulder_midpoint",
                                )
                            ),

                            hip_midpoint=(
                                self._optional_body_attr(
                                    body_geometry,
                                    "hip_midpoint",
                                )
                            ),

                            shoulder_width_pixels=(
                                self._optional_body_attr(
                                    body_geometry,
                                    "shoulder_width_pixels",
                                )
                            ),

                            torso_length_pixels=(
                                self._optional_body_attr(
                                    body_geometry,
                                    "torso_length_pixels",
                                )
                            ),

                            spatial_geometry_valid=True,
                        )
                    )

        # -----------------------------------------------------
        # Body-relative geometry
        # -----------------------------------------------------

        if not self._valid_body_geometry(
            body_geometry
        ):
            return HandSpatialResult(
                state=(
                    HandSpatialState.UNKNOWN
                ),

                palm_center=(
                    palm_center
                ),

                face_center=(
                    face_center
                ),

                face_scale_pixels=(
                    face_scale_pixels
                ),

                distance_to_face_pixels=(
                    distance_to_face_pixels
                ),

                normalized_distance_to_face=(
                    normalized_distance_to_face
                ),

                shoulder_midpoint=None,

                hip_midpoint=None,

                shoulder_width_pixels=None,

                torso_length_pixels=None,

                spatial_geometry_valid=False,
            )

        shoulder_midpoint = (
            body_geometry.shoulder_midpoint
        )

        hip_midpoint = (
            body_geometry.hip_midpoint
        )

        shoulder_width = (
            body_geometry.shoulder_width_pixels
        )

        torso_length = (
            body_geometry.torso_length_pixels
        )

        half_width = (
            shoulder_width
            / 2.0
        )

        lateral_margin = (
            shoulder_width
            * self._torso_lateral_margin_ratio
        )

        torso_left = (
            shoulder_midpoint[0]
            - half_width
            - lateral_margin
        )

        torso_right = (
            shoulder_midpoint[0]
            + half_width
            + lateral_margin
        )

        shoulder_y = min(
            shoulder_midpoint[1],
            hip_midpoint[1],
        )

        hip_y = max(
            shoulder_midpoint[1],
            hip_midpoint[1],
        )

        torso_span = (
            hip_y
            - shoulder_y
        )

        lower_region_start_y = (
            shoulder_y
            + (
                self._lower_region_start_ratio
                * torso_span
            )
        )

        inside_lateral_band = (
            torso_left
            <= palm_center[0]
            <= torso_right
        )

        # -----------------------------------------------------
        # Torso region
        # -----------------------------------------------------

        if (
            inside_lateral_band
            and shoulder_y
            <= palm_center[1]
            < lower_region_start_y
        ):
            state = (
                HandSpatialState.TORSO_REGION
            )

        # -----------------------------------------------------
        # Lower/lap region
        # -----------------------------------------------------

        elif (
            inside_lateral_band
            and lower_region_start_y
            <= palm_center[1]
            <= (
                hip_y
                + (
                    torso_length
                    * self._lower_region_extension_ratio
                )
            )
        ):
            state = (
                HandSpatialState.LOWER_REGION
            )

        # -----------------------------------------------------
        # Outside body region
        # -----------------------------------------------------

        else:
            state = (
                HandSpatialState.OUTSIDE_BODY_REGION
            )

        return HandSpatialResult(
            state=state,

            palm_center=palm_center,

            face_center=(
                face_center
            ),

            face_scale_pixels=(
                face_scale_pixels
            ),

            distance_to_face_pixels=(
                distance_to_face_pixels
            ),

            normalized_distance_to_face=(
                normalized_distance_to_face
            ),

            shoulder_midpoint=(
                shoulder_midpoint
            ),

            hip_midpoint=(
                hip_midpoint
            ),

            shoulder_width_pixels=(
                shoulder_width
            ),

            torso_length_pixels=(
                torso_length
            ),

            spatial_geometry_valid=True,
        )

    @classmethod
    def _valid_face_landmarks(
        cls,
        face_landmarks: Optional[
            Dict[str, Point2D]
        ],
    ) -> bool:

        if face_landmarks is None:
            return False

        return all(
            name in face_landmarks
            for name
            in cls.REQUIRED_FACE_LANDMARKS
        )

    @staticmethod
    def _valid_body_geometry(
        body_geometry,
    ) -> bool:

        if body_geometry is None:
            return False

        required = (
            "shoulder_midpoint",
            "hip_midpoint",
            "shoulder_width_pixels",
            "torso_length_pixels",
            "geometry_valid",
        )

        if not all(
            hasattr(
                body_geometry,
                name,
            )
            for name in required
        ):
            return False

        return bool(
            body_geometry.geometry_valid
            and body_geometry.shoulder_width_pixels
            > 1.0
            and body_geometry.torso_length_pixels
            > 1.0
        )

    @staticmethod
    def _optional_body_attr(
        body_geometry,
        name: str,
    ):

        if body_geometry is None:
            return None

        return getattr(
            body_geometry,
            name,
            None,
        )

    @staticmethod
    def _to_float(
        point: Point2D,
    ) -> Point2DFloat:

        return (
            float(
                point[0]
            ),

            float(
                point[1]
            ),
        )

    @staticmethod
    def _unknown_result(
    ) -> HandSpatialResult:

        return HandSpatialResult(
            state=(
                HandSpatialState.UNKNOWN
            ),

            palm_center=(
                0.0,
                0.0,
            ),

            face_center=None,

            face_scale_pixels=None,

            distance_to_face_pixels=None,

            normalized_distance_to_face=None,

            shoulder_midpoint=None,

            hip_midpoint=None,

            shoulder_width_pixels=None,

            torso_length_pixels=None,

            spatial_geometry_valid=False,
        )


class HandLandmarkDetector:
    """
    MediaPipe Hands wrapper.

    MediaPipe and OpenCV are imported lazily so deterministic
    geometry tests can import this module without loading the
    complete perception runtime.
    """

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 2,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:

        if max_num_hands < 1:
            raise ValueError(
                "max_num_hands must be at least 1."
            )

        if model_complexity not in (
            0,
            1,
        ):
            raise ValueError(
                "model_complexity must be 0 or 1."
            )

        if not (
            0.0
            <= min_detection_confidence
            <= 1.0
        ):
            raise ValueError(
                "min_detection_confidence must "
                "be between 0 and 1."
            )

        if not (
            0.0
            <= min_tracking_confidence
            <= 1.0
        ):
            raise ValueError(
                "min_tracking_confidence must "
                "be between 0 and 1."
            )

        try:
            import mediapipe as mp

        except ImportError as exc:
            raise RuntimeError(
                "MediaPipe is required to construct "
                "HandLandmarkDetector."
            ) from exc

        self._mp_hands = (
            mp.solutions.hands
        )

        self._hands = (
            self._mp_hands.Hands(
                static_image_mode=(
                    static_image_mode
                ),

                max_num_hands=(
                    max_num_hands
                ),

                model_complexity=(
                    model_complexity
                ),

                min_detection_confidence=(
                    min_detection_confidence
                ),

                min_tracking_confidence=(
                    min_tracking_confidence
                ),
            )
        )

    def detect(
        self,
        frame,
    ) -> HandDetectionResult:

        if frame is None:
            return (
                self._empty_result()
            )

        if getattr(
            frame,
            "size",
            0,
        ) == 0:
            return (
                self._empty_result()
            )

        frame_height, frame_width = (
            frame.shape[:2]
        )

        if (
            frame_width <= 0
            or frame_height <= 0
        ):
            return (
                self._empty_result()
            )

        try:
            import cv2

        except ImportError as exc:
            raise RuntimeError(
                "OpenCV is required "
                "for hand detection."
            ) from exc

        rgb_frame = (
            cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )
        )

        results = (
            self._hands.process(
                rgb_frame
            )
        )

        if not (
            results.multi_hand_landmarks
        ):
            return (
                self._empty_result()
            )

        handedness_entries = (
            results.multi_handedness
            if results.multi_handedness
            else []
        )

        detected_hands: List[
            DetectedHand
        ] = []

        for (
            hand_index,
            hand_landmarks,
        ) in enumerate(
            results.multi_hand_landmarks
        ):

            selected_landmarks: Dict[
                str,
                HandLandmark,
            ] = {}

            raw_landmarks = (
                hand_landmarks.landmark
            )

            all_required_landmarks_available = (
                True
            )

            for (
                landmark_name,
                landmark_index,
            ) in (
                SELECTED_HAND_LANDMARKS.items()
            ):

                if (
                    landmark_index
                    >= len(
                        raw_landmarks
                    )
                ):
                    all_required_landmarks_available = (
                        False
                    )
                    continue

                landmark = (
                    raw_landmarks[
                        landmark_index
                    ]
                )

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

                selected_landmarks[
                    landmark_name
                ] = HandLandmark(
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
                )

            handedness_label = (
                None
            )

            handedness_score = (
                None
            )

            if (
                hand_index
                < len(
                    handedness_entries
                )
            ):
                classifications = (
                    handedness_entries[
                        hand_index
                    ].classification
                )

                if classifications:

                    handedness_label = str(
                        classifications[
                            0
                        ].label
                    )

                    handedness_score = float(
                        classifications[
                            0
                        ].score
                    )

            detected_hands.append(
                DetectedHand(
                    landmarks=(
                        selected_landmarks
                    ),

                    model_handedness_label=(
                        handedness_label
                    ),

                    model_handedness_score=(
                        handedness_score
                    ),

                    all_required_landmarks_available=(
                        all_required_landmarks_available
                    ),
                )
            )

        hand_count = (
            len(
                detected_hands
            )
        )

        if hand_count >= 2:
            visibility_state = (
                HandVisibilityState.TWO_HANDS
            )

        elif hand_count == 1:
            visibility_state = (
                HandVisibilityState.SINGLE_HAND
            )

        else:
            visibility_state = (
                HandVisibilityState.NOT_DETECTED
            )

        return HandDetectionResult(
            hands=tuple(
                detected_hands
            ),

            hand_count=(
                hand_count
            ),

            visibility_state=(
                visibility_state
            ),
        )

    def close(
        self,
    ) -> None:
        """
        Release MediaPipe resources.
        """

        if getattr(
            self,
            "_hands",
            None,
        ) is not None:
            self._hands.close()

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

    @staticmethod
    def _empty_result(
    ) -> HandDetectionResult:

        return HandDetectionResult(
            hands=tuple(),

            hand_count=0,

            visibility_state=(
                HandVisibilityState.NOT_DETECTED
            ),
        )