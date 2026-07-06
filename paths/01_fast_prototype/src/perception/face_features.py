from typing import Dict, Optional, Tuple

import mediapipe as mp
import numpy as np


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
    "left_eye_upper": 159,
    "left_eye_lower": 145,
    "right_eye_upper": 386,
    "right_eye_lower": 374,
}


class FaceMeshDetector:
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
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)
        return x, y

    def detect_selected_landmarks(
        self,
        rgb_frame,
        frame_width: int,
        frame_height: int,
    ) -> Optional[Dict[str, Point2D]]:
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
        self._face_mesh.close()


class FacialGeometryExtractor:
    """
    Computes facial geometry features from selected Face Mesh landmarks.

    Milestone 3 features:
    - EAR: Eye Aspect Ratio
    - MAR: Mouth Aspect Ratio
    """

    @staticmethod
    def euclidean_distance(point_a: Point2D, point_b: Point2D) -> float:
        return float(np.linalg.norm(np.array(point_a) - np.array(point_b)))

    def compute_eye_aspect_ratio(
        self,
        outer: Point2D,
        inner: Point2D,
        upper: Point2D,
        lower: Point2D,
    ) -> float:
        vertical_distance = self.euclidean_distance(upper, lower)
        horizontal_distance = self.euclidean_distance(outer, inner)

        if horizontal_distance < 1e-6:
            return 0.0

        return vertical_distance / horizontal_distance

    def compute_mouth_aspect_ratio(
        self,
        mouth_left: Point2D,
        mouth_right: Point2D,
        upper_lip: Point2D,
        lower_lip: Point2D,
    ) -> float:
        vertical_distance = self.euclidean_distance(upper_lip, lower_lip)
        horizontal_distance = self.euclidean_distance(mouth_left, mouth_right)

        if horizontal_distance < 1e-6:
            return 0.0

        return vertical_distance / horizontal_distance

    def compute_features(self, landmarks: Dict[str, Point2D]) -> Dict[str, float]:
        left_ear = self.compute_eye_aspect_ratio(
            outer=landmarks["left_eye_outer"],
            inner=landmarks["left_eye_inner"],
            upper=landmarks["left_eye_upper"],
            lower=landmarks["left_eye_lower"],
        )

        right_ear = self.compute_eye_aspect_ratio(
            outer=landmarks["right_eye_outer"],
            inner=landmarks["right_eye_inner"],
            upper=landmarks["right_eye_upper"],
            lower=landmarks["right_eye_lower"],
        )

        avg_ear = (left_ear + right_ear) / 2.0

        mar = self.compute_mouth_aspect_ratio(
            mouth_left=landmarks["mouth_left"],
            mouth_right=landmarks["mouth_right"],
            upper_lip=landmarks["upper_lip"],
            lower_lip=landmarks["lower_lip"],
        )

        return {
            "left_ear": left_ear,
            "right_ear": right_ear,
            "ear": avg_ear,
            "mar": mar,
        }