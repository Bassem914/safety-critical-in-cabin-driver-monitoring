# Path 1 — Milestone 3: Facial Geometry Features

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 3 |
| Status | Completed |
| Date | 2026-07-06 |
| Author | Bassem Soliman |
| Repository | safety-critical-in-cabin-driver-monitoring |

---

# 1. Objective

The objective of this milestone is to extend the MediaPipe Face Mesh landmark pipeline by extracting interpretable facial geometry features from selected face landmarks.

This milestone introduces:

- Eye Aspect Ratio (EAR)
- Mouth Aspect Ratio (MAR)

These features provide the first measurable driver-monitoring signals for future drowsiness and yawning analysis.

---

# 2. Motivation

Milestone 2 successfully detected facial landmarks, but landmarks alone are not yet driver-state features.

A Driver Monitoring System requires measurable signals that describe driver behavior. Eye openness and mouth openness are two important early indicators for safety-critical cabin perception.

EAR provides a simple geometric estimate of eye openness.

MAR provides a simple geometric estimate of mouth openness.

These features will later support:

- blink detection
- prolonged eye closure detection
- yawning detection
- fatigue estimation
- temporal safety reasoning

This milestone does not yet classify the driver as drowsy or yawning. It only extracts the required geometric measurements.

---

# 3. Software Perspective

This milestone extends the existing modular perception architecture.

Updated modules:

- `src/main.py`
- `src/perception/face_features.py`
- `src/perception/visualization.py`

The implementation keeps detection and feature extraction separated.

`FaceMeshDetector` remains responsible for landmark detection.

`FacialGeometryExtractor` is introduced to compute EAR and MAR from selected landmark coordinates.

This separation improves maintainability and prepares the system for future perception modules such as head pose estimation and gaze estimation.

---

# 4. Computer Vision Perspective

The computer vision pipeline is extended from landmark detection to geometric feature extraction.

Current pipeline:

Camera

↓

OpenCV Frame Acquisition

↓

MediaPipe Face Mesh

↓

Selected Facial Landmarks

↓

Facial Geometry Feature Extraction

↓

EAR / MAR Visualization

EAR is computed using the ratio between vertical eye opening and horizontal eye width.

MAR is computed using the ratio between vertical mouth opening and horizontal mouth width.

The method uses 2D pixel coordinates derived from MediaPipe normalized landmark coordinates.

---

# 5. Python Perspective

This milestone introduces the `FacialGeometryExtractor` class.

The class contains:

- Euclidean distance computation
- left eye EAR computation
- right eye EAR computation
- average EAR computation
- MAR computation

The implementation uses:

- Python dictionaries for named landmarks
- type hints for readability
- NumPy for Euclidean distance computation
- modular class-based design

The main loop remains simple and only orchestrates camera input, landmark detection, feature extraction, visualization, and clean shutdown.

---

# 6. Engineering Perspective

This milestone introduces the first feature extraction layer of the Driver Monitoring System.

The key engineering decision is to avoid directly classifying driver state from a single frame.

EAR and MAR are treated as measurements, not final safety decisions.

This is important because safety-relevant decisions require temporal reasoning. For example, one low EAR value may simply represent a blink, while sustained low EAR over time may indicate drowsiness.

Therefore, this milestone intentionally stops at feature extraction.

Temporal reasoning is deferred to the next milestone.

---

# 7. Implemented Components

## `src/perception/face_features.py`

Implemented:

- additional eye landmarks
- additional mouth landmarks
- `FacialGeometryExtractor`
- Euclidean distance helper
- EAR computation
- MAR computation

## `src/perception/visualization.py`

Updated:

- EAR overlay
- MAR overlay
- fallback display when no face is detected

## `src/main.py`

Updated:

- initializes `FacialGeometryExtractor`
- computes EAR and MAR when face landmarks are detected
- passes feature values to visualization overlay

---

# 8. Project Architecture Impact

This milestone adds the feature extraction layer.

Previous architecture:

Camera

↓

Image Acquisition

↓

Face Landmark Detection

↓

Visualization

Updated architecture:

Camera

↓

Image Acquisition

↓

Face Landmark Detection

↓

Facial Geometry Feature Extraction

↓

EAR / MAR Feature Visualization

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

## Inputs

`FacialGeometryExtractor` receives:

- selected facial landmarks as pixel coordinates

Example:

- `left_eye_outer`
- `left_eye_inner`
- `left_eye_upper`
- `left_eye_lower`
- `right_eye_outer`
- `right_eye_inner`
- `right_eye_upper`
- `right_eye_lower`
- `mouth_left`
- `mouth_right`
- `upper_lip`
- `lower_lip`

## Outputs

The extractor returns a dictionary containing:

- `left_ear`
- `right_ear`
- `ear`
- `mar`

## Dependencies

- OpenCV
- MediaPipe
- NumPy

## Consumers

The output features are consumed by:

- `main.py`
- visualization overlay
- future temporal decision logic

---

# 10. Validation Summary

Manual validation was performed using the webcam.

The following behavior was verified:

- EAR decreases when eyes close
- MAR increases when mouth opens
- EAR and MAR are displayed in real time
- face loss results in `EAR: N/A` and `MAR: N/A`
- the application exits cleanly using `q`

Validation details are documented in:

`docs/validation/path_01_milestone_03_facial_geometry_features_validation.md`

Validation evidence:

`paths/01_fast_prototype/outputs/figures/path_01_milestone_03_facial_geometry_features.png`

---

# 11. Limitations

Current limitations:

- no temporal analysis
- no drowsiness classification
- no yawning classification
- no calibrated thresholds
- no driver-specific baseline
- no head pose compensation
- RGB webcam only
- sensitive to lighting and face orientation

These limitations are expected at this stage.

---

# 12. Future Scalability

This milestone enables the next stage of driver-state reasoning.

Future milestones can use EAR and MAR for:

- blink duration analysis
- prolonged eye closure detection
- yawning candidate detection
- temporal safety logic
- drowsiness candidate state
- unresponsive driver candidate state

The current architecture also allows later replacement of the landmark backend with OpenFace, 3DDFA, RTMPose, or another model while preserving the feature extraction interface.

---

# 13. Research / Technology Notes

EAR and MAR are classical geometry-based computer vision features.

They are useful in early prototypes because they are:

- interpretable
- lightweight
- fast
- easy to visualize
- suitable for real-time experimentation

However, they are not sufficient alone for a safety-critical production system.

A robust Driver Monitoring System should combine geometric features with temporal reasoning, head pose, gaze estimation, body posture, and validation on real cabin datasets.

---

# 14. Lessons Learned

This milestone showed that landmark detection becomes much more useful when converted into interpretable geometric features.

It also reinforced the importance of separating perception detection from feature extraction.

The implementation is now closer to a real Driver Monitoring pipeline because it produces meaningful measurements instead of only visual landmarks.

---

# 15. Next Milestone

The next milestone is:

**Path 1 — Milestone 4: Temporal Safety Logic**

The goal will be to analyze EAR, MAR, and face visibility over time.

This will allow the system to distinguish short events such as blinks from safety-relevant states such as prolonged eye closure or sustained mouth opening.

---

# Milestone Completion Checklist

- [x] Software implementation completed
- [x] Computer vision functionality verified
- [x] Validation completed
- [x] Documentation completed
- [x] Git commit completed
- [x] GitHub updated
- [x] Ready for next milestone