"""Deterministic Milestone 7 posture/calibration regression tests.

Run from paths/01_fast_prototype with:
    PYTHONPATH=src python -m unittest -v tests.test_m7_posture_regression
No camera is required (MediaPipe is imported by the production module).
"""
import unittest

from perception.body_features import (
    BodyGeometryResult,
    BodyPostureEstimator,
    LateralPostureState,
    SagittalPostureState,
)


def geometry(angle=0.0, dz=-0.20, valid=True):
    return BodyGeometryResult(
        shoulder_midpoint=(160., 100.), hip_midpoint=(160., 240.),
        shoulder_angle_degrees=0., hip_angle_degrees=0.,
        torso_lateral_angle_degrees=angle,
        shoulder_depth=dz, hip_depth=0., torso_depth_delta=dz,
        shoulder_width_pixels=120., hip_width_pixels=100.,
        torso_length_pixels=140., normalized_torso_length=140./120.,
        geometry_valid=valid,
    )


class M7PostureRegression(unittest.TestCase):
    def setUp(self):
        self.estimator = BodyPostureEstimator()

    def calibrate(self, dz=-0.20):
        self.estimator.begin_calibration()
        self.assertTrue(self.estimator.is_calibrating)
        for index in range(30):
            finished = self.estimator.update_calibration(geometry(dz=dz))
            self.assertEqual(finished, index == 29)
        self.assertTrue(self.estimator.is_calibrated)
        self.assertAlmostEqual(self.estimator.neutral_torso_depth_delta, dz)

    def test_initial_state(self):
        result = self.estimator.estimate(geometry())
        self.assertEqual(result.sagittal_state, SagittalPostureState.NOT_CALIBRATED)
        self.assertEqual(result.lateral_state, LateralPostureState.UPRIGHT)

    def test_median_calibration(self):
        self.estimator.begin_calibration()
        for i in range(29):
            self.assertFalse(self.estimator.update_calibration(geometry(dz=-.2)))
        self.assertTrue(self.estimator.update_calibration(geometry(dz=-.16)))
        self.assertAlmostEqual(self.estimator.neutral_torso_depth_delta, -.2)

    def test_forward_and_return(self):
        self.calibrate()
        self.assertEqual(self.estimator.estimate(geometry(dz=-.31)).sagittal_state,
                         SagittalPostureState.FORWARD_LEAN)
        self.assertEqual(self.estimator.estimate(geometry(dz=-.20)).sagittal_state,
                         SagittalPostureState.NEUTRAL)

    def test_lateral_and_combined(self):
        self.calibrate()
        self.assertEqual(self.estimator.estimate(geometry(angle=9)).lateral_state,
                         LateralPostureState.LEAN_LEFT)
        combined = self.estimator.estimate(geometry(angle=-11, dz=-.35))
        self.assertEqual(combined.lateral_state, LateralPostureState.LEAN_RIGHT)
        self.assertEqual(combined.sagittal_state, SagittalPostureState.FORWARD_LEAN)

    def test_lateral_boundaries(self):
        self.calibrate()
        for angle in (-6., 6.):
            self.assertEqual(self.estimator.estimate(geometry(angle=angle)).lateral_state,
                             LateralPostureState.UPRIGHT)

    def test_missing_and_invalid_geometry(self):
        self.calibrate()
        for data in (None, geometry(valid=False)):
            result = self.estimator.estimate(data)
            self.assertEqual(result.lateral_state, LateralPostureState.UNKNOWN)
            self.assertEqual(result.sagittal_state, SagittalPostureState.UNKNOWN)
        self.estimator.begin_calibration()
        for _ in range(3):
            self.assertFalse(self.estimator.update_calibration(None))
        self.assertEqual(self.estimator.calibration_progress[0], 0)

    def test_unstable_calibration_rejected(self):
        self.estimator.begin_calibration()
        for i in range(30):
            self.estimator.update_calibration(geometry(dz=-.20 if i % 2 else -.05))
        self.assertFalse(self.estimator.is_calibrated)
        self.assertFalse(self.estimator.is_calibrating)

    def test_reset(self):
        self.calibrate()
        self.estimator.reset_calibration()
        self.assertFalse(self.estimator.is_calibrated)
        self.assertEqual(self.estimator.estimate(geometry()).sagittal_state,
                         SagittalPostureState.NOT_CALIBRATED)


if __name__ == '__main__':
    unittest.main()
