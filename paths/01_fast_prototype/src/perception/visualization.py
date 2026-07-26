from typing import Dict, Optional, Tuple

import cv2


Point2D = Tuple[int, int]


def draw_selected_landmarks(
    frame,
    landmarks: Dict[str, Point2D],
    draw_labels: bool = False,
    color: Tuple[int, int, int] = (0, 255, 0),
) -> None:
    """
    Draw selected facial landmarks on the frame.
    """

    for name, point in landmarks.items():
        cv2.circle(
            frame,
            point,
            4,
            color,
            -1,
        )

        if draw_labels:
            cv2.putText(
                frame,
                name,
                (point[0] + 5, point[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                color,
                1,
                cv2.LINE_AA,
            )


def draw_status_overlay(
    frame,
    fps: float,
    face_detected: bool,
    landmark_count: int,
    milestone_text: str,
    features: Optional[Dict[str, float]] = None,
) -> None:
    """
    Draw general perception-pipeline information.
    """

    frame_height = frame.shape[0]

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    if face_detected:
        status_text = "Driver Face: DETECTED"
        status_color = (0, 255, 0)
    else:
        status_text = "Driver Face: LOST"
        status_color = (0, 0, 255)

    cv2.putText(
        frame,
        status_text,
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        status_color,
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Tracked landmarks: {landmark_count}",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    if features is not None:
        ear_text = f"EAR: {features['ear']:.3f}"
        mar_text = f"MAR: {features['mar']:.3f}"
    else:
        ear_text = "EAR: N/A"
        mar_text = "MAR: N/A"

    cv2.putText(
        frame,
        ear_text,
        (20, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        mar_text,
        (20, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        milestone_text,
        (20, frame_height - 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


def draw_source_metadata_overlay(
    frame,
    source_name: str,
    frame_index: int,
    timestamp_seconds: float,
) -> None:
    """
    Draw source-related metadata on the current frame.

    Args:
        frame:
            OpenCV BGR image.

        source_name:
            Readable identifier of the active video source.

        frame_index:
            Zero-based index of the current source frame.

        timestamp_seconds:
            Current position on the source timeline.
    """

    cv2.putText(
        frame,
        f"Source time: {timestamp_seconds:.2f} s",
        (20, 215),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Frame index: {frame_index}",
        (20, 245),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    source_label = source_name

    if len(source_label) > 65:
        source_label = f"...{source_label[-62:]}"

    cv2.putText(
        frame,
        f"Source: {source_label}",
        (20, 275),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )


def draw_temporal_state_overlay(
    frame,
    temporal_result,
) -> None:
    """
    Draw temporal measurements and the active event candidate.

    The active temporal state uses a state-dependent color.
    Numerical measurements remain white for readability.
    """

    state_name = temporal_result.primary_state.value

    state_colors = {
        "NORMAL": (0, 255, 0),
        "BLINK_CANDIDATE": (0, 255, 255),
        "PROLONGED_EYE_CLOSURE": (0, 0, 255),
        "SUSTAINED_MOUTH_OPENING": (0, 165, 255),
        "PROLONGED_FACE_LOSS": (255, 0, 255),
    }

    state_color = state_colors.get(
        state_name,
        (255, 255, 255),
    )

    state_text = f"Temporal state: {state_name}"

    smoothed_ear_text = (
        f"Smoothed EAR: {temporal_result.smoothed_ear:.3f}"
        if temporal_result.smoothed_ear is not None
        else "Smoothed EAR: N/A"
    )

    smoothed_mar_text = (
        f"Smoothed MAR: {temporal_result.smoothed_mar:.3f}"
        if temporal_result.smoothed_mar is not None
        else "Smoothed MAR: N/A"
    )

    eye_duration_text = (
        "Eye closure duration: "
        f"{temporal_result.eye_closure_duration_seconds:.2f} s"
    )

    mouth_duration_text = (
        "Mouth-open duration: "
        f"{temporal_result.mouth_open_duration_seconds:.2f} s"
    )

    face_loss_text = (
        "Face-loss duration: "
        f"{temporal_result.face_loss_duration_seconds:.2f} s"
    )

    start_x = 20
    start_y = 300
    line_spacing = 25

    cv2.putText(
        frame,
        state_text,
        (start_x, start_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        state_color,
        2,
        cv2.LINE_AA,
    )

    measurement_lines = (
        smoothed_ear_text,
        smoothed_mar_text,
        eye_duration_text,
        mouth_duration_text,
        face_loss_text,
    )

    for index, text in enumerate(
        measurement_lines,
        start=1,
    ):
        cv2.putText(
            frame,
            text,
            (
                start_x,
                start_y + index * line_spacing,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )