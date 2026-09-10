from typing import Dict, Tuple

from perception.gaze import (
    GazeDirection,
    GazeEstimator,
)

Point2D = Tuple[int, int]


def build_landmarks(
    left_horizontal_ratio: float = 0.5,
    right_horizontal_ratio: float = 0.5,
    vertical_ratio: float = 0.5,
) -> Dict[str, Point2D]:
    """
    Construct bilateral synthetic eye geometry.

    The two eyes intentionally have opposite outer-to-inner directions,
    matching the bilateral geometry encountered by the real landmark
    configuration.

    Left project eye:
        outer = (100, 100)
        inner = (200, 100)

    Right project eye:
        outer = (400, 100)
        inner = (300, 100)

    After canonical horizontal normalization, equal physical gaze
    positions should produce equal left/right horizontal ratios.
    """

    left_outer = (100, 100)
    left_inner = (200, 100)

    right_outer = (400, 100)
    right_inner = (300, 100)

    left_iris_x = int(
        round(
            left_outer[0]
            + left_horizontal_ratio
            * (
                left_inner[0]
                - left_outer[0]
            )
        )
    )

    # Raw outer -> inner ratio must be complementary because
    # GazeEstimator canonicalizes the right eye with 1 - raw_ratio.
    right_raw_ratio = (
        1.0 - right_horizontal_ratio
    )

    right_iris_x = int(
        round(
            right_outer[0]
            + right_raw_ratio
            * (
                right_inner[0]
                - right_outer[0]
            )
        )
    )

    iris_y = int(
        round(
            90
            + vertical_ratio
            * 20
        )
    )

    return {
        "left_eye_outer": left_outer,
        "left_eye_inner": left_inner,
        "left_eye_upper": (150, 90),
        "left_eye_lower": (150, 110),
        "left_iris_center": (
            left_iris_x,
            iris_y,
        ),

        "right_eye_outer": right_outer,
        "right_eye_inner": right_inner,
        "right_eye_upper": (350, 90),
        "right_eye_lower": (350, 110),
        "right_iris_center": (
            right_iris_x,
            iris_y,
        ),
    }


def test_missing_landmarks(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        {
            "left_eye_outer": (100, 100),
        }
    )

    assert result is None

    print(
        "Missing-landmark test: passed"
    )


def test_center(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            left_horizontal_ratio=0.5,
            right_horizontal_ratio=0.5,
            vertical_ratio=0.5,
        )
    )

    assert result is not None

    print(
        "Synthetic center            "
        f"H={result.horizontal_ratio:.3f} "
        f"V={result.vertical_ratio:.3f} "
        f"LH={result.left_eye.horizontal_ratio:.3f} "
        f"RH={result.right_eye.horizontal_ratio:.3f}"
    )

    assert abs(
        result.horizontal_ratio - 0.5
    ) < 1e-6

    assert abs(
        result.vertical_ratio - 0.5
    ) < 1e-6

    assert abs(
        result.left_eye.horizontal_ratio
        - result.right_eye.horizontal_ratio
    ) < 1e-6


def test_horizontal_low(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            left_horizontal_ratio=0.25,
            right_horizontal_ratio=0.25,
            vertical_ratio=0.5,
        )
    )

    assert result is not None

    print(
        "Synthetic horizontal 0.25   "
        f"H={result.horizontal_ratio:.3f} "
        f"LH={result.left_eye.horizontal_ratio:.3f} "
        f"RH={result.right_eye.horizontal_ratio:.3f}"
    )

    assert abs(
        result.horizontal_ratio - 0.25
    ) < 1e-6


def test_horizontal_high(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            left_horizontal_ratio=0.75,
            right_horizontal_ratio=0.75,
            vertical_ratio=0.5,
        )
    )

    assert result is not None

    print(
        "Synthetic horizontal 0.75   "
        f"H={result.horizontal_ratio:.3f} "
        f"LH={result.left_eye.horizontal_ratio:.3f} "
        f"RH={result.right_eye.horizontal_ratio:.3f}"
    )

    assert abs(
        result.horizontal_ratio - 0.75
    ) < 1e-6


def test_vertical_low(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            vertical_ratio=0.25,
        )
    )

    assert result is not None

    print(
        "Synthetic vertical 0.25     "
        f"H={result.horizontal_ratio:.3f} "
        f"V={result.vertical_ratio:.3f}"
    )

    assert abs(
        result.vertical_ratio - 0.25
    ) < 1e-6


def test_vertical_high(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            vertical_ratio=0.75,
        )
    )

    assert result is not None

    print(
        "Synthetic vertical 0.75     "
        f"H={result.horizontal_ratio:.3f} "
        f"V={result.vertical_ratio:.3f}"
    )

    assert abs(
        result.vertical_ratio - 0.75
    ) < 1e-6


def test_asymmetric_eyes(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            left_horizontal_ratio=0.25,
            right_horizontal_ratio=0.75,
        )
    )

    assert result is not None

    print(
        "Synthetic asymmetric eyes   "
        f"H={result.horizontal_ratio:.3f} "
        f"LH={result.left_eye.horizontal_ratio:.3f} "
        f"RH={result.right_eye.horizontal_ratio:.3f}"
    )

    assert abs(
        result.left_eye.horizontal_ratio
        - 0.25
    ) < 1e-6

    assert abs(
        result.right_eye.horizontal_ratio
        - 0.75
    ) < 1e-6

    assert abs(
        result.horizontal_ratio
        - 0.5
    ) < 1e-6


def test_degenerate_eye(
    estimator: GazeEstimator,
) -> None:
    landmarks = build_landmarks()

    landmarks["left_eye_inner"] = (
        landmarks["left_eye_outer"]
    )

    result = estimator.estimate(
        landmarks
    )

    assert result is None

    print(
        "Degenerate-eye test: passed"
    )

def test_direction_center(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            left_horizontal_ratio=0.47,
            right_horizontal_ratio=0.47,
            vertical_ratio=0.45,
        )
    )

    assert result is not None
    assert result.direction == GazeDirection.CENTER

    print("Direction CENTER test: passed")


def test_direction_left(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            left_horizontal_ratio=0.65,
            right_horizontal_ratio=0.65,
            vertical_ratio=0.45,
        )
    )

    assert result is not None
    assert result.direction == GazeDirection.LEFT

    print("Direction LEFT test: passed")


def test_direction_right(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            left_horizontal_ratio=0.30,
            right_horizontal_ratio=0.30,
            vertical_ratio=0.45,
        )
    )

    assert result is not None
    assert result.direction == GazeDirection.RIGHT

    print("Direction RIGHT test: passed")


def test_direction_up(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            left_horizontal_ratio=0.47,
            right_horizontal_ratio=0.47,
            vertical_ratio=0.35,
        )
    )

    assert result is not None
    assert result.direction == GazeDirection.UP

    print("Direction UP test: passed")


def test_direction_down(
    estimator: GazeEstimator,
) -> None:
    result = estimator.estimate(
        build_landmarks(
            left_horizontal_ratio=0.47,
            right_horizontal_ratio=0.47,
            vertical_ratio=0.60,
        )
    )

    assert result is not None
    assert result.direction == GazeDirection.DOWN

    print("Direction DOWN test: passed")

def main() -> None:
    estimator = GazeEstimator()

    test_missing_landmarks(estimator)
    test_center(estimator)
    test_horizontal_low(estimator)
    test_horizontal_high(estimator)
    test_vertical_low(estimator)
    test_vertical_high(estimator)
    test_asymmetric_eyes(estimator)
    test_degenerate_eye(estimator)

    print()
    print(
        "[PASS] All gaze smoke tests passed."
    )


if __name__ == "__main__":
    main()