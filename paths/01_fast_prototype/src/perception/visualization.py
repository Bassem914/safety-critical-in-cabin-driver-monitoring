from typing import Dict, Optional, Tuple

import cv2


Point2D = Tuple[int, int]


def draw_selected_landmarks(
    frame,
    landmarks: Dict[str, Point2D],
    draw_labels: bool = False,
    color: Tuple[int, int, int] = (0, 255, 0),
) -> None:
    for name, point in landmarks.items():
        cv2.circle(frame, point, 4, color, -1)

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
        cv2.putText(
            frame,
            f"EAR: {features['ear']:.3f}",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            f"MAR: {features['mar']:.3f}",
            (20, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
    else:
        cv2.putText(
            frame,
            "EAR: N/A",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            "MAR: N/A",
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