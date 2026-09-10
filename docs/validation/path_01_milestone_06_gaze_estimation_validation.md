# Path 1 _ Milestone 6 Validation: Gaze Estimation

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 _ Fast Prototype |
| Milestone | 6 |
| Validation Date | 2026-09-10 |
| Status | Passed _ Prototype Validation |
| Author | Bassem Soliman |
| Python | 3.11.7 |
| MediaPipe | 0.10.35 |
| Operating System | Windows 11 |
| Live Source | RGB Webcam |
| Recorded Source | Private DMD Sample |
| Repository Branch | feat/gaze-estimation |

---

# 1. Validation Objective

The objective of Milestone 6 validation is to verify that the system can estimate interpretable iris-position geometry from both eyes and integrate the result into the existing source-independent cabin perception pipeline.

Validation focuses on iris landmark availability, per-eye horizontal and vertical gaze geometry, bilateral horizontal normalization, combined H/V measurements, inter-eye disagreement, gaze consistency, prototype direction labels, live webcam operation, recorded-video operation, source-independent integration, and graceful handling of difficult observations.

The validation does not attempt to demonstrate production gaze accuracy, calibrated angular gaze error, distraction detection accuracy, attention-state classification accuracy, safety integrity, or medical/cognitive-state inference.

---

# 2. Test Environment

## 2.1 Hardware

Validation was performed on the existing Windows development workstation. Live validation used an RGB webcam. No dedicated infrared or near-infrared Driver Monitoring camera was used.

## 2.2 Software

Main software environment:

```text
Windows 11
Python 3.11.7
OpenCV
MediaPipe 0.10.35
NumPy
```

## 2.3 Input Sources

Two source types were validated.

### Webcam

Live webcam input was used for controlled gaze movements.

### Recorded Video

A local private DMD sample was used through the existing source-independent file-video pipeline. The private DMD sample is not committed to the repository.

---

# 3. Test Configuration

The gaze estimator uses selected eye and iris landmarks from MediaPipe Face Mesh.

MediaPipe refinement is enabled:

```text
refine_landmarks = True
```

Selected iris centers:

```text
left_iris_center  = 468
right_iris_center = 473
```

Prototype bilateral consistency thresholds:

```text
maximum dH = 0.15
maximum dV = 0.20
```

Prototype gaze-direction thresholds:

```text
Horizontal:
H < 0.40  → RIGHT
H > 0.56  → LEFT
otherwise → CENTER

Vertical:
V < 0.41  → UP
V > 0.50  → DOWN
otherwise → CENTER
```

When gaze consistency is low:

```text
Direction → UNKNOWN
```

The thresholds are initial development values rather than calibrated safety thresholds.

---

# 4. Deterministic Validation

A dedicated smoke-test module is provided:

```text
src/experiments/gaze_smoke_test.py
```

The synthetic geometry tests are intended to verify algorithmic behavior independently of webcam landmark noise.

The test design covers:

| Test | Validation Purpose |
|------|--------------------|
| Missing landmarks | Estimator rejects incomplete input |
| Center geometry | H/V midpoint calculation |
| Horizontal low ratio | Normalized horizontal projection |
| Horizontal high ratio | Normalized horizontal projection |
| Vertical low ratio | Normalized vertical projection |
| Vertical high ratio | Normalized vertical projection |
| Bilateral geometry | Right-eye horizontal canonicalization |
| Combined H/V | Correct bilateral averaging |
| Asymmetric eyes | Fusion behavior |
| Degenerate geometry | Invalid geometry handled safely |
| CENTER label | Direction classification |
| LEFT label | Direction classification |
| RIGHT label | Direction classification |
| UP label | Direction classification |
| DOWN label | Direction classification |
| dH / dV | Inter-eye disagreement calculation |
| Consistency gate | GOOD / LOW determination |

The deterministic tests are designed to validate the mathematical implementation rather than real-world gaze-estimation accuracy.

A final regression rerun should be performed immediately before Git commit and pull-request creation.

---

# 5. Webcam Validation

## 5.1 Validation Procedure

The live pipeline was executed using:

```bash
PYTHONPATH=src python src/main.py --source webcam
```

The driver intentionally changed eye direction while attempting to keep head orientation relatively stable.

Primary controlled states included:

```text
CENTER
LEFT
RIGHT
UP
DOWN
```

The following dashboard outputs were monitored:

```text
Direction
Combined H
Combined V
Left eye H/V
Right eye H/V
dH / dV
Consistency
Head Pose
```

## 5.2 Horizontal Direction Validation

Controlled webcam testing established:

```text
Higher H → LEFT
Lower H  → RIGHT
```

A representative intentional LEFT-gaze sample produced approximately:

```text
Combined H = 0.678
Combined V = 0.471
```

The associated head pose was approximately:

```text
Yaw   = -1.6 degrees
Pitch = -1.2 degrees
Roll  = -1.6 degrees
```

The approximately neutral head orientation provides useful qualitative evidence that the large horizontal gaze value was primarily associated with eye movement rather than large head rotation.

This observation was used to confirm the horizontal semantic mapping.

## 5.3 Vertical Direction Validation

Controlled webcam testing established:

```text
Lower V → UP
Higher V → DOWN
```

A representative intentional UP-gaze observation produced approximately:

```text
Combined H = 0.501
Combined V = 0.399
Left eye H/V  = 0.490 / 0.434
Right eye H/V = 0.512 / 0.365
dH = 0.022
dV = 0.069
Consistency = GOOD
```

The head-pose pitch was approximately:

```text
Pitch = -0.4 degrees
```

This provided useful qualitative evidence that the decrease in vertical gaze ratio was caused primarily by eye movement.

---

# 6. Bilateral Consistency Validation

The disagreement metrics were manually observed under multiple webcam conditions.

Representative observations included:

| dH | dV | Result |
|----|----|--------|
| 0.031 | 0.072 | GOOD |
| 0.122 | 0.032 | GOOD |
| 0.031 | 0.032 | GOOD |
| 0.016 | 0.292 | LOW |
| 0.051 | 0.054 | GOOD |
| 0.335 | 0.095 | LOW |

These results confirm that the consistency logic mechanically follows the configured thresholds.

For example, `dV = 0.292` exceeds the maximum `dV = 0.20` and therefore produces `Consistency = LOW`. Similarly, `dH = 0.335` exceeds the maximum `dH = 0.15` and produces `Consistency = LOW`.

---

# 7. Important Consistency Finding

One of the most important observations from Milestone 6 is that inter-eye agreement should not be interpreted as absolute gaze accuracy.

A representative strong-yaw observation produced approximately:

```text
Head yaw = +40.9 degrees
Combined H = 0.408
Combined V = 0.676
dH = 0.051
dV = 0.054
Consistency = GOOD
```

Although both eyes agreed numerically, the strong head rotation means that perspective distortion can still affect absolute gaze geometry.

Therefore, `GOOD consistency` means that the two eyes agree sufficiently. It does not mean that the gaze estimate is guaranteed correct.

This distinction must be preserved in future development and documentation.

---

# 8. Direction Classification Validation

The following primary direction states were manually checked using the webcam:

| Intended Eye Direction | Expected H/V Trend | Prototype Output | Status |
|------------------------|----------------------|------------------|--------|
| CENTER | Middle H / middle V | CENTER | Pass |
| LEFT | Increased H | LEFT | Pass |
| RIGHT | Decreased H | RIGHT | Pass |
| UP | Decreased V | UP | Pass |
| DOWN | Increased V | DOWN | Pass |

Diagonal direction states are implemented by combining horizontal and vertical decisions:

```text
LEFT_UP
LEFT_DOWN
RIGHT_UP
RIGHT_DOWN
```

They are supported by the classification implementation. The main manual validation focus of this milestone was the five primary directions.

---

# 9. Recorded DMD Video Validation

## 9.1 Objective

Recorded-video testing verifies that gaze estimation is not coupled only to webcam acquisition.

The existing source-independent architecture was used with a local private DMD sample.

Example execution:

```bash
PYTHONPATH=src python src/main.py \
  --source file \
  --video-path "/d/Cabin_sensing/practical/safety-critical-in-cabin-driver-monitoring/data/private/sample_DMD_face.mp4"
```

Mirroring was not enabled.

## 9.2 Observed Behavior

The DMD sample successfully passed through the same perception pipeline used for the webcam.

The following functions operated during recorded-video playback:

```text
video acquisition
face detection
facial landmarks
EAR / MAR
temporal state
head pose
iris geometry
combined gaze H/V
dH / dV
consistency
prototype gaze direction
dashboard visualization
```

The recorded video operated successfully with the Milestone 6 gaze pipeline. No source-specific gaze-estimation implementation was required.

This supports the architectural goal of source-independent perception processing.

---

# 10. Face-Loss and Invalid-Geometry Behavior

The gaze estimator requires all necessary eye and iris landmarks. If the required geometry is unavailable, the estimator does not force a numerical gaze result. This avoids propagating stale or fabricated gaze measurements.

The dashboard can therefore represent unavailable gaze information when the face or required landmarks cannot be reliably processed.

Degenerate eye geometry is also rejected by minimum geometry checks. This is preferable to division by near-zero eye dimensions or arbitrary numerical output.

---

# 11. Integration Regression

Milestone 6 was integrated without intentionally modifying the logic of previous perception stages.

Existing components retained their responsibilities:

```text
FacialGeometryExtractor → EAR / MAR

TemporalRuleEngine →
    NORMAL
    BLINK_CANDIDATE
    PROLONGED_EYE_CLOSURE
    SUSTAINED_MOUTH_OPENING
    PROLONGED_FACE_LOSS

HeadPoseEstimator →
    yaw
    pitch
    roll

GazeEstimator →
    H/V
    disagreement
    consistency
    direction
```

Gaze direction does not currently modify the temporal state machine. This is intentional.

A final regression run before commit should include:

```bash
python -m compileall src
PYTHONPATH=src python -m experiments.temporal_rules_smoke_test
PYTHONPATH=src python -m experiments.head_pose_smoke_test
PYTHONPATH=src python -m experiments.gaze_smoke_test
```

---

# 12. Dashboard Validation

Milestone 6 introduced a reorganized visualization layout. The runtime display separates the camera image from numerical perception output.

Target layout:

```text
┌──────────────────────────────────────┬─────────────────────────┐
│                                      │ CABIN SENSING DASHBOARD │
│                                      │ Runtime                 │
│          VIDEO IMAGE                 │ Face Geometry           │
│                                      │ Source Metadata         │
│                                      │ Temporal State          │
│                                      │ Head Pose               │
│ Path 1 — Milestone 6                 │ Gaze Geometry           │
└──────────────────────────────────────┴─────────────────────────┘
```

Validation confirmed that this layout provides clearer runtime inspection than placing all measurements over the driver image.

The gaze dashboard displays:

```text
Direction
Combined H
Combined V
Left eye H/V
Right eye H/V
dH / dV
Consistency
```

The video is kept visually separated from numerical debug information.

---

# 13. Performance Summary

| Metric | Observation |
|--------|-------------|
| Webcam operation | Real-time prototype operation |
| Recorded-video operation | Successful |
| Iris detection | Successful under tested conditions |
| Horizontal gaze response | Correct qualitative trend |
| Vertical gaze response | Correct qualitative trend |
| Bilateral canonicalization | Verified |
| dH/dV calculation | Verified |
| Consistency logic | Correct according to configured thresholds |
| Direction labels | Primary directions verified |
| Source independence | Verified with webcam and file video |
| Integration stability | Acceptable for Fast Prototype |
| Quantitative angular accuracy | Not measured |
| Dataset benchmark | Not performed |
| Safety validation | Not performed |

No formal latency, CPU-load, GPU-load, or gaze-angle error benchmark was performed in this milestone.

---

# 14. Evidence

Validation evidence consists of controlled webcam observations, runtime dashboard screenshots, DMD recorded-video observations, and deterministic smoke tests.

Private dataset material should remain outside the repository. The DMD sample is stored under the project's private data area and must not be committed unless redistribution rights explicitly permit it.

Recommended repository evidence should contain only material that is legally and ethically suitable for publication.

---

# 15. Known Issues

## Issue 1 — Strong Head Pose

### Observation

Large head yaw can change apparent iris/eye geometry. Inter-eye consistency may still remain `GOOD`.

### Cause

The current estimator uses 2D image-space geometry.

### Current Handling

Raw head pose and gaze values are displayed separately.

### Future Improvement

Introduce head-pose-aware validity gating, calibration, 3D gaze estimation, or a learned gaze model.

## Issue 2 — Eye Closure

### Observation

Iris geometry may become unreliable when the eye is nearly closed.

### Cause

The current gaze estimator does not explicitly gate measurements according to eye openness.

### Current Handling

EAR remains available independently for diagnostic inspection.

### Future Improvement

Introduce per-eye openness validity criteria before accepting gaze geometry.

## Issue 3 — Fixed Direction Thresholds

### Observation

Neutral gaze position and range may vary between drivers.

### Cause

Current thresholds are empirical Fast Prototype values.

### Current Handling

Thresholds remain configurable estimator parameters.

### Future Improvement

Use driver-specific and camera-specific calibration.

## Issue 4 — Consistency Does Not Equal Accuracy

### Observation

Both eyes can agree while both are biased by pose or perspective.

### Cause

`dH` and `dV` measure bilateral disagreement only.

### Current Handling

The dashboard uses the term `Consistency`, not calibrated confidence.

### Future Improvement

Develop a broader validity model incorporating head pose, eye openness, landmark confidence, image quality, occlusion, and temporal stability.

## Issue 5 — No Temporal Gaze Reasoning

### Observation

Direction is classified independently for each frame.

### Cause

Gaze has not yet been integrated with the temporal decision layer.

### Current Handling

Gaze remains a perception-level output.

### Future Improvement

Add duration-aware gaze events in a later milestone.

## Issue 6 — No Behavioral Interpretation

### Observation

The system does not currently infer distraction or inattention from gaze.

### Cause

A single geometric direction does not provide enough behavioral context.

### Current Handling

Direction labels remain geometric only.

### Future Improvement

Fuse gaze with head pose, duration, cabin/road regions, vehicle context, posture, and hand activity.

## Issue 7 — Head-Pose Roll Ambiguity

### Observation

The existing head-pose estimator can occasionally produce roll values near approximately ±180 degrees.

### Cause

This is related to the existing PnP/Euler representation and pose-solution ambiguity.

### Current Handling

It is treated as an upstream head-pose limitation.

### Future Improvement

Continue improving pose continuity and rotation representation in the head-pose module.

This issue is not attributed to the gaze-estimation algorithm.

---

# 16. Engineering Assessment

Milestone 6 successfully introduces an interpretable gaze-estimation baseline into the Fast Prototype architecture.

Strengths include simple mathematical formulation, modular implementation, bilateral eye processing, corrected horizontal coordinate convention, transparent H/V measurements, explicit inter-eye disagreement, explicit consistency state, prototype gaze-direction classification, webcam operation, recorded-video operation, source-independent integration, and separation from behavioral reasoning.

The main limitations are 2D geometry only, no camera calibration, no driver calibration, no angular gaze ground truth, sensitivity to head pose, no eye-openness gate, no quantitative dataset benchmark, no temporal gaze behavior, and no production safety validation.

Overall assessment:

**Path 1 — Milestone 6 passes prototype validation as an interpretable geometric gaze-estimation baseline.**

The system is suitable for continued research and engineering development. It should not yet be presented as a calibrated or production-ready Driver Monitoring gaze estimator.

---

# 17. Recommendations

Immediate recommendations:

- preserve raw H/V output
- preserve per-eye values
- preserve dH/dV
- preserve consistency output
- preserve head pose as a separate signal
- do not convert gaze direction directly into distraction
- rerun all deterministic tests before commit
- keep private DMD material outside Git

Near-term technical improvements:

- eye-openness gaze gating
- temporal smoothing
- temporal gaze-duration analysis
- stronger head-pose validity criteria
- configurable calibration
- quantitative dataset experiments

Long-term research improvements:

- calibrated 3D gaze estimation
- learning-based gaze estimation
- ROI-based gaze interpretation
- driver-specific adaptation
- multimodal driver-state fusion
- uncertainty estimation
- comparison against labeled ground truth

---

# 18. Next Validation

The next validation stage should depend on the next Path 1 perception module.

For later gaze development, dedicated validation should include:

```text
multiple drivers
multiple camera positions
different distances
glasses
different lighting
head yaw sweeps
head pitch sweeps
eye closure
partial occlusion
defined gaze targets
longer recorded sequences
quantitative gaze error
temporal gaze transitions
```

This would move the system from qualitative prototype validation toward reproducible research evaluation.

---

# Validation Completion Checklist

- [x] Iris landmark integration checked
- [x] Horizontal gaze geometry validated
- [x] Vertical gaze geometry validated
- [x] Bilateral horizontal canonicalization validated
- [x] Combined H/V behavior validated
- [x] dH/dV behavior validated
- [x] GOOD / LOW consistency behavior validated
- [x] CENTER direction checked
- [x] LEFT direction checked
- [x] RIGHT direction checked
- [x] UP direction checked
- [x] DOWN direction checked
- [x] Webcam validation completed
- [x] Recorded DMD video validation completed
- [x] Source-independent pipeline validated
- [x] Dashboard validated
- [x] Known limitations documented
- [x] Engineering assessment completed
- [x] Final regression tests rerun
- [x] Git commit completed
- [x] GitHub pull request merged
