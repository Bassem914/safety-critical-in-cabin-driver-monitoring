import argparse
import csv
import math
from bisect import bisect_right
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from perception.body_features import (
    BodyGeometryExtractor,
    BodyPoseDetector,
    BodyPostureEstimator,
)

WINDOW_NAME = "Milestone 7 - Body Pose Smoke Test"
CSV_FIELDS = [
    "frame_index", "timestamp_s", "phase", "pose_detected",
    "landmarks_visible", "geometry_valid", "calibration_state",
    "calibration_valid_frames", "neutral_torso_dz", "current_torso_dz",
    "relative_dz", "torso_lateral_deg", "shoulder_angle_deg",
    "hip_angle_deg", "shoulder_width_px", "hip_width_px",
    "normalized_torso_length", "lateral_state", "sagittal_state",
    "manual_label",
]


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("webcam", "file"), default="webcam")
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--video-path", type=Path,
                        help="MP4 or other video file; required for --source file")
    parser.add_argument("--csv-path", type=Path,
                        help="CSV output path. File mode defaults beside the input MP4.")
    parser.add_argument("--calibration-start-seconds", type=float, default=1.0,
                        help="File mode: beginning of known-neutral segment (default 1 s).")
    parser.add_argument("--calibration-end-seconds", type=float, default=10.0,
                        help="File mode: end of known-neutral segment (default 10 s). "
                             "Classification begins after this point.")
    parser.add_argument("--annotations-csv", type=Path,
                        help="Optional independently annotated CSV with start_s,end_s,manual_label. "
                             "Unannotated frames remain blank; no labels are guessed.")
    parser.add_argument("--no-display", action="store_true",
                        help="Process without a video window (file mode only).")
    parser.add_argument("--max-frames", type=int, default=0,
                        help="Optional debugging limit; 0 processes entire input.")
    args = parser.parse_args(argv)
    if args.source == "file" and args.video_path is None:
        parser.error("--video-path is required with --source file")
    if args.source == "webcam" and args.no_display:
        parser.error("--no-display is intended for file mode")
    if (not math.isfinite(args.calibration_start_seconds)
            or not math.isfinite(args.calibration_end_seconds)
            or args.calibration_start_seconds < 0
            or args.calibration_end_seconds <= args.calibration_start_seconds):
        parser.error("Provide a valid neutral segment: 0 <= start < end")
    if args.max_frames < 0:
        parser.error("--max-frames must be nonnegative")
    return args


# Permitted values express the movement the person intentionally performs.
# These are observations supplied by the experimenter, not model predictions.
MOVEMENT_LABELS = {
    "NEUTRAL", "FORWARD_LEAN", "LEAN_LEFT", "LEAN_RIGHT",
    "FORWARD_LEFT", "FORWARD_RIGHT", "TRANSITION", "UNCERTAIN",
}


def load_annotations(path: Optional[Path]):
    """Load nonoverlapping, independently annotated [start,end) intervals."""
    if path is None:
        return []
    path = path.expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Annotation CSV not found: {path}")
    intervals = []
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {"start_s", "end_s", "manual_label"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("Annotation CSV requires start_s,end_s,manual_label columns")
        for line, row in enumerate(reader, start=2):
            try:
                start, end = float(row["start_s"]), float(row["end_s"])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Invalid annotation time at row {line}") from exc
            label = (row["manual_label"] or "").strip().upper()
            if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end):
                raise ValueError(f"Invalid annotation interval at row {line}")
            if label not in MOVEMENT_LABELS:
                raise ValueError(f"Invalid manual_label {label!r} at row {line}; "
                                 f"use one of {sorted(MOVEMENT_LABELS)}")
            intervals.append((start, end, label))
    intervals.sort()
    for previous, following in zip(intervals, intervals[1:]):
        if previous[1] > following[0]:
            raise ValueError("Annotation intervals must not overlap")
    return intervals


def manual_label_at(timestamp_s, intervals, starts):
    """Look up an independently supplied label, or return blank if absent."""
    index = bisect_right(starts, timestamp_s) - 1
    if index >= 0 and timestamp_s < intervals[index][1]:
        return intervals[index][2]
    return ""


def draw_body_landmarks(frame, body_result):
    if body_result is None:
        return
    colors = {"left_shoulder": (0, 255, 0), "right_shoulder": (0, 255, 0),
              "left_hip": (0, 255, 255), "right_hip": (0, 255, 255)}
    for name, landmark in body_result.landmarks.items():
        point = landmark.pixel
        color = colors.get(name, (255, 255, 255))
        cv2.circle(frame, point, 6, color, -1)
        cv2.putText(frame, name, (point[0] + 8, point[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.47, color, 1, cv2.LINE_AA)


def draw_body_geometry(frame, geometry):
    if geometry is None:
        return
    shoulder = tuple(round(v) for v in geometry.shoulder_midpoint)
    hip = tuple(round(v) for v in geometry.hip_midpoint)
    cv2.circle(frame, shoulder, 7, (255, 0, 255), -1)
    cv2.circle(frame, hip, 7, (255, 0, 255), -1)
    cv2.line(frame, shoulder, hip, (255, 0, 255), 3)


def draw_status_panel(frame, pose, geometry, posture, estimator, *,
                      source, frame_index, timestamp_s, phase, manual_label=""):
    """Original video on the left and a white diagnostic sidebar on the right."""
    height, width = frame.shape[:2]
    panel_width = 470
    canvas = np.full((max(height, 675), width + panel_width, 3), 255, np.uint8)
    canvas[:height, :width] = frame
    x, y, step = width + 15, 31, 28

    def add(label, value, color=(40, 40, 40), scale=0.54):
        nonlocal y
        cv2.putText(canvas, f"{label}: {value}", (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)
        y += step

    def fmt(value, digits=4):
        return "N/A" if value is None else f"{value:.{digits}f}"

    add("Source", source)
    add("Frame / time", f"{frame_index} / {timestamp_s:.2f} s")
    add("Phase", phase)
    if manual_label:
        add("Manual label", manual_label)
    y += 5
    add("Body pose", "VALID" if pose and pose.all_required_landmarks_visible
        else "LOW VISIBILITY" if pose else "NOT DETECTED", (0, 140, 0))
    add("Body geometry", "VALID" if geometry and geometry.geometry_valid
        else "INVALID", (0, 140, 0) if geometry and geometry.geometry_valid
        else (0, 0, 195))
    calibration = ("CALIBRATING" if estimator.is_calibrating else
                   "CALIBRATED" if estimator.is_calibrated else "NOT CALIBRATED")
    add("Calibration", calibration,
        (0, 140, 0) if estimator.is_calibrated else (0, 120, 210))
    count, target = estimator.calibration_progress
    add("Valid calibration frames", f"{count}/{target}")
    add("Lateral", posture.lateral_state.value, (170, 105, 0))
    add("Sagittal", posture.sagittal_state.value, (170, 105, 0))
    y += 5
    add("Neutral torso dZ", fmt(posture.neutral_torso_depth_delta))
    add("Current torso dZ", fmt(geometry.torso_depth_delta if geometry else None))
    add("Relative dZ", fmt(posture.torso_depth_change))
    add("Torso lateral", fmt(geometry.torso_lateral_angle_degrees if geometry else None, 2) + " deg")
    if geometry:
        add("Shoulder angle", fmt(geometry.shoulder_angle_degrees, 2) + " deg")
        add("Hip angle", fmt(geometry.hip_angle_degrees, 2) + " deg")
        add("Shoulder width", fmt(geometry.shoulder_width_pixels, 1) + " px")
        add("Hip width", fmt(geometry.hip_width_pixels, 1) + " px")
        add("Normalized torso", fmt(geometry.normalized_torso_length, 3))
    y += 5
    msg = estimator.calibration_message
    for segment in (msg[i:i + 48] for i in range(0, len(msg), 48)):
        if y > canvas.shape[0] - 60:
            break
        cv2.putText(canvas, segment, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.41, (110, 80, 30), 1, cv2.LINE_AA)
        y += 19
    controls = ("SPACE: pause  |  Q/ESC: exit" if source == "file" else
                "C: calibrate  |  R: reset  |  Q/ESC: exit")
    cv2.putText(canvas, controls, (16, canvas.shape[0] - 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 1, cv2.LINE_AA)
    return canvas


def build_csv_row(frame_index, timestamp_s, phase, pose, geometry,
                  posture, estimator, manual_label=""):
    count, _ = estimator.calibration_progress
    calibration = ("CALIBRATING" if estimator.is_calibrating else
                   "CALIBRATED" if estimator.is_calibrated else "NOT_CALIBRATED")
    return {
        "frame_index": frame_index,
        "timestamp_s": round(timestamp_s, 5),
        "phase": phase,
        "pose_detected": bool(pose is not None and pose.pose_detected),
        "landmarks_visible": bool(pose is not None and pose.all_required_landmarks_visible),
        "geometry_valid": bool(geometry is not None and geometry.geometry_valid),
        "calibration_state": calibration,
        "calibration_valid_frames": count,
        "neutral_torso_dz": posture.neutral_torso_depth_delta,
        "current_torso_dz": geometry.torso_depth_delta if geometry else None,
        "relative_dz": posture.torso_depth_change,
        "torso_lateral_deg": geometry.torso_lateral_angle_degrees if geometry else None,
        "shoulder_angle_deg": geometry.shoulder_angle_degrees if geometry else None,
        "hip_angle_deg": geometry.hip_angle_degrees if geometry else None,
        "shoulder_width_px": geometry.shoulder_width_pixels if geometry else None,
        "hip_width_px": geometry.hip_width_pixels if geometry else None,
        "normalized_torso_length": geometry.normalized_torso_length if geometry else None,
        "lateral_state": posture.lateral_state.value,
        "sagittal_state": posture.sagittal_state.value,
        "manual_label": manual_label,
    }


def main(argv=None):
    args = parse_arguments(argv)
    is_file = args.source == "file"
    annotations = load_annotations(args.annotations_csv)
    annotation_starts = [start for start, _, _ in annotations]
    if annotations:
        print(f"[M7] Loaded {len(annotations)} independent annotation intervals")
    if is_file:
        path = args.video_path.expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Video not found: {path}")
        cap = cv2.VideoCapture(str(path))
    else:
        cap = cv2.VideoCapture(args.camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.source} source")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not math.isfinite(fps) or fps <= 0:
        fps = 30.0
    # Keep private test CSV outside Git by default (alongside input video).
    csv_path: Optional[Path] = args.csv_path
    if is_file and csv_path is None:
        csv_path = path.with_name(path.stem + "_m7_validation.csv")
    if csv_path:
        csv_path = csv_path.expanduser()
        csv_path.parent.mkdir(parents=True, exist_ok=True)

    detector = None
    csv_file = None
    count = 0
    calibration_started = False
    calibration_failure = False
    paused = False
    try:
        detector = BodyPoseDetector()
        extractor = BodyGeometryExtractor()
        estimator = BodyPostureEstimator(calibration_target_frames=30)
        if csv_path:
            csv_file = csv_path.open("w", newline="", encoding="utf-8")
            writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
            writer.writeheader()
            print(f"[M7] Logging per-frame measurements to: {csv_path}")
        else:
            writer = None
        if not args.no_display:
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        if is_file:
            print(f"[M7] Playing: {path} ({fps:.2f} FPS)")
            print(f"[M7] Neutral calibration interval: "
                  f"{args.calibration_start_seconds:g}–{args.calibration_end_seconds:g} s")
            print("[M7] Evaluation begins as soon as 30 valid neutral frames "
                  "pass median calibration. SPACE pauses; Q exits.")
        else:
            print("[M7] Webcam: press C ONCE while sitting neutral to collect "
                  "30 valid frames; R resets; Q exits.")

        while True:
            if args.max_frames and count >= args.max_frames:
                break
            if paused:
                key = cv2.waitKey(50) & 0xFF
                if key == ord(' ') or key in (ord('p'), ord('P')):
                    paused = False
                elif key in (ord('q'), ord('Q'), 27):
                    break
                continue

            ok, frame = cap.read()
            if not ok:
                break
            count += 1
            timestamp_s = (count - 1) / fps if is_file else count / fps
            if is_file:
                # These frame-count timestamps are appropriate for the constant-
                # frame-rate reference recording. For variable-frame-rate input,
                # use source presentation timestamps instead.
                within_neutral_window = (
                    args.calibration_start_seconds <= timestamp_s
                    < args.calibration_end_seconds
                )
                if within_neutral_window and not calibration_started:
                    estimator.begin_calibration()
                    calibration_started = True
                    print("[CALIBRATION] Automatic file calibration started.")
                if timestamp_s < args.calibration_start_seconds:
                    phase = "PRE_CALIBRATION"
                elif estimator.is_calibrated:
                    phase = "EVALUATION"
                elif within_neutral_window:
                    phase = "CALIBRATION_SEGMENT"
                else:
                    phase = "UNCALIBRATED_EVALUATION"
            else:
                phase = "WEBCAM"

            pose = detector.detect(frame)
            geometry = extractor.compute_features(pose)
            if estimator.is_calibrating:
                completed = estimator.update_calibration(geometry)
                if completed:
                    print("[CALIBRATION]", estimator.calibration_message,
                          f"baseline={estimator.neutral_torso_depth_delta:.4f}")
                    if is_file:
                        # Evaluate this very frame and every subsequent frame;
                        # don't discard valid frames until neutral-window end.
                        phase = "EVALUATION"
                        print(f"[M7] Evaluation begins at {timestamp_s:.3f} s "
                              f"(frame {count}).")
                elif not estimator.is_calibrating:
                    print("[CALIBRATION]", estimator.calibration_message)
                    calibration_failure = True
            if is_file and timestamp_s >= args.calibration_end_seconds and not estimator.is_calibrated:
                if not calibration_failure:
                    print("[ERROR] No valid calibration by end of neutral interval. "
                          "Check video or adjust --calibration-start-seconds/"
                          "--calibration-end-seconds. Predictions will not be trusted.")
                    calibration_failure = True
                if estimator.is_calibrating:
                    estimator.reset_calibration()
                phase = "UNCALIBRATED_EVALUATION"

            posture = estimator.estimate(geometry)
            manual_label = manual_label_at(timestamp_s, annotations, annotation_starts)
            if writer:
                writer.writerow(build_csv_row(count, timestamp_s, phase, pose,
                                               geometry, posture, estimator,
                                               manual_label=manual_label))
            if not args.no_display:
                draw_body_landmarks(frame, pose)
                draw_body_geometry(frame, geometry)
                display = draw_status_panel(frame, pose, geometry, posture, estimator,
                                            source=args.source, frame_index=count,
                                            timestamp_s=timestamp_s, phase=phase,
                                            manual_label=manual_label)
                cv2.imshow(WINDOW_NAME, display)
                key = cv2.waitKey(max(1, round(1000 / fps)) if is_file else 1) & 0xFF
                if key in (ord('q'), ord('Q'), 27):
                    break
                if is_file:
                    if key in (ord(' '), ord('p'), ord('P')):
                        paused = True
                else:
                    if key in (ord('c'), ord('C')):
                        estimator.begin_calibration()
                        print("[CALIBRATION] Started: stay neutral for 30 valid frames.")
                    elif key in (ord('r'), ord('R')):
                        estimator.reset_calibration()
                        print("[CALIBRATION] Reset.")
            if count % 300 == 0 and is_file:
                print(f"[M7] Processed frame {count}, time {timestamp_s:.1f} s")
    finally:
        if csv_file:
            csv_file.close()
        if detector is not None:
            detector.close()
        cap.release()
        if not args.no_display:
            cv2.destroyAllWindows()
    print(f"[M7] Finished: {count} frames.")
    if csv_path:
        print(f"[M7] CSV: {csv_path}")
    if not annotations and is_file:
        print("[M7] Predictions have no independently annotated ground truth. "
              "Add --annotations-csv after labeling intervals to assess errors.")


if __name__ == "__main__":
    main()
