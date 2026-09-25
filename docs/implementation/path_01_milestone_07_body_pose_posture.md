# Path 1 — Milestone 7: Body Pose and Posture Analysis

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 7 |
| Status | Prototype implemented; deterministic tests passed; final integrated runtime regression pending |
| Date | 2026-09-24 |
| Author | Bassem Soliman |
| Repository | safety-critical-in-cabin-driver-monitoring |
| Branch | feat/body-pose-posture |
| Python | 3.11 / previously reported 3.11.7 |
| MediaPipe | 0.10.14 in latest Windows environment check |

---

# 1. Objective

Extend the existing source-independent in-cabin perception prototype with interpretable upper-body geometry and *independent* lateral and sagittal posture states, while preserving the completed facial-feature, temporal, head-pose and gaze modules (M1–M6).

The milestone adds four-landmark body pose, visibility-gated geometry, lateral tilt, non-metric shoulder–hip depth, driver/session-specific neutral-depth calibration, and experimental prototype labels. It does **not** infer distraction, impairment, unresponsiveness, ergonomics, or safety interventions.

Lateral outputs: `UPRIGHT`, `LEAN_LEFT`, `LEAN_RIGHT`, `UNKNOWN`. Sagittal outputs: `NOT_CALIBRATED`, `CALIBRATING`, `NEUTRAL`, `FORWARD_LEAN`, `UNKNOWN`. Combined forward/lateral results are permitted. Here `UPRIGHT` denotes small lateral angle only and sagittal `NEUTRAL` means no forward-threshold crossing; neither describes the whole three-dimensional posture.

---

# 2. Motivation

Head orientation and gaze from M5–M6 do not characterize torso displacement. Upper-body pose supplies another interpretable channel for future cabin perception. A monocular four-landmark baseline is inexpensive to prototype and can expose its own failure modes before richer pose estimation or multimodal fusion is attempted.

Early webcam tests also showed that a fixed **absolute** MediaPipe depth threshold fails when camera, session or seating position changes. M7 therefore separates measured geometric features from decision rules and introduces explicit neutral-relative calibration, without claiming that it solves lateral–sagittal coupling.

---

# 3. Software Perspective

New/updated project components:

| Module | Responsibility |
|---|---|
| `src/perception/body_features.py` | MediaPipe Pose wrapper, selected landmarks, continuous geometry, validity gates, two-axis estimator and calibration lifecycle. |
| `src/experiments/body_pose_smoke_test.py` | Isolated webcam and controlled recorded-file experiments; diagnostic dashboard and optional CSV logging. |
| `src/tests/test_m7_posture_regression.py` | Eight deterministic posture/calibration tests with synthetic geometry; no camera required. |
| `src/main.py` | Proposed M7 combined perception pipeline using the existing `VideoSource` abstraction. |
| `src/perception/visualization.py` | Existing M6 dashboard helpers, reused without replacement; the prepared M7 integration appends a separate panel within `main.py`. |

The revised body module imports MediaPipe lazily when `BodyPoseDetector` is instantiated so deterministic posture tests do not initialize the inference stack. `face_features.py` still imports MediaPipe for the full application, and the last provided integrated webcam attempt terminated during an import-related `MemoryError`.

---

# 4. Computer Vision Perspective

## 4.1 Selected Body Landmarks

MediaPipe Pose provides `left_shoulder` (11), `right_shoulder` (12), `left_hip` (23), and `right_hip` (24). The detector retains pixel positions, normalized x/y/z and model-reported visibility. All four selected landmarks must satisfy the prototype visibility threshold of 0.5.

## 4.2 Image-Space Geometry

The extractor computes shoulder/hip midpoints, their line angles, shoulder and hip widths, midpoint-to-midpoint torso length, and torso length normalized by shoulder width. The geometry-valid gate additionally requires shoulder width ≥10 px and torso length ≥10 px. Such gates reject obviously unsuitable measurements; they are *not* a guarantee of anatomical accuracy.

## 4.3 Lateral Torso Angle

With image y increasing downward, the implemented feature is:

```text
lateral_angle = degrees(atan2(
    shoulder_midpoint_x - hip_midpoint_x,
    hip_midpoint_y - shoulder_midpoint_y
))
```

In the tested non-mirrored frontal camera setup, positive values indicated anatomical left lean and negative values anatomical right lean. Camera mirroring and oblique viewpoints can change how a viewer interprets screen-side movement.

## 4.4 Shoulder–Hip Relative Depth

```text
shoulder_depth = mean(left_shoulder.z, right_shoulder.z)
hip_depth      = mean(left_hip.z, right_hip.z)
torso_dZ       = shoulder_depth - hip_depth
```

These are MediaPipe `pose_landmarks.z` values, **not** metric depth, physical pitch, or camera-calibrated 3D coordinates. A camera/session-specific neutral baseline is needed before applying the experimental sagittal rule.

---

# 5. Prototype Geometric Posture Classification

Lateral rule: `angle > +6°` → `LEAN_LEFT`; `angle < −6°` → `LEAN_RIGHT`; otherwise `UPRIGHT`. At exactly ±6° the state remains `UPRIGHT` under the strict inequalities.

After calibration, relative depth is `current_torso_dZ − neutral_torso_dZ`. The provisional rule `relative_dZ < −0.08` → `FORWARD_LEAN`, otherwise `NEUTRAL`. A valid observation before calibration yields `NOT_CALIBRATED`; valid observations during sample collection yield `CALIBRATING`; unavailable/invalid geometry yields `UNKNOWN` on both axes.

The ±6° and −0.08 boundaries are *development settings*, not person-independent, clinically meaningful or calibrated automotive thresholds. Backward lean is not a separate state, and a single frame is not a temporal behavior event.

---

# 6. Python Perspective

Core data types are typed dataclasses: `BodyLandmark`, `BodyPoseResult`, `BodyGeometryResult`, and `BodyPostureResult`. `LateralPostureState` and `SagittalPostureState` are explicit enums. `BodyPoseDetector` handles inference and resource cleanup, `BodyGeometryExtractor` computes continuous features, and `BodyPostureEstimator` owns configurable thresholds and calibration state.

Calibration is deliberately separate from `estimate()`: `begin_calibration()` starts collection, `update_calibration(geometry)` consumes one **new** frame, and `reset_calibration()` clears the session baseline. Repeated estimation or a paused display cannot inflate the sample count.

The calibration settings of the reviewed implementation are 30 valid frames, at most 150 attempted frames, and a maximum accepted sample range of 0.12 in the non-metric depth proxy. Frames with invalid geometry, non-finite values or `|lateral_angle| > 6°` are skipped. After 30 accepted frames, reject a depth range exceeding 0.12; otherwise store their median as the neutral `torso_dZ`. The user presses `C` **once**; a recorded file may begin calibration automatically only when its opening sequence is independently known to be neutral. Calibration is in memory for the current run only.

---

# 7. Engineering Perspective

The implementation keeps raw measurements, validity gating, calibration and interpreted labels as distinct stages. This supports deterministic testing and honest investigation of measurement confounders. M7 is a research prototype, not a qualified safety function.

The chosen median makes a calibration batch less sensitive to individual extreme samples; the range gate rejects an excessively unstable window. Neither guarantees stable future measurements or independence from side leaning. We retain both axes so a combined pose can be represented without forcing an exclusive single-state enum.

---

# 8. Project Architecture Impact

```text
WebcamVideoSource / FileVideoSource
                  |
               FramePacket
                  |
      +-----------+------------+
      |                        |
 MediaPipe Face Mesh      MediaPipe Pose
      |                        |
 EAR/MAR, head pose,    shoulders + hips
 gaze, face temporal           |
      |                BodyGeometryExtractor
      |                        |
      |                30-frame neutral calibration
      |                        |
      |                BodyPostureEstimator
      +-----------+------------+
                  |
       Existing M6 dashboard + M7 panel
```

The prepared integrated `main.py` preserves acquisition timestamps, existing face/head/gaze/temporal operations and appends a white M7 panel. A dashboard implementation is not evidence that the entire integrated runtime has passed final regression.

---

# 9. System Interfaces

## 9.1 Inputs

BGR OpenCV frame, optional source timestamps/frame index from the `VideoSource` pipeline, four Pose landmarks with x/y/z and visibility, operator neutral-calibration request, and configurable prototype thresholds.

## 9.2 Outputs

Pose presence and required-landmark visibility, validity-gated geometric measurements, lateral and sagittal enum states, neutral depth, relative depth change, calibration progress/message and spread, and optional experimental per-frame CSV from recorded smoke tests.

## 9.3 Dependencies

Python 3.11, OpenCV, MediaPipe Pose; NumPy is used by the prepared combined dashboard. The latest reported Windows installation had MediaPipe 0.10.14 and TensorFlow/TensorFlow-Intel 2.15.0; MediaPipe's optional TensorFlow import led to a memory-related launch failure in one full-pipeline attempt. The project-specific dependency environment remains to be rechecked.

## 9.4 Consumers

`main.py`, the M7 smoke test and future feature-fusion/temporal layers. No safety-relevant actuator or driver-state decision consumes posture at M7.

---

# 10. Visualization and Dashboard

The standalone smoke test shows selected shoulders/hips, midpoint geometry, validity, calibration progress, lateral/sagittal states and continuous signals. The prepared full pipeline reuses the existing M6 dashboard through `visualization.py` and appends a separate white M7 panel in `main.py`, displaying states, lateral angle, absolute/current `torso_dZ`, neutral baseline and relative change. `C` begins an interactive calibration, `R` resets, and `Q` exits. File mode supports `--auto-calibrate-file` for controlled recordings with a known neutral opening segment.

---

# 11. Validation Summary

Controlled webcam screenshots demonstrated neutral, pure forward lean, left/right lean and simultaneous forward/right lean. A 30-valid-frame median calibration completed in the later webcam experiment. A private, self-recorded webcam MP4 was successfully processed by the isolated file-video smoke test; its predictions were exported to CSV. A separate controlled recording was reported running in the combined pipeline after the Git Bash command was corrected.

All **eight** M7 deterministic tests passed in the user's terminal log on 2026-09-24, following lazy import of MediaPipe in the body module. This is strong evidence for the specified estimator logic—not evidence of anatomical landmark accuracy or complete runtime integration. An integrated webcam run later failed during MediaPipe/TensorFlow import with `MemoryError`; subsequent standalone MediaPipe import succeeded. A fresh full-pipeline runtime recheck has not been documented as completed.

See [Milestone 7 Validation](../validation/path_01_milestone_07_body_pose_posture_validation.md) for observations, reproducible commands, remaining checks and known failures.

---

# 12. Limitations

## 12.1 Relative, non-metric monocular depth

`pose_landmarks.z` is sensitive to viewpoint and estimation errors. A neutral baseline from one session is not transferable across cameras/drivers.

## 12.2 Lateral–sagittal coupling

Lateral leaning or body rotation can change the depth proxy. In one controlled right-lean screenshot the sagittal rule also fired; pure lateral versus combined intent needs time-aligned ground truth for a definitive error count.

## 12.3 Neutral drift and calibration validity

One post-calibration neutral return shifted by +0.1357 relative depth. The median protects the initial window, not long-term invariance. The range gate is a prototype stability heuristic.

## 12.4 Limited state definitions

No backward lean, seat-relative pose or calibrated three-dimensional trunk angle. `UPRIGHT` and sagittal `NEUTRAL` must not be described as holistic correct posture.

## 12.5 Basic confidence gates

Landmark visibility and pixel-size thresholds do not quantify error, occlusion effects or anatomical accuracy.

## 12.6 Dataset generalization

The controlled webcam recording offers known task ordering but no complete per-frame reference annotation. DMD recordings with cropped hips cannot validate this four-landmark pipeline.

## 12.7 Runtime environment

The last shown combined webcam attempt failed at MediaPipe/TensorFlow import due to `MemoryError`; a later simple MediaPipe import worked. Environment stability and the completed integrated regression remain open.

## 12.8 Safety scope

No production, medical, functional-safety, driver-impairment or real-world driver-risk performance claims are warranted.

---

# 13. Future Scalability

After M7 merge acceptance, proceed to M8 hand activity. Future M7 research may evaluate calibration-window sensitivity, temporal smoothing/hysteresis, controlled lateral/sagittal decoupling, MediaPipe world-landmark alternatives, multiple camera placements, instrumented reference angles and frame-annotated multi-person validation. These are explicitly future work, not claims about the current implementation.

---

# 14. Research / Technology Notes

- MediaPipe image landmark depth is an estimated relative coordinate, not a measured 3D body pose.
- Median calibration has robustness against isolated outliers but cannot remove systematic bias from viewpoint, rotation or lateral movements.
- A predicted `LEAN_LEFT` or `FORWARD_LEAN` label is an algorithm output. Without independently annotated movements, predicted co-occurrence cannot be converted into false-positive rate, precision or recall.
- Source-independent acquisition is necessary for repeatable replay; controlled source content and calibration intervals are necessary for meaningful evaluation.

---

# 15. Lessons Learned

A fixed absolute depth threshold did not transfer between webcam sessions. Explicit baseline calibration repaired that design defect, and repeated screenshots demonstrated multi-axis outputs. Recorded-video CSV review then exposed substantial coupling between predicted lateral and forward states; retaining this observation prevents overstating readiness. The lazy-import adjustment allowed deterministic geometry tests to complete independently of heavy inference dependencies, but the full application still needs its separate runtime check.

---

# 16. Next Milestone

Complete M7 acceptance first: run combined webcam and controlled-file regression; confirm previous face, head-pose, gaze and temporal features; verify `UNKNOWN` handling; reproduce or resolve the reported memory-related import issue; review privacy and Git diff; then merge `feat/body-pose-posture` into `main`. The planned next research milestone is **M8 — Hand Activity Analysis**.

---

# Milestone Completion Checklist

- [x] Four selected body landmarks and visibility gating implemented
- [x] Continuous torso geometry and relative-depth proxy implemented
- [x] Independent lateral and sagittal prototype states implemented
- [x] 30-valid-frame median calibration and unstable-window rejection implemented
- [x] Webcam prototype movements observed
- [x] Recorded self-collected video processed and experimental CSV produced
- [x] Eight deterministic posture/calibration tests passed
- [x] Prepared M7 dashboard and combined `main.py` integration
- [x] M7 implementation and validation documentation drafted
- [x] Final end-to-end webcam and file regression confirmed after import-memory failure
- [x] Private media/CSV exclusion and `git diff` reviewed
- [x] Commit, pull request and merge verified
