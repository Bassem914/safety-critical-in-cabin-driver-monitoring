from typing import Dict, Tuple

import cv2


Point2D = Tuple[int, int]


def draw_selected_landmarks(
    frame,
    landmarks: Dict[str, Point2D],
    draw_labels: bool = False,
    color: Tuple[int, int, int] = (0, 255, 0),
) -> None:
    """
    Draw selected face landmarks on the frame.

    By default, only points are drawn. Labels are disabled because they
    quickly overlap and make the visualization noisy.

    Labels can be enabled later for debugging.
    """
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
) -> None:
    """
    Draw real-time status overlay.

    Color convention:
    - green: detected / normal
    - red: missing / unsafe candidate
    - white: neutral information
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