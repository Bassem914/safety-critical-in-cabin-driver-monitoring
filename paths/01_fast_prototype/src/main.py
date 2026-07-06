import time

import cv2

from perception.face_features import FaceMeshDetector, FacialGeometryExtractor
from perception.visualization import draw_selected_landmarks, draw_status_overlay


def main() -> None:
    """
    Path 1 — Fast Prototype
    Milestone 3 — Facial Geometry Feature Extraction.

    Milestone 1 remains preserved in:
    src/experiments/webcam_smoke_test.py

    Milestone 2 introduced:
    MediaPipe Face Mesh landmark detection.

    Milestone 3 adds:
    EAR and MAR facial geometry features.
    """

    camera_index = 0
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"[ERROR] Could not open webcam with camera index {camera_index}.")
        print("[HINT] Try changing camera_index to 1 or 2.")
        return

    face_detector = FaceMeshDetector()
    geometry_extractor = FacialGeometryExtractor()

    previous_time = time.time()

    print("[INFO] Milestone 3 facial geometry feature pipeline started.")
    print("[INFO] Press 'q' inside the video window to quit.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("[ERROR] Could not read frame from webcam.")
            break

        frame = cv2.flip(frame, 1)
        frame_height, frame_width = frame.shape[:2]

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        selected_landmarks = face_detector.detect_selected_landmarks(
            rgb_frame=rgb_frame,
            frame_width=frame_width,
            frame_height=frame_height,
        )

        current_time = time.time()
        elapsed_time = current_time - previous_time
        fps = 1.0 / elapsed_time if elapsed_time > 0 else 0.0
        previous_time = current_time

        face_detected = selected_landmarks is not None
        landmark_count = len(selected_landmarks) if selected_landmarks is not None else 0
        features = None

        if selected_landmarks is not None:
            features = geometry_extractor.compute_features(selected_landmarks)

            draw_selected_landmarks(
                frame=frame,
                landmarks=selected_landmarks,
                draw_labels=False,
            )

        draw_status_overlay(
            frame=frame,
            fps=fps,
            face_detected=face_detected,
            landmark_count=landmark_count,
            milestone_text="Path 1 - Milestone 3: EAR + MAR Feature Extraction",
            features=features,
        )

        cv2.imshow("Cabin Sensing - Facial Geometry Features", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("[INFO] Quit requested by user.")
            break

    face_detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Facial geometry feature pipeline finished cleanly.")


if __name__ == "__main__":
    main()