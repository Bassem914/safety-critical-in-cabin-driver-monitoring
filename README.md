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

`paths/01_fast_prototype/`

---

# Project Progress

Current Stage

**Path 1 – Fast Prototype**

Progress

**2 / 10 planned milestones completed (20%)**

### Completed

- ✅ Milestone 1 — OpenCV Webcam Smoke Test
- ✅ Milestone 2 — MediaPipe Face Mesh Landmark Pipeline

### Current

- 🚧 Milestone 3 — Facial Geometry Feature Extraction (EAR & MAR)

---

# Current Implementation Status

| Path | Milestone | Status | Description |
|------|-----------|--------|-------------|
| Path 1 — Fast Prototype | Milestone 1 | ✅ Completed | OpenCV webcam smoke test with FPS overlay and clean shutdown |
| Path 1 — Fast Prototype | Milestone 2 | ✅ Completed | MediaPipe Face Mesh landmark pipeline with modular perception architecture |
| Path 1 — Fast Prototype | Milestone 3 | ✅ Completed | Eye Aspect Ratio (EAR) and Mouth Aspect Ratio (MAR) feature extraction |

---

# Implemented Features

## Milestone 1

- Webcam acquisition
- FPS computation
- Camera validation
- Clean application shutdown

## Milestone 2

- MediaPipe Face Mesh integration
- Facial landmark extraction
- Landmark visualization
- Modular perception architecture
- Validation framework
- Documentation framework

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

Next Milestone

---

# Roadmap

## Completed

- ✅ Webcam Smoke Test
- ✅ MediaPipe Face Mesh Landmark Pipeline

## In Progress

- 🚧 Facial Geometry Feature Extraction (EAR & MAR)

## Planned

- Head Pose Estimation
- Gaze Estimation
- Body Pose Analysis
- Hand Tracking
- Driver State Estimation
- Temporal Decision Layer
- Safety-Critical Driver Monitoring Pipeline
