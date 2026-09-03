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

- ✅ 6 milestones completed
- 🚧 Milestone 6 in preparation

Completed milestones currently include:

- Milestone 1
- Milestone 2
- Milestone 3
- Milestone 4A
- Milestone 4B
- Milestone 5

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
| Milestone 6 | 🔜 Next | Gaze estimation |
| Milestone 7 | Planned | Body pose and posture analysis |
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

Next milestone:

**Path 1 — Milestone 6: Gaze Estimation**

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
- real-time temporal-state visualization
- real-time head-pose visualization
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
Selected Facial Landmarks
        ┌───────────────┴───────────────┐
        ↓                               ↓
EAR / MAR Feature Extraction      Head Pose Estimation
        ↓                               ↓
Temporal Rule Engine              Yaw / Pitch / Roll
        └───────────────┬───────────────┘
                        ↓
              State / Pose Visualization
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

decision/temporal_rules.py
    timestamp-based temporal candidates

perception/visualization.py
    state and measurement visualization

main.py
    pipeline orchestration
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

## Next

- 🔜 Gaze Estimation

## Planned

- Body Pose and Posture Analysis
- Hand Activity Analysis
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
- no final gaze estimation yet
- no behavioral distraction classification yet
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

The next planned milestone is:

**Path 1 — Milestone 6: Gaze Estimation**

The objective will be to extend the current perception stack from:

```text
Where is the driver's head oriented?
```

toward:

```text
Where are the driver's eyes / visual attention directed?
```

Head pose will remain an independent geometric signal and will later provide context for gaze and attention reasoning.

Behavioral distraction classification will remain separate until sufficient temporal and multimodal evidence is available.
