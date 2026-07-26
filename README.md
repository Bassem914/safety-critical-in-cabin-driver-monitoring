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

- ✅ 4 milestones completed
- 🚧 Milestone 5 in preparation

---

# Current Implementation Status

| Milestone | Status | Description |
|-----------|--------|-------------|
| Milestone 1 | ✅ Completed | Webcam smoke test |
| Milestone 2 | ✅ Completed | MediaPipe Face Mesh landmark pipeline |
| Milestone 3 | ✅ Completed | Facial geometry features: EAR and MAR |
| Milestone 4A | ✅ Completed | Source-independent webcam and recorded-video input |
| Milestone 4B | ✅ Completed | Face-level temporal state baseline |
| Milestone 5 | 🔜 Next | Head pose estimation |
| Milestone 6 | Planned | Gaze estimation |
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

## Milestone 2 — MediaPipe Face Mesh Landmark Pipeline

- MediaPipe Face Mesh integration
- Facial landmark extraction
- Landmark visualization
- Modular perception architecture
- Validation framework
- Documentation framework

## Milestone 3 — Facial Geometry Features

- Eye Aspect Ratio (EAR)
- Mouth Aspect Ratio (MAR)
- Real-time feature overlay
- Modular facial geometry extractor
- Feature-level validation

---
## Milestone 4A: Source-Independent Video Input

The perception pipeline now supports both live webcam input and local recorded-video input through a common acquisition interface.

Implemented capabilities:

- abstract `VideoSource` interface
- `WebcamVideoSource`
- `FileVideoSource`
- timestamped `FramePacket`
- source frame indexing
- optional webcam mirroring
- shared Face Mesh and EAR/MAR processing pipeline
- private dataset and video-file protection

### Path 1 — Milestone 4B: Face-Level Temporal State Baseline

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

Validation evidence currently includes a locally stored annotated output video and screenshots containing all temporal states. Public evidence will be added after privacy and dataset-redistribution review.

Documentation:

- [Implementation](docs/implementation/path_01_milestone_04B_face_temporal_state_baseline.md)
- [Validation](docs/validation/path_01_milestone_04B_face_temporal_state_baseline_validation.md)

Next milestone:

**Path 1 — Milestone 5: Head Pose Estimation**
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
- real-time state visualization
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
                ↓
EAR / MAR Feature Extraction
                ↓
Temporal Rule Engine
                ↓
Face-Level Temporal Candidates
                ↓
State and Measurement Visualization
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
Git Review
    ↓
Commit
    ↓
Pull Request
    ↓
Merge
    ↓
README Update
    ↓
Next Milestone
```

---

# Roadmap

## Completed

- ✅ Webcam Smoke Test
- ✅ MediaPipe Face Mesh Landmark Pipeline
- ✅ Facial Geometry Feature Extraction
- ✅ Source-Independent Video Input
- ✅ Face-Level Temporal State Baseline

## Next

- 🔜 Head Pose Estimation

## Planned

- Gaze Estimation
- Body Pose Analysis
- Hand Tracking
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

---

# Project Purpose

This project is designed as a research and engineering portfolio for:

- Driver Monitoring Systems
- In-cabin sensing
- Safety-critical perception
- Autonomous Driving / ADAS
- PhD and research preparation
