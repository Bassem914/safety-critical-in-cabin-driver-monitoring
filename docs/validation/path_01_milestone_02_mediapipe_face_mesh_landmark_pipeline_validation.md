# Path 1 — Milestone 2 Validation: MediaPipe Face Mesh Landmark Pipeline

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 2 |
| Validation Date | 2026-07-06 |
| Status | Passed |
| Author | Bassem Soliman |
| Repository | safety-critical-in-cabin-driver-monitoring |
| Operating System | Windows 11 |
| Python | 3.11.7 |
| OpenCV | Installed via requirements.txt |
| MediaPipe | 0.10.21 |
| Camera | Integrated RGB Webcam |

---

# 1. Validation Objective

The objective of this validation is to verify that the MediaPipe Face Mesh landmark pipeline operates correctly under real-time conditions using a standard RGB webcam.

The validation focuses on confirming that the perception pipeline can reliably detect the driver's face, extract the selected facial landmarks, maintain stable real-time performance, and provide the expected visualization overlay.

---

# 2. Test Environment

## Hardware

- Laptop with integrated RGB webcam
- Standard office workstation

## Software

- Windows 11
- Python 3.11.7
- OpenCV
- MediaPipe 0.10.21

## Lighting

Normal indoor office lighting.

## Camera

Default integrated webcam.

---

# 3. Test Configuration

Camera configuration:

- Camera Index: 0
- Live RGB webcam input
- Approximate operating distance: 40–80 cm
- Frontal driver position
- Normal office illumination
- No additional preprocessing

Visualization enabled:

- Landmark points
- FPS overlay
- Driver face status
- Landmark count

---

# 4. Test Cases

| Test Case | Expected Result | Actual Result | Status |
|------------|----------------|---------------|--------|
| Webcam initialization | Camera opens successfully | Camera opened | ✅ Pass |
| Face visible | Driver Face: DETECTED | Correct | ✅ Pass |
| Face leaves image | Driver Face: LOST | Correct | ✅ Pass |
| Landmark extraction | Selected landmarks displayed | Correct | ✅ Pass |
| Landmark tracking | Landmarks follow head movement | Correct | ✅ Pass |
| FPS display | Real-time FPS shown | Correct | ✅ Pass |
| Runtime stability | Continuous execution | Stable | ✅ Pass |
| Program exit | Pressing **q** closes application cleanly | Correct | ✅ Pass |

---

# 5. Results

The MediaPipe Face Mesh pipeline operated successfully throughout the validation.

Observed behavior:

- Stable face detection
- Consistent landmark tracking
- Smooth visualization
- Real-time performance
- Clean application shutdown

Observed runtime:

Approximately **30–33 FPS** on the development laptop.

No significant tracking instability was observed during normal frontal head movements.

---

# 6. Performance Summary

| Metric | Observation |
|---------|-------------|
| Average FPS | ~30–33 FPS |
| Face Detection | Stable |
| Landmark Stability | High |
| Runtime | Real-time |
| CPU Usage | Acceptable for prototype |
| Memory Usage | Not formally measured |

The achieved frame rate is sufficient for the next development milestones.

---

# 7. Evidence

Validation evidence is stored in:

```text
paths/01_fast_prototype/outputs/
```

Available evidence:

## Figures

- `path_01_milestone_02_face_mesh_pipeline.png`

Future milestones may also include:

- validation videos
- benchmark tables
- runtime logs

---

# 8. Known Issues

## Issue 1

Landmark labels overlapped during the initial implementation.

### Resolution

Visualization was redesigned to display landmark points only.

Text labels remain available for future debugging if required.

---

## Issue 2

MediaPipe 0.10.35 produced an API compatibility issue because the project relies on the classic MediaPipe Solutions API.

### Resolution

The dependency was pinned to:

```text
mediapipe==0.10.21
```

This restored compatibility and improved reproducibility.

---

# 9. Engineering Assessment

This milestone successfully establishes the first perception component of the Driver Monitoring System.

Strengths:

- Modular software structure
- Clean separation of perception and visualization
- Stable real-time performance
- Maintainable implementation
- Reproducible dependency management

Limitations:

- RGB camera only
- No temporal processing
- No driver state estimation
- No facial feature computation yet

Overall Assessment:

**Milestone 2 is considered complete and provides a stable foundation for feature extraction in subsequent milestones.**

---

# 10. Recommendations

## Immediate

- Preserve current implementation.
- Keep MediaPipe pinned to version 0.10.21.
- Continue using the modular perception architecture.

## Future

Implement:

- Eye Aspect Ratio (EAR)
- Mouth Aspect Ratio (MAR)
- Head Pose Estimation
- Gaze Estimation
- Temporal safety logic

---

# 11. Next Validation

The next validation will verify the correctness of facial geometry feature extraction.

Validation will include:

- EAR stability
- MAR stability
- Blink detection
- Mouth opening detection
- Landmark consistency during head movement

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