# Path 1 — Milestone 2: MediaPipe Face Mesh Landmark Pipeline

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 2 |
| Status | Completed |
| Date | 2026-07-06 |
| Author | Bassem Soliman |
| Repository | safety-critical-in-cabin-driver-monitoring |

---

# 1. Objective

The objective of this milestone is to extend the initial webcam acquisition prototype by introducing real-time facial landmark detection using the MediaPipe Face Mesh framework.

This milestone establishes the first perception layer capable of extracting stable facial geometry from a live RGB camera stream. The extracted landmarks provide the foundation for future driver monitoring features such as eye aspect ratio (EAR), mouth aspect ratio (MAR), head pose estimation, gaze estimation, distraction detection, and drowsiness analysis.

---

# 2. Motivation

The webcam smoke test completed in Milestone 1 verified camera access and frame acquisition but did not extract any semantic information from the driver.

A Driver Monitoring System requires structured facial information rather than raw image frames. Facial landmarks provide a compact geometric representation of the driver's face while remaining computationally efficient for real-time applications.

Introducing MediaPipe Face Mesh at this stage enables subsequent milestones to build feature extraction algorithms without redesigning the perception pipeline.

---

# 3. Software Perspective

This milestone introduces the first modular perception architecture.

The implementation separates responsibilities into dedicated modules:

- `main.py` orchestrates the complete perception pipeline.
- `face_features.py` manages MediaPipe Face Mesh initialization and landmark extraction.
- `visualization.py` provides reusable visualization utilities.

The implementation intentionally avoids embedding perception logic inside `main.py`, improving maintainability and supporting future extension.

---

# 4. Computer Vision Perspective

The perception pipeline operates as follows:

RGB Camera

↓

OpenCV Frame Acquisition

↓

BGR → RGB Conversion

↓

MediaPipe Face Mesh

↓

468 Facial Landmarks

↓

Selection of Driver Monitoring landmarks

↓

Pixel Coordinate Conversion

↓

Visualization

Only a subset of facial landmarks is currently extracted because these points are sufficient for future computation of EAR, MAR, and head pose while reducing unnecessary complexity.

---

# 5. Python Perspective

The implementation follows a modular object-oriented structure.

The `FaceMeshDetector` class encapsulates MediaPipe initialization, inference, and resource management.

Utility functions are isolated inside `visualization.py`, avoiding duplicated drawing code and simplifying future modifications.

Type hints are used throughout the implementation to improve readability and maintainability.

---

# 6. Engineering Perspective

The milestone emphasizes software modularity over rapid prototyping.

Rather than implementing all functionality in a single script, perception and visualization are separated into reusable modules.

This organization minimizes coupling between software components and allows future milestones to replace the perception backend without affecting visualization or higher-level decision logic.

---

# 7. Implemented Components

Implemented modules:

- `src/main.py`
- `src/perception/face_features.py`
- `src/perception/visualization.py`

Responsibilities:

- camera acquisition
- MediaPipe initialization
- landmark extraction
- normalized-to-pixel conversion
- visualization
- runtime overlay

---

# 8. Project Architecture Impact

This milestone implements the perception stage of the Driver Monitoring pipeline.

Current architecture:

Camera

↓

Image Acquisition

↓

Face Landmark Detection

↓

Visualization

Future architecture:

Camera

↓

Image Acquisition

↓

Face Landmark Detection

↓

Feature Extraction

↓

Temporal Analysis

↓

Safety Decision Layer

↓

Driver State Estimation

---

# 9. System Interfaces

### Inputs

- RGB camera frames

### Outputs

- selected facial landmark coordinates
- visualization overlay

### Dependencies

- OpenCV
- MediaPipe

### Consumers

Future milestones:

- EAR computation
- MAR computation
- Head Pose Estimation
- Gaze Estimation
- Driver State Estimation

---

# 10. Validation Summary

The implementation was successfully validated using a standard webcam.

The system maintained real-time performance while correctly detecting the driver's face and visualizing the selected landmarks.

Validation details are documented in:

`docs/validation/path_01_milestone_02_mediapipe_face_mesh_landmark_pipeline_validation.md`

---

# 11. Limitations

Current limitations include:

- RGB camera only
- no temporal analysis
- no EAR
- no MAR
- no head pose estimation
- no gaze estimation
- no driver state classification

These limitations are intentional and will be addressed incrementally.

---

# 12. Future Scalability

The current implementation provides the perception backbone for future Driver Monitoring functionality.

Planned extensions include:

- Eye Aspect Ratio (EAR)
- Mouth Aspect Ratio (MAR)
- Head Pose Estimation
- Gaze Estimation
- Driver Attention Monitoring
- Drowsiness Detection
- Temporal Safety Logic

---

# 13. Research / Technology Notes

MediaPipe Face Mesh was selected because it provides robust real-time landmark estimation with minimal computational overhead.

The project uses:

- Python 3.11
- MediaPipe 0.10.21
- OpenCV

MediaPipe was pinned to version `0.10.21` because newer releases modified parts of the Solutions API used by this milestone.

---

# 14. Lessons Learned

This milestone demonstrated the importance of modular software architecture during perception pipeline development.

Separating acquisition, perception, and visualization simplifies future feature extraction and reduces implementation complexity.

Dependency management also proved critical for reproducible computer vision experiments.

---

# 15. Next Milestone

The next milestone will introduce facial geometry feature extraction, beginning with Eye Aspect Ratio (EAR) and Mouth Aspect Ratio (MAR), enabling the first safety-relevant driver state indicators.

---

# Milestone Completion Checklist

- [x] Software implementation completed
- [x] Computer vision functionality verified
- [x] Validation completed
- [x] Documentation completed
- [x] Git commit completed
- [x] GitHub updated
- [x] Ready for next milestone