# Path 1 _ Milestone 6: Gaze Estimation

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 _ Fast Prototype |
| Milestone | 6 |
| Status | Implemented and Validated |
| Date | 2026-09-10 |
| Author | Bassem Soliman |
| Repository | safety-critical-in-cabin-driver-monitoring |
| Branch | feat/gaze-estimation |
| Python | 3.11.7 |
| MediaPipe | 0.10.35 |

---

# 1. Objective

The objective of this milestone is to extend the in-cabin perception pipeline with an interpretable geometric gaze-estimation baseline.

The milestone estimates iris position relative to the visible eye geometry and produces:

- normalized horizontal iris position for each eye
- normalized vertical iris position for each eye
- bilateral combined horizontal gaze geometry
- bilateral combined vertical gaze geometry
- horizontal inter-eye disagreement
- vertical inter-eye disagreement
- an inter-eye consistency flag
- prototype geometric gaze-direction labels

The implemented prototype direction labels are:

- `CENTER`
- `LEFT`
- `RIGHT`
- `UP`
- `DOWN`
- `LEFT_UP`
- `LEFT_DOWN`
- `RIGHT_UP`
- `RIGHT_DOWN`
- `UNKNOWN`

These outputs are geometric perception features. They do not directly represent driver distraction, driver inattention, cognitive state, drowsiness, road-scene awareness, or safety-critical intervention decisions.

Behavioral and temporal interpretation remains intentionally separated from the gaze perception layer.

---

# 2. Motivation

Previous milestones established face landmark detection, facial geometry features, temporal face-level reasoning, source-independent acquisition, and head pose estimation.

However, head orientation alone does not fully represent visual attention. A driver can maintain approximately the same head orientation while moving the eyes toward another region of the cabin or road environment.

Therefore, gaze geometry provides a complementary perception signal to head pose.

For the Fast Prototype path, the goal is not yet to implement a calibrated 3D gaze vector or production Driver Monitoring System. Instead, this milestone introduces a lightweight, interpretable, real-time baseline that can later support head-pose and gaze fusion, gaze-away temporal analysis, region-of-interest reasoning, distraction candidate detection, driver-specific calibration, and comparison with more advanced gaze-estimation approaches.

The staged design preserves the distinction between measurable perception features and later safety interpretation.

---

# 3. Software Perspective

Milestone 6 extends the modular perception architecture without modifying the existing temporal decision logic.

New module:

```text
src/perception/gaze.py
```

New deterministic validation module:

```text
src/experiments/gaze_smoke_test.py
```

Updated modules:

```text
src/perception/face_features.py
src/perception/visualization.py
src/main.py
```

The responsibilities remain separated. `FaceMeshDetector` is responsible for facial and iris landmark detection. `FacialGeometryExtractor` remains responsible for EAR and MAR. `HeadPoseEstimator` remains responsible for head orientation. `GazeEstimator` is responsible for iris-based gaze geometry. `TemporalRuleEngine` continues to operate on face visibility, EAR, and MAR and is not yet driven by gaze direction. `main.py` orchestrates the perception modules.

This separation prevents the gaze estimation prototype from being tightly coupled to behavioral classification.

---

# 4. Computer Vision Perspective

## 4.1 Iris Landmark Extension

MediaPipe Face Mesh is configured with:

```python
refine_landmarks=True
```

This configuration provides refined eye landmarks and iris landmarks.

Milestone 6 extends the selected landmark set with:

```text
left_iris_center  = landmark 468
right_iris_center = landmark 473
```

The existing selected landmarks are preserved.

For each eye, the estimator uses the outer eye corner, inner eye corner, upper eyelid point, lower eyelid point, and iris center.

## 4.2 Horizontal Iris Geometry

For one eye, the horizontal eye axis is defined as:

\[
\mathbf{a}_H = \mathbf{p}_{inner} - \mathbf{p}_{outer}
\]

The iris-center displacement from the outer corner is:

\[
\mathbf{d}_H = \mathbf{p}_{iris} - \mathbf{p}_{outer}
\]

The normalized horizontal iris position is calculated using vector projection:

\[
H_{raw} = \frac{\mathbf{d}_H \cdot \mathbf{a}_H}{\mathbf{a}_H \cdot \mathbf{a}_H}
\]

Approximate geometric interpretation is `H = 0` at the start of the eye axis, `H = 0.5` near its midpoint, and `H = 1` near the other end.

The values are intentionally not clamped. Values outside the nominal range can remain visible during validation and may indicate landmark noise, unusual geometry, occlusion, or extreme head orientation.

## 4.3 Bilateral Horizontal Canonicalization

The left and right eye corner axes have opposite image-space orientations. Without correction, equivalent physical gaze directions produce opposite numerical trends between the two eyes.

The left eye uses its normalized horizontal value directly:

\[
H_L = H_{L,raw}
\]

The right eye is canonicalized:

\[
H_R = 1 - H_{R,raw}
\]

This makes the bilateral horizontal measurements follow the same numerical convention.

The combined horizontal feature is:

\[
H = \frac{H_L + H_R}{2}
\]

Initial webcam validation demonstrated the importance of this correction. Before canonicalization, approximately equivalent eye positions could produce values such as:

```text
Left H  ≈ 0.315
Right H ≈ 0.690
```

while their simple average misleadingly appeared close to center. After canonicalization, both eye measurements follow the same direction convention and can be meaningfully fused.

## 4.4 Vertical Iris Geometry

The vertical eye axis is defined as:

\[
\mathbf{a}_V = \mathbf{p}_{lower} - \mathbf{p}_{upper}
\]

The iris displacement is:

\[
\mathbf{d}_V = \mathbf{p}_{iris} - \mathbf{p}_{upper}
\]

The normalized vertical iris position is:

\[
V = \frac{\mathbf{d}_V \cdot \mathbf{a}_V}{\mathbf{a}_V \cdot \mathbf{a}_V}
\]

The combined bilateral vertical feature is:

\[
V_{combined} = \frac{V_L + V_R}{2}
\]

The values remain image-space geometric features rather than gaze angles.

## 4.5 Inter-Eye Disagreement

Bilateral fusion alone can hide disagreement between the two eyes. One eye may be partially occluded or affected by stronger perspective distortion.

Horizontal disagreement:

\[
dH = |H_L - H_R|
\]

Vertical disagreement:

\[
dV = |V_L - V_R|
\]

These values measure inter-eye agreement. They do not directly measure absolute gaze accuracy.

## 4.6 Gaze Consistency

Prototype consistency thresholds are currently:

```text
maximum horizontal disagreement = 0.15
maximum vertical disagreement   = 0.20
```

The gaze geometry is considered consistent when:

\[
dH \leq 0.15
\]

and:

\[
dV \leq 0.20
\]

The resulting flag is displayed as `GOOD` or `LOW`.

This is intentionally described as a consistency or quality indicator rather than a confidence score. Low disagreement means that both eyes produce similar normalized measurements. It does not prove that the absolute gaze estimate is correct.

For example, strong head yaw can introduce similar geometric bias into both eyes, resulting in good inter-eye agreement despite reduced absolute gaze reliability.

---

# 5. Prototype Geometric Gaze Direction

Controlled webcam validation established the coordinate convention used by the current non-mirrored pipeline:

```text
Higher H → LEFT
Lower H  → RIGHT

Lower V  → UP
Higher V → DOWN
```

Initial empirical prototype thresholds are:

```text
H < 0.40  → RIGHT
H > 0.56  → LEFT
otherwise → horizontal CENTER

V < 0.41  → UP
V > 0.50  → DOWN
otherwise → vertical CENTER
```

Horizontal and vertical states are combined when appropriate, including `LEFT_UP`, `LEFT_DOWN`, `RIGHT_UP`, and `RIGHT_DOWN`.

If bilateral gaze consistency is insufficient, the geometric direction is reported as `UNKNOWN`.

The thresholds are empirical prototype parameters. They are not universal gaze thresholds, calibrated gaze angles, driver-independent safety thresholds, or production Driver Monitoring System specifications.

---

# 6. Python Perspective

Milestone 6 introduces typed data structures for gaze perception:

```text
EyeGazeResult
GazeResult
GazeDirection
GazeEstimator
```

`EyeGazeResult` contains:

```text
horizontal_ratio
vertical_ratio
```

`GazeResult` contains:

```text
left_eye
right_eye
horizontal_ratio
vertical_ratio
horizontal_disagreement
vertical_disagreement
is_consistent
direction
```

`GazeDirection` is represented using an enumeration. This prevents arbitrary string values from propagating through the system and gives the gaze-direction interface a defined state space.

NumPy is used for vector representation, Euclidean vector magnitude, dot products, and normalized vector projection.

The implementation also performs geometry validity checks before calculating normalized values. Degenerate eye geometry returns no gaze result rather than forcing an unreliable measurement.

---

# 7. Engineering Perspective

The principal engineering decision in Milestone 6 is to preserve several abstraction levels:

```text
iris landmarks
↓
normalized eye geometry
↓
bilateral fusion
↓
inter-eye consistency
↓
prototype geometric direction
↓
future temporal / behavioral interpretation
```

The following shortcut is intentionally avoided:

```text
gaze LEFT
↓
driver DISTRACTED
```

Such a mapping would be scientifically unjustified at the current development stage. A driver may intentionally look left for legitimate reasons such as mirror checking, intersection scanning, environmental awareness, or instrument interaction.

A future behavioral decision requires additional information such as duration, head orientation, road/cabin regions of interest, vehicle context, repeated gaze behavior, driver baseline, and uncertainty or validity conditions.

Therefore, the current milestone terminates at geometric gaze-direction estimation.

---

# 8. Project Architecture Impact

Before Milestone 6:

```text
VideoSource
    ↓
FramePacket
    ↓
FaceMeshDetector
    ↓
Selected Facial Landmarks
    ├── FacialGeometryExtractor
    │       ↓
    │     EAR / MAR
    │
    └── HeadPoseEstimator
            ↓
       Yaw / Pitch / Roll

EAR / MAR / Face Visibility
    ↓
TemporalRuleEngine
```

After Milestone 6:

```text
VideoSource
    ↓
FramePacket
    ↓
FaceMeshDetector
    ↓
Selected Facial + Iris Landmarks
    │
    ├── FacialGeometryExtractor
    │       ↓
    │     EAR / MAR
    │
    ├── HeadPoseEstimator
    │       ↓
    │     Yaw / Pitch / Roll
    │
    └── GazeEstimator
            ↓
        Left H/V
        Right H/V
        Combined H/V
        dH / dV
        Consistency
        Geometric Direction

EAR / MAR / Face Visibility
    ↓
TemporalRuleEngine
```

The temporal engine remains independent from the gaze direction output in this milestone.

---

# 9. System Interfaces

## 9.1 Inputs

`GazeEstimator` receives a dictionary of selected pixel-space landmarks.

Required landmarks:

```text
left_eye_outer
left_eye_inner
left_eye_upper
left_eye_lower
left_iris_center

right_eye_outer
right_eye_inner
right_eye_upper
right_eye_lower
right_iris_center
```

## 9.2 Outputs

The estimator produces:

```text
left_eye.horizontal_ratio
left_eye.vertical_ratio
right_eye.horizontal_ratio
right_eye.vertical_ratio
horizontal_ratio
vertical_ratio
horizontal_disagreement
vertical_disagreement
is_consistent
direction
```

## 9.3 Dependencies

Main dependencies:

```text
Python
NumPy
OpenCV
MediaPipe Face Mesh
```

## 9.4 Consumers

Gaze results are currently consumed by:

```text
src/main.py
src/perception/visualization.py
```

The temporal decision layer does not currently consume gaze results.

---

# 10. Visualization and Dashboard

Milestone 6 reorganizes runtime visualization. Previous overlays placed increasing amounts of text directly over the camera image, reducing visual clarity as additional perception modules were introduced.

The new visualization separates:

```text
video image | white perception dashboard
```

The original video aspect ratio is preserved. The driver image remains primarily dedicated to the visual scene and landmark visualization, while runtime data is displayed in an organized external dashboard.

Dashboard sections include:

```text
Runtime
Face Geometry
Source Metadata
Temporal State
Head Pose
Gaze Geometry
```

The gaze section displays:

```text
Direction
Combined H
Combined V
Left eye H/V
Right eye H/V
dH / dV
Consistency
```

The milestone title remains associated with the image rather than being mixed into perception measurements.

This layout improves readability, debugging, screenshot documentation, modular extensibility, and separation between image evidence and numerical state.

---

# 11. Validation Summary

Milestone 6 was validated using:

1. deterministic synthetic gaze geometry tests
2. live RGB webcam testing
3. controlled gaze-direction testing
4. source-independent recorded-video testing using a private DMD sample
5. integration with the existing facial geometry, temporal, and head-pose pipeline

Controlled webcam validation confirmed the current geometric sign convention:

```text
Higher H → LEFT
Lower H  → RIGHT
Lower V  → UP
Higher V → DOWN
```

A representative LEFT-gaze observation produced:

```text
Combined H ≈ 0.678
Combined V ≈ 0.471
Consistency = GOOD
```

with approximately neutral head orientation.

A representative UP-gaze observation produced approximately:

```text
Combined H ≈ 0.501
Combined V ≈ 0.399
dH ≈ 0.022
dV ≈ 0.069
Consistency = GOOD
```

Recorded-video validation using the private DMD sample confirmed that the same gaze pipeline operates through the source-independent `FileVideoSource` architecture.

Detailed validation is documented in:

```text
docs/validation/path_01_milestone_06_gaze_estimation_validation.md
```

---

# 12. Limitations

## 12.1 No calibrated 3D gaze vector

The current method measures 2D iris position relative to 2D eye geometry. It does not estimate a calibrated 3D optical or visual gaze vector.

## 12.2 No camera calibration

Camera intrinsic and extrinsic parameters are not used for gaze estimation. Therefore, H/V values should not be interpreted as gaze angles.

## 12.3 Prototype thresholds

Current direction thresholds were selected from initial controlled development observations. They require substantially broader validation before being treated as robust thresholds.

## 12.4 No driver-specific calibration

Neutral iris position varies between drivers, eye anatomy, camera position, seating position, and head orientation. A fixed neutral region cannot be assumed to be optimal for every driver.

## 12.5 Sensitivity to head pose

The current eye geometry is based on 2D image-space projection. Strong yaw, pitch, or roll can distort the apparent eye geometry. Inter-eye consistency can detect some difficult poses but cannot guarantee absolute gaze correctness.

A case with large head yaw may still produce `GOOD` consistency if both eyes are biased similarly.

## 12.6 Eye closure and eyelid geometry

The gaze estimator currently does not explicitly reject gaze measurements based on eye openness. When the eyes are nearly closed, iris localization may become less reliable, eyelid geometry becomes compressed, and normalized vertical measurements can become unstable.

Future work should introduce an eye-openness validity gate or another quality criterion.

## 12.7 Partial occlusion

Glasses, eyelashes, face orientation, hands, reflections, and cabin illumination may affect iris and eyelid localization.

## 12.8 Webcam mirroring

Direction semantics depend on the coordinate system used by the runtime pipeline. The current sign convention was validated for the current non-mirrored geometric coordinate convention. Mirroring must therefore be handled deliberately when interpreting semantic LEFT and RIGHT labels.

## 12.9 Inter-eye consistency is not confidence

`dH`, `dV`, and `is_consistent` indicate bilateral agreement only. They are not statistically calibrated confidence estimates.

## 12.10 No temporal gaze interpretation

Direction is currently frame-level. There is no temporal filtering or duration reasoning for gaze direction. Therefore, a short glance and a sustained gaze-away event are not distinguished.

## 12.11 No behavioral classification

The milestone does not classify `DISTRACTED`, `INATTENTIVE`, `DROWSY`, or `UNRESPONSIVE` from gaze measurements. These require later multimodal and temporal reasoning.

## 12.12 Head-pose upstream limitations remain

The existing head-pose baseline may occasionally exhibit large roll-angle ambiguity near approximately ±180 degrees under certain observations. This is an upstream head-pose issue and should not be interpreted as a gaze-estimation failure.

---

# 13. Future Scalability

The current architecture supports several future extensions:

- eye-openness gating
- temporal smoothing of gaze H/V
- temporal gaze-direction states
- driver-specific neutral calibration
- camera-specific calibration
- head-pose-aware gaze compensation
- 3D gaze estimation
- gaze region-of-interest mapping
- steering wheel / mirror / dashboard / road-region reasoning
- uncertainty estimation
- model-based gaze estimation
- comparison against dedicated gaze-estimation networks
- dataset-level quantitative evaluation
- multimodal fusion with head pose and posture

The `GazeEstimator` interface can also be replaced or extended later without redesigning acquisition or the complete application loop.

---

# 14. Research / Technology Notes

The implemented method is an interpretable geometric gaze baseline.

Its main advantages are lightweight computation, real-time suitability, transparent mathematics, easy debugging, no dedicated gaze neural network requirement, and straightforward integration with MediaPipe iris landmarks.

Its limitations are also transparent. The method relies on 2D image geometry and therefore cannot provide the accuracy or invariance expected from a calibrated model-based or learning-based gaze-estimation system.

For a safety-critical Driver Monitoring System, gaze estimation should eventually be evaluated with multiple drivers, different eye anatomies, glasses, varying illumination, multiple camera positions, head-pose variation, realistic cabin movement, labeled gaze targets, recorded datasets, and quantitative error metrics.

Milestone 6 should therefore be treated as a baseline for engineering experimentation rather than a production-ready gaze estimator.

---

# 15. Lessons Learned

Milestone 6 demonstrated several important engineering points.

First, bilateral eye measurements cannot be averaged safely without establishing a common coordinate convention. The right-eye horizontal canonicalization was necessary before meaningful bilateral fusion.

Second, a fused average alone can hide disagreement. Explicit `dH` and `dV` measurements improve observability of the perception pipeline.

Third, agreement and accuracy are different concepts. Two eyes can agree numerically while both measurements are affected by the same perspective distortion.

Fourth, semantic labels such as LEFT and RIGHT require empirical verification of the coordinate convention rather than assumptions based only on landmark indices.

Finally, gaze geometry should remain separated from behavioral interpretation until sufficient temporal, contextual, and validation evidence exists.

---

# 16. Next Milestone

The next development stage should build on the perception signals now available:

```text
EAR / MAR
Temporal face-level states
Head Pose
Gaze Geometry
Gaze Direction
```

The next milestone should continue toward broader driver-state perception while preserving the staged architecture.

Potential next topics include pose/body posture, hand activity, gaze and head-pose temporal fusion, and distraction candidate reasoning. The exact next implementation should follow the established Path 1 roadmap.

---

# Milestone Completion Checklist

- [x] Iris landmarks integrated
- [x] Per-eye H/V gaze geometry implemented
- [x] Bilateral horizontal canonicalization implemented
- [x] Combined H/V implemented
- [x] Inter-eye disagreement implemented
- [x] Consistency quality gate implemented
- [x] Prototype gaze-direction labels implemented
- [x] Webcam validation completed
- [x] Recorded DMD sample validation completed
- [x] Source-independent integration verified
- [x] Dashboard integration completed
- [x] Implementation documentation completed
- [x] Validation documentation completed
- [x] Final regression tests rerun after documentation
- [x] Git commit completed
- [x] GitHub pull request merged
