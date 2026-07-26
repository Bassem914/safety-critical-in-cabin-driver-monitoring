from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Deque, Optional


class TemporalState(str, Enum):
    """
    Interpretable face-level temporal candidates.

    These states are prototype decision outputs, not final medical
    diagnoses or production safety classifications.
    """

    NORMAL = "NORMAL"
    BLINK_CANDIDATE = "BLINK_CANDIDATE"
    PROLONGED_EYE_CLOSURE = "PROLONGED_EYE_CLOSURE"
    SUSTAINED_MOUTH_OPENING = "SUSTAINED_MOUTH_OPENING"
    PROLONGED_FACE_LOSS = "PROLONGED_FACE_LOSS"


@dataclass(frozen=True)
class TemporalRuleConfig:
    """
    Configuration for the face-level temporal rule baseline.

    The default thresholds are initial prototype values and require
    later calibration using multiple drivers, cabin conditions,
    camera positions, and recorded datasets.
    """

    eye_closed_ear_threshold: float = 0.20
    mouth_open_mar_threshold: float = 0.60

    blink_min_duration_seconds: float = 0.08
    blink_max_duration_seconds: float = 0.50
    blink_display_hold_seconds: float = 0.40

    prolonged_eye_closure_seconds: float = 1.50
    sustained_mouth_opening_seconds: float = 1.00
    prolonged_face_loss_seconds: float = 1.00

    smoothing_window_size: int = 5


@dataclass(frozen=True)
class TemporalDecisionResult:
    """
    Result produced by one temporal-rule update.

    Attributes:
        primary_state:
            Highest-priority temporal candidate.

        smoothed_ear:
            Moving-average Eye Aspect Ratio.

        smoothed_mar:
            Moving-average Mouth Aspect Ratio.

        eye_closure_duration_seconds:
            Current continuous eye-closure duration.

        mouth_open_duration_seconds:
            Current continuous mouth-opening duration.

        face_loss_duration_seconds:
            Current continuous face-loss duration.

        blink_detected:
            True for the update immediately after a valid blink ends.
    """

    primary_state: TemporalState
    smoothed_ear: Optional[float]
    smoothed_mar: Optional[float]
    eye_closure_duration_seconds: float
    mouth_open_duration_seconds: float
    face_loss_duration_seconds: float
    blink_detected: bool


class TemporalRuleEngine:
    """
    Convert frame-level facial measurements into temporal candidates.

    Source timestamps are used instead of processing FPS. This keeps
    duration calculations consistent for live and recorded inputs.
    """

    def __init__(
        self,
        config: Optional[TemporalRuleConfig] = None,
    ) -> None:
        self._config = config or TemporalRuleConfig()

        self._validate_config()

        self._ear_history: Deque[float] = deque(
            maxlen=self._config.smoothing_window_size
        )

        self._mar_history: Deque[float] = deque(
            maxlen=self._config.smoothing_window_size
        )

        self._eye_closure_start: Optional[float] = None
        self._mouth_open_start: Optional[float] = None
        self._face_loss_start: Optional[float] = None
        self._blink_display_until: Optional[float] = None

        self._previous_timestamp: Optional[float] = None

    @property
    def config(self) -> TemporalRuleConfig:
        """Return the active temporal-rule configuration."""

        return self._config

    def update(
        self,
        timestamp_seconds: float,
        face_detected: bool,
        ear: Optional[float],
        mar: Optional[float],
    ) -> TemporalDecisionResult:
        """
        Update temporal reasoning using one timestamped observation.
        """

        self._validate_timestamp(timestamp_seconds)

        if not face_detected:
            result = self._handle_face_loss(
                timestamp_seconds=timestamp_seconds
            )

            self._previous_timestamp = timestamp_seconds
            return result

        result = self._handle_visible_face(
            timestamp_seconds=timestamp_seconds,
            ear=ear,
            mar=mar,
        )

        self._previous_timestamp = timestamp_seconds
        return result

    def reset(self) -> None:
        """Reset histories, timers, and timestamp state."""

        self._ear_history.clear()
        self._mar_history.clear()

        self._eye_closure_start = None
        self._mouth_open_start = None
        self._face_loss_start = None
        self._blink_display_until = None

        self._previous_timestamp = None

    def _handle_face_loss(
        self,
        timestamp_seconds: float,
    ) -> TemporalDecisionResult:
        """Process an observation in which no face was detected."""

        self._ear_history.clear()
        self._mar_history.clear()

        self._eye_closure_start = None
        self._mouth_open_start = None

        if self._face_loss_start is None:
            self._face_loss_start = timestamp_seconds

        face_loss_duration = self._calculate_duration(
            start_timestamp=self._face_loss_start,
            current_timestamp=timestamp_seconds,
        )

        primary_state = TemporalState.NORMAL

        if (
            face_loss_duration
            >= self._config.prolonged_face_loss_seconds
        ):
            primary_state = TemporalState.PROLONGED_FACE_LOSS

        return TemporalDecisionResult(
            primary_state=primary_state,
            smoothed_ear=None,
            smoothed_mar=None,
            eye_closure_duration_seconds=0.0,
            mouth_open_duration_seconds=0.0,
            face_loss_duration_seconds=face_loss_duration,
            blink_detected=False,
        )

    def _handle_visible_face(
        self,
        timestamp_seconds: float,
        ear: Optional[float],
        mar: Optional[float],
    ) -> TemporalDecisionResult:
        """Process an observation in which the face is visible."""

        self._face_loss_start = None

        smoothed_ear = self._update_moving_average(
            history=self._ear_history,
            value=ear,
        )

        smoothed_mar = self._update_moving_average(
            history=self._mar_history,
            value=mar,
        )

        (
            eye_closure_duration,
            blink_detected,
        ) = self._update_eye_state(
            timestamp_seconds=timestamp_seconds,
            smoothed_ear=smoothed_ear,
        )
        if blink_detected:
            self._blink_display_until = (
                timestamp_seconds
                + self._config.blink_display_hold_seconds
            )

        blink_candidate_active = (
            self._blink_display_until is not None
            and timestamp_seconds <= self._blink_display_until
        )
        

        mouth_open_duration = self._update_mouth_state(
            timestamp_seconds=timestamp_seconds,
            smoothed_mar=smoothed_mar,
        )

        primary_state = self._select_primary_state(
            blink_candidate_active=blink_candidate_active,
            eye_closure_duration=eye_closure_duration,
            mouth_open_duration=mouth_open_duration,
        )

        return TemporalDecisionResult(
            primary_state=primary_state,
            smoothed_ear=smoothed_ear,
            smoothed_mar=smoothed_mar,
            eye_closure_duration_seconds=eye_closure_duration,
            mouth_open_duration_seconds=mouth_open_duration,
            face_loss_duration_seconds=0.0,
            blink_detected=blink_detected,
        )

    def _update_eye_state(
        self,
        timestamp_seconds: float,
        smoothed_ear: Optional[float],
    ) -> tuple[float, bool]:
        """Update eye-closure duration and blink detection."""

        blink_detected = False
        eye_closure_duration = 0.0

        eyes_closed = (
            smoothed_ear is not None
            and smoothed_ear
            < self._config.eye_closed_ear_threshold
        )

        if eyes_closed:
            if self._eye_closure_start is None:
                self._eye_closure_start = timestamp_seconds

            eye_closure_duration = self._calculate_duration(
                start_timestamp=self._eye_closure_start,
                current_timestamp=timestamp_seconds,
            )

            return eye_closure_duration, blink_detected

        if self._eye_closure_start is not None:
            completed_closure_duration = self._calculate_duration(
                start_timestamp=self._eye_closure_start,
                current_timestamp=timestamp_seconds,
            )

            blink_detected = (
                self._config.blink_min_duration_seconds
                <= completed_closure_duration
                <= self._config.blink_max_duration_seconds
            )

        self._eye_closure_start = None

        return eye_closure_duration, blink_detected

    def _update_mouth_state(
        self,
        timestamp_seconds: float,
        smoothed_mar: Optional[float],
    ) -> float:
        """Update continuous mouth-opening duration."""

        mouth_open_duration = 0.0

        mouth_open = (
            smoothed_mar is not None
            and smoothed_mar
            > self._config.mouth_open_mar_threshold
        )

        if mouth_open:
            if self._mouth_open_start is None:
                self._mouth_open_start = timestamp_seconds

            mouth_open_duration = self._calculate_duration(
                start_timestamp=self._mouth_open_start,
                current_timestamp=timestamp_seconds,
            )

            return mouth_open_duration

        self._mouth_open_start = None

        return mouth_open_duration

    def _select_primary_state(
        self,
        blink_candidate_active: bool,
        eye_closure_duration: float,
        mouth_open_duration: float,
    ) -> TemporalState:
        """
        Select the highest-priority active temporal candidate.

        Priority:
            1. Prolonged eye closure
            2. Sustained mouth opening
            3. Blink candidate
            4. Normal
        """

        if (
            eye_closure_duration
            >= self._config.prolonged_eye_closure_seconds
        ):
            return TemporalState.PROLONGED_EYE_CLOSURE

        if (
            mouth_open_duration
            >= self._config.sustained_mouth_opening_seconds
        ):
            return TemporalState.SUSTAINED_MOUTH_OPENING

        if blink_candidate_active:
            return TemporalState.BLINK_CANDIDATE

        return TemporalState.NORMAL

    def _validate_config(self) -> None:
        """Validate temporal-rule configuration values."""

        if self._config.smoothing_window_size < 1:
            raise ValueError(
                "smoothing_window_size must be at least 1."
            )

        if self._config.eye_closed_ear_threshold <= 0.0:
            raise ValueError(
                "eye_closed_ear_threshold must be positive."
            )

        if self._config.mouth_open_mar_threshold <= 0.0:
            raise ValueError(
                "mouth_open_mar_threshold must be positive."
            )
        if self._config.blink_display_hold_seconds < 0.0:
            raise ValueError( "blink_display_hold_seconds must not be negative."
)
        if self._config.blink_min_duration_seconds < 0.0:
            raise ValueError(
                "blink_min_duration_seconds must not be negative."
            )

        if (
            self._config.blink_max_duration_seconds
            < self._config.blink_min_duration_seconds
        ):
            raise ValueError(
                "blink_max_duration_seconds must be greater than "
                "or equal to blink_min_duration_seconds."
            )

        if self._config.prolonged_eye_closure_seconds <= 0.0:
            raise ValueError(
                "prolonged_eye_closure_seconds must be positive."
            )

        if self._config.sustained_mouth_opening_seconds <= 0.0:
            raise ValueError(
                "sustained_mouth_opening_seconds must be positive."
            )

        if self._config.prolonged_face_loss_seconds <= 0.0:
            raise ValueError(
                "prolonged_face_loss_seconds must be positive."
            )

    def _validate_timestamp(
        self,
        timestamp_seconds: float,
    ) -> None:
        """Validate source timestamp ordering."""

        if timestamp_seconds < 0.0:
            raise ValueError(
                "timestamp_seconds must not be negative."
            )

        if (
            self._previous_timestamp is not None
            and timestamp_seconds < self._previous_timestamp
        ):
            raise ValueError(
                "Source timestamps must be monotonically increasing."
            )

    @staticmethod
    def _update_moving_average(
        history: Deque[float],
        value: Optional[float],
    ) -> Optional[float]:
        """Update and return a simple moving average."""

        if value is None:
            history.clear()
            return None

        history.append(float(value))

        return sum(history) / len(history)

    @staticmethod
    def _calculate_duration(
        start_timestamp: float,
        current_timestamp: float,
    ) -> float:
        """Calculate a non-negative event duration."""

        return max(
            0.0,
            current_timestamp - start_timestamp,
        )