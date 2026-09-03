import cv2
import numpy as np

from perception.head_pose import (
    HeadPoseEstimator,
    HeadPoseResult,
)


FRAME_WIDTH = 1280
FRAME_HEIGHT = 720


def build_synthetic_landmarks(
    estimator: HeadPoseEstimator,
    pitch_degrees: float = 0.0,
    yaw_degrees: float = 0.0,
    roll_degrees: float = 0.0,
) -> dict[str, tuple[int, int]]:
    """
    Generate deterministic synthetic 2D landmarks for a known
    camera-facing head orientation.
    """

    camera_matrix = estimator._build_camera_matrix(
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
    )

    distortion_coefficients = np.zeros(
        (4, 1),
        dtype=np.float64,
    )

    pitch = np.radians(pitch_degrees)
    yaw = np.radians(yaw_degrees)
    roll = np.radians(roll_degrees)

    rotation_x = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, np.cos(pitch), -np.sin(pitch)],
            [0.0, np.sin(pitch), np.cos(pitch)],
        ],
        dtype=np.float64,
    )

    rotation_y = np.array(
        [
            [np.cos(yaw), 0.0, np.sin(yaw)],
            [0.0, 1.0, 0.0],
            [-np.sin(yaw), 0.0, np.cos(yaw)],
        ],
        dtype=np.float64,
    )

    rotation_z = np.array(
        [
            [np.cos(roll), -np.sin(roll), 0.0],
            [np.sin(roll), np.cos(roll), 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    relative_rotation = (
        rotation_z
        @ rotation_y
        @ rotation_x
    )

    model_rotation = (
        relative_rotation
        @ estimator._model_to_camera_neutral
    )

    rotation_vector, _ = cv2.Rodrigues(
        model_rotation
    )

    translation_vector = np.array(
        [
            [0.0],
            [0.0],
            [600.0],
        ],
        dtype=np.float64,
    )

    projected_points, _ = cv2.projectPoints(
        estimator._model_points,
        rotation_vector,
        translation_vector,
        camera_matrix,
        distortion_coefficients,
    )

    projected_points = projected_points.reshape(-1, 2)

    landmarks = {}

    for name, point in zip(
        estimator.REQUIRED_LANDMARKS,
        projected_points,
    ):
        landmarks[name] = (
            int(round(point[0])),
            int(round(point[1])),
        )

    return landmarks


def estimate_synthetic_pose(
    estimator: HeadPoseEstimator,
    pitch_degrees: float = 0.0,
    yaw_degrees: float = 0.0,
    roll_degrees: float = 0.0,
) -> HeadPoseResult:
    """
    Generate a synthetic pose and estimate it.
    """

    landmarks = build_synthetic_landmarks(
        estimator=estimator,
        pitch_degrees=pitch_degrees,
        yaw_degrees=yaw_degrees,
        roll_degrees=roll_degrees,
    )

    result = estimator.estimate(
        landmarks=landmarks,
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
    )

    assert result is not None
    assert isinstance(result, HeadPoseResult)

    return result


def print_pose(
    label: str,
    result: HeadPoseResult,
) -> None:
    """
    Print one head-pose result.
    """

    print(
        f"{label:<28}"
        f" yaw={result.yaw_degrees:>7.2f}"
        f" pitch={result.pitch_degrees:>7.2f}"
        f" roll={result.roll_degrees:>7.2f}"
    )


def run_camera_matrix_test(
    estimator: HeadPoseEstimator,
) -> None:
    """
    Verify the approximate camera intrinsic matrix.
    """

    camera_matrix = estimator._build_camera_matrix(
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
    )

    expected_matrix = np.array(
        [
            [1280.0, 0.0, 640.0],
            [0.0, 1280.0, 360.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        camera_matrix,
        expected_matrix,
    )

    print("Camera-matrix test: passed")


def run_missing_landmark_test(
    estimator: HeadPoseEstimator,
) -> None:
    """
    Verify graceful handling of incomplete landmarks.
    """

    estimator.reset()

    incomplete_landmarks = {
        "nose_tip": (640, 360),
        "chin": (640, 500),
    }

    result = estimator.estimate(
        landmarks=incomplete_landmarks,
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
    )

    assert result is None

    print("Missing-landmark test: correctly rejected")


def run_neutral_pose_test(
    estimator: HeadPoseEstimator,
) -> None:
    """
    Verify a synthetic neutral pose.
    """

    estimator.reset()

    result = estimate_synthetic_pose(
        estimator=estimator,
    )

    print_pose(
        "Synthetic neutral",
        result,
    )

    assert abs(result.yaw_degrees) < 3.0
    assert abs(result.pitch_degrees) < 3.0
    assert abs(result.roll_degrees) < 3.0


def run_positive_yaw_test(
    estimator: HeadPoseEstimator,
) -> None:
    """
    Verify positive synthetic yaw.
    """

    estimator.reset()

    result = estimate_synthetic_pose(
        estimator=estimator,
        yaw_degrees=30.0,
    )

    print_pose(
        "Synthetic +yaw",
        result,
    )

    assert result.yaw_degrees > 20.0
    assert abs(result.roll_degrees) < 10.0


def run_negative_yaw_test(
    estimator: HeadPoseEstimator,
) -> None:
    """
    Verify negative synthetic yaw.
    """

    estimator.reset()

    result = estimate_synthetic_pose(
        estimator=estimator,
        yaw_degrees=-30.0,
    )

    print_pose(
        "Synthetic -yaw",
        result,
    )

    assert result.yaw_degrees < -20.0
    assert abs(result.roll_degrees) < 10.0


def run_pitch_test(
    estimator: HeadPoseEstimator,
) -> None:
    """
    Verify synthetic pitch response.
    """

    estimator.reset()

    result = estimate_synthetic_pose(
        estimator=estimator,
        pitch_degrees=-25.0,
    )

    print_pose(
        "Synthetic pitch",
        result,
    )

    assert result.pitch_degrees < -15.0
    assert abs(result.yaw_degrees) < 10.0
    assert abs(result.roll_degrees) < 10.0


def run_roll_test(
    estimator: HeadPoseEstimator,
) -> None:
    """
    Verify synthetic roll response.
    """

    estimator.reset()

    result = estimate_synthetic_pose(
        estimator=estimator,
        roll_degrees=30.0,
    )

    print_pose(
        "Synthetic roll",
        result,
    )

    assert result.roll_degrees > 20.0
    assert abs(result.yaw_degrees) < 10.0
    assert abs(result.pitch_degrees) < 10.0


def run_angular_difference_test() -> None:
    """
    Verify wrap-around angular difference.
    """

    difference = (
        HeadPoseEstimator._angular_difference(
            179.0,
            -179.0,
        )
    )

    assert abs(difference - 2.0) < 1e-6

    print(
        "Angular-difference test: passed"
    )


def run_reset_test(
    estimator: HeadPoseEstimator,
) -> None:
    """
    Verify temporal-state reset.
    """

    estimator.reset()

    result = estimate_synthetic_pose(
        estimator=estimator,
        yaw_degrees=15.0,
    )

    assert result is not None
    assert estimator._previous_result is not None

    estimator.reset()

    assert estimator._previous_result is None
    assert estimator._previous_rotation_vector is None
    assert estimator._previous_translation_vector is None

    print("Reset test: passed")


def run_pose_continuity_test(
    estimator: HeadPoseEstimator,
) -> None:
    """
    Verify continuity through a gradual yaw sequence.
    """

    estimator.reset()

    sequence = (
        0.0,
        10.0,
        20.0,
        30.0,
        40.0,
        50.0,
    )

    previous_result = None

    for yaw_degrees in sequence:
        result = estimate_synthetic_pose(
            estimator=estimator,
            yaw_degrees=yaw_degrees,
        )

        print_pose(
            f"Continuity yaw {yaw_degrees:.0f}",
            result,
        )

        if previous_result is not None:
            difference = (
                HeadPoseEstimator._angular_difference(
                    result.yaw_degrees,
                    previous_result.yaw_degrees,
                )
            )

            assert difference < 20.0

        previous_result = result

    assert previous_result is not None
    assert previous_result.yaw_degrees > 40.0

    print("Pose-continuity test: passed")


def main() -> None:
    """
    Run deterministic Milestone 5 head-pose smoke tests.
    """

    estimator = HeadPoseEstimator()

    run_camera_matrix_test(estimator)
    run_missing_landmark_test(estimator)

    run_neutral_pose_test(estimator)
    run_positive_yaw_test(estimator)
    run_negative_yaw_test(estimator)
    run_pitch_test(estimator)
    run_roll_test(estimator)

    run_angular_difference_test()
    run_reset_test(estimator)
    run_pose_continuity_test(estimator)

    print()
    print("[PASS] All head-pose smoke tests passed.")


if __name__ == "__main__":
    main()