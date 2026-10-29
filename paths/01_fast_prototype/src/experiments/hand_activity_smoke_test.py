import cv2
from time import perf_counter

from perception.body_features import (
    BodyGeometryExtractor,
    BodyPoseDetector,
)
from perception.face_features import FaceMeshDetector
from perception.hand_features import (
    HandGeometryExtractor,
    HandLandmarkDetector,
    HandSpatialEstimator,
)
from perception.hand_tracking import (
    HandTemporalTracker,
    build_hand_observations,
)


WINDOW_NAME = "Milestone 8 - Hand Activity Temporal Smoke Test"


def draw_hand_points(
    frame,
    detection_result,
) -> None:
    for detection_index, hand in enumerate(
        detection_result.hands
    ):
        for landmark in hand.landmarks.values():
            cv2.circle(
                frame,
                landmark.pixel,
                4,
                (0, 255, 0),
                -1,
            )

        wrist = hand.landmarks.get("wrist")
        middle_mcp = hand.landmarks.get("middle_mcp")

        if wrist is not None and middle_mcp is not None:
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
                f"D{detection_index + 1}",
                (
                    wrist.pixel[0] + 8,
                    wrist.pixel[1] - 8,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )


def draw_reference_geometry(
    frame,
    face_landmarks,
    body_geometry,
) -> None:
    if (
        face_landmarks is not None
        and "forehead" in face_landmarks
        and "chin" in face_landmarks
    ):
        cv2.line(
            frame,
            face_landmarks["forehead"],
            face_landmarks["chin"],
            (255, 0, 255),
            2,
        )

    if (
        body_geometry is not None
        and body_geometry.geometry_valid
    ):
        shoulder = (
            int(round(body_geometry.shoulder_midpoint[0])),
            int(round(body_geometry.shoulder_midpoint[1])),
        )

        hip = (
            int(round(body_geometry.hip_midpoint[0])),
            int(round(body_geometry.hip_midpoint[1])),
        )

        cv2.line(
            frame,
            shoulder,
            hip,
            (255, 255, 0),
            3,
        )


def draw_track_markers(
    frame,
    track_results,
) -> None:
    for track in track_results:
        if track.palm_center is None:
            continue

        point = (
            int(round(track.palm_center[0])),
            int(round(track.palm_center[1])),
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
            0.65,
            (255, 0, 255),
            2,
            cv2.LINE_AA,
        )


def draw_status_panel(
    frame,
    detection_result,
    track_results,
) -> None:
    x = 20
    y = 35
    line_height = 26

    cv2.putText(
        frame,
        "M8 Hand Activity - Temporal Geometry",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.70,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    y += 38

    cv2.putText(
        frame,
        (
            f"Frame detections: {detection_result.hand_count} | "
            f"{detection_result.visibility_state.value}"
        ),
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.56,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    y += 36

    for track in track_results:
        handedness = (
            track.model_handedness_label
            or "UNKNOWN"
        )

        cv2.putText(
            frame,
            (
                f"T{track.track_id}: "
                f"{track.visibility_state.value} | "
                f"model={handedness}"
            ),
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.56,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        y += line_height

        cv2.putText(
            frame,
            (
                f"  region={track.spatial_state.value} | "
                f"dwell={track.spatial_dwell_seconds:.2f}s"
            ),
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        y += line_height

        speed_text = (
            f"{track.speed_pixels_per_second:.1f}"
            if track.speed_pixels_per_second is not None
            else "N/A"
        )

        cv2.putText(
            frame,
            (
                f"  speed={speed_text} px/s | "
                f"missing={track.missing_duration_seconds:.2f}s"
            ),
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        y += line_height + 6

    cv2.putText(
        frame,
        "D*=current detection | T*=temporal track",
        (20, frame.shape[0] - 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.47,
        (200, 200, 200),
        1,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        "Geometry only - no behavior/safety judgment | q: quit",
        (20, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.47,
        (200, 200, 200),
        1,
        cv2.LINE_AA,
    )


def run_webcam_smoke_test(
    camera_index: int = 0,
) -> None:
    cap = cv2.VideoCapture(
        camera_index
    )

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open webcam index {camera_index}."
        )

    hand_detector = HandLandmarkDetector(
        static_image_mode=False,
        max_num_hands=2,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    hand_geometry_extractor = HandGeometryExtractor()
    spatial_estimator = HandSpatialEstimator()

    tracker = HandTemporalTracker(
    maximum_match_distance_pixels=320.0,
    missing_tolerance_seconds=0.60,
    handedness_mismatch_penalty_pixels=50.0,
    handedness_confidence_threshold=0.80,
    lost_track_retention_seconds=1.00,
    maximum_prediction_seconds=0.35,
    )

    face_detector = FaceMeshDetector()
    body_detector = BodyPoseDetector()
    body_geometry_extractor = BodyGeometryExtractor()

    start_time = perf_counter()

    print("[M8] Temporal hand smoke test started.")
    print("[M8] Move one or two hands between regions.")
    print("[M8] Briefly hide one hand for <0.5 s.")
    print("[M8] Hide one hand for >0.5 s to observe LOST.")
    print("[M8] Press 'q' inside the video window to quit.")

    try:
        while True:
            ok, frame = cap.read()

            if not ok or frame is None:
                print(
                    "[M8] Webcam frame acquisition stopped."
                )
                break

            timestamp_seconds = (
                perf_counter()
                - start_time
            )

            frame_height, frame_width = frame.shape[:2]

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )

            face_landmarks = (
                face_detector.detect_selected_landmarks(
                    rgb_frame=rgb_frame,
                    frame_width=frame_width,
                    frame_height=frame_height,
                )
            )

            body_result = body_detector.detect(
                frame
            )

            body_geometry = (
                body_geometry_extractor.compute_features(
                    body_result
                )
            )

            detection_result = (
                hand_detector.detect(
                    frame
                )
            )

            geometry_results = tuple(
                hand_geometry_extractor.compute_geometry(
                    hand
                )
                for hand in detection_result.hands
            )

            spatial_results = tuple(
                spatial_estimator.estimate(
                    hand_geometry=geometry,
                    face_landmarks=face_landmarks,
                    body_geometry=body_geometry,
                )
                for geometry in geometry_results
            )

            observations = build_hand_observations(
                detected_hands=detection_result.hands,
                geometry_results=geometry_results,
                spatial_results=spatial_results,
            )

            track_results = tracker.update(
                timestamp_seconds=timestamp_seconds,
                observations=observations,
            )

            draw_reference_geometry(
                frame,
                face_landmarks,
                body_geometry,
            )

            draw_hand_points(
                frame,
                detection_result,
            )

            draw_track_markers(
                frame,
                track_results,
            )

            draw_status_panel(
                frame,
                detection_result,
                track_results,
            )

            cv2.imshow(
                WINDOW_NAME,
                frame,
            )

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):
                print(
                    "[M8] Quit requested."
                )
                break

    finally:
        hand_detector.close()
        face_detector.close()
        body_detector.close()

        cap.release()
        cv2.destroyAllWindows()

        print(
            "[M8] Temporal hand smoke test finished cleanly."
        )


if __name__ == "__main__":
    run_webcam_smoke_test()
