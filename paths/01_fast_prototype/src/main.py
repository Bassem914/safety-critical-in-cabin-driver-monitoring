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
from perception.face_features import (
    FaceMeshDetector,
    FacialGeometryExtractor,
)
from perception.visualization import (
    draw_selected_landmarks,
    draw_source_metadata_overlay,
    draw_status_overlay,
    draw_temporal_state_overlay,
)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for source selection and display behavior.
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
        help="Webcam index when --source webcam is selected.",
    )

    parser.add_argument(
        "--video-path",
        type=str,
        default=None,
        help="Local video path when --source file is selected.",
    )

    parser.add_argument(
        "--mirror",
        action="store_true",
        help=(
            "Horizontally mirror frames. "
            "Recommended only for webcam visualization."
        ),
    )

    return parser.parse_args()


def create_video_source(args: argparse.Namespace) -> VideoSource:
    """
    Create the selected source implementation.
    """

    if args.source == "webcam":
        return WebcamVideoSource(
            camera_index=args.camera_index
        )

    if not args.video_path:
        raise ValueError(
            "--video-path is required when --source file is selected."
        )

    return FileVideoSource(
        video_path=args.video_path
    )


def run_pipeline(
    video_source: VideoSource,
    mirror: bool,
) -> None:
    """
    Run the shared perception pipeline for any VideoSource.
    """

    if not video_source.is_opened():
        raise RuntimeError(
            f"Could not open video source: {video_source.source_name}"
        )

    face_detector = FaceMeshDetector()
    geometry_extractor = FacialGeometryExtractor()
    temporal_engine = TemporalRuleEngine()

    previous_processing_time = perf_counter()

    print("[INFO] Source-independent perception pipeline started.")
    print(f"[INFO] Source: {video_source.source_name}")
    print(f"[INFO] Source FPS: {video_source.fps:.2f}")
    print(f"[INFO] Mirroring enabled: {mirror}")
    print("[INFO] Press 'q' inside the video window to quit.")

    try:
        while True:
            frame_packet = video_source.read()

            if frame_packet is None:
                print(
                    "[INFO] Video source ended or acquisition stopped."
                )
                break

            frame = frame_packet.frame

            if mirror:
                frame = cv2.flip(frame, 1)

            frame_height, frame_width = frame.shape[:2]

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

            current_processing_time = perf_counter()

            processing_duration = (
                current_processing_time
                - previous_processing_time
            )

            processing_fps = (
                1.0 / processing_duration
                if processing_duration > 0.0
                else 0.0
            )

            previous_processing_time = current_processing_time

            face_detected = selected_landmarks is not None

            landmark_count = (
                len(selected_landmarks)
                if selected_landmarks is not None
                else 0
            )

            features: Optional[dict[str, float]] = None

            if selected_landmarks is not None:
                features = geometry_extractor.compute_features(
                    selected_landmarks
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

            temporal_result: TemporalDecisionResult = (
                temporal_engine.update(
                    timestamp_seconds=frame_packet.timestamp_seconds,
                    face_detected=face_detected,
                    ear=ear,
                    mar=mar,
                )
            )
            draw_status_overlay(
                frame=frame,
                fps=processing_fps,
                face_detected=face_detected,
                landmark_count=landmark_count,
                milestone_text=(
                    "Path 1 - Milestone 4B: "
                    "Face-Level Temporal State Baseline"
                ),
                features=features,
            )

            draw_source_metadata_overlay(
                frame=frame,
                source_name=frame_packet.source_name,
                frame_index=frame_packet.frame_index,
                timestamp_seconds=frame_packet.timestamp_seconds,           
            )
            draw_temporal_state_overlay(
                frame=frame,
                temporal_result=temporal_result,
)
            cv2.imshow(
                "Cabin Sensing - Source Independent Perception",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print("[INFO] Quit requested by user.")
                break

    finally:
        face_detector.close()
        video_source.release()
        cv2.destroyAllWindows()

    print("[INFO] Perception pipeline finished cleanly.")


def main() -> None:
    args = parse_arguments()

    try:
        video_source = create_video_source(args)

        run_pipeline(
            video_source=video_source,
            mirror=args.mirror,
        )

    except (ValueError, RuntimeError) as error:
        print(f"[ERROR] {error}")


if __name__ == "__main__":
    main()