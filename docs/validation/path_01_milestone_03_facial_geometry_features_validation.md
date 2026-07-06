# Path 1 — Milestone 3 Validation: Facial Geometry Features

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 3 |
| Validation Date | 2026-07-06 |
| Status | Passed |
| Author | Bassem Soliman |
| Python | 3.11.7 |
| OpenCV | Installed via requirements.txt |
| MediaPipe | 0.10.21 |
| Operating System | Windows 11 |
| Camera | Integrated RGB Webcam |

---

# 1. Validation Objective

The objective of this validation is to verify that the system correctly computes and displays facial geometry features from MediaPipe Face Mesh landmarks.

The validation focuses on:

- Eye Aspect Ratio behavior
- Mouth Aspect Ratio behavior
- real-time overlay display
- stability during normal head movement
- graceful handling of face loss

---

# 2. Test Environment

## Hardware

- Laptop or workstation
- Integrated RGB webcam

## Software

- Windows 11
- Python 3.11.7
- OpenCV
- MediaPipe 0.10.21
- NumPy

## Camera

- Default webcam
- Camera index: 0

## Lighting

- Normal indoor lighting

---

# 3. Test Configuration

The validation was performed using live webcam input.

Configuration:

- face positioned approximately in front of the camera
- normal indoor lighting
- no external IR or NIR camera
- no additional preprocessing
- visualization overlay enabled

Displayed values:

- FPS
- driver face status
- tracked landmark count
- EAR
- MAR

---

# 4. Test Cases

| Test Case | Expected Result | Actual Result | Status |
|------------|----------------|---------------|--------|
| Webcam initialization | Camera opens successfully | Camera opened successfully | ✅ Pass |
| Face visible | Driver Face: DETECTED | Correct | ✅ Pass |
| EAR display | EAR value appears on overlay | Correct | ✅ Pass |
| MAR display | MAR value appears on overlay | Correct | ✅ Pass |
| Eyes closed | EAR decreases noticeably | Correct | ✅ Pass |
| Mouth opened | MAR increases noticeably | Correct | ✅ Pass |
| Normal head movement | EAR/MAR remain reasonably stable | Correct | ✅ Pass |
| Face leaves image | EAR/MAR show unavailable state | Correct | ✅ Pass |
| Program exit | Pressing `q` closes application cleanly | Correct | ✅ Pass |

---

# 5. Results

The facial geometry feature pipeline operated successfully.

Observed behavior:

- EAR was displayed in real time.
- EAR decreased when the eyes were closed.
- MAR was displayed in real time.
- MAR increased when the mouth was opened.
- Face loss was handled correctly.
- Runtime remained real-time.
- Application shutdown was clean.

The system is considered ready for temporal reasoning in the next milestone.

---

# 6. Performance Summary

| Metric | Observation |
|---------|-------------|
| Runtime | Real-time |
| FPS | Approximately webcam real-time performance |
| EAR behavior | Correct trend |
| MAR behavior | Correct trend |
| Face-loss handling | Correct |
| Stability | Acceptable for prototype |

No formal latency or CPU benchmark was performed in this milestone.

---

# 7. Evidence

Validation evidence is stored in:

```text
paths/01_fast_prototype/outputs/figures/
```

Evidence file:

```text
path_01_milestone_03_facial_geometry_features.png
```

---

# 8. Known Issues

## Issue 1 — No temporal interpretation

EAR and MAR are currently single-frame measurements.

### Possible Cause

Temporal logic has not yet been implemented.

### Temporary Workaround

Interpret EAR and MAR only as debug feature values.

### Future Improvement

Add temporal state tracking in Milestone 4.

---

## Issue 2 — No calibrated thresholds

The system does not yet define final thresholds for drowsiness or yawning.

### Possible Cause

Thresholds require validation over multiple users, lighting conditions, and camera positions.

### Temporary Workaround

Use EAR and MAR qualitatively during development.

### Future Improvement

Add configurable thresholds and temporal filtering.

---

## Issue 3 — Head pose may affect geometry values

EAR and MAR may change when the face rotates away from the camera.

### Possible Cause

The current implementation uses 2D image-space geometry.

### Temporary Workaround

Validate primarily with frontal or near-frontal face orientation.

### Future Improvement

Add head pose estimation and compensate or gate feature interpretation based on pose.

---

# 9. Engineering Assessment

The milestone successfully converts raw facial landmarks into meaningful perception features.

Strengths:

- simple and interpretable feature extraction
- real-time operation
- modular feature extractor
- clear separation between detection and geometry computation
- ready for temporal logic

Limitations:

- no time-based reasoning yet
- no safety-state decision
- no user calibration
- no dataset-based evaluation

Overall assessment:

**Path 1 — Milestone 3 passed validation and is ready to support temporal safety logic in Milestone 4.**

---

# 10. Recommendations

## Immediate Improvements

- Preserve the current modular architecture.
- Use EAR and MAR as feature measurements only.
- Avoid single-frame driver-state classification.

## Future Improvements

- Add temporal thresholds.
- Add smoothing or moving averages.
- Add configurable threshold values.
- Add validation on recorded videos.
- Add head pose estimation before interpreting distraction states.

---

# 11. Next Validation

The next validation will focus on temporal safety logic.

Milestone 4 validation should include:

- short blink versus prolonged eye closure
- short mouth opening versus sustained mouth opening
- face present versus face lost over time
- time-based warning state activation
- false-positive behavior during normal movement

---

# Validation Completion Checklist

- [x] Validation executed
- [x] Test cases completed
- [x] Results documented
- [x] Evidence stored
- [x] Known issues documented
- [x] Engineering assessment completed
- [x] Git commit completed
- [x] GitHub updated
- [x] Ready for next milestone