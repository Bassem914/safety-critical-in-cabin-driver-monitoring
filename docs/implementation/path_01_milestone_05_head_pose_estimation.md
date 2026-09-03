# Path 1 — Milestone 5: Head Pose Estimation

---

# Metadata

| Item | Value |
|------|-------|
| Project | Safety-Critical In-Cabin Driver Monitoring |
| Path | Path 1 — Fast Prototype |
| Milestone | 5 |
| Title | Head Pose Estimation |
| Status | Completed |
| Date | 2026-09-03 |
| Author | Bassem Soliman |
| Repository | `safety-critical-in-cabin-driver-monitoring` |
| Main Output | Geometric yaw, pitch, and roll estimation |
| Primary Method | OpenCV Perspective-n-Point (`solvePnP`) |
| Facial Input | MediaPipe Face Mesh selected landmarks |
| Validation | Deterministic smoke tests, live webcam, recorded-video sample |
| Dataset Handling | Private dataset media retained outside public repository |

---

# 1. Objective

The objective of Milestone 5 is to extend the existing in-cabin facial perception pipeline with geometric head-pose estimation.

Previous milestones established:

- live webcam acquisition
- recorded-video acquisition
- source-independent `VideoSource` abstraction
- MediaPipe Face Mesh landmark extraction
- Eye Aspect Ratio (EAR)
- Mouth Aspect Ratio (MAR)
- timestamp-based temporal reasoning
- blink candidate detection
- prolonged eye-closure detection
- sustained mouth-opening detection
- prolonged face-loss detection

Milestone 5 adds geometric head-orientation measurements while preserving the existing modular architecture.

The implemented outputs are:

- yaw
- pitch
- roll

The milestone also introduces:

- 2D–3D facial point correspondence
- approximate camera intrinsics
- OpenCV `solvePnP`
- coordinate-system normalization
- rotation-matrix-to-Euler conversion
- previous-pose initialization
- frame-to-frame pose-continuity validation
- estimator reset after prolonged face loss
- source-independent webcam and recorded-video integration
- dedicated head-pose visualization

The outputs remain geometric perception measurements.

This milestone does not yet classify the driver as:

- distracted
- inattentive
- looking away
- drowsy
- unresponsive

Higher-level behavioral interpretation is intentionally deferred to later milestones.

---

# 2. Motivation

EAR and MAR provide useful information about local facial geometry, but they do not describe the spatial orientation of the driver's head.

For example:

```text
EAR = 0.29
MAR = 0.31
```

may indicate that the eyes and mouth are in a normal geometric state, but this does not indicate whether the driver is:

- facing forward
- looking toward the side
- looking upward
- looking downward
- tilting the head

Head orientation is therefore an important geometric feature for later Driver Monitoring System functions such as:

- gaze estimation
- head-away analysis
- driver-attention modeling
- distraction reasoning
- visual-attention estimation
- multimodal driver-state estimation
- explainable driver-behavior analysis

Milestone 5 introduces this missing geometric layer while maintaining the project principle:

```text
measurement
≠
behavioral interpretation
```

For example:

```text
Yaw = 45°
```

is treated as a geometric measurement.

It is not directly interpreted as:

```text
DISTRACTED
```

because distraction depends on additional context such as:

- duration
- gaze direction
- driving context
- head/gaze combination
- body posture
- hand activity
- temporal behavior

---

# 3. Software Perspective

Milestone 5 introduces a dedicated head-pose module:

```text
paths/01_fast_prototype/src/perception/head_pose.py
```

The main affected files are:

```text
src/perception/head_pose.py
src/perception/visualization.py
src/experiments/head_pose_smoke_test.py
src/main.py
```

The existing facial landmark implementation remains in:

```text
src/perception/face_features.py
```

The existing temporal decision implementation remains in:

```text
src/decision/temporal_rules.py
```

This preserves separation of responsibilities.

Current responsibility boundaries:

```text
acquisition/
    frame acquisition
    timestamps
    source metadata

perception/face_features.py
    Face Mesh landmarks
    EAR
    MAR

perception/head_pose.py
    3D geometric head orientation
    yaw
    pitch
    roll

decision/temporal_rules.py
    temporal face-level event candidates

perception/visualization.py
    visualization only

main.py
    pipeline orchestration
```

This design prevents `main.py` from becoming responsible for geometric algorithms and prevents the head-pose module from performing behavioral classification.

---

# 4. Computer Vision Perspective

Milestone 5 implements a classical geometric head-pose baseline.

The problem is formulated as a Perspective-n-Point problem.

The system has:

1. approximate 3D facial reference coordinates
2. corresponding 2D facial landmarks detected in the image
3. an approximate camera intrinsic model

OpenCV then estimates the rigid transformation between the 3D face model and the camera observation.

Conceptually:

```text
Approximate 3D facial model
              +
Detected 2D facial landmarks
              +
Camera intrinsic matrix
              ↓
          solvePnP
              ↓
        rotation vector
       translation vector
              ↓
          Rodrigues
              ↓
        rotation matrix
              ↓
coordinate-system normalization
              ↓
       yaw / pitch / roll
```

This approach is lightweight and interpretable.

It does not require a separate trained neural network for head-pose estimation.

---

# 5. Python Perspective

The implementation uses several important Python concepts.

## 5.1 Dataclass

Head-pose results are represented using:

```python
@dataclass(frozen=True)
class HeadPoseResult:
```

The result object stores:

- yaw
- pitch
- roll
- rotation vector
- translation vector

Using a dataclass makes the output structured and self-documenting.

Instead of returning an unordered tuple such as:

```text
yaw, pitch, roll, rvec, tvec
```

the caller accesses:

```text
result.yaw_degrees
result.pitch_degrees
result.roll_degrees
result.rotation_vector
result.translation_vector
```

---

## 5.2 Frozen Result Object

`HeadPoseResult` is frozen.

This means the returned result is treated as immutable after creation.

This reduces accidental mutation and makes the output suitable for:

- logging
- validation
- downstream processing
- reproducible debugging

---

## 5.3 Optional Return Type

The estimator returns:

```python
Optional[HeadPoseResult]
```

A valid `HeadPoseResult` means pose estimation succeeded.

`None` means a valid pose is not currently available.

Possible reasons include:

- missing required landmarks
- no detected face
- unavailable image geometry

This is preferable to returning fake values such as:

```text
yaw = 0
pitch = 0
roll = 0
```

when no actual measurement exists.

---

## 5.4 NumPy

NumPy is used for:

- 3D reference points
- 2D image-point arrays
- camera matrices
- rotation matrices
- translation vectors
- trigonometric angle conversion

---

## 5.5 Stateful Class Design

Unlike a purely frame-independent pose function, the final `HeadPoseEstimator` stores previous valid pose information.

This makes the estimator stateful.

It retains:

```text
previous rotation vector
previous translation vector
previous accepted HeadPoseResult
```

This state is used to improve temporal continuity.

---

# 6. Engineering Perspective

Several engineering decisions were important during this milestone.

## 6.1 Geometric Output Before Behavior

Head pose is exposed as:

```text
yaw
pitch
roll
```

rather than immediately producing:

```text
LOOKING_LEFT
LOOKING_RIGHT
DISTRACTED
```

This preserves a clean hierarchy:

```text
sensor observation
        ↓
geometric perception
        ↓
temporal feature
        ↓
behavioral interpretation
```

---

## 6.2 Reuse Existing Landmarks

The implementation reuses facial landmarks already produced by the Face Mesh pipeline.

No duplicate detector was introduced.

This reduces:

- processing cost
- code duplication
- architecture complexity

---

## 6.3 Source Independence

The estimator does not know whether the frame came from:

- a webcam
- a recorded local video
- a dataset sample

It receives only:

```text
selected landmarks
frame width
frame height
```

This preserves the source-independent architecture introduced in Milestone 4A.

---

## 6.4 Real Validation Before Acceptance

The first geometric implementation passed simple synthetic testing but showed problems during real webcam validation.

Two important failures were discovered:

1. approximately 180° neutral-pose offset
2. unrealistic roll values near ±180° during strong yaw

The algorithm was therefore not accepted after the first successful `solvePnP` implementation.

Instead, the milestone was iteratively refined until the live geometric behavior became plausible.

This demonstrates the engineering principle:

```text
successful execution
≠
validated perception behavior
```

---

# 7. Implemented Components

Milestone 5 contains four primary implementation areas.

## 7.1 `HeadPoseResult`

Purpose:

Store one valid geometric head-pose estimate.

Fields:

```text
yaw_degrees
pitch_degrees
roll_degrees
rotation_vector
translation_vector
```

---

## 7.2 `HeadPoseEstimator`

Purpose:

Convert 2D facial landmarks into geometric head orientation.

Responsibilities:

- validate required landmarks
- construct 2D image points
- maintain approximate 3D face model
- construct approximate camera matrix
- solve the PnP problem
- convert rotation vector to rotation matrix
- normalize coordinate conventions
- extract Euler angles
- maintain previous-pose state
- check angular continuity
- reset stale state

---

## 7.3 Head-Pose Smoke Test

File:

```text
src/experiments/head_pose_smoke_test.py
```

Purpose:

Validate the geometric estimator deterministically without requiring:

- webcam input
- private datasets
- manual driver motion

Synthetic image landmarks are generated from known 3D rotations using:

```text
cv2.projectPoints
```

The estimator then reconstructs the pose using:

```text
cv2.solvePnP
```

---

## 7.4 Visualization

Head-pose output is displayed in a dedicated right-side panel.

The panel contains:

```text
HEAD POSE
Yaw
Pitch
Roll
```

The visualization uses:

- semi-transparent background
- outlined text
- compact layout
- separate left/right diagnostic regions

This prevents the head-pose values from overlapping with:

- EAR/MAR
- temporal states
- source metadata
- milestone information

---

# 8. Head-Pose Landmark Model

The current estimator uses six 2D facial landmarks.

Required landmarks:

```text
nose_tip
chin
left_eye_outer
right_eye_outer
mouth_left
mouth_right
```

These landmarks were already available from the existing Face Mesh selection.

Corresponding MediaPipe landmark indices are defined in:

```text
src/perception/face_features.py
```

The six points were selected because they provide spatial coverage across:

- upper face
- central face
- lower face
- left side
- right side

Conceptually:

```text
left eye outer         right eye outer
      ●---------------------●

                ●
             nose tip

      ●                     ●
  mouth left            mouth right

                ●
               chin
```

This geometric spread improves the conditioning of the PnP problem compared with using tightly clustered landmarks.

---

# 9. Generic 3D Facial Model

A lightweight approximate 3D facial model is used.

The current reference points correspond to:

```text
nose tip
chin
left eye outer
right eye outer
left mouth corner
right mouth corner
```

The model is generic.

It is not based on:

- a personalized facial scan
- driver-specific measurements
- calibrated anatomical dimensions

This means the system estimates a practical relative head orientation rather than a personalized ground-truth pose.

The generic model is appropriate for the current fast-prototype path because it provides:

- low implementation complexity
- real-time operation
- interpretable geometry
- no additional training requirement

---

# 10. Camera Intrinsic Approximation

`solvePnP` requires a camera matrix.

The current prototype assumes a pinhole camera.

The focal length is approximated using:

```text
focal_length = frame_width
```

The principal point is assumed to be the image center:

```text
cx = frame_width / 2
cy = frame_height / 2
```

Conceptually:

```text
K =

[ fx   0   cx ]
[  0  fy   cy ]
[  0   0    1 ]
```

Current approximation:

```text
fx = frame_width
fy = frame_width
```

Lens-distortion coefficients are currently initialized to zero.

This approximation avoids requiring camera calibration for the initial prototype.

However, it also introduces a known accuracy limitation.

---

# 11. Perspective-n-Point Pose Estimation

OpenCV `solvePnP` is used to estimate pose.

Inputs:

```text
3D facial model points
2D facial image points
camera matrix
distortion coefficients
```

Outputs:

```text
rotation vector
translation vector
```

The solver configuration uses:

```text
cv2.SOLVEPNP_ITERATIVE
```

The iterative method is suitable for the current multi-point geometric estimation problem.

---

# 12. Rotation Representation

`solvePnP` returns a Rodrigues rotation vector.

This representation is converted to a 3×3 rotation matrix using:

```text
cv2.Rodrigues
```

The rotation matrix is then used for:

- coordinate normalization
- Euler-angle extraction
- future geometric extensions

The raw rotation vector is preserved in `HeadPoseResult`.

---

# 13. Coordinate-System Normalization

During initial webcam validation, near-frontal head poses produced pitch values close to approximately:

```text
180°
```

This indicated that the estimated physical transformation was being interpreted using incompatible coordinate conventions.

The generic face model and OpenCV camera frame use different axis directions.

A neutral model-to-camera transformation was therefore added.

The correction matrix represents an approximately 180° rotation around the X axis.

Conceptually:

```text
generic face-model coordinates
              ↓
neutral coordinate correction
              ↓
camera-facing neutral orientation
```

After this correction, a near-frontal real head produces values approximately near:

```text
yaw ≈ 0°
pitch ≈ 0°
roll ≈ 0°
```

subject to normal prototype error.

---

# 14. Euler-Angle Extraction

The corrected rotation matrix is converted into:

```text
pitch
yaw
roll
```

using an explicit rotation-matrix-to-Euler implementation.

This provides more control over the project's orientation convention than directly accepting a generic decomposition result.

The conversion includes handling for near-singular rotation configurations.

---

# 15. Axis Interpretation

Current semantic interpretation:

## 15.1 Yaw

Yaw represents horizontal head rotation.

Conceptually:

```text
turn head left / right
        ↓
yaw changes
```

---

## 15.2 Pitch

Pitch represents vertical head rotation.

Conceptually:

```text
look upward / downward
        ↓
pitch changes
```

---

## 15.3 Roll

Roll represents head tilt around the camera viewing direction.

Conceptually:

```text
tilt ear toward shoulder
        ↓
roll changes
```

---

## 15.4 Sign Convention

Positive and negative values represent opposite directions.

However, final semantic labels such as:

```text
positive yaw = driver left
```

are not yet hard-coded.

This is intentional because image mirroring and source-coordinate conventions can affect left/right interpretation.

A standardized source-coordinate convention should be defined before behavioral direction labels are introduced.

---

# 16. Initial Strong-Yaw Failure Mode

During early webcam validation, moderate poses behaved correctly.

Examples included:

```text
frontal pose
pitch-dominant vertical motion
roll-dominant head tilt
```

However, strong horizontal head rotation sometimes produced:

```text
yaw ≈ ±40° to ±50°
roll ≈ ±158° to ±180°
```

The driver had not physically rolled the head by 180°.

This revealed a geometric solution-branch instability.

The problem remained even when webcam mirroring was disabled.

Therefore:

```text
mirroring
```

was not identified as the root cause.

The issue originated from pose-solution continuity under difficult geometry.

---

# 17. Previous-Pose Initialization

To improve pose stability, the estimator stores the previous valid:

```text
rotation_vector
translation_vector
```

After the first valid estimate, these values are supplied to `solvePnP` as an initial estimate.

Conceptually:

```text
Frame N
   ↓
valid pose
   ↓
store rvec / tvec

Frame N+1
   ↓
current landmarks
+
previous rvec / tvec
   ↓
solvePnP(useExtrinsicGuess=True)
   ↓
solution near previous physical pose
```

This encourages temporal continuity between consecutive frames.

---

# 18. Pose-Continuity Guard

Previous-pose initialization improves solver behavior but does not guarantee that every candidate pose is physically plausible.

A second validation layer therefore checks frame-to-frame angular change.

The estimator compares:

```text
new yaw vs previous yaw
new pitch vs previous pitch
new roll vs previous roll
```

The prototype continuity parameter is:

```text
max_angle_jump_degrees = 75°
```

If any angular change exceeds the allowed value:

```text
candidate pose
    ↓
rejected
```

and the previous valid result is retained.

This avoids displaying implausible instantaneous orientation jumps.

The threshold is an engineering prototype parameter.

It is not a validated human-motion or safety threshold.

---

# 19. Angular Wraparound

Angle comparison cannot use a simple subtraction.

For example:

```text
179°
-179°
```

are geometrically close.

Naive subtraction gives:

```text
358°
```

but the actual shortest angular difference is:

```text
2°
```

The implementation therefore computes the shortest angular difference across the ±180° boundary.

This is necessary for robust orientation continuity checking.

---

# 20. Estimator Reset

`HeadPoseEstimator` provides:

```text
reset()
```

The reset clears:

```text
previous rotation vector
previous translation vector
previous accepted result
```

This prevents old geometric state from being incorrectly reused after tracking continuity is lost.

---

# 21. Face-Loss Recovery

The system distinguishes between:

```text
short face-detection dropout
```

and:

```text
prolonged face loss
```

Short landmark loss preserves the previous head-pose state.

This avoids unnecessary solver reinitialization after one or two unstable frames.

When face loss becomes prolonged according to the existing temporal threshold, the head-pose estimator is reset.

Current flow:

```text
face visible
    ↓
pose state stored

short face loss
    ↓
pose state preserved

prolonged face loss
    ↓
HeadPoseEstimator.reset()

face returns
    ↓
fresh pose initialization
```

This links geometric estimator recovery with the existing temporal face-loss infrastructure from Milestone 4B.

---

# 22. Source-Independent Integration

The head-pose estimator is integrated into the shared pipeline.

No separate webcam-specific implementation exists.

Processing remains:

```text
VideoSource
    ↓
FramePacket
    ↓
frame
    ↓
FaceMeshDetector
    ↓
selected landmarks
    ↓
HeadPoseEstimator
```

This same path works for:

```text
WebcamVideoSource
FileVideoSource
```

The head-pose module therefore remains independent of the acquisition source.

---

# 23. Main Pipeline Integration

`HeadPoseEstimator` is instantiated once before the main processing loop.

This is important because the estimator stores previous-pose state.

Incorrect design:

```text
create new estimator every frame
```

would erase temporal continuity.

Correct design:

```text
create estimator once
        ↓
process frame 1
        ↓
store pose
        ↓
process frame 2
        ↓
reuse previous pose
        ↓
...
```

Within each frame:

```text
selected landmarks
      ↓
EAR / MAR extraction
      +
head-pose estimation
      ↓
TemporalRuleEngine
      ↓
visualization
```

---

# 24. Visualization Design

The Milestone 5 visualization was reorganized to prevent text overlap.

The interface now uses two primary diagnostic regions.

## Left Side

Contains:

```text
FPS
face status
landmark count
EAR
MAR
source timestamp
frame index
source name
temporal state
temporal durations
```

## Right Side

Contains a dedicated:

```text
HEAD POSE
```

panel with:

```text
Yaw
Pitch
Roll
```

A semi-transparent dark panel and outlined text improve readability under variable image backgrounds.

The OpenCV window is also configured as resizable and initially displayed at approximately:

```text
1280 × 720
```

This improves demonstration visibility without changing the underlying camera resolution.

---

# 25. Deterministic Smoke-Test Design

A dedicated test is implemented in:

```text
src/experiments/head_pose_smoke_test.py
```

The test does not depend on:

- a real driver
- webcam conditions
- dataset availability

Synthetic head orientations are generated from the same 3D geometry.

Workflow:

```text
known synthetic orientation
        ↓
rotation matrix
        ↓
cv2.projectPoints
        ↓
synthetic 2D landmarks
        ↓
HeadPoseEstimator
        ↓
estimated orientation
        ↓
compare with expected pose
```

This validates the estimator deterministically.

---

# 26. Deterministic Test Coverage

The final head-pose smoke test verifies:

- camera-matrix construction
- missing-landmark rejection
- neutral pose
- positive yaw
- negative yaw
- pitch
- roll
- angular wraparound
- reset functionality
- gradual yaw continuity

Observed deterministic results:

```text
Synthetic neutral
yaw   ≈ 0°
pitch ≈ 0°
roll  ≈ 0°

Synthetic +yaw
expected ≈ +30°
estimated ≈ +29.9°

Synthetic -yaw
expected ≈ -30°
estimated ≈ -29.9°

Synthetic pitch
expected ≈ -25°
estimated ≈ -25.4°

Synthetic roll
expected ≈ +30°
estimated ≈ +29.9°
```

The gradual yaw sequence also successfully tracked approximately:

```text
0°
10°
20°
30°
40°
50°
```

without discontinuity failure.

---

# 27. Webcam Validation

Live webcam validation covered:

- frontal pose
- moderate left/right yaw
- strong left/right yaw
- vertical pitch
- roll / head tilt
- variable illumination
- face loss
- face re-entry

After the final stabilization update, observed qualitative examples included approximately:

```text
Neutral:
Yaw   ≈ -7°
Pitch ≈ -3°
Roll  ≈ 0°

Strong yaw:
Yaw   ≈ +51°
Pitch ≈ -12°
Roll  ≈ -7°

Opposite strong yaw:
Yaw   ≈ -48°
Pitch ≈ -11°
Roll  ≈ -3°

Vertical pose:
Yaw   ≈ -1°
Pitch ≈ -32°
Roll  ≈ -5°

Head tilt:
Yaw   ≈ -7°
Pitch ≈ -11°
Roll  ≈ -42°
```

These results demonstrate useful axis separation for the prototype.

They are qualitative engineering observations and not quantitative ground-truth accuracy results.

---

# 28. Recorded-Video Validation

The same pipeline was tested using a local recorded DMD sample through:

```text
FileVideoSource
```

The recorded-video validation confirmed that Milestone 5 works through the same source-independent architecture used for webcam processing.

Observed recorded-video behavior included:

- valid face landmark tracking
- valid head-pose output
- side head orientations producing strong yaw
- near-frontal sections producing smaller yaw/pitch/roll values
- simultaneous operation with Milestone 4B temporal reasoning
- no separate dataset-specific head-pose implementation

The DMD sample remains private.

Raw or derived DMD media is not included in the public repository.

---

# 29. Regression Validation

After Milestone 5 integration, the existing Milestone 4B temporal smoke test was rerun.

Result:

```text
[PASS] All temporal-rule smoke tests passed.
```

The Milestone 5 head-pose test also passed:

```text
[PASS] All head-pose smoke tests passed.
```

This confirms that the new geometric functionality did not break the previous temporal face-level baseline.

---

# 30. Project Architecture Impact

Before Milestone 5:

```text
Video Source
    ↓
FramePacket
    ↓
Face Mesh
    ↓
Selected Facial Landmarks
    ↓
EAR / MAR
    ↓
Temporal Rule Engine
    ↓
Visualization
```

After Milestone 5:

```text
Video Source
    ↓
FramePacket
    ↓
Face Mesh
    ↓
Selected Facial Landmarks
       ├─────────────────────┐
       ↓                     ↓
EAR / MAR             HeadPoseEstimator
       ↓                     ↓
Temporal Rules          yaw / pitch / roll
       └──────────┬──────────┘
                  ↓
             Visualization
```

Future architecture:

```text
Video Acquisition
       ↓
Facial / Body / Hand Perception
       ↓
Geometric Feature Layer
       ↓
EAR / MAR / Head Pose / Gaze / Pose / Hands
       ↓
Unified Temporal Representation
       ↓
Multimodal Driver-Behavior Modeling
       ↓
ML / XAI Driver-State Estimation
```

---

# 31. System Interfaces

## Inputs

`HeadPoseEstimator.estimate()` receives:

```text
landmarks
frame_width
frame_height
```

Landmarks:

```text
Dict[str, Point2D]
```

Required keys:

```text
nose_tip
chin
left_eye_outer
right_eye_outer
mouth_left
mouth_right
```

---

## Outputs

Return type:

```text
Optional[HeadPoseResult]
```

Valid result fields:

```text
yaw_degrees
pitch_degrees
roll_degrees
rotation_vector
translation_vector
```

---

## Dependencies

Current dependencies:

```text
OpenCV
NumPy
MediaPipe Face Mesh output
```

---

## Current Consumers

Current consumers:

```text
main.py
visualization.py
head_pose_smoke_test.py
```

---

## Future Consumers

Potential future consumers:

```text
gaze estimation
head-away temporal logic
attention model
driver-behavior model
logging
evaluation
ROS
ML/XAI
```

---

# 32. Limitations

Milestone 5 remains a prototype geometric baseline.

Known limitations include:

- generic non-personalized 3D facial model
- approximate focal length
- approximate camera principal point
- no physical camera calibration
- zero-distortion assumption
- dependence on MediaPipe landmark quality
- possible cross-axis coupling
- reduced robustness during extreme occlusion
- reduced robustness at extreme head rotation
- prototype-level continuity threshold
- no formal pose-confidence value
- no reprojection-error rejection yet
- no quantitative ground-truth accuracy benchmark
- no driver-specific neutral-pose calibration
- no explicit uncertainty representation
- no final semantic left/right sign standardization across mirrored/non-mirrored sources
- no behavioral head-away interpretation

These limitations are expected for the fast-prototype path.

---

# 33. Possible Edge Cases

Important edge cases include:

## Missing Landmarks

If one or more required landmarks are unavailable:

```text
HeadPoseResult = None
```

---

## Brief Face Dropout

Short face-detection failures preserve estimator state.

---

## Prolonged Face Loss

The estimator is reset.

---

## Extreme Yaw

Large horizontal rotation may reduce landmark quality or increase PnP ambiguity.

Temporal initialization and continuity checking reduce this risk but do not eliminate it mathematically.

---

## Camera Changes

Changing:

- camera
- focal length
- image resolution
- lens
- camera position

may affect pose accuracy because the current camera model is approximate.

---

## Mirroring

Horizontal mirroring changes image-space handedness.

Therefore mirroring must be treated as a presentation concern and carefully considered when assigning semantic left/right labels.

---

# 34. Alternative Approaches

Several alternative head-pose methods could be evaluated later.

## 34.1 Calibrated solvePnP

Advantages:

- improved geometric accuracy
- physically meaningful camera model

Requires:

- camera calibration
- distortion coefficients

---

## 34.2 More Facial Correspondences

Additional landmarks may improve robustness.

Potential disadvantage:

- some landmarks may be less geometrically stable
- incorrect 3D correspondences may reduce accuracy

---

## 34.3 Dense Face Geometry

A denser facial mesh could be used for pose fitting.

Potential benefit:

- more geometric information

Potential cost:

- increased complexity
- greater sensitivity to model assumptions

---

## 34.4 Learning-Based Head Pose

A neural-network head-pose model could directly estimate orientation.

Advantages:

- potentially better robustness under difficult conditions

Disadvantages:

- model dependency
- inference cost
- dataset requirements
- reduced geometric interpretability

---

## 34.5 Quaternion Representation

Quaternion-based orientation could reduce some Euler-angle representation issues.

Euler angles would still be useful for user-facing interpretation.

---

## 34.6 Temporal Filtering

Possible future filters:

- exponential smoothing
- Kalman filter
- One Euro Filter

These could reduce measurement jitter.

Filtering should be evaluated carefully to avoid excessive response delay.

---

# 35. Future Scalability

The head-pose module creates a reusable geometric signal for later milestones.

## Gaze Estimation

Head orientation can be combined with eye orientation.

Conceptually:

```text
head orientation
       +
eye orientation
       ↓
estimated gaze
```

---

## Temporal Head-Away Analysis

Later temporal logic can measure:

```text
how long has yaw remained outside a calibrated region?
```

instead of reacting to one pose frame.

---

## Multimodal Driver Behavior

Future behavior reasoning can combine:

```text
head pose
gaze
EAR
MAR
body pose
hand activity
```

---

## ROS Integration

The output could later become a message such as:

```text
Header
yaw
pitch
roll
confidence
```

with source timestamps.

---

## ML / XAI

Head-pose signals can later become interpretable features for:

- ML driver-state estimation
- feature attribution
- event explanation
- behavior classification

---

# 36. Research / Technology Notes

This milestone demonstrates several core robotics and computer-vision concepts.

## 2D–3D Correspondence

Image-space points are associated with known approximate 3D reference points.

---

## Camera Geometry

The projection model connects:

```text
3D world/model coordinates
```

to:

```text
2D image coordinates
```

---

## Rigid Pose Estimation

The output contains:

```text
rotation
translation
```

between the facial model and the camera.

---

## Coordinate Frames

The milestone showed that coordinate conventions are not merely software details.

A numerically valid rotation can still be semantically misleading if the reference frames are inconsistent.

---

## Temporal Estimator Stabilization

Geometric estimation benefits from physical continuity.

Human head motion is continuous between neighboring video frames.

This prior information can be used to reject mathematically possible but physically implausible pose jumps.

---

## Source Independence

Because acquisition is abstracted, the same perception implementation can be validated against:

```text
live sensor
recorded sensor data
dataset samples
```

This is important for robotics-perception development.

---

# 37. Engineering Lessons Learned

Key lessons from Milestone 5:

1. `solvePnP` execution success does not guarantee semantically correct head-pose angles.

2. Camera and model coordinate conventions must be explicitly defined.

3. Real webcam testing can expose failures that synthetic neutral tests do not reveal.

4. Extreme rotations can create ambiguous PnP solution branches.

5. Previous-pose initialization improves solver continuity.

6. A continuity guard is preferable to arbitrarily clamping incorrect angles.

7. Angular wraparound must be handled correctly.

8. Short detector dropouts and prolonged tracking loss should be handled differently.

9. Head-pose measurements should remain separate from distraction labels.

10. Recorded-video validation is required for a source-independent perception pipeline.

11. Private dataset media must remain outside the public repository unless redistribution is explicitly permitted.

12. A generic face model is useful for prototyping but should not be confused with calibrated ground-truth pose estimation.

---

# 38. Validation Summary

Milestone 5 has successfully completed:

```text
Deterministic geometry tests
Webcam validation
Strong-yaw validation
Pitch validation
Roll validation
Pose-continuity validation
Face-loss recovery validation
Recorded-video validation
Milestone 4B regression validation
```

Detailed validation results are documented separately in:

```text
docs/validation/path_01_milestone_05_head_pose_estimation_validation.md
```

---

# 39. Next Milestone

The next planned milestone is:

```text
Path 1 — Milestone 6: Gaze Estimation
```

The next stage will extend cabin perception from:

```text
where is the head oriented?
```

toward:

```text
where are the eyes / visual attention directed?
```

Head orientation will become an important geometric input for later gaze and attention reasoning.

Behavioral distraction classification will still remain separate until sufficient multimodal and temporal evidence is available.

---

# Milestone Completion Checklist

## Implementation

- [x] Head-pose module created
- [x] `HeadPoseResult` implemented
- [x] Required landmarks defined
- [x] 3D facial reference model implemented
- [x] Approximate camera matrix implemented
- [x] `solvePnP` integrated
- [x] Rodrigues conversion implemented
- [x] Coordinate-system normalization implemented
- [x] Euler-angle extraction implemented
- [x] Yaw output implemented
- [x] Pitch output implemented
- [x] Roll output implemented
- [x] Previous-pose initialization implemented
- [x] Angular continuity guard implemented
- [x] Angular wraparound handling implemented
- [x] Estimator reset implemented
- [x] Prolonged face-loss recovery integrated
- [x] Source-independent integration completed
- [x] Head-pose visualization implemented
- [x] Resizable OpenCV display implemented

## Validation

- [x] Camera-matrix test passed
- [x] Missing-landmark test passed
- [x] Synthetic neutral-pose test passed
- [x] Positive-yaw test passed
- [x] Negative-yaw test passed
- [x] Pitch test passed
- [x] Roll test passed
- [x] Angular-difference test passed
- [x] Reset test passed
- [x] Pose-continuity test passed
- [x] Webcam validation completed
- [x] Strong-yaw validation completed
- [x] Pitch validation completed
- [x] Roll validation completed
- [x] Face-loss recovery validated
- [x] Recorded-video validation completed
- [x] Existing temporal regression test passed
- [x] Head-pose smoke-test suite passed

## Documentation / Repository Closure

- [x] Implementation documentation prepared
- [x] Validation documentation completed
- [x] README updated
- [x] Final Git diff reviewed
- [x] Milestone 5 committed
- [x] Feature branch pushed
- [x] Pull request created
- [x] Pull request merged
- [x] Local `main` synchronized
- [x] Milestone 5 officially closed
