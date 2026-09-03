# Path 1 — Milestone 5 Validation: Head Pose Estimation

---

# Metadata

| Item | Value |
|------|-------|
| Project | Safety-Critical In-Cabin Driver Monitoring |
| Path | Path 1 — Fast Prototype |
| Milestone | 5 |
| Validation Target | Head Pose Estimation |
| Status | Passed |
| Date | 2026-09-03 |
| Author | Bassem Soliman |
| Repository | `safety-critical-in-cabin-driver-monitoring` |
| Primary Method | OpenCV Perspective-n-Point (`solvePnP`) |
| Inputs | MediaPipe Face Mesh selected landmarks |
| Outputs | Yaw, pitch, roll, rotation vector, translation vector |
| Validation Modes | Deterministic synthetic tests, webcam, recorded-video sample |
| Dataset Handling | Private DMD media retained outside public repository |

---

# 1. Validation Objective

The objective of this validation is to verify that the Milestone 5 head-pose implementation behaves correctly as a geometric perception baseline and integrates without regression into the existing source-independent in-cabin perception pipeline.

The validation covers:

- camera-matrix construction
- required-landmark handling
- neutral head orientation
- positive and negative yaw
- pitch
- roll
- angular wraparound
- estimator reset
- gradual pose continuity
- strong-yaw stability
- prolonged face-loss recovery
- live webcam execution
- recorded-video execution
- compatibility with the existing Milestone 4B temporal logic

The validation does not attempt to demonstrate:

- calibrated ground-truth head-pose accuracy
- medical or behavioral driver-state classification
- production safety performance
- final distraction detection
- final gaze estimation

---

# 2. Test Environment

Validation was performed in the Path 1 fast-prototype environment.

Primary software stack:

```text
Python 3.11
OpenCV
MediaPipe Face Mesh
NumPy
```

Project execution directory:

```text
paths/01_fast_prototype/
```

Primary implementation files:

```text
src/perception/head_pose.py
src/perception/face_features.py
src/perception/visualization.py
src/decision/temporal_rules.py
src/experiments/head_pose_smoke_test.py
src/experiments/temporal_rules_smoke_test.py
src/main.py
```

Input modes validated:

```text
WebcamVideoSource
FileVideoSource
```

Recorded-video validation used a private local DMD sample.

The raw and derived DMD media are not intended for public repository distribution unless redistribution permission is explicitly confirmed.

---

# 3. Test Configuration

## 3.1 Head-Pose Geometry

The head-pose estimator uses six facial landmarks:

```text
nose_tip
chin
left_eye_outer
right_eye_outer
mouth_left
mouth_right
```

These 2D image points are matched with a generic 3D facial reference model.

---

## 3.2 Camera Approximation

The current camera intrinsic approximation is:

```text
fx = frame_width
fy = frame_width
cx = frame_width / 2
cy = frame_height / 2
```

Lens-distortion coefficients are approximated as zero.

For the deterministic synthetic tests, the test frame resolution is:

```text
1280 × 720
```

The expected camera matrix is:

```text
[1280    0    640]
[   0 1280    360]
[   0    0      1]
```

---

## 3.3 PnP Configuration

The estimator uses:

```text
cv2.SOLVEPNP_ITERATIVE
```

For the first valid frame, pose is solved without a prior pose guess.

For subsequent frames, the previous valid:

```text
rotation_vector
translation_vector
```

are supplied as the initial estimate through `useExtrinsicGuess=True`.

---

## 3.4 Pose Continuity Configuration

Prototype continuity parameter:

```text
max_angle_jump_degrees = 75°
```

The continuity guard compares:

- yaw change
- pitch change
- roll change

between the current candidate and the previously accepted pose.

The smallest angular difference is used across the ±180° boundary.

The 75° value is an engineering prototype guard and is not a validated safety or biomechanical threshold.

---

## 3.5 Face-Loss Recovery

The head-pose estimator retains previous pose state during short face-detection interruptions.

When face-loss duration reaches the existing prolonged face-loss threshold from the temporal engine, the head-pose estimator is reset.

Current prolonged face-loss threshold:

```text
1.00 s
```

---

# 4. Test Cases

## 4.1 Camera-Matrix Construction

Purpose:

Verify that the approximate intrinsic matrix is generated correctly for a known frame size.

Expected:

```text
frame_width = 1280
frame_height = 720

fx = 1280
fy = 1280
cx = 640
cy = 360
```

Result:

```text
Camera-matrix test: passed
```

Status:

**PASS**

---

## 4.2 Missing-Landmark Handling

Purpose:

Verify graceful rejection of incomplete facial geometry.

Input contains only a subset of required landmarks.

Expected:

```text
HeadPoseEstimator.estimate(...) → None
```

Observed:

```text
Missing-landmark test: correctly rejected
```

Status:

**PASS**

---

## 4.3 Synthetic Neutral Pose

Purpose:

Verify that a synthetic camera-facing neutral pose reconstructs approximately:

```text
yaw ≈ 0°
pitch ≈ 0°
roll ≈ 0°
```

Observed:

```text
Synthetic neutral
yaw   = -0.00°
pitch =  0.31°
roll  = -0.00°
```

Status:

**PASS**

---

## 4.4 Synthetic Positive Yaw

Purpose:

Verify response to a known positive yaw input.

Synthetic input:

```text
yaw = +30°
```

Observed:

```text
yaw   = +29.89°
pitch ≈  0.00°
roll  ≈ +0.02°
```

Status:

**PASS**

---

## 4.5 Synthetic Negative Yaw

Purpose:

Verify response to a known negative yaw input.

Synthetic input:

```text
yaw = -30°
```

Observed:

```text
yaw   = -29.89°
pitch ≈  0.00°
roll  ≈ -0.02°
```

Status:

**PASS**

---

## 4.6 Synthetic Pitch

Purpose:

Verify pitch-axis response and limited cross-axis contamination under synthetic geometry.

Synthetic input:

```text
pitch = -25°
```

Observed:

```text
yaw   ≈  0.00°
pitch = -25.35°
roll  ≈  0.00°
```

Status:

**PASS**

---

## 4.7 Synthetic Roll

Purpose:

Verify roll-axis response.

Synthetic input:

```text
roll = +30°
```

Observed:

```text
yaw   ≈ +0.10°
pitch ≈ -0.01°
roll  = +29.89°
```

Status:

**PASS**

---

## 4.8 Angular Wraparound

Purpose:

Verify correct angular comparison near the ±180° boundary.

Test:

```text
angle A = +179°
angle B = -179°
```

Expected shortest angular difference:

```text
2°
```

Observed:

```text
Angular-difference test: passed
```

Status:

**PASS**

---

## 4.9 Estimator Reset

Purpose:

Verify that pose-history state is cleared correctly.

State cleared:

```text
_previous_result
_previous_rotation_vector
_previous_translation_vector
```

Observed:

```text
Reset test: passed
```

Status:

**PASS**

---

## 4.10 Gradual Yaw Continuity

Purpose:

Verify stable tracking across a deterministic gradual yaw sequence.

Synthetic sequence:

```text
0°
10°
20°
30°
40°
50°
```

Observed:

```text
Continuity yaw 0
yaw = -0.00°

Continuity yaw 10
yaw = 10.28°

Continuity yaw 20
yaw = 19.96°

Continuity yaw 30
yaw = 29.89°

Continuity yaw 40
yaw = 40.11°

Continuity yaw 50
yaw = 49.85°
```

Observed final status:

```text
Pose-continuity test: passed
```

Status:

**PASS**

---

## 4.11 Existing Temporal Regression Test

Purpose:

Verify that Milestone 5 integration did not break Milestone 4B temporal reasoning.

Validated existing cases:

- NORMAL
- BLINK_CANDIDATE
- blink display hold
- blink display expiration
- PROLONGED_EYE_CLOSURE
- SUSTAINED_MOUTH_OPENING
- PROLONGED_FACE_LOSS
- invalid timestamp rejection

Observed:

```text
[PASS] All temporal-rule smoke tests passed.
```

Status:

**PASS**

---

# 5. Webcam Validation

Live webcam validation was performed through the shared source-independent pipeline.

Execution mode:

```bash
PYTHONPATH=src python src/main.py --source webcam
```

Mirrored webcam visualization was also tested during development.

The non-mirrored mode was specifically used to investigate whether horizontal mirroring caused the strong-yaw pose instability.

The issue remained without mirroring, so mirroring was not identified as the root cause.

---

## 5.1 Near-Neutral Pose

Observed representative result:

```text
Yaw   ≈ -6.9°
Pitch ≈ -3.4°
Roll  ≈ -0.5°
```

Assessment:

The pose is reasonably close to neutral for a generic uncalibrated face model and approximate camera intrinsics.

Status:

**PASS**

---

## 5.2 Strong Positive Yaw

Observed representative result:

```text
Yaw   ≈ +51.4°
Pitch ≈ -11.5°
Roll  ≈ -6.9°
```

Assessment:

Yaw dominates as expected.

Some pitch/roll cross-axis coupling remains, but the result is physically plausible for the prototype.

Status:

**PASS**

---

## 5.3 Strong Negative Yaw

Observed representative result:

```text
Yaw   ≈ -48.4°
Pitch ≈ -11.4°
Roll  ≈ -3.4°
```

Assessment:

Yaw dominates and the previous pathological ±180° roll flip is absent.

Status:

**PASS**

---

## 5.4 Pitch-Dominant Motion

Observed representative result:

```text
Yaw   ≈ -1.4°
Pitch ≈ -32.4°
Roll  ≈ -4.5°
```

Assessment:

Pitch dominates as expected.

Status:

**PASS**

---

## 5.5 Roll-Dominant Head Tilt

Observed representative result:

```text
Yaw   ≈ -7.4°
Pitch ≈ -10.9°
Roll  ≈ -42.4°
```

Assessment:

Roll dominates and corresponds qualitatively to the visible head tilt.

Status:

**PASS**

---

# 6. Strong-Yaw Failure Investigation

Initial webcam validation exposed a significant failure mode.

Representative early outputs included:

```text
Yaw   ≈ -40° to -43°
Roll  ≈ +158° to ±180°
```

The actual head was primarily turned sideways and was not physically rolled by approximately 180°.

This indicated an alternative pose-solution branch rather than genuine motion.

---

## 6.1 Mirroring Investigation

The webcam was rerun without:

```text
--mirror
```

The extreme-roll failure still occurred.

Conclusion:

```text
horizontal mirroring was not the root cause
```

---

## 6.2 Stabilization Changes

The following changes were introduced:

- previous valid rotation vector storage
- previous valid translation vector storage
- `solvePnP(..., useExtrinsicGuess=True)` after the first valid pose
- previous accepted `HeadPoseResult`
- angular wraparound handling
- frame-to-frame angular continuity guard

After these changes, the same type of strong-yaw movement produced yaw-dominant results without the previous ±180° roll artifact during the validated sequences.

Status:

**PASS after refinement**

---

# 7. Face-Loss Recovery Validation

Purpose:

Verify correct behavior when face tracking is temporarily or persistently unavailable.

Procedure:

1. obtain a stable head pose
2. move the face out of the frame / hide the face
3. maintain face loss for more than the prolonged face-loss threshold
4. return to the frame

Expected behavior:

```text
short face loss
→ head-pose history preserved

prolonged face loss
→ HeadPoseEstimator.reset()

face returns
→ fresh PnP initialization
```

Observed behavior:

- head pose became unavailable while the face was absent
- prolonged face loss triggered estimator reset
- after re-entry, the estimator recovered from a fresh pose
- stale previous orientation was not carried indefinitely

Status:

**PASS**

---

# 8. Recorded-Video Validation

Recorded-video validation was performed through the existing `FileVideoSource`.

Private local sample:

```text
DMD-derived/local validation video
```

The raw dataset material remains private.

No separate head-pose implementation was created for recorded video.

The same pipeline used for webcam input was used for the recorded file.

Conceptually:

```text
FileVideoSource
      ↓
FramePacket
      ↓
FaceMeshDetector
      ↓
selected landmarks
      ↓
HeadPoseEstimator
      ↓
yaw / pitch / roll
```

---

## 8.1 Recorded-Video Observations

Observed representative behavior included:

- valid facial landmark tracking
- valid yaw/pitch/roll output
- strong side head orientation producing substantial yaw
- near-frontal sections producing smaller pose angles
- simultaneous operation of Milestone 4B temporal reasoning
- no dataset-specific pose-estimation code path

Representative sampled observations included approximately:

```text
side-oriented pose:
Yaw ≈ +46°
Pitch ≈ -5°
Roll ≈ -8°
```

and:

```text
moderate side pose:
Yaw ≈ +32°
```

Near-frontal/less rotated sections produced substantially smaller pose values.

No sampled validation frame showed the previous pathological roll value near ±180° after the final stabilization changes.

Status:

**PASS**

---

# 9. Source-Independent Validation

A key validation requirement is that head-pose estimation remains independent of the acquisition source.

Validated sources:

```text
WebcamVideoSource
FileVideoSource
```

No conditional logic of the form:

```text
if webcam:
    use head pose implementation A
else:
    use head pose implementation B
```

was introduced.

The same `HeadPoseEstimator` operates on selected landmarks produced from both input modes.

Status:

**PASS**

---

# 10. Visualization Validation

The initial Milestone 5 overlay became crowded because the new head-pose information was added below the existing temporal diagnostics.

Observed issue:

- head-pose values were positioned too low
- some text was difficult to read
- milestone text and pose values competed for vertical space

The visualization was subsequently reorganized.

Final layout:

```text
Left side:
- FPS
- face status
- landmark count
- EAR
- MAR
- source information
- temporal state
- temporal durations

Right side:
- HEAD POSE
- yaw
- pitch
- roll
```

A semi-transparent dark panel and outlined text were added for readability.

The OpenCV display was made resizable and initially opened at approximately:

```text
1280 × 720
```

Status:

**PASS**

---

# 11. Performance Summary

Milestone 5 was evaluated as a real-time fast-prototype component rather than through a formal benchmark.

Observed characteristics:

- head-pose estimation executes within the existing real-time webcam pipeline
- EAR/MAR processing remains active
- temporal-rule processing remains active
- visualization remains interactive
- recorded-video processing remains functional

No formal latency benchmark was completed in this milestone.

No claim is made regarding:

- worst-case processing latency
- deterministic real-time guarantees
- production ECU timing
- embedded target performance

A dedicated benchmark stage remains planned for later milestones.

---

# 12. Evidence

Validation evidence includes:

- deterministic smoke-test console output
- webcam screenshots from neutral, yaw, pitch, and roll validation
- recorded private DMD/local sample output
- manual face-loss recovery test
- regression-test output

Important privacy and redistribution rule:

```text
Raw DMD media and DMD-derived validation media remain local/private unless public redistribution rights are explicitly confirmed.
```

Therefore, private dataset images or videos should not be committed to the public repository.

Public evidence, if added later, should use:

- author-owned webcam recordings
- privacy-reviewed screenshots
- redistribution-safe media

---

# 13. Known Issues and Limitations

The following limitations remain.

## 13.1 Approximate Camera Intrinsics

The current implementation does not use a physically calibrated camera.

Impact:

- angle accuracy can vary across camera models and resolutions

---

## 13.2 Generic 3D Face Model

The face model is not personalized.

Impact:

- absolute angle accuracy may vary across drivers

---

## 13.3 Zero Distortion Assumption

Lens distortion is currently assumed to be zero.

Impact:

- geometric error may increase toward image boundaries or with wide-angle optics

---

## 13.4 Cross-Axis Coupling

Strong motion on one axis can produce smaller changes on other axes.

Examples:

```text
strong yaw may also influence pitch/roll
```

This is expected in the current generic geometric baseline.

---

## 13.5 Extreme Pose / Occlusion

At large head rotations:

- landmarks become less visible
- landmark geometry becomes less reliable
- the PnP problem can become more ambiguous

Pose initialization and continuity checks reduce this problem but do not mathematically eliminate it.

---

## 13.6 Continuity Threshold

Current:

```text
75°
```

This threshold is not calibrated from driver-motion datasets.

It is used as a prototype estimator guard.

---

## 13.7 No Reprojection-Error Quality Metric

The current estimator does not expose:

```text
reprojection error
```

as a confidence or quality indicator.

This is a recommended future improvement.

---

## 13.8 No Pose Confidence

The current `HeadPoseResult` does not contain an explicit confidence value.

---

## 13.9 No Quantitative Ground Truth

The current webcam and DMD validation is qualitative.

The synthetic tests validate internal geometry but do not represent independent real-world ground truth.

A quantitative benchmark against labeled head-pose data remains future work.

---

## 13.10 Sign Convention Not Yet Standardized for Behavior

Yaw, pitch, and roll signs are numerically consistent within the current geometry, but final semantic labels such as:

```text
LEFT
RIGHT
UP
DOWN
```

are intentionally deferred until source mirroring and coordinate conventions are standardized.

---

# 14. Engineering Assessment

Milestone 5 meets its fast-prototype objective.

The final implementation demonstrates:

- modular geometric head-pose estimation
- clear separation from behavioral classification
- synthetic deterministic verification
- real webcam operation
- recorded-video operation
- pose continuity stabilization
- recovery after prolonged face loss
- compatibility with existing temporal reasoning

The most important engineering finding was that a basic `solvePnP` implementation could appear correct at neutral poses while failing under strong yaw.

The milestone therefore required iterative validation and stabilization rather than accepting the first numerically successful solution.

This substantially improves the technical credibility of the implementation.

---

# 15. Recommendations

Recommended future improvements:

1. calibrate the camera intrinsics and lens distortion
2. compute reprojection error per pose
3. expose a pose confidence / validity score
4. evaluate additional facial point configurations
5. compare generic and personalized 3D models
6. compare classical `solvePnP` with learning-based head-pose models
7. evaluate temporal filtering such as a One Euro Filter or Kalman filter
8. benchmark against a labeled head-pose dataset
9. standardize the source-coordinate and mirroring convention
10. evaluate quaternion-based internal orientation representation
11. log pose values with source timestamps for later analysis
12. preserve geometric outputs separately from higher-level distraction states

---

# 16. Next Validation

The next milestone is:

```text
Path 1 — Milestone 6: Gaze Estimation
```

The next validation should determine whether eye/gaze-direction estimates behave consistently under:

- neutral head pose
- non-neutral head pose
- left/right eye movement
- vertical eye movement
- partial occlusion
- different lighting
- recorded-video input

Head pose should be used as contextual geometric information for gaze interpretation rather than replaced by gaze estimation.

---

# Validation Completion Checklist

## Deterministic Validation

- [x] Camera matrix validated
- [x] Missing landmarks validated
- [x] Synthetic neutral pose validated
- [x] Synthetic positive yaw validated
- [x] Synthetic negative yaw validated
- [x] Synthetic pitch validated
- [x] Synthetic roll validated
- [x] Angular wraparound validated
- [x] Reset behavior validated
- [x] Gradual yaw continuity validated
- [x] Head-pose smoke-test suite passed

## Regression Validation

- [x] Milestone 4B temporal smoke-test suite rerun
- [x] Existing temporal-rule tests passed

## Webcam Validation

- [x] Neutral pose tested
- [x] Positive yaw tested
- [x] Negative yaw tested
- [x] Strong yaw tested
- [x] Pitch tested
- [x] Roll tested
- [x] Mirroring investigated
- [x] Strong-yaw pose flip investigated
- [x] Strong-yaw stabilization validated
- [x] Face-loss recovery validated

## Recorded-Video Validation

- [x] `FileVideoSource` path tested
- [x] Head-pose output confirmed
- [x] Existing temporal reasoning confirmed simultaneously
- [x] No separate recorded-video pose code path required
- [x] Private DMD media retained outside public repository

## Visualization

- [x] Head-pose panel added
- [x] Text overlap corrected
- [x] Readability improved
- [x] Resizable display validated

## Remaining Repository Closure

- [x] Validation documentation prepared
- [x] README updated
- [x] Final `compileall` executed after documentation changes
- [x] Final smoke tests rerun before commit
- [x] Git status reviewed
- [x] Git diff reviewed
- [x] Milestone 5 committed
- [x] Feature branch pushed
- [x] Pull request created
- [x] Pull request merged
- [x] Local `main` synchronized
- [x] Milestone 5 officially closed
