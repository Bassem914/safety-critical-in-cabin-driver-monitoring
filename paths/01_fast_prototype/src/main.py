import argparse
from time import perf_counter
from typing import Optional

import cv2

from acquisition.video_source import (
    FileVideoSource,
    VideoSource,
    WebcamVideoSource,
)
from decision.temporal_rules import (
    TemporalDecisionResult,
    TemporalRuleEngine,
)
from perception.body_features import (
    BodyGeometryExtractor,
    BodyPoseDetector,
    BodyPostureEstimator,
)
from perception.face_features import (
    FaceMeshDetector,
    FacialGeometryExtractor,
)
from perception.gaze import (
    GazeEstimator,
    GazeResult,
)
from perception.hand_features import (
    HandGeometryExtractor,
    HandLandmarkDetector,
    HandSpatialEstimator,
)
from perception.hand_tracking import (
    HandTemporalTracker,
    build_hand_observations,
)
from perception.head_pose import (
    HeadPoseEstimator,
    HeadPoseResult,
)
from perception.visualization import (
    append_body_dashboard,
    append_hand_dashboard,
    create_dashboard_canvas,
    draw_body_landmarks,
    draw_dashboard_sidebar,
    draw_hand_landmarks,
    draw_hand_tracks,
    draw_milestone_title,
    draw_selected_landmarks,
)


WINDOW_NAME = "Cabin Sensing - M8 Integrated Perception"


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Safety-Critical In-Cabin Driver Monitoring — "
            "source-independent perception pipeline"
        )
    )

    parser.add_argument(
        "--source",
        choices=("webcam", "file"),
        default="webcam",
        help="Input source type.",
    )

    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Webcam index.",
    )

    parser.add_argument(
        "--video-path",
        type=str,
        default=None,
        help="Local video path.",
    )

    parser.add_argument(
        "--mirror",
        action="store_true",
        help="Horizontally mirror frames.",
    )

    parser.add_argument(
        "--auto-calibrate-file",
        action="store_true",
        help=(
            "For a controlled file starting neutral: collect the first "
            "30 valid neutral body frames automatically. Never use this "
            "option on an arbitrary clip."
        ),
    )

    return parser.parse_args()


def create_video_source(
    args: argparse.Namespace,
) -> VideoSource:

    if args.source == "webcam":
        return WebcamVideoSource(
            camera_index=args.camera_index
        )

    if not args.video_path:
        raise ValueError(
            "--video-path is required when "
            "--source file is selected."
        )

    return FileVideoSource(
        video_path=args.video_path
    )


def run_pipeline(
    video_source: VideoSource,
    mirror: bool,
    auto_calibrate_file: bool = False,
) -> None:

    if not video_source.is_opened():
        raise RuntimeError(
            "Could not open video source: "
            f"{video_source.source_name}"
        )

    # ---------------------------------------------------------
    # M1-M6 face/head/gaze stack
    # ---------------------------------------------------------

    face_detector = FaceMeshDetector()
    facial_geometry_extractor = FacialGeometryExtractor()
    head_pose_estimator = HeadPoseEstimator()
    gaze_estimator = GazeEstimator()
    temporal_engine = TemporalRuleEngine()

    # ---------------------------------------------------------
    # M7 body posture stack
    # ---------------------------------------------------------

    body_detector = BodyPoseDetector()
    body_geometry_extractor = BodyGeometryExtractor()
    body_posture_estimator = BodyPostureEstimator()

    automatic_file_calibration = (
        isinstance(video_source, FileVideoSource)
        and auto_calibrate_file
    )

    if automatic_file_calibration:
        body_posture_estimator.begin_calibration()

    # ---------------------------------------------------------
    # M8 hand activity stack
    # ---------------------------------------------------------

    hand_detector = HandLandmarkDetector(
        static_image_mode=False,
        max_num_hands=2,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    hand_geometry_extractor = HandGeometryExtractor()

    hand_spatial_estimator = HandSpatialEstimator(
        near_face_threshold=1.10,
        torso_lateral_margin_ratio=0.65,
        lower_region_start_ratio=0.65,
        lower_region_extension_ratio=0.80,
    )

    # Prototype temporal association.
    # Long-term identity stability remains a documented M8 limitation.
    hand_tracker = HandTemporalTracker(
        maximum_match_distance_pixels=320.0,
        missing_tolerance_seconds=0.60,
        handedness_mismatch_penalty_pixels=50.0,
    )

    previous_processing_time = perf_counter()

    print(
        "[INFO] Source-independent perception pipeline started."
    )
    print(
        f"[INFO] Source: {video_source.source_name}"
    )
    print(
        f"[INFO] Source FPS: {video_source.fps:.2f}"
    )
    print(
        f"[INFO] Mirroring enabled: {mirror}"
    )
    print(
        "[INFO] M8 hand activity integration enabled."
    )
    print(
        "[INFO] Press 'q' inside the video window to quit."
    )

    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL,
    )

    try:
        while True:

            frame_packet = video_source.read()

            if frame_packet is None:
                print(
                    "[INFO] Video source ended "
                    "or acquisition stopped."
                )
                break

            frame = frame_packet.frame

            if mirror:
                frame = cv2.flip(
                    frame,
                    1,
                )

            # =================================================
            # M7 BODY POSE / POSTURE
            # =================================================

            body_pose = body_detector.detect(
                frame
            )

            body_geometry = (
                body_geometry_extractor.compute_features(
                    body_pose
                )
            )

            if body_posture_estimator.is_calibrating:
                just_completed = (
                    body_posture_estimator.update_calibration(
                        body_geometry
                    )
                )

                if just_completed:
                    print(
                        "[M7] "
                        + body_posture_estimator.calibration_message
                    )

            body_posture = (
                body_posture_estimator.estimate(
                    body_geometry
                )
            )

            draw_body_landmarks(
                frame=frame,
                body_pose=body_pose,
            )

            # =================================================
            # M1-M6 FACE / HEAD / GAZE
            # =================================================

            frame_height, frame_width = (
                frame.shape[:2]
            )

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )

            selected_landmarks = (
                face_detector.detect_selected_landmarks(
                    rgb_frame=rgb_frame,
                    frame_width=frame_width,
                    frame_height=frame_height,
                )
            )

            face_detected = (
                selected_landmarks is not None
            )

            landmark_count = (
                len(selected_landmarks)
                if selected_landmarks is not None
                else 0
            )

            features: Optional[
                dict[str, float]
            ] = None

            head_pose_result: Optional[
                HeadPoseResult
            ] = None

            gaze_result: Optional[
                GazeResult
            ] = None

            if selected_landmarks is not None:

                features = (
                    facial_geometry_extractor.compute_features(
                        selected_landmarks
                    )
                )

                head_pose_result = (
                    head_pose_estimator.estimate(
                        landmarks=selected_landmarks,
                        frame_width=frame_width,
                        frame_height=frame_height,
                    )
                )

                gaze_result = (
                    gaze_estimator.estimate(
                        landmarks=selected_landmarks
                    )
                )

                draw_selected_landmarks(
                    frame=frame,
                    landmarks=selected_landmarks,
                    draw_labels=False,
                )

            ear = (
                features.get("ear")
                if features is not None
                else None
            )

            mar = (
                features.get("mar")
                if features is not None
                else None
            )

            temporal_result: (
                TemporalDecisionResult
            ) = temporal_engine.update(
                timestamp_seconds=(
                    frame_packet.timestamp_seconds
                ),
                face_detected=face_detected,
                ear=ear,
                mar=mar,
            )

            if (
                not face_detected
                and temporal_result.face_loss_duration_seconds
                >= temporal_engine.config.prolonged_face_loss_seconds
            ):
                head_pose_estimator.reset()

            # =================================================
            # M8 HAND DETECTION / GEOMETRY / SPATIAL STATE
            # =================================================

            hand_detection = hand_detector.detect(
                frame
            )

            hand_geometry_results = tuple(
                hand_geometry_extractor.compute_geometry(
                    hand
                )
                for hand in hand_detection.hands
            )

            hand_spatial_results = tuple(
                hand_spatial_estimator.estimate(
                    hand_geometry=geometry,
                    face_landmarks=selected_landmarks,
                    body_geometry=body_geometry,
                )
                for geometry in hand_geometry_results
            )

            hand_observations = (
                build_hand_observations(
                    detected_hands=hand_detection.hands,
                    geometry_results=hand_geometry_results,
                    spatial_results=hand_spatial_results,
                )
            )

            hand_track_results = (
                hand_tracker.update(
                    timestamp_seconds=(
                        frame_packet.timestamp_seconds
                    ),
                    observations=hand_observations,
                )
            )

            draw_hand_landmarks(
                frame=frame,
                detection_result=hand_detection,
            )

            draw_hand_tracks(
                frame=frame,
                track_results=hand_track_results,
            )

            # =================================================
            # PROCESSING FPS
            # =================================================

            current_processing_time = (
                perf_counter()
            )

            processing_duration = (
                current_processing_time
                - previous_processing_time
            )

            processing_fps = (
                1.0 / processing_duration
                if processing_duration > 0.0
                else 0.0
            )

            previous_processing_time = (
                current_processing_time
            )

            # =================================================
            # DASHBOARD
            # =================================================

            draw_milestone_title(
                frame=frame,
                milestone_text=(
                    "Path 1 - Milestone 8: "
                    "Integrated Hand Activity Geometry"
                ),
            )

            (
                display_frame,
                display_image_width,
            ) = create_dashboard_canvas(
                frame=frame,
            )

            draw_dashboard_sidebar(
                canvas=display_frame,
                image_width=display_image_width,
                fps=processing_fps,
                face_detected=face_detected,
                landmark_count=landmark_count,
                source_name=frame_packet.source_name,
                frame_index=frame_packet.frame_index,
                timestamp_seconds=(
                    frame_packet.timestamp_seconds
                ),
                features=features,
                temporal_result=temporal_result,
                head_pose_result=head_pose_result,
                gaze_result=gaze_result,
            )

            display_frame = append_body_dashboard(
                canvas=display_frame,
                body_pose=body_pose,
                body_geometry=body_geometry,
                body_posture=body_posture,
                estimator=body_posture_estimator,
            )

            display_frame = append_hand_dashboard(
                canvas=display_frame,
                detection_result=hand_detection,
                geometry_results=hand_geometry_results,
                spatial_results=hand_spatial_results,
                track_results=hand_track_results,
            )

            cv2.imshow(
                WINDOW_NAME,
                display_frame,
            )

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("c"):

                body_posture_estimator.begin_calibration()

                print(
                    "[M7] Calibrating: remain neutral "
                    "for 30 valid frames."
                )

            elif key == ord("r"):

                body_posture_estimator.reset_calibration()

                print(
                    "[M7] Calibration reset."
                )

            elif key == ord("q"):

                print(
                    "[INFO] Quit requested by user."
                )

                break

    finally:

        face_detector.close()
        body_detector.close()
        hand_detector.close()

        video_source.release()

        cv2.destroyAllWindows()

    print(
        "[INFO] Perception pipeline finished cleanly."
    )


def main() -> None:

    args = parse_arguments()

    try:

        video_source = (
            create_video_source(
                args
            )
        )

        run_pipeline(
            video_source=video_source,
            mirror=args.mirror,
            auto_calibrate_file=(
                args.auto_calibrate_file
            ),
        )

    except (
        ValueError,
        RuntimeError,
    ) as error:

        print(
            f"[ERROR] {error}"
        )


if __name__ == "__main__":
    main()
