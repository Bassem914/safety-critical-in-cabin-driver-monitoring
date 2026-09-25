import argparse
from time import perf_counter
from typing import Optional

import cv2
import numpy as np

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
from perception.head_pose import (
    HeadPoseEstimator,
    HeadPoseResult,
)
from perception.visualization import (
    create_dashboard_canvas,
    draw_dashboard_sidebar,
    draw_milestone_title,
    draw_selected_landmarks,
)


WINDOW_NAME = "Cabin Sensing"


def draw_body_landmarks(frame, pose) -> None:
    """Draw selected shoulders/hips only when landmarks are available."""
    if pose is None:
        return
    colors = {"left_shoulder": (0, 170, 0), "right_shoulder": (0, 170, 0),
              "left_hip": (0, 190, 220), "right_hip": (0, 190, 220)}
    for name, landmark in pose.landmarks.items():
        cv2.circle(frame, landmark.pixel, 6, colors.get(name, (255, 255, 255)), -1)


def append_body_dashboard(canvas, body_pose, body_geometry, body_posture, estimator):
    """Preserve the existing M6 dashboard; append a separate white M7 panel."""
    height, width = canvas.shape[:2]
    panel_width = 420
    out = np.full((max(height, 480), width + panel_width, 3), 255, dtype=np.uint8)
    out[:height, :width] = canvas
    x, y = width + 16, 36

    def line(label, value, *, color=(45, 45, 45), step=32):
        nonlocal y
        cv2.putText(out, f"{label}: {value}", (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.54, color, 1, cv2.LINE_AA)
        y += step

    def fmt(value, precision=4):
        return "N/A" if value is None else f"{value:.{precision}f}"

    cv2.putText(out, "BODY POSTURE", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.60, (25, 25, 25), 2, cv2.LINE_AA)
    y += 42
    line("Pose", "VALID" if body_pose and body_pose.all_required_landmarks_visible
         else "LOW VISIBILITY" if body_pose else "NOT DETECTED")
    line("Geometry", "VALID" if body_geometry and body_geometry.geometry_valid else "INVALID")
    status = "CALIBRATING" if estimator.is_calibrating else (
        "CALIBRATED" if estimator.is_calibrated else "NOT CALIBRATED")
    line("Calibration", status)
    valid_count, target_count = estimator.calibration_progress
    line("Neutral samples", f"{valid_count}/{target_count}")
    line("Lateral", body_posture.lateral_state.value)
    line("Sagittal", body_posture.sagittal_state.value)
    y += 8
    line("Lateral angle", fmt(body_posture.torso_lateral_angle_degrees, 2) + " deg")
    line("Current torso dZ", fmt(body_geometry.torso_depth_delta if body_geometry else None))
    line("Neutral torso dZ", fmt(estimator.neutral_torso_depth_delta))
    line("Relative dZ", fmt(body_posture.torso_depth_change))
    line("Normalized torso", fmt(body_geometry.normalized_torso_length if body_geometry else None, 3))
    y += 10
    cv2.putText(out, "C: calibrate  |  R: reset  |  Q: quit", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.46, (60, 60, 60), 1, cv2.LINE_AA)
    y += 32
    cv2.putText(out, "Depth is non-metric; lateral motion may", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.43, (90, 90, 90), 1, cv2.LINE_AA)
    y += 23
    cv2.putText(out, "also trigger forward-lean classification.", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.43, (90, 90, 90), 1, cv2.LINE_AA)
    return out



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
        "--auto-calibrate-file", action="store_true",
        help="For a controlled file starting neutral: collect the first 30 valid "
             "neutral frames automatically. Never use on arbitrary clips.",
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

    face_detector = FaceMeshDetector()
    geometry_extractor = FacialGeometryExtractor()
    head_pose_estimator = HeadPoseEstimator()
    gaze_estimator = GazeEstimator()
    temporal_engine = TemporalRuleEngine()
    body_detector = BodyPoseDetector()
    body_geometry_extractor = BodyGeometryExtractor()
    body_posture_estimator = BodyPostureEstimator()
    # Only controlled research clips with a confirmed neutral opening segment
    # should be automatically calibrated. Otherwise press C while neutral.
    automatic_file_calibration = (
        isinstance(video_source, FileVideoSource)
        and auto_calibrate_file
    )
    if automatic_file_calibration:
        body_posture_estimator.begin_calibration()

    previous_processing_time = perf_counter()

    print(
        "[INFO] Source-independent "
        "perception pipeline started."
    )
    print(
        f"[INFO] Source: "
        f"{video_source.source_name}"
    )
    print(
        f"[INFO] Source FPS: "
        f"{video_source.fps:.2f}"
    )
    print(
        f"[INFO] Mirroring enabled: "
        f"{mirror}"
    )
    print(
        "[INFO] Press 'q' inside "
        "the video window to quit."
    )

    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL,
    )

    try:
        while True:
            frame_packet = (
                video_source.read()
            )

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

            body_pose = body_detector.detect(frame)
            body_geometry = body_geometry_extractor.compute_features(body_pose)
            # One fresh frame per update; calibration is never fed on UI redraw.
            if body_posture_estimator.is_calibrating:
                just_completed = body_posture_estimator.update_calibration(body_geometry)
                if just_completed:
                    print("[M7] " + body_posture_estimator.calibration_message)
            body_posture = body_posture_estimator.estimate(body_geometry)
            draw_body_landmarks(frame, body_pose)

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
                    geometry_extractor.compute_features(
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

            draw_milestone_title(
                frame=frame,
                milestone_text=(
                    "Path 1 - Milestone 7: "
                    "Integrated Body Posture"
                ),
            )

            display_frame, display_image_width = (
                create_dashboard_canvas(
                    frame=frame,
                )
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
                display_frame, body_pose, body_geometry, body_posture,
                body_posture_estimator,
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
                print("Calibrating: remain neutral for 30 valid frames.")
            elif key == ord("r"):
                body_posture_estimator.reset_calibration()
                print("Calibration reset.")
            elif key == ord("q"):
                print(
                    "[INFO] Quit requested "
                    "by user."
                )
                break

    finally:
        face_detector.close()
        body_detector.close()
        video_source.release()
        cv2.destroyAllWindows()

    print(
        "[INFO] Perception pipeline "
        "finished cleanly."
    )


def main() -> None:

    args = parse_arguments()

    try:
        video_source = (
            create_video_source(args)
        )

        run_pipeline(
            video_source=video_source,
            mirror=args.mirror,
            auto_calibrate_file=args.auto_calibrate_file,
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