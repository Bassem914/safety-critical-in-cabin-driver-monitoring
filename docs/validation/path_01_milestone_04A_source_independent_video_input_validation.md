# Path 1 — Milestone 4A Validation: Source-Independent Video Input

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 4A |
| Validation Date | 2026-07-16 |
| Status | Passed |
| Author | Bassem Soliman |
| Python | 3.11.7 |
| OpenCV | Installed via requirements.txt |
| MediaPipe | 0.10.21 |
| Operating System | Windows 11 |
| Live Camera | Integrated RGB Webcam |
| Recorded Input | Local MP4 video |
| Dataset Sample | DMD face-camera sample |

---

# 1. Validation Objective

The objective of this validation is to verify that the perception pipeline can operate independently of the selected video input source.

The validation focuses on:

- live webcam input
- mirrored webcam input
- local video-file input
- DMD sample-video input
- source frame indexing
- source timestamp behavior
- shared perception processing
- command-line source selection
- invalid-input handling
- clean resource release

The validation also verifies that the previously implemented Face Mesh, EAR and MAR functionality remains operational after introducing the acquisition abstraction.

---

# 2. Test Environment

## Hardware

- Laptop or workstation
- Integrated RGB webcam
- Local storage for recorded videos

## Software

- Windows 11
- Python 3.11.7
- OpenCV
- MediaPipe 0.10.21
- NumPy
- Git Bash
- Visual Studio Code

## Live Camera

- Integrated RGB webcam
- Camera index: 0

## Recorded Video

- Local MP4 video
- DMD face-camera sample stored locally
- Dataset video excluded from Git tracking

## Lighting

- Normal indoor lighting for webcam validation
- Recorded lighting conditions for local video input

---

# 3. Test Configuration

The validation was performed using the source-independent command-line interface.

Supported source types:

```text
webcam
file
```

The shared perception pipeline included:

- OpenCV frame acquisition
- optional horizontal mirroring
- BGR-to-RGB conversion
- MediaPipe Face Mesh
- selected landmark extraction
- EAR computation
- MAR computation
- source metadata visualization
- clean resource release

Displayed values:

- processing FPS
- driver face status
- tracked landmark count
- EAR
- MAR
- source timestamp
- frame index
- source name

---

# 4. Validation Commands

## Webcam input

```bash
python src/main.py --source webcam --camera-index 0
```

## Mirrored webcam input

```bash
python src/main.py --source webcam --camera-index 0 --mirror
```

## Local file input

```bash
python src/main.py \
  --source file \
  --video-path "/path/to/video.mp4"
```

## DMD sample input

```bash
python src/main.py \
  --source file \
  --video-path "/d/Cabin_sensing/practical/safety-critical-in-cabin-driver-monitoring/data/private/sample_DMD_face.mp4"
```

## Missing file-path test

```bash
python src/main.py --source file
```

## Invalid file-path test

```bash
python src/main.py \
  --source file \
  --video-path "/invalid/path/video.mp4"
```

---

# 5. Test Cases

| Test Case | Expected Result | Actual Result | Status |
|------------|----------------|---------------|--------|
| Source-independent compilation | All source files compile successfully | Compilation completed successfully | ✅ Pass |
| Webcam initialization | Camera opens successfully | Camera opened successfully | ✅ Pass |
| Webcam frame acquisition | Live frames are acquired continuously | Correct | ✅ Pass |
| Webcam source name | Webcam identifier is displayed | Correct | ✅ Pass |
| Webcam frame index | Frame index increases sequentially | Correct | ✅ Pass |
| Webcam source time | Elapsed source time increases monotonically | Correct | ✅ Pass |
| Webcam Face Mesh | Facial landmarks are detected | Correct | ✅ Pass |
| Webcam EAR display | EAR remains available when the face is detected | Correct | ✅ Pass |
| Webcam MAR display | MAR remains available when the face is detected | Correct | ✅ Pass |
| Mirrored webcam | Frame is horizontally flipped only when requested | Correct | ✅ Pass |
| Non-mirrored webcam | Original left-right orientation is preserved | Correct | ✅ Pass |
| Local video initialization | MP4 file opens successfully | Correct | ✅ Pass |
| Local video frame acquisition | Recorded frames are processed sequentially | Correct | ✅ Pass |
| Local video frame index | Frame index increases sequentially | Correct | ✅ Pass |
| Local video source time | Timestamp follows the video source timeline | Correct | ✅ Pass |
| Local video Face Mesh | Facial landmarks are detected in recorded frames | Correct | ✅ Pass |
| Local video EAR/MAR | Geometry features remain operational | Correct | ✅ Pass |
| DMD sample input | DMD sample is processed by the shared pipeline | Correct | ✅ Pass |
| Shared pipeline behavior | Webcam and file input use the same perception loop | Correct | ✅ Pass |
| Missing `--video-path` | Clear error message is printed | Correct | ✅ Pass |
| Invalid video path | Source-open failure is handled | Correct | ✅ Pass |
| End of local video | Pipeline stops without crashing | Correct | ✅ Pass |
| User-requested exit | Pressing `q` closes the application cleanly | Correct | ✅ Pass |
| Resource release | Camera/video and OpenCV windows are released | Correct | ✅ Pass |
| Private-data protection | Dataset and local media files remain ignored | Correct | ✅ Pass |

---

# 6. Results

The source-independent acquisition pipeline operated successfully.

Observed behavior:

- The webcam source opened correctly.
- The local MP4 source opened correctly.
- The DMD face-camera sample was processed successfully.
- The same Face Mesh and facial-geometry pipeline operated for both source types.
- Source frame indices increased sequentially.
- Webcam timestamps increased using monotonic elapsed time.
- File-video timestamps followed the recorded source timeline.
- EAR and MAR remained operational.
- Mirroring was applied only when explicitly requested.
- Non-mirrored video preserved original left-right semantics.
- Missing and invalid video paths were handled without an unhandled exception.
- End-of-video behavior did not crash the pipeline.
- Application shutdown was clean.
- Dataset media remained local and excluded from Git tracking.

The system is considered ready for face-level temporal analysis in Milestone 4B.

---

# 7. Performance Summary

| Metric | Observation |
|---------|-------------|
| Webcam runtime | Real-time |
| Recorded-video runtime | Near real-time or processing-dependent |
| Face Mesh functionality | Preserved |
| EAR behavior | Preserved |
| MAR behavior | Preserved |
| Source frame indexing | Correct |
| Webcam timestamp behavior | Correct |
| File timestamp behavior | Correct |
| Source switching | Correct |
| Mirroring behavior | Correct |
| Invalid-input handling | Correct |
| Resource cleanup | Correct |
| Stability | Acceptable for prototype |

No formal CPU, GPU, memory or latency benchmark was performed in this milestone.

The displayed processing FPS is not interpreted as the source timeline.

Temporal decisions in future milestones should use:

```text
frame_packet.timestamp_seconds
```

rather than processing-loop duration.

---

# 8. Source Timing Validation

## Webcam Timing

Webcam timestamps are generated using:

```python
perf_counter()
```

relative to the beginning of the acquisition session.

Expected behavior:

- timestamp starts near zero
- timestamp increases monotonically
- timestamp is independent of wall-clock changes
- timestamp represents live elapsed time

Observed behavior:

- timestamp increased continuously
- no backward jumps were observed
- the behavior was suitable for live temporal reasoning

Status:

```text
Passed
```

---

## File-Video Timing

File-video timestamps are read using:

```python
cv2.CAP_PROP_POS_MSEC
```

When unavailable, the fallback is:

```text
frame_index / source_fps
```

Expected behavior:

- timestamp follows the recorded video timeline
- repeated execution produces the same approximate timeline
- timestamp does not depend on processing speed

Observed behavior:

- source time increased during playback
- timing remained associated with the recorded file
- processing speed did not define the source timeline

Status:

```text
Passed
```

---

# 9. Mirroring Validation

The mirroring option was tested using live webcam input.

## Mirroring Disabled

Command:

```bash
python src/main.py --source webcam --camera-index 0
```

Expected behavior:

- original camera orientation is preserved
- no horizontal flip is applied

Observed behavior:

- source orientation remained unchanged

Status:

```text
Passed
```

---

## Mirroring Enabled

Command:

```bash
python src/main.py --source webcam --camera-index 0 --mirror
```

Expected behavior:

- frame is horizontally flipped
- Face Mesh remains operational
- EAR and MAR remain operational

Observed behavior:

- frame was mirrored correctly
- facial landmarks remained stable
- EAR and MAR remained available

Status:

```text
Passed
```

---

# 10. Error-Handling Validation

## Missing Video Path

Command:

```bash
python src/main.py --source file
```

Expected result:

```text
A clear error message states that --video-path is required.
```

Observed result:

- the error was caught
- the program did not crash with a traceback
- the user received a readable message

Status:

```text
Passed
```

---

## Invalid Video Path

Command:

```bash
python src/main.py \
  --source file \
  --video-path "/invalid/path/video.mp4"
```

Expected result:

```text
The source fails to open and a clear error message is printed.
```

Observed result:

- the invalid source was detected
- perception processing did not start
- the application terminated safely

Status:

```text
Passed
```

---

## End of File

Expected result:

- the pipeline stops when no further frames are available
- resources are released
- no unhandled exception occurs

Observed result:

- the processing loop stopped
- OpenCV resources were released
- the application terminated cleanly

Status:

```text
Passed
```

The current simplified interface does not distinguish between:

```text
natural end of file
frame acquisition failure
```

Both currently return:

```python
None
```

This behavior is accepted for Milestone 4A.

---

# 11. Evidence

Validation evidence is stored in:

```text
paths/01_fast_prototype/outputs/figures/
```

Planned evidence file:

```text
path_01_milestone_04A_source_independent_video_input.png
```

Recommended evidence composition:

```text
Webcam input | Local recorded-video input
```

The evidence should show:

- detected facial landmarks
- EAR
- MAR
- processing FPS
- source timestamp
- frame index
- source identifier

Privacy requirements:

- personal webcam images must be privacy-preserving
- identifiable faces should be blurred where appropriate
- DMD-derived video frames should remain local unless publication rights are confirmed
- public evidence may use approved plots, architecture diagrams or private recordings owned by the author

---

# 12. Known Issues

## Issue 1 — End of stream and read failure are not distinguished

The current `VideoSource.read()` interface returns:

```python
Optional[FramePacket]
```

A `None` result may represent either:

- natural end of a recorded video
- webcam acquisition failure
- corrupted or unreadable video frame

### Possible Cause

The acquisition interface was intentionally kept simple for the fast prototype.

### Temporary Workaround

Stop the pipeline safely whenever `None` is returned.

### Future Improvement

Introduce explicit acquisition-state reporting when additional source types require it.

Possible future states:

```text
FRAME_AVAILABLE
END_OF_STREAM
READ_FAILURE
SOURCE_DISCONNECTED
```

---

## Issue 2 — No automated acquisition tests

Validation was performed manually.

### Possible Cause

The milestone prioritizes rapid architecture development and functional validation.

### Temporary Workaround

Use repeated webcam and file-based regression tests before merging.

### Future Improvement

Add unit tests using:

- mocked `cv2.VideoCapture`
- short synthetic videos
- frame-index assertions
- timestamp assertions
- invalid-path assertions

---

## Issue 3 — No output-video writer

The current pipeline displays annotated frames but does not automatically save them.

### Possible Cause

Output recording was kept outside the scope of the acquisition abstraction.

### Temporary Workaround

Use screenshots or external screen recording for local validation.

### Future Improvement

Add a dedicated output module with configurable:

- output path
- codec
- resolution
- FPS
- privacy policy
- metadata logging

---

## Issue 4 — No playback controls

The recorded-video mode does not support:

- pause
- seek
- replay
- playback speed
- frame stepping

### Possible Cause

The current implementation focuses on sequential processing.

### Temporary Workaround

Restart the application to replay a sequence.

### Future Improvement

Introduce an experiment-player interface if required for annotation or detailed event inspection.

---

## Issue 5 — Single stream only

Only one video source is processed at a time.

### Possible Cause

The current architecture targets the face-level fast prototype.

### Temporary Workaround

Process each stream separately.

### Future Improvement

Add synchronized acquisition for:

- face camera
- body camera
- hand camera
- RGB and IR streams
- physiological sensors

---

## Issue 6 — Dataset-video publication restrictions

Dataset-derived media may not be suitable for public repository publication.

### Possible Cause

Dataset access does not automatically imply public redistribution rights.

### Temporary Workaround

Keep source and annotated dataset videos under ignored private directories.

### Future Improvement

Publish only:

- derived quantitative results
- plots
- privacy-preserving evidence
- approved screenshots
- recordings owned by the project author

---

# 13. Engineering Assessment

The milestone successfully separates video acquisition from perception processing.

Strengths:

- clean input abstraction
- shared processing pipeline
- webcam and file support
- source metadata propagation
- source-timeline awareness
- configurable mirroring
- preserved Face Mesh functionality
- preserved EAR and MAR functionality
- improved privacy protection
- improved reproducibility
- improved readiness for dataset-based experiments

Limitations:

- simplified end-of-stream handling
- no automated tests
- no output-video writer
- no multi-stream synchronization
- no IR-specific handling
- no experiment logger
- no formal performance benchmark

Overall assessment:

**Path 1 — Milestone 4A passed validation and is ready to support face-level temporal analysis in Milestone 4B.**

---

# 14. Recommendations

## Immediate Improvements

- Preserve the acquisition-perception separation.
- Use source timestamps for temporal logic.
- Keep mirroring disabled for recorded datasets by default.
- Keep private recordings and dataset videos outside Git tracking.
- Avoid introducing source-specific conditions inside perception modules.
- Preserve the shared `FramePacket` interface.

## Future Improvements

- Add automated tests for acquisition classes.
- Add annotated output-video writing.
- Add structured experiment logging.
- Add explicit acquisition statuses when technically justified.
- Add ROS image-source support.
- Add synchronized multimodal acquisition.
- Add IR and NIR source metadata.
- Add playback controls for offline evaluation.
- Add formal processing-latency and throughput benchmarks.

---

# 15. Next Validation

The next validation will focus on face-level temporal state analysis.

Milestone 4B validation should include:

- normal eye-open state
- short blink
- repeated blinking
- prolonged eye closure
- brief mouth opening
- sustained mouth opening
- temporary face loss
- prolonged face loss
- webcam timing
- file-video timing
- behavior under different processing speeds
- false-positive behavior during normal head movement

The validation should verify that event duration is based on source timestamps rather than frame count alone.

Planned candidate states:

```text
BLINK_CANDIDATE
PROLONGED_EYE_CLOSURE
SUSTAINED_MOUTH_OPENING
PROLONGED_FACE_LOSS
```

These should remain interpretable temporal candidates rather than final medical or safety classifications.

---

# Validation Completion Checklist

- [x] Validation executed
- [x] Compilation test completed
- [x] Webcam test completed
- [x] Mirrored webcam test completed
- [x] Local-video test completed
- [x] DMD sample test completed
- [x] Source timestamp behavior verified
- [x] Frame indexing verified
- [x] EAR/MAR regression verified
- [x] Error handling verified
- [x] Resource cleanup verified
- [x] Results documented
- [ ] Evidence stored
- [x] Known issues documented
- [x] Engineering assessment completed
- [x] Git commit completed
- [x] GitHub updated
- [x] Ready for milestone closure