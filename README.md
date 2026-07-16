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

- ✅ 3 milestones completed
- 🚧 Milestone 4 in preparation

---

# Current Implementation Status

| Path | Milestone | Status | Description |
|------|-----------|--------|-------------|
| Path 1 | Milestone 1 | ✅ Completed | Webcam smoke test |
| Path 1 | Milestone 2 | ✅ Completed | MediaPipe Face Mesh |
| Path 1 | Milestone 3 | ✅ Completed | Facial geometry features: EAR and MAR |
| Path 1 | Milestone 4A | ✅ Completed | Source-independent webcam and recorded-video input |
| Path 1 | Milestone 4B | 🔜 Next | Face-level temporal state baseline |

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

## In Progress

- 🚧 Temporal Safety Logic

## Planned

- Head Pose Estimation
- Gaze Estimation
- Body Pose Analysis
- Hand Tracking
- Driver State Estimation
- Safety-Critical Driver Monitoring Pipeline

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
