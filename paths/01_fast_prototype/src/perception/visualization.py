from typing import Dict, Optional, Tuple

import cv2


Point2D = Tuple[int, int]


def _draw_text(
    frame,
    text: str,
    position: Tuple[int, int],
    font_scale: float,
    color: Tuple[int, int, int],
    thickness: int = 1,
) -> None:
    """
    Draw readable text with a black outline.
    """

    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 0, 0),
        thickness + 2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def _draw_overlay_panel(
    frame,
    width: int = 330,
    alpha: float = 0.45,
) -> None:
    """
    Draw a semi-transparent dark panel on the left side
    for better readability.
    """

    overlay = frame.copy()
    panel_height = frame.shape[0]

    cv2.rectangle(
        overlay,
        (0, 0),
        (width, panel_height),
        (25, 25, 25),
        -1,
    )

    cv2.addWeighted(
        overlay,
        alpha,
        frame,
        1.0 - alpha,
        0,
        frame,
    )


def draw_selected_landmarks(
    frame,
    landmarks: Dict[str, Point2D],
    draw_labels: bool = False,
    color: Tuple[int, int, int] = (0, 255, 0),
) -> None:
    """
    Draw selected facial landmarks.
    """

    for name, point in landmarks.items():
        cv2.circle(frame, point, 4, color, -1)

        if draw_labels:
            _draw_text(
                frame=frame,
                text=name,
                position=(point[0] + 5, point[1] - 5),
                font_scale=0.35,
                color=color,
                thickness=1,
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
    Draw top-level runtime and face-feature status.
    """

    _draw_overlay_panel(frame)

    frame_height = frame.shape[0]

    if face_detected:
        status_text = "Driver Face: DETECTED"
        status_color = (0, 255, 0)
    else:
        status_text = "Driver Face: LOST"
        status_color = (0, 0, 255)

    ear_text = (
        f"EAR: {features['ear']:.3f}"
        if features is not None
        else "EAR: N/A"
    )

    mar_text = (
        f"MAR: {features['mar']:.3f}"
        if features is not None
        else "MAR: N/A"
    )

    _draw_text(
        frame,
        f"FPS: {fps:.1f}",
        (20, 35),
        0.85,
        (0, 255, 0),
        2,
    )

    _draw_text(
        frame,
        status_text,
        (20, 75),
        0.82,
        status_color,
        2,
    )

    _draw_text(
        frame,
        f"Tracked landmarks: {landmark_count}",
        (20, 110),
        0.68,
        (235, 235, 235),
        2,
    )

    _draw_text(
        frame,
        ear_text,
        (20, 145),
        0.68,
        (235, 235, 235),
        2,
    )

    _draw_text(
        frame,
        mar_text,
        (20, 180),
        0.68,
        (235, 235, 235),
        2,
    )

    _draw_text(
        frame,
        milestone_text,
        (20, frame_height - 18),
        0.60,
        (255, 255, 255),
        2,
    )


def draw_source_metadata_overlay(
    frame,
    source_name: str,
    frame_index: int,
    timestamp_seconds: float,
) -> None:
    """
    Draw source metadata.
    """

    source_label = source_name

    if len(source_label) > 45:
        source_label = f"...{source_label[-42:]}"

    _draw_text(
        frame,
        f"Source time: {timestamp_seconds:.2f} s",
        (20, 215),
        0.58,
        (220, 220, 220),
        1,
    )

    _draw_text(
        frame,
        f"Frame index: {frame_index}",
        (20, 242),
        0.58,
        (220, 220, 220),
        1,
    )

    _draw_text(
        frame,
        f"Source: {source_label}",
        (20, 269),
        0.52,
        (200, 200, 200),
        1,
    )


def draw_temporal_state_overlay(
    frame,
    temporal_result,
) -> None:
    """
    Draw temporal-state summary.
    """

    state_name = temporal_result.primary_state.value

    state_colors = {
        "NORMAL": (0, 255, 0),
        "BLINK_CANDIDATE": (0, 255, 255),
        "PROLONGED_EYE_CLOSURE": (0, 80, 255),
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
    line_spacing = 24

    _draw_text(
        frame,
        state_text,
        (start_x, start_y),
        0.60,
        state_color,
        2,
    )

    measurement_lines = (
        smoothed_ear_text,
        smoothed_mar_text,
        eye_duration_text,
        mouth_duration_text,
        face_loss_text,
    )

    for index, text in enumerate(measurement_lines, start=1):
        _draw_text(
            frame,
            text,
            (start_x, start_y + index * line_spacing),
            0.54,
            (230, 230, 230),
            1,
        )


def draw_head_pose_overlay(
    frame,
    head_pose_result,
) -> None:
    """
    Draw head-pose measurements on the upper-right side
    of the current frame.
    """

    frame_width = frame.shape[1]

    if head_pose_result is None:
        yaw_text = "Yaw: N/A"
        pitch_text = "Pitch: N/A"
        roll_text = "Roll: N/A"
    else:
        yaw_text = (
            f"Yaw: {head_pose_result.yaw_degrees:.1f} deg"
        )

        pitch_text = (
            f"Pitch: {head_pose_result.pitch_degrees:.1f} deg"
        )

        roll_text = (
            f"Roll: {head_pose_result.roll_degrees:.1f} deg"
        )

    panel_width = 230
    panel_height = 145
    margin = 15

    panel_left = max(
        0,
        frame_width - panel_width - margin,
    )

    panel_top = 15

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (panel_left, panel_top),
        (
            frame_width - margin,
            panel_top + panel_height,
        ),
        (25, 25, 25),
        -1,
    )

    cv2.addWeighted(
        overlay,
        0.55,
        frame,
        0.45,
        0,
        frame,
    )

    text_x = panel_left + 15

    _draw_text(
        frame,
        "HEAD POSE",
        (text_x, panel_top + 30),
        0.60,
        (120, 210, 255),
        2,
    )

    pose_lines = (
        yaw_text,
        pitch_text,
        roll_text,
    )

    for index, text in enumerate(
        pose_lines,
        start=1,
    ):
        _draw_text(
            frame,
            text,
            (
                text_x,
                panel_top + 30 + index * 28,
            ),
            0.55,
            (240, 240, 240),
            1,
        )