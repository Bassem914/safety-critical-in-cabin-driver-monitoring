from typing import Dict, Optional, Tuple

import cv2
import numpy as np


Point2D = Tuple[int, int]


def _enum_value(value) -> str:
    if value is None:
        return "N/A"
    return str(getattr(value, "value", value))


def _fmt(value, precision: int = 2) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.{precision}f}"
    except (TypeError, ValueError):
        return str(value)


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
                (
                    point[0] + 5,
                    point[1] - 5,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                color,
                1,
                cv2.LINE_AA,
            )


def draw_body_landmarks(
    frame,
    body_pose,
) -> None:
    """
    Draw the selected M7 shoulder/hip landmarks.
    """

    if body_pose is None:
        return

    colors = {
        "left_shoulder": (0, 170, 0),
        "right_shoulder": (0, 170, 0),
        "left_hip": (0, 190, 220),
        "right_hip": (0, 190, 220),
    }

    for name, landmark in (
        body_pose.landmarks.items()
    ):

        cv2.circle(
            frame,
            landmark.pixel,
            6,
            colors.get(
                name,
                (255, 255, 255),
            ),
            -1,
        )


def draw_hand_landmarks(
    frame,
    detection_result,
) -> None:
    """
    Draw current-frame M8 hand landmarks.

    D1/D2 are frame-local detections, not persistent identities.
    """

    if detection_result is None:
        return

    for detection_index, hand in enumerate(
        detection_result.hands,
        start=1,
    ):

        for landmark in hand.landmarks.values():

            cv2.circle(
                frame,
                landmark.pixel,
                4,
                (0, 255, 0),
                -1,
            )

        wrist = hand.landmarks.get(
            "wrist"
        )

        middle_mcp = hand.landmarks.get(
            "middle_mcp"
        )

        if (
            wrist is not None
            and middle_mcp is not None
        ):

            cv2.line(
                frame,
                wrist.pixel,
                middle_mcp.pixel,
                (0, 255, 255),
                2,
            )

        if wrist is not None:

            cv2.putText(
                frame,
                f"D{detection_index}",
                (
                    wrist.pixel[0] + 7,
                    wrist.pixel[1] - 7,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.58,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )


def draw_hand_tracks(
    frame,
    track_results,
) -> None:
    """
    Draw temporal hand-track centers.

    T* identifiers are prototype temporal identities and are not
    guaranteed to remain stable through long occlusions.
    """

    if track_results is None:
        return

    for track in track_results:

        if track.palm_center is None:
            continue

        if (
            _enum_value(
                track.visibility_state
            )
            == "LOST"
        ):
            continue

        point = (
            int(
                round(
                    track.palm_center[0]
                )
            ),
            int(
                round(
                    track.palm_center[1]
                )
            ),
        )

        cv2.circle(
            frame,
            point,
            10,
            (255, 0, 255),
            2,
        )

        cv2.putText(
            frame,
            f"T{track.track_id}",
            (
                point[0] + 10,
                point[1] - 10,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (255, 0, 255),
            2,
            cv2.LINE_AA,
        )


def draw_milestone_title(
    frame,
    milestone_text: str,
) -> None:
    """
    Draw milestone title on the image region.
    """

    cv2.rectangle(
        frame,
        (0, 0),
        (
            frame.shape[1],
            42,
        ),
        (0, 0, 0),
        -1,
    )

    cv2.putText(
        frame,
        milestone_text,
        (16, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


def create_dashboard_canvas(
    frame,
    sidebar_width: int = 360,
):
    """
    Create the existing image + white sidebar dashboard.
    """

    height, width = (
        frame.shape[:2]
    )

    canvas_height = max(
        height,
        620,
    )

    canvas = np.full(
        (
            canvas_height,
            width + sidebar_width,
            3,
        ),
        255,
        dtype=np.uint8,
    )

    canvas[
        :height,
        :width,
    ] = frame

    cv2.line(
        canvas,
        (
            width,
            0,
        ),
        (
            width,
            canvas_height,
        ),
        (210, 210, 210),
        1,
    )

    return (
        canvas,
        width,
    )


def draw_dashboard_sidebar(
    canvas,
    image_width: int,
    fps: float,
    face_detected: bool,
    landmark_count: int,
    source_name: str,
    frame_index: int,
    timestamp_seconds: float,
    features=None,
    temporal_result=None,
    head_pose_result=None,
    gaze_result=None,
) -> None:
    """
    Draw the M1-M6 dashboard summary.

    This function intentionally keeps the established interface used by
    the integrated pipeline.
    """

    x = (
        image_width
        + 16
    )

    y = 32

    line_height = 26

    def line(
        label,
        value,
        *,
        color=(45, 45, 45),
        bold=False,
        step=line_height,
    ):
        nonlocal y

        cv2.putText(
            canvas,
            f"{label}: {value}",
            (
                x,
                y,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.53,
            color,
            2 if bold else 1,
            cv2.LINE_AA,
        )

        y += step

    cv2.putText(
        canvas,
        "M1-M6  FACE / HEAD / GAZE",
        (
            x,
            y,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (25, 25, 25),
        2,
        cv2.LINE_AA,
    )

    y += 38

    line(
        "FPS",
        f"{fps:.1f}",
        bold=True,
    )

    line(
        "Face",
        (
            "DETECTED"
            if face_detected
            else "LOST"
        ),
    )

    line(
        "Face landmarks",
        landmark_count,
    )

    if features is not None:

        line(
            "EAR",
            _fmt(
                features.get(
                    "ear"
                ),
                3,
            ),
        )

        line(
            "MAR",
            _fmt(
                features.get(
                    "mar"
                ),
                3,
            ),
        )

    else:

        line(
            "EAR",
            "N/A",
        )

        line(
            "MAR",
            "N/A",
        )

    if temporal_result is not None:

        line(
            "Temporal",
            _enum_value(
                getattr(
                    temporal_result,
                    "primary_state",
                    None,
                )
            ),
        )

    else:

        line(
            "Temporal",
            "N/A",
        )

    y += 6

    if head_pose_result is not None:

        line(
            "Head yaw",
            _fmt(
                getattr(
                    head_pose_result,
                    "yaw_degrees",
                    None,
                ),
                1,
            )
            + " deg",
        )

        line(
            "Head pitch",
            _fmt(
                getattr(
                    head_pose_result,
                    "pitch_degrees",
                    None,
                ),
                1,
            )
            + " deg",
        )

        line(
            "Head roll",
            _fmt(
                getattr(
                    head_pose_result,
                    "roll_degrees",
                    None,
                ),
                1,
            )
            + " deg",
        )

    else:

        line(
            "Head pose",
            "N/A",
        )

    y += 6

    if gaze_result is not None:

        line(
            "Gaze",
            _enum_value(
                getattr(
                    gaze_result,
                    "direction",
                    None,
                )
            ),
        )

        line(
            "Gaze H",
            _fmt(
                getattr(
                    gaze_result,
                    "horizontal_ratio",
                    None,
                ),
                3,
            ),
        )

        line(
            "Gaze V",
            _fmt(
                getattr(
                    gaze_result,
                    "vertical_ratio",
                    None,
                ),
                3,
            ),
        )

    else:

        line(
            "Gaze",
            "N/A",
        )

    y += 12

    line(
        "Frame",
        frame_index,
    )

    line(
        "Time",
        (
            f"{timestamp_seconds:.2f} s"
        ),
    )

    source_label = str(
        source_name
    )

    if len(
        source_label
    ) > 44:

        source_label = (
            "..."
            + source_label[
                -41:
            ]
        )

    line(
        "Source",
        source_label,
        step=24,
    )


def append_body_dashboard(
    canvas,
    body_pose,
    body_geometry,
    body_posture,
    estimator,
):
    """
    Append the existing M7 prototype body-posture panel.
    """

    height, width = (
        canvas.shape[:2]
    )

    panel_width = 420

    out = np.full(
        (
            max(
                height,
                620,
            ),
            width + panel_width,
            3,
        ),
        255,
        dtype=np.uint8,
    )

    out[
        :height,
        :width,
    ] = canvas

    cv2.line(
        out,
        (
            width,
            0,
        ),
        (
            width,
            out.shape[0],
        ),
        (210, 210, 210),
        1,
    )

    x = (
        width
        + 16
    )

    y = 36

    def line(
        label,
        value,
        *,
        color=(45, 45, 45),
        step=30,
    ):
        nonlocal y

        cv2.putText(
            out,
            f"{label}: {value}",
            (
                x,
                y,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            color,
            1,
            cv2.LINE_AA,
        )

        y += step

    cv2.putText(
        out,
        "M7  BODY POSTURE (PROTOTYPE)",
        (
            x,
            y,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (25, 25, 25),
        2,
        cv2.LINE_AA,
    )

    y += 40

    if body_pose is None:

        pose_status = (
            "NOT DETECTED"
        )

    elif (
        body_pose.all_required_landmarks_visible
    ):

        pose_status = (
            "VALID"
        )

    else:

        pose_status = (
            "LOW VISIBILITY"
        )

    line(
        "Pose",
        pose_status,
    )

    line(
        "Geometry",
        (
            "VALID"
            if (
                body_geometry is not None
                and body_geometry.geometry_valid
            )
            else "INVALID"
        ),
    )

    calibration_status = (
        "CALIBRATING"
        if estimator.is_calibrating
        else (
            "CALIBRATED"
            if estimator.is_calibrated
            else "NOT CALIBRATED"
        )
    )

    line(
        "Calibration",
        calibration_status,
    )

    (
        valid_count,
        target_count,
    ) = estimator.calibration_progress

    line(
        "Neutral samples",
        (
            f"{valid_count}/"
            f"{target_count}"
        ),
    )

    line(
        "Lateral",
        _enum_value(
            body_posture.lateral_state
        ),
    )

    line(
        "Sagittal",
        _enum_value(
            body_posture.sagittal_state
        ),
    )

    y += 6

    line(
        "Lateral angle",
        _fmt(
            body_posture.torso_lateral_angle_degrees,
            2,
        )
        + " deg",
    )

    line(
        "Current torso dZ",
        _fmt(
            (
                body_geometry.torso_depth_delta
                if body_geometry is not None
                else None
            ),
            4,
        ),
    )

    line(
        "Neutral torso dZ",
        _fmt(
            estimator.neutral_torso_depth_delta,
            4,
        ),
    )

    line(
        "Relative dZ",
        _fmt(
            body_posture.torso_depth_change,
            4,
        ),
    )

    line(
        "Normalized torso",
        _fmt(
            (
                body_geometry.normalized_torso_length
                if body_geometry is not None
                else None
            ),
            3,
        ),
    )

    y += 8

    cv2.putText(
        out,
        "C: calibrate  |  R: reset  |  Q: quit",
        (
            x,
            y,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.44,
        (60, 60, 60),
        1,
        cv2.LINE_AA,
    )

    y += 28

    cv2.putText(
        out,
        "Non-metric depth; lateral/sagittal coupling",
        (
            x,
            y,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.40,
        (90, 90, 90),
        1,
        cv2.LINE_AA,
    )

    y += 21

    cv2.putText(
        out,
        "remains a documented prototype limitation.",
        (
            x,
            y,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.40,
        (90, 90, 90),
        1,
        cv2.LINE_AA,
    )

    return out


def append_hand_dashboard(
    canvas,
    detection_result,
    geometry_results,
    spatial_results,
    track_results,
):
    """
    Append the M8 hand-activity prototype panel.

    The panel reports observable geometry and temporal tracking only.
    It does not infer phone use, steering-wheel contact, distraction,
    engagement, or safety state.
    """

    height, width = (
        canvas.shape[:2]
    )

    panel_width = 455

    out = np.full(
        (
            max(
                height,
                620,
            ),
            width + panel_width,
            3,
        ),
        255,
        dtype=np.uint8,
    )

    out[
        :height,
        :width,
    ] = canvas

    cv2.line(
        out,
        (
            width,
            0,
        ),
        (
            width,
            out.shape[0],
        ),
        (210, 210, 210),
        1,
    )

    x = (
        width
        + 16
    )

    y = 36

    def line(
        text,
        *,
        color=(45, 45, 45),
        step=25,
        bold=False,
    ):
        nonlocal y

        cv2.putText(
            out,
            text,
            (
                x,
                y,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.49,
            color,
            2 if bold else 1,
            cv2.LINE_AA,
        )

        y += step

    cv2.putText(
        out,
        "M8  HAND ACTIVITY (PROTOTYPE)",
        (
            x,
            y,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (25, 25, 25),
        2,
        cv2.LINE_AA,
    )

    y += 40

    line(
        (
            "Hands detected: "
            f"{detection_result.hand_count}"
        ),
        bold=True,
    )

    line(
        (
            "Visibility: "
            f"{_enum_value(detection_result.visibility_state)}"
        ),
    )

    y += 7

    for index, (
        hand,
        geometry,
        spatial,
    ) in enumerate(
        zip(
            detection_result.hands,
            geometry_results,
            spatial_results,
        ),
        start=1,
    ):

        label = (
            hand.model_handedness_label
            or "UNKNOWN"
        )

        confidence = _fmt(
            hand.model_handedness_score,
            2,
        )

        line(
            (
                f"D{index} model: "
                f"{label} ({confidence})"
            ),
            color=(0, 120, 0),
            bold=True,
        )

        line(
            (
                "  shape: "
                f"{_enum_value(geometry.open_state)}"
            ),
        )

        line(
            (
                "  region: "
                f"{_enum_value(spatial.state)}"
            ),
        )

        if (
            spatial.normalized_distance_to_face
            is not None
        ):

            line(
                (
                    "  face distance/scale: "
                    f"{_fmt(spatial.normalized_distance_to_face, 2)}"
                ),
            )

        y += 4

    line(
        "Temporal tracks:",
        bold=True,
        step=27,
    )

    # Keep the integrated dashboard readable even when the current
    # prototype tracker creates stale identities. Show active/recent tracks.
    active_tracks = [
        track
        for track in track_results
        if _enum_value(
            track.visibility_state
        ) != "LOST"
    ]

    tracks_to_show = (
        active_tracks[-3:]
        if active_tracks
        else list(
            track_results[-2:]
        )
    )

    if not tracks_to_show:

        line(
            "  none",
        )

    for track in tracks_to_show:

        line(
            (
                f"  T{track.track_id}: "
                f"{_enum_value(track.visibility_state)}"
            ),
            color=(120, 0, 120),
        )

        line(
            (
                "    region="
                f"{_enum_value(track.spatial_state)}"
            ),
        )

        line(
            (
                "    dwell="
                f"{_fmt(track.spatial_dwell_seconds, 2)} s"
            ),
        )

        line(
            (
                "    speed="
                f"{_fmt(track.speed_pixels_per_second, 1)} px/s"
            ),
        )

    y += 7

    line(
        "Geometry only; no behavior/safety judgment.",
        color=(90, 90, 90),
        step=23,
    )

    line(
        "Temporal identity persistence needs refinement.",
        color=(90, 90, 90),
        step=23,
    )

    return out


# -----------------------------------------------------------------
# Legacy overlay helpers retained for experiment compatibility.
# -----------------------------------------------------------------

def draw_status_overlay(
    frame,
    fps: float,
    face_detected: bool,
    landmark_count: int,
    milestone_text: str,
    features: Optional[
        Dict[str, float]
    ] = None,
) -> None:

    frame_height = (
        frame.shape[0]
    )

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (
            20,
            35,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        (
            "Driver Face: DETECTED"
            if face_detected
            else "Driver Face: LOST"
        ),
        (
            20,
            75,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (
            (0, 255, 0)
            if face_detected
            else (0, 0, 255)
        ),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        (
            "Tracked landmarks: "
            f"{landmark_count}"
        ),
        (
            20,
            110,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    if features is not None:

        ear_text = (
            f"EAR: {features['ear']:.3f}"
        )

        mar_text = (
            f"MAR: {features['mar']:.3f}"
        )

    else:

        ear_text = (
            "EAR: N/A"
        )

        mar_text = (
            "MAR: N/A"
        )

    cv2.putText(
        frame,
        ear_text,
        (
            20,
            145,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        mar_text,
        (
            20,
            180,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        milestone_text,
        (
            20,
            frame_height - 30,
        ),
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

    cv2.putText(
        frame,
        (
            "Source time: "
            f"{timestamp_seconds:.2f} s"
        ),
        (
            20,
            215,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        (
            "Frame index: "
            f"{frame_index}"
        ),
        (
            20,
            245,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    source_label = (
        str(
            source_name
        )
    )

    if len(
        source_label
    ) > 65:

        source_label = (
            "..."
            + source_label[
                -62:
            ]
        )

    cv2.putText(
        frame,
        (
            "Source: "
            f"{source_label}"
        ),
        (
            20,
            275,
        ),
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

    state_name = (
        temporal_result.primary_state.value
    )

    state_colors = {
        "NORMAL": (
            0,
            255,
            0,
        ),
        "BLINK_CANDIDATE": (
            0,
            255,
            255,
        ),
        "PROLONGED_EYE_CLOSURE": (
            0,
            0,
            255,
        ),
        "SUSTAINED_MOUTH_OPENING": (
            0,
            165,
            255,
        ),
        "PROLONGED_FACE_LOSS": (
            255,
            0,
            255,
        ),
    }

    state_color = (
        state_colors.get(
            state_name,
            (255, 255, 255),
        )
    )

    cv2.putText(
        frame,
        (
            "Temporal state: "
            f"{state_name}"
        ),
        (
            20,
            300,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        state_color,
        2,
        cv2.LINE_AA,
    )
