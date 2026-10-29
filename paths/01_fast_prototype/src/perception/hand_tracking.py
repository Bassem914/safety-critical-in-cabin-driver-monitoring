from dataclasses import dataclass
from enum import Enum
import math
from typing import Dict, Iterable, Optional, Tuple

from perception.hand_features import (
    DetectedHand,
    HandGeometryResult,
    HandSpatialResult,
    HandSpatialState,
)


Point2DFloat = Tuple[float, float]


class HandTrackVisibilityState(Enum):
    """
    Temporal visibility state of a geometric hand track.

    These states describe tracking continuity only.
    They are not behavioral or safety judgments.
    """

    VISIBLE = "VISIBLE"
    TEMPORARILY_MISSING = "TEMPORARILY_MISSING"
    LOST = "LOST"


@dataclass(frozen=True)
class HandObservation:
    """
    Per-frame geometric observation passed into the tracker.
    """

    model_handedness_label: Optional[str]
    model_handedness_score: Optional[float]

    palm_center: Point2DFloat

    geometry: HandGeometryResult
    spatial: HandSpatialResult


@dataclass(frozen=True)
class HandTrackResult:
    """
    Public immutable snapshot of one temporal hand track.
    """

    track_id: int

    visibility_state: HandTrackVisibilityState

    model_handedness_label: Optional[str]

    palm_center: Optional[Point2DFloat]

    spatial_state: HandSpatialState

    spatial_dwell_seconds: float

    track_age_seconds: float

    missing_duration_seconds: float

    displacement_pixels: Optional[float]

    speed_pixels_per_second: Optional[float]


@dataclass
class _MutableHandTrack:
    """
    Internal mutable state for one tracked hand.
    """

    track_id: int

    model_handedness_label: Optional[str]
    model_handedness_score: Optional[float]

    last_palm_center: Optional[Point2DFloat]

    first_timestamp_seconds: float
    last_timestamp_seconds: float
    last_visible_timestamp_seconds: float

    current_spatial_state: HandSpatialState
    spatial_state_start_timestamp_seconds: float

    visibility_state: HandTrackVisibilityState

    displacement_pixels: Optional[float] = None
    speed_pixels_per_second: Optional[float] = None

    velocity_x_pixels_per_second: float = 0.0
    velocity_y_pixels_per_second: float = 0.0


class HandTemporalTracker:
    """
    Prototype temporal hand tracker.

    Association uses:

    1. palm-center spatial continuity;
    2. simple motion prediction;
    3. MediaPipe handedness only as a soft cue;
    4. temporary disappearance tolerance.

    Important:
    - track IDs are temporal geometric identities;
    - MediaPipe Left/Right is not treated as absolute anatomical truth;
    - no behavioral or safety interpretation is produced here.
    """

    def __init__(
        self,
        maximum_match_distance_pixels: float = 320.0,
        missing_tolerance_seconds: float = 0.60,
        handedness_mismatch_penalty_pixels: float = 50.0,
        handedness_confidence_threshold: float = 0.80,
        lost_track_retention_seconds: float = 1.00,
        maximum_prediction_seconds: float = 0.35,
    ) -> None:

        if maximum_match_distance_pixels <= 0.0:
            raise ValueError(
                "maximum_match_distance_pixels must be positive."
            )

        if missing_tolerance_seconds < 0.0:
            raise ValueError(
                "missing_tolerance_seconds must be non-negative."
            )

        if handedness_mismatch_penalty_pixels < 0.0:
            raise ValueError(
                "handedness_mismatch_penalty_pixels "
                "must be non-negative."
            )

        if not (
            0.0
            <= handedness_confidence_threshold
            <= 1.0
        ):
            raise ValueError(
                "handedness_confidence_threshold "
                "must be between 0 and 1."
            )

        if lost_track_retention_seconds < 0.0:
            raise ValueError(
                "lost_track_retention_seconds must be non-negative."
            )

        if maximum_prediction_seconds < 0.0:
            raise ValueError(
                "maximum_prediction_seconds must be non-negative."
            )

        self._maximum_match_distance_pixels = (
            maximum_match_distance_pixels
        )

        self._missing_tolerance_seconds = (
            missing_tolerance_seconds
        )

        self._handedness_mismatch_penalty_pixels = (
            handedness_mismatch_penalty_pixels
        )

        self._handedness_confidence_threshold = (
            handedness_confidence_threshold
        )

        self._lost_track_retention_seconds = (
            lost_track_retention_seconds
        )

        self._maximum_prediction_seconds = (
            maximum_prediction_seconds
        )

        self._tracks: Dict[
            int,
            _MutableHandTrack,
        ] = {}

        self._next_track_id = 1

    def reset(
        self,
    ) -> None:
        """
        Reset all temporal tracking state.
        """

        self._tracks.clear()
        self._next_track_id = 1

    def update(
        self,
        timestamp_seconds: float,
        observations: Iterable[
            HandObservation
        ],
    ) -> Tuple[
        HandTrackResult,
        ...,
    ]:
        """
        Update temporal hand tracks for one frame.
        """

        if not math.isfinite(
            timestamp_seconds
        ):
            raise ValueError(
                "timestamp_seconds must be finite."
            )

        observation_list = list(
            observations
        )

        # -----------------------------------------------------
        # First update existing tracks according to elapsed time.
        # -----------------------------------------------------

        self._update_visibility_states(
            timestamp_seconds=(
                timestamp_seconds
            )
        )

        # -----------------------------------------------------
        # Remove tracks that have been LOST long enough.
        # -----------------------------------------------------

        self._prune_stale_tracks(
            timestamp_seconds=(
                timestamp_seconds
            )
        )

        # -----------------------------------------------------
        # Associate current observations with existing tracks.
        # -----------------------------------------------------

        assignments = self._associate(
            timestamp_seconds=(
                timestamp_seconds
            ),
            observations=(
                observation_list
            ),
        )

        assigned_observation_indices = set()

        for (
            track_id,
            observation_index,
        ) in assignments.items():

            observation = (
                observation_list[
                    observation_index
                ]
            )

            assigned_observation_indices.add(
                observation_index
            )

            self._update_existing_track(
                track=self._tracks[
                    track_id
                ],
                timestamp_seconds=(
                    timestamp_seconds
                ),
                observation=(
                    observation
                ),
            )

        # -----------------------------------------------------
        # Unmatched observations become new tracks.
        # -----------------------------------------------------

        for (
            observation_index,
            observation,
        ) in enumerate(
            observation_list
        ):

            if (
                observation_index
                in assigned_observation_indices
            ):
                continue

            self._create_track(
                timestamp_seconds=(
                    timestamp_seconds
                ),
                observation=(
                    observation
                ),
            )

        # -----------------------------------------------------
        # Re-evaluate LOST states after this frame.
        # -----------------------------------------------------

        self._update_visibility_states(
            timestamp_seconds=(
                timestamp_seconds
            )
        )

        return self._snapshot(
            timestamp_seconds=(
                timestamp_seconds
            )
        )

    # =========================================================
    # Association
    # =========================================================

    def _associate(
        self,
        timestamp_seconds: float,
        observations: list[
            HandObservation
        ],
    ) -> Dict[int, int]:
        """
        Greedy nearest-neighbor association.

        Since this prototype handles at most two hands,
        a complex assignment algorithm is unnecessary.
        """

        candidate_pairs = []

        for (
            track_id,
            track,
        ) in self._tracks.items():

            if (
                track.visibility_state
                == HandTrackVisibilityState.LOST
            ):
                continue

            if (
                track.last_palm_center
                is None
            ):
                continue

            predicted_center = (
                self._predict_center(
                    track=track,
                    timestamp_seconds=(
                        timestamp_seconds
                    ),
                )
            )

            missing_duration = max(
                0.0,
                timestamp_seconds
                - track.last_visible_timestamp_seconds,
            )

            # Slightly enlarge the matching gate while a
            # hand is temporarily missing.
            dynamic_gate = (
                self._maximum_match_distance_pixels
                * (
                    1.0
                    + min(
                        missing_duration,
                        self._missing_tolerance_seconds,
                    )
                )
            )

            for (
                observation_index,
                observation,
            ) in enumerate(
                observations
            ):

                distance = self._distance(
                    predicted_center,
                    observation.palm_center,
                )

                if (
                    distance
                    > dynamic_gate
                ):
                    continue

                score = distance

                # MediaPipe handedness is deliberately a soft cue.
                if self._confident_handedness_mismatch(
                    track=track,
                    observation=observation,
                ):
                    score += (
                        self._handedness_mismatch_penalty_pixels
                    )

                # Prefer currently visible tracks slightly over
                # temporarily missing tracks.
                if (
                    track.visibility_state
                    == HandTrackVisibilityState.TEMPORARILY_MISSING
                ):
                    score += 10.0

                candidate_pairs.append(
                    (
                        score,
                        track_id,
                        observation_index,
                    )
                )

        candidate_pairs.sort(
            key=lambda item: item[0]
        )

        assigned_tracks = set()
        assigned_observations = set()

        assignments: Dict[
            int,
            int,
        ] = {}

        for (
            _score,
            track_id,
            observation_index,
        ) in candidate_pairs:

            if (
                track_id
                in assigned_tracks
            ):
                continue

            if (
                observation_index
                in assigned_observations
            ):
                continue

            assignments[
                track_id
            ] = observation_index

            assigned_tracks.add(
                track_id
            )

            assigned_observations.add(
                observation_index
            )

        return assignments

    # =========================================================
    # Track creation
    # =========================================================

    def _create_track(
        self,
        timestamp_seconds: float,
        observation: HandObservation,
    ) -> None:

        track_id = (
            self._next_track_id
        )

        self._next_track_id += 1

        self._tracks[
            track_id
        ] = _MutableHandTrack(
            track_id=(
                track_id
            ),

            model_handedness_label=(
                observation.model_handedness_label
            ),

            model_handedness_score=(
                observation.model_handedness_score
            ),

            last_palm_center=(
                observation.palm_center
            ),

            first_timestamp_seconds=(
                timestamp_seconds
            ),

            last_timestamp_seconds=(
                timestamp_seconds
            ),

            last_visible_timestamp_seconds=(
                timestamp_seconds
            ),

            current_spatial_state=(
                observation.spatial.state
            ),

            spatial_state_start_timestamp_seconds=(
                timestamp_seconds
            ),

            visibility_state=(
                HandTrackVisibilityState.VISIBLE
            ),

            displacement_pixels=None,

            speed_pixels_per_second=None,

            velocity_x_pixels_per_second=0.0,

            velocity_y_pixels_per_second=0.0,
        )

    # =========================================================
    # Track update
    # =========================================================

    def _update_existing_track(
        self,
        track: _MutableHandTrack,
        timestamp_seconds: float,
        observation: HandObservation,
    ) -> None:

        previous_center = (
            track.last_palm_center
        )

        previous_visible_timestamp = (
            track.last_visible_timestamp_seconds
        )

        delta_time = (
            timestamp_seconds
            - previous_visible_timestamp
        )

        displacement = None
        speed = None

        velocity_x = (
            track.velocity_x_pixels_per_second
        )

        velocity_y = (
            track.velocity_y_pixels_per_second
        )

        if (
            previous_center is not None
            and delta_time > 0.0
        ):

            delta_x = (
                observation.palm_center[0]
                - previous_center[0]
            )

            delta_y = (
                observation.palm_center[1]
                - previous_center[1]
            )

            displacement = (
                math.hypot(
                    delta_x,
                    delta_y,
                )
            )

            speed = (
                displacement
                / delta_time
            )

            measured_velocity_x = (
                delta_x
                / delta_time
            )

            measured_velocity_y = (
                delta_y
                / delta_time
            )

            # Mild smoothing avoids unstable prediction
            # from single-frame landmark jitter.
            velocity_x = (
                0.65
                * velocity_x
                + 0.35
                * measured_velocity_x
            )

            velocity_y = (
                0.65
                * velocity_y
                + 0.35
                * measured_velocity_y
            )

        # -----------------------------------------------------
        # Region transition
        # -----------------------------------------------------

        if (
            observation.spatial.state
            != track.current_spatial_state
        ):

            track.current_spatial_state = (
                observation.spatial.state
            )

            track.spatial_state_start_timestamp_seconds = (
                timestamp_seconds
            )

        # -----------------------------------------------------
        # Update handedness softly.
        # -----------------------------------------------------

        if (
            observation.model_handedness_label
            is not None
        ):

            observation_score = (
                observation.model_handedness_score
            )

            current_score = (
                track.model_handedness_score
            )

            if (
                current_score is None
                or observation_score is None
                or observation_score
                >= current_score
                * 0.85
            ):
                track.model_handedness_label = (
                    observation.model_handedness_label
                )

                track.model_handedness_score = (
                    observation_score
                )

        # -----------------------------------------------------
        # Store current track state
        # -----------------------------------------------------

        track.last_palm_center = (
            observation.palm_center
        )

        track.last_timestamp_seconds = (
            timestamp_seconds
        )

        track.last_visible_timestamp_seconds = (
            timestamp_seconds
        )

        track.visibility_state = (
            HandTrackVisibilityState.VISIBLE
        )

        track.displacement_pixels = (
            displacement
        )

        track.speed_pixels_per_second = (
            speed
        )

        track.velocity_x_pixels_per_second = (
            velocity_x
        )

        track.velocity_y_pixels_per_second = (
            velocity_y
        )

    # =========================================================
    # Visibility lifecycle
    # =========================================================

    def _update_visibility_states(
        self,
        timestamp_seconds: float,
    ) -> None:

        for track in (
            self._tracks.values()
        ):

            missing_duration = max(
                0.0,
                timestamp_seconds
                - track.last_visible_timestamp_seconds,
            )

            if (
                missing_duration
                <= 1e-9
            ):
                track.visibility_state = (
                    HandTrackVisibilityState.VISIBLE
                )

            elif (
                missing_duration
                <= self._missing_tolerance_seconds
            ):
                track.visibility_state = (
                    HandTrackVisibilityState.TEMPORARILY_MISSING
                )

            else:
                track.visibility_state = (
                    HandTrackVisibilityState.LOST
                )

            track.last_timestamp_seconds = (
                timestamp_seconds
            )

    def _prune_stale_tracks(
        self,
        timestamp_seconds: float,
    ) -> None:
        """
        Delete LOST tracks after a short retention period.

        This prevents old track IDs from accumulating
        indefinitely in the visualization.
        """

        track_ids_to_remove = []

        for (
            track_id,
            track,
        ) in self._tracks.items():

            if (
                track.visibility_state
                != HandTrackVisibilityState.LOST
            ):
                continue

            missing_duration = max(
                0.0,
                timestamp_seconds
                - track.last_visible_timestamp_seconds,
            )

            remove_after = (
                self._missing_tolerance_seconds
                + self._lost_track_retention_seconds
            )

            if (
                missing_duration
                > remove_after
            ):
                track_ids_to_remove.append(
                    track_id
                )

        for track_id in (
            track_ids_to_remove
        ):
            del self._tracks[
                track_id
            ]

    # =========================================================
    # Motion prediction
    # =========================================================

    def _predict_center(
        self,
        track: _MutableHandTrack,
        timestamp_seconds: float,
    ) -> Point2DFloat:

        if (
            track.last_palm_center
            is None
        ):
            return (
                0.0,
                0.0,
            )

        elapsed = max(
            0.0,
            timestamp_seconds
            - track.last_visible_timestamp_seconds,
        )

        prediction_time = min(
            elapsed,
            self._maximum_prediction_seconds,
        )

        predicted_x = (
            track.last_palm_center[0]
            + track.velocity_x_pixels_per_second
            * prediction_time
        )

        predicted_y = (
            track.last_palm_center[1]
            + track.velocity_y_pixels_per_second
            * prediction_time
        )

        return (
            predicted_x,
            predicted_y,
        )

    # =========================================================
    # Snapshot
    # =========================================================

    def _snapshot(
        self,
        timestamp_seconds: float,
    ) -> Tuple[
        HandTrackResult,
        ...,
    ]:

        results = []

        for track_id in sorted(
            self._tracks.keys()
        ):

            track = (
                self._tracks[
                    track_id
                ]
            )

            track_age_seconds = max(
                0.0,
                timestamp_seconds
                - track.first_timestamp_seconds,
            )

            missing_duration_seconds = max(
                0.0,
                timestamp_seconds
                - track.last_visible_timestamp_seconds,
            )

            if (
                track.visibility_state
                == HandTrackVisibilityState.VISIBLE
            ):

                spatial_dwell_seconds = max(
                    0.0,
                    timestamp_seconds
                    - track.spatial_state_start_timestamp_seconds,
                )

            else:

                spatial_dwell_seconds = max(
                    0.0,
                    track.last_visible_timestamp_seconds
                    - track.spatial_state_start_timestamp_seconds,
                )

            results.append(
                HandTrackResult(
                    track_id=(
                        track.track_id
                    ),

                    visibility_state=(
                        track.visibility_state
                    ),

                    model_handedness_label=(
                        track.model_handedness_label
                    ),

                    palm_center=(
                        track.last_palm_center
                    ),

                    spatial_state=(
                        track.current_spatial_state
                    ),

                    spatial_dwell_seconds=(
                        spatial_dwell_seconds
                    ),

                    track_age_seconds=(
                        track_age_seconds
                    ),

                    missing_duration_seconds=(
                        missing_duration_seconds
                    ),

                    displacement_pixels=(
                        track.displacement_pixels
                    ),

                    speed_pixels_per_second=(
                        track.speed_pixels_per_second
                    ),
                )
            )

        return tuple(
            results
        )

    # =========================================================
    # Helpers
    # =========================================================

    def _confident_handedness_mismatch(
        self,
        track: _MutableHandTrack,
        observation: HandObservation,
    ) -> bool:

        track_label = (
            track.model_handedness_label
        )

        observation_label = (
            observation.model_handedness_label
        )

        if (
            track_label is None
            or observation_label is None
        ):
            return False

        track_score = (
            track.model_handedness_score
        )

        observation_score = (
            observation.model_handedness_score
        )

        if (
            track_score is None
            or observation_score is None
        ):
            return False

        if (
            track_score
            < self._handedness_confidence_threshold
            or observation_score
            < self._handedness_confidence_threshold
        ):
            return False

        return (
            track_label.strip().lower()
            != observation_label.strip().lower()
        )

    @staticmethod
    def _distance(
        point_a: Point2DFloat,
        point_b: Point2DFloat,
    ) -> float:

        return math.hypot(
            point_a[0]
            - point_b[0],

            point_a[1]
            - point_b[1],
        )


def build_hand_observations(
    detected_hands: Tuple[
        DetectedHand,
        ...,
    ],
    geometry_results: Tuple[
        HandGeometryResult,
        ...,
    ],
    spatial_results: Tuple[
        HandSpatialResult,
        ...,
    ],
) -> Tuple[
    HandObservation,
    ...,
]:
    """
    Convert aligned per-frame M8 outputs into tracker observations.
    """

    observations = []

    for (
        hand,
        geometry,
        spatial,
    ) in zip(
        detected_hands,
        geometry_results,
        spatial_results,
    ):

        if not (
            geometry.geometry_valid
        ):
            continue

        observations.append(
            HandObservation(
                model_handedness_label=(
                    hand.model_handedness_label
                ),

                model_handedness_score=(
                    hand.model_handedness_score
                ),

                palm_center=(
                    geometry.palm_center
                ),

                geometry=(
                    geometry
                ),

                spatial=(
                    spatial
                ),
            )
        )

    return tuple(
        observations
    )