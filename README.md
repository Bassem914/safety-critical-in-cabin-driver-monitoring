# Safety-Critical In-Cabin Driver Monitoring

## A Staged Computer Vision Framework for Driver State Estimation, Pose Analysis, and Safety-Critical Cabin Perception

---

# Project Overview

This repository documents the development of a safety-critical in-cabin driver monitoring system using modern computer vision techniques.

The project is developed incrementally through engineering milestones, with each milestone including:

- Software implementation
- Computer vision design
- Validation
- Engineering documentation
- Research and technology notes

The long-term objective is to build a modular Driver Monitoring System (DMS) capable of estimating:

- Driver drowsiness
- Driver distraction
- Head pose
- Gaze direction
- Unsafe body posture
- Hand activity
- Unresponsive driver state

---

# Current Development Path

The active implementation path is:

```text
paths/01_fast_prototype/
```

---

# Project Progress

Current Stage:

**Path 1 — Fast Prototype**

Current Progress:

- ✅ Milestones 1–7: prototype implementation completed (including Milestones 4A and 4B)
- ✅ Milestone 7: 8/8 deterministic tests passed; integrated recorded-video replay completed with 30-frame auto-calibration and clean exit
- 📋 Separate release status: M7 branch awaits Git review and merge. Final-code combined webcam/UI and previous-feature regression are not independently documented in the last supplied run.

Completed prototype milestones currently include:

- Milestone 1
- Milestone 2
- Milestone 3
- Milestone 4A
- Milestone 4B
- Milestone 5
- Milestone 6
- Milestone 7

Milestone 7 is complete at the agreed prototype scope on `feat/body-pose-posture`. Its integrated recorded-file runtime check passed on 2026-09-24. The final Git merge is pending; the latest-code combined webcam/UI and M1–M6 regression checks are not separately confirmed in the available final log.

---

# Current Implementation Status

| Milestone | Status | Description |
|-----------|--------|-------------|
| Milestone 1 | ✅ Completed | Webcam smoke test |
| Milestone 2 | ✅ Completed | MediaPipe Face Mesh landmark pipeline |
| Milestone 3 | ✅ Completed | Facial geometry features: EAR and MAR |
| Milestone 4A | ✅ Completed | Source-independent webcam and recorded-video input |
| Milestone 4B | ✅ Completed | Face-level temporal state baseline |
| Milestone 5 | ✅ Completed | Geometric head pose estimation: yaw, pitch, and roll |
| Milestone 6 | ✅ Completed | Geometric gaze estimation and prototype gaze-direction baseline |
| Milestone 7 | ✅ Completed | Four-landmark body geometry, lateral/sagittal posture |
| Milestone 8 | Planned | Hand activity analysis |
| Milestone 9 | Planned | Unified temporal feature layer |
| Milestone 10 | Planned | Multimodal driver-behavior modeling |
| Milestone 11 | Planned | ML and explainable AI |
| Milestone 12 | Planned | Benchmarking and research evaluation |

---

# Implemented Features

## Milestone 1 — Webcam Smoke Test

- Webcam acquisition
- FPS computation
- Camera validation
- Clean application shutdown

---

## Milestone 2 — MediaPipe Face Mesh Landmark Pipeline

- MediaPipe Face Mesh integration
- Facial landmark extraction
- Landmark visualization
- Modular perception architecture
- Validation framework
- Documentation framework

---

## Milestone 3 — Facial Geometry Features

- Eye Aspect Ratio (EAR)
- Mouth Aspect Ratio (MAR)
- Real-time feature overlay
- Modular facial geometry extractor
- Feature-level validation

---

## Milestone 4A — Source-Independent Video Input

The perception pipeline supports both live webcam input and local recorded-video input through a common acquisition interface.

Implemented capabilities:

- abstract `VideoSource` interface
- `WebcamVideoSource`
- `FileVideoSource`
- timestamped `FramePacket`
- source frame indexing
- optional webcam mirroring
- shared Face Mesh and EAR/MAR processing pipeline
- private dataset and video-file protection

The same perception modules therefore operate independently of whether frames originate from a webcam or a recorded file.

---

## Milestone 4B — Face-Level Temporal State Baseline

Milestone 4B converts frame-level EAR, MAR, and face visibility into timestamp-based temporal event candidates.

Implemented capabilities:

- configurable temporal thresholds
- source-timestamp-based duration tracking
- EAR and MAR moving-average support
- blink candidate detection
- blink display hold
- prolonged eye-closure detection
- sustained mouth-opening detection
- prolonged face-loss detection
- state-priority logic
- timestamp-order validation
- deterministic temporal-rule smoke tests
- webcam integration
- recorded-video integration
- local DMD sample validation
- state-dependent visualization colors

Current temporal candidates:

```text
NORMAL
BLINK_CANDIDATE
PROLONGED_EYE_CLOSURE
SUSTAINED_MOUTH_OPENING
PROLONGED_FACE_LOSS
```

These outputs are interpretable prototype event candidates. They are not final medical diagnoses or production safety classifications.

Validation evidence currently includes locally stored annotated output video and screenshots containing temporal states. Public evidence will only be added after privacy and dataset-redistribution review.

Documentation:

- [Implementation](docs/implementation/path_01_milestone_04B_face_temporal_state_baseline.md)
- [Validation](docs/validation/path_01_milestone_04B_face_temporal_state_baseline_validation.md)

---

## Milestone 5 — Head Pose Estimation

Milestone 5 extends the facial perception pipeline with geometric head-orientation estimation.

Implemented capabilities:

- six-point 2D–3D facial correspondence
- generic 3D facial reference model
- approximate pinhole-camera intrinsic matrix
- OpenCV Perspective-n-Point estimation using `solvePnP`
- rotation-vector and translation-vector estimation
- Rodrigues rotation-matrix conversion
- coordinate-system normalization
- explicit yaw, pitch, and roll extraction
- previous-pose initialization
- frame-to-frame angular continuity checking
- angular wraparound handling
- estimator reset functionality
- prolonged face-loss recovery
- source-independent webcam integration
- source-independent recorded-video integration
- deterministic synthetic head-pose smoke tests
- dedicated head-pose visualization panel

Current geometric outputs:

```text
Yaw
Pitch
Roll
```

These outputs are geometric perception measurements.

They are not yet interpreted as final driver distraction, inattention, gaze-away, or safety classifications.

### Head-Pose Stabilization

Initial live validation exposed two important geometric issues:

1. a near-frontal pitch offset close to 180° caused by coordinate-frame convention mismatch
2. unrealistic roll values near ±180° during strong yaw caused by alternative PnP solution behavior

The implementation was refined using:

- explicit model-to-camera coordinate normalization
- previous valid pose initialization
- `solvePnP(..., useExtrinsicGuess=True)` for subsequent frames
- angular wraparound handling
- frame-to-frame pose-continuity validation

After refinement, strong yaw produced yaw-dominant measurements without the previous ±180° roll artifact during the validated sequences.

### Face-Loss Recovery

Short detector dropouts preserve head-pose history to support continuity.

When face loss becomes prolonged according to the existing temporal face-loss threshold, the head-pose estimator is reset.

This prevents stale pose state from being reused indefinitely after meaningful tracking loss.

### Validation

Validation includes:

- camera-matrix construction
- missing-landmark handling
- synthetic neutral pose
- positive yaw
- negative yaw
- pitch
- roll
- angular wraparound
- estimator reset
- gradual yaw continuity
- webcam near-neutral validation
- strong positive and negative yaw validation
- pitch validation
- roll validation
- prolonged face-loss recovery
- recorded-video validation
- Milestone 4B regression testing

Representative deterministic results:

```text
Synthetic neutral
Yaw   ≈ 0.00°
Pitch ≈ 0.31°
Roll  ≈ 0.00°

Synthetic +Yaw
Expected ≈ +30°
Estimated ≈ +29.89°

Synthetic -Yaw
Expected ≈ -30°
Estimated ≈ -29.89°

Synthetic Pitch
Expected ≈ -25°
Estimated ≈ -25.35°

Synthetic Roll
Expected ≈ +30°
Estimated ≈ +29.89°
```

Gradual yaw continuity was also validated across approximately:

```text
0° → 10° → 20° → 30° → 40° → 50°
```

Final regression results:

```text
[PASS] All temporal-rule smoke tests passed.
[PASS] All head-pose smoke tests passed.
```

Recorded-video validation was also completed using the same `FileVideoSource` path as the rest of the perception pipeline.

Private DMD media and derived validation media remain outside the public repository unless redistribution rights are explicitly confirmed.

Documentation:

- [Implementation](docs/implementation/path_01_milestone_05_head_pose_estimation.md)
- [Validation](docs/validation/path_01_milestone_05_head_pose_estimation_validation.md)

---

## Milestone 6 — Gaze Estimation

Milestone 6 extends the facial perception pipeline with an interpretable geometric gaze-estimation baseline using refined MediaPipe iris landmarks.

Implemented capabilities:

- refined iris landmark integration
- per-eye normalized horizontal and vertical iris geometry
- bilateral horizontal coordinate canonicalization
- combined horizontal and vertical gaze features
- horizontal inter-eye disagreement `dH`
- vertical inter-eye disagreement `dV`
- configurable bilateral consistency thresholds
- `GOOD` / `LOW` gaze-consistency state
- prototype geometric gaze-direction labels
- `CENTER`, `LEFT`, `RIGHT`, `UP`, `DOWN`
- diagonal gaze labels
- `UNKNOWN` output for inconsistent bilateral measurements
- deterministic gaze smoke tests
- controlled webcam gaze-direction validation
- source-independent recorded-video validation
- private DMD sample validation
- dedicated external perception dashboard

Current geometric outputs:

```text
Left eye H / V
Right eye H / V
Combined H / V
dH / dV
Consistency
Direction
```

Validated geometric convention:

```text
Higher H → LEFT
Lower H  → RIGHT
Lower V  → UP
Higher V → DOWN
```

Current prototype direction thresholds:

```text
H < 0.40  → RIGHT
H > 0.56  → LEFT
otherwise → horizontal CENTER

V < 0.41  → UP
V > 0.50  → DOWN
otherwise → vertical CENTER
```

These thresholds are prototype parameters derived from initial controlled validation. They are not calibrated gaze angles, universal driver thresholds, or production DMS specifications.

### Bilateral Consistency

The implementation tracks disagreement between the two eyes:

```text
dH = |H_left - H_right|
dV = |V_left - V_right|
```

Current prototype consistency limits are:

```text
dH <= 0.15
dV <= 0.20
```

A `GOOD` consistency state means that both eyes agree sufficiently according to these thresholds. It does not guarantee absolute gaze accuracy. Strong head pose can introduce common geometric bias into both eyes while preserving low inter-eye disagreement.

### Direction Semantics

The direction output is a geometric perception label only. It is not directly interpreted as `DISTRACTED`, `INATTENTIVE`, `DROWSY`, or `UNRESPONSIVE`. Behavioral interpretation remains reserved for later temporal and multimodal milestones.

### Validation

Validation includes deterministic synthetic gaze tests, bilateral canonicalization checks, inter-eye disagreement and consistency checks, controlled webcam testing for the five primary directions, recorded-video validation through `FileVideoSource`, and private DMD sample validation.

Representative webcam observations included:

```text
Intentional LEFT gaze:
Combined H ≈ 0.678
Combined V ≈ 0.471
Head pose approximately neutral
Consistency = GOOD

Intentional UP gaze:
Combined H ≈ 0.501
Combined V ≈ 0.399
dH ≈ 0.022
dV ≈ 0.069
Consistency = GOOD
```

Private DMD media and derived validation material remain outside the repository unless redistribution rights are explicitly confirmed.

Documentation:

- [Implementation](docs/implementation/path_01_milestone_06_gaze_estimation.md)
- [Validation](docs/validation/path_01_milestone_06_gaze_estimation_validation.md)

Milestones 6 and 7 are complete at prototype scope. Milestone 7 remains on its feature branch pending final Git review and merge.

---

## Milestone 7 — Body Pose and Posture Analysis

**Status:** **Prototype completed** on `feat/body-pose-posture` (2026-09-24); eight deterministic tests passed and the integrated controlled-file run completed with 30-frame automatic calibration and clean shutdown. Repository merge remains pending. The latest-code combined webcam/UI and M1–M6 regression checks were not separately confirmed in the final runtime log.

- MediaPipe Pose extraction of left/right shoulders and hips (landmarks 11, 12, 23, 24)
- Visibility and minimum torso-geometry validity checks
- Shoulder/hip midpoints, line angles, torso lateral angle, shoulder/hip widths and normalized torso length
- Non-metric shoulder-minus-hip depth feature, `torso_dZ`
- Two independent geometric states: `UPRIGHT` / `LEAN_LEFT` / `LEAN_RIGHT` and `NOT_CALIBRATED` / `CALIBRATING` / `NEUTRAL` / `FORWARD_LEAN`
- Explicit 30-valid-frame neutral calibration, median baseline, calibration-spread rejection and reset
- Provisional ±6° lateral and −0.08 *calibration-relative* depth decision boundaries
- Webcam smoke test, controlled local video playback and experimental CSV logging
- Integrated source-independent `main.py` pipeline with an additional white M7 dashboard panel
- Eight passing deterministic tests for estimator logic and calibration lifecycle

**Interpretation caution:** MediaPipe depth is not a physical distance. Lateral leaning can alter the sagittal depth proxy and sometimes co-trigger `FORWARD_LEAN` without intentional forward movement. The classifier has not been benchmarked against frame-annotated ground truth or validated as a safety function. All eight deterministic M7 tests passed and the integrated controlled-file run completed successfully. Latest-code combined webcam/UI and M1–M6 regressions are remaining release checks, not unresolved M7 algorithm-development tasks.

Run deterministic tests from `paths/01_fast_prototype`:

```bash
PYTHONPATH=src python -m unittest discover -s src/tests -p "test_m7_posture_regression.py" -v
```

Controlled file demonstration (only when the first frames are confirmed neutral):

```bash
PYTHONPATH=src python -m main --source file --video-path "D:/Cabin_sensing/practical/full_scenario_webcam_test.mp4" --auto-calibrate-file
```

Manual webcam calibration: run `PYTHONPATH=src python -m main --source webcam`, sit still and press `C` once; press `R` to reset. Calibration is held in memory for the session and is not saved across application runs.

Implementation: `docs/implementation/path_01_milestone_07_body_pose_posture.md`.  
Validation: `docs/validation/path_01_milestone_07_body_pose_posture_validation.md`.

---

# Current Capabilities

The current Path 1 prototype supports:

- live webcam input
- local recorded-video input
- source-independent acquisition
- source timestamps and frame indices
- optional webcam mirroring
- MediaPipe Face Mesh
- selected facial landmark extraction
- Eye Aspect Ratio
- Mouth Aspect Ratio
- temporal EAR and MAR processing
- blink candidate detection
- prolonged eye-closure detection
- sustained mouth-opening detection
- prolonged face-loss detection
- deterministic temporal-rule tests
- geometric head pose estimation
- yaw estimation
- pitch estimation
- roll estimation
- stateful PnP pose tracking
- previous-pose initialization
- angular continuity validation
- angular wraparound handling
- prolonged face-loss pose reset
- deterministic head-pose smoke tests
- source-independent head-pose processing
- refined iris landmark extraction
- per-eye normalized gaze H/V geometry
- bilateral horizontal gaze canonicalization
- combined gaze H/V features
- inter-eye disagreement `dH` / `dV`
- gaze consistency assessment
- prototype geometric gaze-direction labels
- deterministic gaze smoke tests
- source-independent gaze processing
- selected shoulder/hip pose landmarks and continuous body geometry
- independent lateral and sagittal prototype posture states
- 30-valid-frame median neutral calibration
- controlled body-pose recorded-video and webcam testing
- deterministic M7 posture regression tests
- real-time temporal-state visualization
- real-time head-pose visualization
- external perception dashboard
- privacy-aware local validation

---

# Current Path 1 Architecture

```text
Webcam / Local Video / Dataset Sample
                ↓
Source-Independent Acquisition
                ↓
Timestamped FramePacket
                ↓
MediaPipe Face Mesh
                ↓
Selected Facial + Iris Landmarks
        ┌───────────────┼────────────────┐
        ↓               ↓                ↓
EAR / MAR          Head Pose         Gaze Estimation
Extraction         Estimation             ↓
    ↓                  ↓            Left / Right H/V
Temporal           Yaw / Pitch      Combined H/V
Rule Engine        / Roll           dH / dV
                                    Consistency
                                    Direction
        └───────────────┬────────────────┘
                        ↓
          External Perception Dashboard
                        ↑
              MediaPipe Body Pose
                        ↓
          Shoulder / Hip Landmarks
                        ↓
         Geometry + Neutral Calibration
                        ↓
         Lateral + Sagittal State (M7)
```

Current module responsibilities:

```text
acquisition/
    video source abstraction
    frame acquisition
    timestamps
    source metadata

perception/face_features.py
    selected facial landmarks
    EAR
    MAR

perception/head_pose.py
    2D–3D geometry
    solvePnP
    yaw
    pitch
    roll
    pose continuity

perception/body_features.py
    shoulder/hip landmark detection
    continuous body geometry
    30-frame median neutral calibration
    lateral/sagittal prototype posture states

perception/gaze.py
    iris geometry
    bilateral H/V normalization
    inter-eye disagreement
    consistency
    prototype geometric direction

decision/temporal_rules.py
    timestamp-based temporal candidates

perception/visualization.py
    state and measurement visualization

main.py
    source-independent M1–M7 orchestration
    appended M7 white diagnostic panel

src/tests/test_m7_posture_regression.py
    deterministic body posture and calibration tests
```

---

# Repository Structure

```text
docs/
research/
paths/
shared/
tests/
deliverables/
```

The active prototype implementation is located under:

```text
paths/01_fast_prototype/
```

---

# Documentation

| Folder | Purpose |
|---------|---------|
| `docs/implementation/` | Engineering implementation reports |
| `docs/validation/` | Validation reports |
| `docs/templates/` | Documentation templates |
| `research/technology_notes/` | Technology notes |
| `research/model_reviews/` | Model comparison studies |
| `research/benchmarks/` | Benchmark results |

Current milestone documentation includes:

```text
docs/implementation/path_01_milestone_04B_face_temporal_state_baseline.md
docs/validation/path_01_milestone_04B_face_temporal_state_baseline_validation.md

docs/implementation/path_01_milestone_05_head_pose_estimation.md
docs/validation/path_01_milestone_05_head_pose_estimation_validation.md

docs/implementation/path_01_milestone_06_gaze_estimation.md
docs/validation/path_01_milestone_06_gaze_estimation_validation.md

docs/implementation/path_01_milestone_07_body_pose_posture.md
docs/validation/path_01_milestone_07_body_pose_posture_validation.md
```

---

# Development Workflow

Every milestone follows the same engineering workflow:

```text
Planning
    ↓
Implementation
    ↓
Validation
    ↓
Documentation
    ↓
README Update
    ↓
Final Regression Check
    ↓
Git Review
    ↓
Commit
    ↓
Pull Request
    ↓
Merge
    ↓
Synchronize Main
    ↓
Next Milestone
```

The workflow is intended to preserve:

- traceability
- modular development
- reproducible validation
- explicit limitations
- disciplined Git history
- milestone-level technical documentation

---

# Validation Philosophy

The project does not treat successful execution as sufficient evidence that a perception component is correct.

Each milestone should be validated through multiple complementary methods when applicable.

Current validation strategy includes:

```text
Deterministic Tests
        +
Live Webcam Validation
        +
Recorded-Video Validation
        +
Regression Tests
        ↓
Engineering Assessment
```

For source-independent perception components, both webcam and recorded-video execution are required where practical.

Synthetic tests verify deterministic mathematical behavior, while real video exposes:

- landmark noise
- occlusion
- camera effects
- solver instability
- temporal discontinuities
- visualization problems

Private dataset media remains local unless redistribution is explicitly permitted.

---

# Roadmap

## Completed

- ✅ Webcam Smoke Test
- ✅ MediaPipe Face Mesh Landmark Pipeline
- ✅ Facial Geometry Feature Extraction
- ✅ Source-Independent Video Input
- ✅ Face-Level Temporal State Baseline
- ✅ Head Pose Estimation
- ✅ Gaze Estimation
- ✅ Body Pose and Posture Analysis (Milestone 7)

M7 evidence: live webcam posture experiments, 30-frame median calibration, recorded-video experiments, eight passing deterministic regression tests, and a successful integrated recorded-file run.

## Repository release (separate from milestone completion)

- Review and commit M7 code and documentation; check Git changes for private video, dataset, screenshot, and CSV files.
- Verify combined webcam/dashboard and prior-feature behavior on the final code revision if those checks have not already been recorded.
- Create and merge the M7 pull request after repository review.

## Next development milestone

- 🔜 Milestone 8 — Hand Activity Analysis

## Planned after M8
- Unified Temporal Feature Layer
- Multimodal Driver Behavior Modeling
- ML and Explainable AI
- Benchmarking and Research Evaluation

---

# Current Technical Stack

- Python
- OpenCV
- MediaPipe
- NumPy

Current geometric and perception concepts include:

- facial landmark detection
- 2D facial geometry
- temporal feature reasoning
- source timestamps
- 2D–3D correspondences
- Perspective-n-Point estimation
- rigid pose estimation
- rotation matrices
- Euler angles
- coordinate-frame normalization
- temporal estimator continuity
- refined iris landmarks
- normalized iris-position geometry
- bilateral gaze coordinate canonicalization
- inter-eye gaze disagreement
- prototype gaze-direction classification
- MediaPipe Pose shoulder/hip geometry
- frontal-view torso lateral angle
- non-metric relative-depth proxy
- neutral-frame median calibration and stability gating
- independent lateral and sagittal prototype labels

---

# Current Limitations

The project is currently a fast-prototype research and engineering implementation.

Current limitations include:

- generic non-personalized 3D facial model
- approximate camera intrinsics
- no physical camera calibration
- zero lens-distortion assumption for head pose
- dependence on MediaPipe landmark quality
- possible head-pose cross-axis coupling
- reduced reliability at extreme pose or occlusion
- prototype temporal and continuity thresholds
- no formal head-pose confidence output
- no reprojection-error quality metric
- no quantitative real-world head-pose ground-truth benchmark yet
- 2D gaze geometry only; no calibrated 3D gaze vector
- no camera-specific gaze calibration
- no driver-specific gaze calibration
- fixed prototype gaze-direction thresholds
- gaze sensitivity to strong head pose and perspective distortion
- no explicit eye-openness gate for gaze validity
- inter-eye consistency is not calibrated gaze confidence
- no quantitative real-world gaze ground-truth benchmark yet
- no temporal gaze-away interpretation yet
- no behavioral distraction classification yet
- body-pose validity gates do not verify true landmark accuracy
- forward-depth proxy varies with camera placement, body rotation and subject
- lateral leaning can co-trigger sagittal FORWARD_LEAN without intentional forward movement
- no frame-annotated body-posture accuracy benchmark or multi-driver calibration
- M7 integrated recorded-file run passed. A prior TensorFlow/MediaPipe import `MemoryError` did not recur during that run; its cause remains unconfirmed. Combined webcam/UI and M1–M6 regressions are release checks pending independent confirmation.
- no production or medical safety claims

These limitations are documented intentionally and will guide later model comparison, calibration, benchmarking, and research stages.

---

# Research Direction

The project follows a staged progression from interpretable classical perception toward multimodal driver-state modeling.

Current progression:

```text
Video Acquisition
        ↓
Facial Landmarks
        ↓
EAR / MAR
        ↓
Temporal Face-Level Reasoning
        ↓
Head Pose
        ↓
Gaze Estimation
        ↓
Body Pose / Hand Activity
        ↓
Unified Temporal Features
        ↓
Multimodal Driver Behavior Modeling
        ↓
ML / XAI
        ↓
Benchmarking and Research Evaluation
```

The staged approach is intended to maintain interpretability and allow each subsystem to be validated independently before higher-level fusion.

---

# Project Purpose

This project is designed as a research and engineering portfolio for:

- Driver Monitoring Systems
- In-cabin sensing
- Safety-critical perception
- Autonomous Driving / ADAS
- Robotics Vision and Perception
- Computer Vision Engineering
- Applied AI / ML
- PhD and research preparation

The repository emphasizes:

- modular software architecture
- interpretable computer vision
- validation discipline
- source-independent perception
- temporal reasoning
- explicit engineering limitations
- research-oriented extensibility

---

# Next Development Step

Milestone 7 is completed at the agreed research-prototype scope. The next development milestone is M8 (Hand Activity Analysis). Before merging the completed M7 work from `feat/body-pose-posture`, carry out the separate repository release review:

1. If not already verified on the final code revision, confirm the combined webcam/dashboard and existing M1–M6 functions. This is release regression, not further posture feature development. If the earlier import `MemoryError` recurs, investigate it as an environment issue.
2. Preserve the successful 2026-09-24 controlled recorded-file regression log: video opened (reported source FPS 30.18), auto-calibration accepted 30 valid frames (sample range 0.0911), end of source reached, and clean shutdown. Re-run only if code or dependencies change.
3. Preserve the eight passing deterministic M7 tests; confirm invalid body geometry does not break the integrated facial pipeline.
4. Review implementation/validation documentation and `git diff`; keep private videos, screenshots and derived CSVs outside version control.
5. Commit the reviewed code and documentation, create the milestone pull request, and merge after the release checks.

After M7, the planned path proceeds to Milestone 8 (hand activity analysis). Longer-term improvements include lateral/sagittal decoupling, calibrated posture geometry and annotated multi-person evaluation. None of these are claimed to be solved in M7.
