from typing import Dict, Optional, Tuple

import cv2
import numpy as np


Point2D = Tuple[int, int]


DASHBOARD_WIDTH = 520
DASHBOARD_HEIGHT = 900


def _draw_text(
    frame,
    text: str,
    position: Tuple[int, int],
    font_scale: float,
    color: Tuple[int, int, int],
    thickness: int = 1,
) -> None:
    """
    Draw anti-aliased text.
    """

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


def _draw_image_text(
    frame,
    text: str,
    position: Tuple[int, int],
    font_scale: float,
    color: Tuple[int, int, int],
    thickness: int = 2,
) -> None:
    """
    Draw text on the video image with a dark outline.
    """

    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 0, 0),
        thickness + 3,
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


def draw_selected_landmarks(
    frame,
    landmarks: Dict[str, Point2D],
    draw_labels: bool = False,
    color: Tuple[int, int, int] = (0, 255, 0),
) -> None:
    """
    Draw selected landmarks on the original video frame.
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
            _draw_image_text(
                frame,
                name,
                (
                    point[0] + 5,
                    point[1] - 5,
                ),
                0.35,
                color,
                1,
            )


def draw_milestone_title(
    frame,
    milestone_text: str,
) -> None:
    """
    Draw the active milestone at the bottom-left of the video image.
    """

    frame_height = frame.shape[0]

    _draw_image_text(
        frame,
        milestone_text,
        (
            24,
            frame_height - 24,
        ),
        0.72,
        (255, 255, 255),
        2,
    )


def _fit_image_preserving_aspect_ratio(
    frame,
    target_height: int,
) -> np.ndarray:
    """
    Resize the video uniformly.

    Width and height are scaled by the same factor, so the original
    camera aspect ratio is preserved.
    """

    frame_height, frame_width = frame.shape[:2]

    scale = (
        target_height
        / float(frame_height)
    )

    resized_width = int(
        round(
            frame_width * scale
        )
    )

    return cv2.resize(
        frame,
        (
            resized_width,
            target_height,
        ),
        interpolation=cv2.INTER_LINEAR,
    )


def create_dashboard_canvas(
    frame,
    dashboard_width: int = DASHBOARD_WIDTH,
    dashboard_height: int = DASHBOARD_HEIGHT,
) -> Tuple[np.ndarray, int]:
    """
    Create a side-by-side visualization.

    Left:
        video image resized uniformly while preserving aspect ratio.

    Right:
        fixed white dashboard with enough vertical space for all
        measurements.

    Returns:
        canvas
        image_width_on_canvas
    """

    fitted_frame = (
        _fit_image_preserving_aspect_ratio(
            frame=frame,
            target_height=dashboard_height,
        )
    )

    image_height, image_width = (
        fitted_frame.shape[:2]
    )

    canvas = np.full(
        (
            dashboard_height,
            image_width + dashboard_width,
            3,
        ),
        255,
        dtype=np.uint8,
    )

    canvas[
        0:image_height,
        0:image_width,
    ] = fitted_frame

    cv2.line(
        canvas,
        (
            image_width,
            0,
        ),
        (
            image_width,
            dashboard_height,
        ),
        (210, 210, 210),
        2,
    )

    return canvas, image_width


def _draw_section_title(
    canvas,
    text: str,
    x: int,
    y: int,
    color: Tuple[int, int, int],
) -> int:
    """
    Draw a dashboard section title.
    """

    _draw_text(
        canvas,
        text,
        (
            x,
            y,
        ),
        0.62,
        color,
        2,
    )

    cv2.line(
        canvas,
        (
            x,
            y + 9,
        ),
        (
            canvas.shape[1] - 18,
            y + 9,
        ),
        (215, 215, 215),
        1,
    )

    return y + 31


def _draw_value_line(
    canvas,
    label: str,
    value: str,
    x: int,
    y: int,
    value_color: Tuple[int, int, int] = (25, 25, 25),
    font_scale: float = 0.49,
) -> int:
    """
    Draw one dashboard label/value pair.
    """

    _draw_text(
        canvas,
        label,
        (
            x,
            y,
        ),
        font_scale,
        (75, 75, 75),
        1,
    )

    _draw_text(
        canvas,
        value,
        (
            x + 205,
            y,
        ),
        font_scale,
        value_color,
        1,
    )

    return y + 24


def draw_dashboard_sidebar(
    canvas,
    image_width: int,
    fps: float,
    face_detected: bool,
    landmark_count: int,
    source_name: str,
    frame_index: int,
    timestamp_seconds: float,
    features: Optional[Dict[str, float]] = None,
    temporal_result=None,
    head_pose_result=None,
    gaze_result=None,
) -> None:
    """
    Draw all runtime and perception measurements in the white sidebar.
    """

    x = image_width + 22
    y = 38

    # Dashboard title
    _draw_text(
        canvas,
        "CABIN SENSING DASHBOARD",
        (
            x,
            y,
        ),
        0.72,
        (25, 25, 25),
        2,
    )

    cv2.line(
        canvas,
        (
            x,
            y + 13,
        ),
        (
            canvas.shape[1] - 18,
            y + 13,
        ),
        (190, 190, 190),
        1,
    )

    y += 48

    # Runtime
    y = _draw_section_title(
        canvas,
        "Runtime",
        x,
        y,
        (0, 110, 230),
    )

    face_text = (
        "DETECTED"
        if face_detected
        else "LOST"
    )

    face_color = (
        (0, 145, 0)
        if face_detected
        else (0, 0, 210)
    )

    y = _draw_value_line(
        canvas,
        "FPS",
        f"{fps:.1f}",
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Driver face",
        face_text,
        x,
        y,
        face_color,
    )

    y = _draw_value_line(
        canvas,
        "Tracked landmarks",
        str(landmark_count),
        x,
        y,
    )

    y += 9

    # Face geometry
    y = _draw_section_title(
        canvas,
        "Face Geometry",
        x,
        y,
        (0, 135, 0),
    )

    ear_text = (
        f"{features['ear']:.3f}"
        if features is not None
        else "N/A"
    )

    mar_text = (
        f"{features['mar']:.3f}"
        if features is not None
        else "N/A"
    )

    y = _draw_value_line(
        canvas,
        "EAR",
        ear_text,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "MAR",
        mar_text,
        x,
        y,
    )

    y += 9

    # Source
    y = _draw_section_title(
        canvas,
        "Source Metadata",
        x,
        y,
        (150, 85, 0),
    )

    if len(source_name) > 26:
        source_display = (
            f"...{source_name[-23:]}"
        )
    else:
        source_display = source_name

    y = _draw_value_line(
        canvas,
        "Source time",
        f"{timestamp_seconds:.2f} s",
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Frame index",
        str(frame_index),
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Source",
        source_display,
        x,
        y,
        font_scale=0.45,
    )

    y += 9

    # Temporal state
    y = _draw_section_title(
        canvas,
        "Temporal State",
        x,
        y,
        (150, 0, 170),
    )

    if temporal_result is None:
        state_name = "N/A"
        state_color = (70, 70, 70)

        smoothed_ear = "N/A"
        smoothed_mar = "N/A"

        eye_duration = "N/A"
        mouth_duration = "N/A"
        face_loss = "N/A"

    else:
        state_name = (
            temporal_result.primary_state.value
        )

        state_colors = {
            "NORMAL": (0, 145, 0),
            "BLINK_CANDIDATE": (0, 160, 210),
            "PROLONGED_EYE_CLOSURE": (0, 80, 220),
            "SUSTAINED_MOUTH_OPENING": (0, 140, 230),
            "PROLONGED_FACE_LOSS": (170, 0, 170),
        }

        state_color = state_colors.get(
            state_name,
            (70, 70, 70),
        )

        smoothed_ear = (
            f"{temporal_result.smoothed_ear:.3f}"
            if temporal_result.smoothed_ear is not None
            else "N/A"
        )

        smoothed_mar = (
            f"{temporal_result.smoothed_mar:.3f}"
            if temporal_result.smoothed_mar is not None
            else "N/A"
        )

        eye_duration = (
            f"{temporal_result.eye_closure_duration_seconds:.2f} s"
        )

        mouth_duration = (
            f"{temporal_result.mouth_open_duration_seconds:.2f} s"
        )

        face_loss = (
            f"{temporal_result.face_loss_duration_seconds:.2f} s"
        )

    y = _draw_value_line(
        canvas,
        "State",
        state_name,
        x,
        y,
        state_color,
    )

    y = _draw_value_line(
        canvas,
        "Smoothed EAR",
        smoothed_ear,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Smoothed MAR",
        smoothed_mar,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Eye closure",
        eye_duration,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Mouth open",
        mouth_duration,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Face loss",
        face_loss,
        x,
        y,
    )

    y += 9

    # Head pose
    y = _draw_section_title(
        canvas,
        "Head Pose",
        x,
        y,
        (220, 135, 0),
    )

    if head_pose_result is None:
        yaw_text = "N/A"
        pitch_text = "N/A"
        roll_text = "N/A"
    else:
        yaw_text = (
            f"{head_pose_result.yaw_degrees:.1f} deg"
        )

        pitch_text = (
            f"{head_pose_result.pitch_degrees:.1f} deg"
        )

        roll_text = (
            f"{head_pose_result.roll_degrees:.1f} deg"
        )

    y = _draw_value_line(
        canvas,
        "Yaw",
        yaw_text,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Pitch",
        pitch_text,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Roll",
        roll_text,
        x,
        y,
    )

    y += 9

    # Gaze
    y = _draw_section_title(
        canvas,
        "Gaze Geometry",
        x,
        y,
        (0, 135, 80),
    )

    if gaze_result is None:
        combined_h = "N/A"
        combined_v = "N/A"
        left_hv = "N/A"
        right_hv = "N/A"
        disagreement = "N/A"

        consistency = "N/A"
        consistency_color = (
            70,
            70,
            70,
        )

        direction_text = "N/A"
        direction_color = (
            70,
            70,
            70,
        )

    else:
        combined_h = (
            f"{gaze_result.horizontal_ratio:.3f}"
        )

        combined_v = (
            f"{gaze_result.vertical_ratio:.3f}"
        )

        left_hv = (
            f"{gaze_result.left_eye.horizontal_ratio:.3f}"
            " / "
            f"{gaze_result.left_eye.vertical_ratio:.3f}"
        )

        right_hv = (
            f"{gaze_result.right_eye.horizontal_ratio:.3f}"
            " / "
            f"{gaze_result.right_eye.vertical_ratio:.3f}"
        )

        disagreement = (
            f"{gaze_result.horizontal_disagreement:.3f}"
            " / "
            f"{gaze_result.vertical_disagreement:.3f}"
        )

        if gaze_result.is_consistent:
            consistency = "GOOD"
            consistency_color = (
                0,
                145,
                0,
            )
        else:
            consistency = "LOW"
            consistency_color = (
                0,
                140,
                220,
            )

        direction_text = (
            gaze_result.direction.value
        )

        if direction_text == "UNKNOWN":
            direction_color = (
                0,
                140,
                220,
            )

        elif direction_text == "CENTER":
            direction_color = (
                0,
                145,
                0,
            )

        else:
            direction_color = (
                180,
                80,
                0,
            )

    y = _draw_value_line(
        canvas,
        "Direction",
        direction_text,
        x,
        y,
        direction_color,
    )

    y = _draw_value_line(
        canvas,
        "Combined H",
        combined_h,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Combined V",
        combined_v,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Left eye H/V",
        left_hv,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "Right eye H/V",
        right_hv,
        x,
        y,
    )

    y = _draw_value_line(
        canvas,
        "dH / dV",
        disagreement,
        x,
        y,
    )

    _draw_value_line(
        canvas,
        "Consistency",
        consistency,
        x,
        y,
        consistency_color,
    )