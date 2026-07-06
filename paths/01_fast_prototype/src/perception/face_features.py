from typing import Dict, Optional, Tuple

import mediapipe as mp


Point2D = Tuple[int, int]


SELECTED_FACE_LANDMARKS = {
    "left_eye_outer": 33,
    "left_eye_inner": 133,
    "right_eye_inner": 362,
    "right_eye_outer": 263,
    "nose_tip": 1,
    "mouth_left": 61,
    "mouth_right": 291,
    "upper_lip": 13,
    "lower_lip": 14,
    "chin": 152,
    "forehead": 10,
}


class FaceMeshDetector:
    """
    MediaPipe Face Mesh wrapper for the fast prototype.

    Responsibility:
    - initialize MediaPipe Face Mesh
    - process RGB frames
    - extract selected facial landmarks
    - convert normalized landmarks to pixel coordinates
    """

    def __init__(
        self,
        max_num_faces: int = 1,
        refine_landmarks: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self._mp_face_mesh = mp.solutions.face_mesh
        self._face_mesh = self._mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    @staticmethod
    def landmark_to_pixel(landmark, frame_width: int, frame_height: int) -> Point2D:
        """
        Convert MediaPipe normalized coordinates to OpenCV pixel coordinates.

        MediaPipe:
        - x and y are normalized between 0 and 1

        OpenCV:
        - x and y are pixel positions
        """
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)
        return x, y

    def detect_selected_landmarks(
        self,
        rgb_frame,
        frame_width: int,
        frame_height: int,
    ) -> Optional[Dict[str, Point2D]]:
        """
        Detect a face and return selected facial landmarks.

        Returns:
            dict[str, Point2D] if a face is detected
            None if no face is detected
        """
        results = self._face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None

        face_landmarks = results.multi_face_landmarks[0]

        selected_points: Dict[str, Point2D] = {}

        for name, index in SELECTED_FACE_LANDMARKS.items():
            landmark = face_landmarks.landmark[index]
            selected_points[name] = self.landmark_to_pixel(
                landmark,
                frame_width,
                frame_height,
            )

        return selected_points

    def close(self) -> None:
        """
        Release MediaPipe resources.
        """
        self._face_mesh.close()