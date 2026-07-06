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
| Path 1 — Fast Prototype | Milestone 1 | ✅ Completed | OpenCV webcam smoke test with FPS overlay and clean shutdown |
| Path 1 — Fast Prototype | Milestone 2 | ✅ Completed | MediaPipe Face Mesh landmark pipeline with modular perception architecture |
| Path 1 — Fast Prototype | Milestone 3 | ✅ Completed | Facial geometry feature extraction using EAR and MAR |
| Path 1 — Fast Prototype | Milestone 4 | 🚧 Next | Temporal safety logic for eye closure, mouth opening, and face loss |

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
