# Path 1 — Milestone 4B Validation: Face-Level Temporal State Baseline

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 4B |
| Validation Date | 2026-07-26 |
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

The objective of this validation is to verify that the system correctly converts frame-level facial measurements into timestamp-based temporal event candidates.

The validation focuses on:

- normal visible-face behavior
- blink candidate detection
- blink display hold
- blink display expiration
- prolonged eye closure
- sustained mouth opening
- prolonged face loss
- EAR and MAR moving-average behavior
- source-timestamp duration tracking
- decreasing timestamp rejection
- webcam integration
- recorded-video integration
- state-dependent visualization
- clean resource release

The validation also verifies that the temporal engine produces cautious and interpretable event candidates rather than unsupported medical or behavioral conclusions.

---

# 2. Test Environment

## Hardware

- Laptop or workstation
- Integrated RGB webcam
- Local storage for recorded validation media

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

- local MP4 video
- local DMD face-camera sample
- annotated temporal-state output video
- local validation screenshots

## Lighting

- normal indoor lighting for webcam validation
- original recorded conditions for DMD validation

---

# 3. Test Configuration

The temporal baseline was validated using:

- frame-level EAR
- frame-level MAR
- face visibility
- source timestamps
- configurable duration thresholds
- source-independent video input

Prototype thresholds:

| Parameter | Value |
|-----------|-------|
| Eye-closed EAR threshold | 0.20 |
| Mouth-open MAR threshold | 0.60 |
| Minimum blink duration | 0.08 s |
| Maximum blink duration | 0.50 s |
| Blink display hold | 0.40 s |
| Prolonged eye closure | 1.50 s |
| Sustained mouth opening | 1.00 s |
| Prolonged face loss | 1.00 s |
| Live validation smoothing window | 1 frame |

These values are prototype defaults and are not interpreted as final calibrated safety thresholds.

---

# 4. Deterministic Smoke-Test Configuration

The deterministic temporal test was executed with:

```bash
PYTHONPATH=src python -m experiments.temporal_rules_smoke_test
```

The test uses artificial observations rather than camera measurements.

Each observation contains:

```text
timestamp
face visibility
EAR
MAR
```

The test verifies:

- predictable temporal transitions
- exact event durations
- state activation
- state expiration
- invalid timestamp rejection

The deterministic test isolates temporal logic from:

- MediaPipe landmark variability
- camera noise
- driver movement
- lighting changes
- recorded-video content

---

# 5. Test Cases

| Test Case | Expected Result | Actual Result | Status |
|------------|----------------|---------------|--------|
| Source compilation | All Python source files compile | Compilation completed successfully | ✅ Pass |
| Normal visible face | State remains `NORMAL` | Correct | ✅ Pass |
| Short valid eye closure | Blink event is generated after reopening | Correct | ✅ Pass |
| Blink display hold | `BLINK_CANDIDATE` remains visible briefly | Correct | ✅ Pass |
| Blink display expiration | State returns to `NORMAL` after hold interval | Correct | ✅ Pass |
| Long eye closure | State becomes `PROLONGED_EYE_CLOSURE` | Correct | ✅ Pass |
| Long mouth opening | State becomes `SUSTAINED_MOUTH_OPENING` | Correct | ✅ Pass |
| Long face loss | State becomes `PROLONGED_FACE_LOSS` | Correct | ✅ Pass |
| EAR smoothing | Smoothed EAR updates correctly | Correct | ✅ Pass |
| MAR smoothing | Smoothed MAR updates correctly | Correct | ✅ Pass |
| Eye timer reset | Duration resets after eyes reopen | Correct | ✅ Pass |
| Mouth timer reset | Duration resets after mouth closes | Correct | ✅ Pass |
| Face-loss timer reset | Duration resets when face returns | Correct | ✅ Pass |
| Face loss clears histories | EAR and MAR histories become unavailable | Correct | ✅ Pass |
| Monotonic timestamps | Increasing timestamps are accepted | Correct | ✅ Pass |
| Decreasing timestamp | `ValueError` is raised | Correct | ✅ Pass |
| Webcam integration | Temporal states update from live features | Correct | ✅ Pass |
| Mirrored webcam | Temporal logic remains functional | Correct | ✅ Pass |
| Recorded video | Temporal logic operates on source timestamps | Correct | ✅ Pass |
| DMD local sample | Shared temporal pipeline operates correctly | Correct | ✅ Pass |
| Colored state overlay | State colors match configured categories | Correct | ✅ Pass |
| No text overlap | Overlay remains readable | Correct | ✅ Pass |
| Clean user exit | Pressing `q` closes the application | Correct | ✅ Pass |
| End of video | Pipeline terminates without crashing | Correct | ✅ Pass |
| Output recording | Annotated all-state video recorded locally | Correct | ✅ Pass |
| Screenshots | Temporal-state screenshots captured locally | Correct | ✅ Pass |

---

# 6. Results

The face-level temporal state baseline operated successfully.

Observed behavior:

- The normal state remained stable while the face was visible and no event threshold was active.
- A completed short eye closure produced `BLINK_CANDIDATE`.
- The blink state remained visible for the configured display interval.
- The state returned to `NORMAL` after the display hold expired.
- Closing the eyes longer than the configured threshold produced `PROLONGED_EYE_CLOSURE`.
- Keeping the mouth open longer than the configured threshold produced `SUSTAINED_MOUTH_OPENING`.
- Removing the face from view longer than the configured threshold produced `PROLONGED_FACE_LOSS`.
- Eye, mouth and face-loss durations reset correctly.
- Source timestamps controlled all duration calculations.
- Decreasing timestamps were rejected.
- The same temporal pipeline operated with webcam and recorded-video input.
- State-dependent colors improved live observability.
- The pipeline processed the local DMD sample without failure.
- An annotated output video containing all temporal states was recorded locally.
- Supporting screenshots were captured locally.

The milestone is considered ready for completion.

---

# 7. Performance Summary

| Metric | Observation |
|---------|-------------|
| Runtime | Real-time |
| Deterministic test | Passed |
| Webcam integration | Passed |
| Recorded-video integration | Passed |
| Blink candidate | Detected |
| Blink display hold | Correct |
| Prolonged eye closure | Correct |
| Sustained mouth opening | Correct |
| Prolonged face loss | Correct |
| Timestamp validation | Correct |
| State reset behavior | Correct |
| Overlay readability | Correct |
| Application stability | Acceptable for prototype |

No formal CPU, GPU, memory or end-to-end latency benchmark was performed.

---

# 8. Blink Validation

## Objective

Verify that a short completed eye closure is recognized as a blink candidate.

## Expected sequence

```text
Eyes open
↓
EAR falls below threshold
↓
Closure duration remains within blink interval
↓
Eyes reopen
↓
BLINK_CANDIDATE
```

## Deterministic result

The artificial sequence produced:

```text
BLINK_CANDIDATE
```

with:

```text
blink_detected = True
```

on the reopening update.

Status:

```text
Passed
```

---

## Live webcam result

A short intentional blink was performed.

Observed behavior:

- eye-closure duration increased briefly
- the eyes reopened within the configured interval
- `BLINK_CANDIDATE` appeared
- the yellow state remained visible briefly
- the state returned to `NORMAL`

Status:

```text
Passed
```

---

# 9. Blink Display-Hold Validation

## Objective

Verify that the visible blink state remains readable without changing the underlying blink event duration.

Expected behavior:

- `blink_detected` is true only on the detection update
- the primary displayed state remains `BLINK_CANDIDATE` during the hold interval
- the state expires after the configured interval

Observed behavior:

- blink pulse occurred correctly
- the state remained visible for approximately 0.40 seconds
- `blink_detected` returned to false
- the displayed state returned to `NORMAL` after expiration

Status:

```text
Passed
```

---

# 10. Prolonged Eye-Closure Validation

## Objective

Verify that continuous low EAR activates the prolonged eye-closure candidate.

Expected behavior:

```text
EAR below 0.20
for at least 1.50 seconds
→ PROLONGED_EYE_CLOSURE
```

Observed behavior:

- eye-closure duration increased continuously
- the state remained `NORMAL` before the threshold
- the state changed to `PROLONGED_EYE_CLOSURE` after the threshold
- the displayed state became red
- the duration reset when the eyes reopened

Status:

```text
Passed
```

---

# 11. Sustained Mouth-Opening Validation

## Objective

Verify that continuous high MAR activates the sustained mouth-opening candidate.

Expected behavior:

```text
MAR above 0.60
for at least 1.00 second
→ SUSTAINED_MOUTH_OPENING
```

Observed behavior:

- mouth-opening duration increased continuously
- the state changed after the configured threshold
- the displayed state became orange
- the timer reset after the mouth closed

Status:

```text
Passed
```

The result is interpreted as a sustained mouth-opening candidate and not a confirmed yawn.

---

# 12. Face-Loss Validation

## Objective

Verify that continuous face-detection loss activates the prolonged face-loss candidate.

Expected behavior:

```text
face_detected = False
for at least 1.00 second
→ PROLONGED_FACE_LOSS
```

Observed behavior:

- EAR and MAR became unavailable
- feature histories were cleared
- face-loss duration increased
- the state changed to `PROLONGED_FACE_LOSS`
- the displayed state became magenta
- the timer reset when the face returned

Status:

```text
Passed
```

---

# 13. Timestamp Validation

## Source timestamps

Temporal updates used:

```python
frame_packet.timestamp_seconds
```

Webcam timestamps were based on monotonic elapsed time.

Recorded-video timestamps followed the source timeline.

Observed behavior:

- durations were independent of processing FPS
- recorded-video timing remained connected to the video timeline
- repeated test sequences produced consistent temporal behavior

Status:

```text
Passed
```

---

## Invalid timestamp order

A decreasing timestamp was provided in the deterministic test.

Expected result:

```text
ValueError
```

Observed result:

- the timestamp was rejected
- temporal state was not silently corrupted
- the smoke test confirmed the expected exception

Status:

```text
Passed
```

---

# 14. Recorded-Video Validation

The source-independent pipeline was executed with a local recorded video and a local DMD sample.

Command format:

```bash
python src/main.py \
  --source file \
  --video-path "/path/to/video.mp4"
```

Observed behavior:

- the source opened correctly
- frames were processed sequentially
- source timestamps updated
- frame indices increased
- Face Mesh remained operational
- EAR and MAR remained operational
- the temporal engine updated correctly
- no dataset mirroring was applied
- the video ended without crashing
- resources were released correctly

Status:

```text
Passed
```

Not every recorded clip is required to contain every temporal event.

The purpose of the recorded-video validation was to confirm source-timestamp compatibility and shared-pipeline operation.

---

# 15. Visualization Validation

The overlay displays:

- primary temporal state
- smoothed EAR
- smoothed MAR
- eye-closure duration
- mouth-opening duration
- face-loss duration
- source timestamp
- frame index
- source name
- perception measurements

State colors:

| State | Display Color |
|-------|---------------|
| `NORMAL` | Green |
| `BLINK_CANDIDATE` | Yellow |
| `PROLONGED_EYE_CLOSURE` | Red |
| `SUSTAINED_MOUTH_OPENING` | Orange |
| `PROLONGED_FACE_LOSS` | Magenta |

Observed behavior:

- state colors changed correctly
- measurements remained white
- the overlay remained readable
- text did not overlap
- the milestone label remained visible

Status:

```text
Passed
```

---

# 16. Evidence

Local validation evidence includes:

```text
annotated temporal-state video
screenshots of all temporal states
webcam validation output
recorded-video validation output
```

The annotated video contains:

```text
NORMAL
BLINK_CANDIDATE
PROLONGED_EYE_CLOSURE
SUSTAINED_MOUTH_OPENING
PROLONGED_FACE_LOSS
```

The evidence is currently stored locally.

The planned public repository evidence location is:

```text
paths/01_fast_prototype/outputs/figures/
```

Planned figure name:

```text
path_01_milestone_04B_face_temporal_state_baseline.png
```

Planned local or approved video name:

```text
path_01_milestone_04B_face_temporal_state_baseline.mp4
```

Privacy and dataset policy:

- identifiable personal recordings should be reviewed before publication
- private recordings should remain local until approved
- DMD-derived videos and screenshots should not be publicly redistributed unless publication rights are confirmed
- public evidence may use privacy-preserving screenshots or author-owned recordings

---

# 17. Known Issues

## Issue 1 — Thresholds are not calibrated

EAR and MAR thresholds use prototype defaults.

### Possible Cause

Driver-specific and dataset-level calibration has not yet been performed.

### Temporary Workaround

Use thresholds for qualitative prototype validation only.

### Future Improvement

Evaluate distributions across drivers and use adaptive baselines.

---

## Issue 2 — One smoothing strategy is shared

EAR and MAR currently use the same moving-average mechanism.

### Possible Cause

The milestone uses a compact baseline architecture.

### Temporary Workaround

Use a small smoothing window during rapid blink validation.

### Future Improvement

Use separate filters for:

- blink detection
- prolonged eye closure
- mouth-opening analysis

---

## Issue 3 — No hysteresis

The same threshold is used for entering and leaving a condition.

### Possible Cause

Threshold hysteresis was outside the milestone scope.

### Temporary Workaround

Use temporal duration requirements to reduce rapid changes.

### Future Improvement

Introduce separate activation and release thresholds.

---

## Issue 4 — No head-pose compensation

EAR and MAR may change when the face rotates.

### Possible Cause

Measurements are based on 2D image-space geometry.

### Temporary Workaround

Validate primarily with frontal or near-frontal orientation.

### Future Improvement

Use head pose to gate or compensate feature interpretation.

---

## Issue 5 — Mouth opening is not equivalent to yawning

Speech and other facial activity can increase MAR.

### Possible Cause

The current state uses geometry and duration only.

### Temporary Workaround

Describe the state only as sustained mouth opening.

### Future Improvement

Combine mouth duration, shape dynamics, frequency, head behavior and additional facial features.

---

## Issue 6 — Face loss is ambiguous

Face loss may represent multiple technical or behavioral conditions.

### Possible Cause

No additional pose, body or camera-health signal is available.

### Temporary Workaround

Treat it only as prolonged face loss.

### Future Improvement

Combine face loss with:

- body presence
- head pose
- camera status
- seat occupancy
- steering interaction

---

## Issue 7 — No structured event log

Temporal states are displayed but not stored as structured events.

### Possible Cause

Experiment logging is not yet implemented.

### Temporary Workaround

Use local annotated video and screenshots.

### Future Improvement

Add CSV or JSON logging with:

```text
timestamp
frame index
state
EAR
MAR
durations
thresholds
source
```

---

# 18. Engineering Assessment

The milestone successfully converts frame-level facial measurements into time-based event candidates.

Strengths:

- interpretable rule-based design
- source-timestamp timing
- modular decision layer
- deterministic testing
- clear configuration
- clean reset behavior
- webcam and recorded-video support
- human-readable visualization
- blink display hold
- cautious state terminology
- privacy-aware validation evidence

Limitations:

- uncalibrated thresholds
- no head-pose compensation
- no threshold hysteresis
- no adaptive baseline
- no event logger
- no formal dataset benchmark
- no multimodal confirmation
- no confidence score

Overall assessment:

**Path 1 — Milestone 4B passed validation and is ready to support Head Pose Estimation in Milestone 5.**

---

# 19. Recommendations

## Immediate Recommendations

- Preserve source-timestamp-based timing.
- Preserve cautious candidate-state terminology.
- Keep recorded DMD evidence local.
- Store only approved or privacy-preserving public evidence.
- Preserve deterministic tests during future refactoring.
- Avoid interpreting one temporal signal as a final driver state.

## Future Recommendations

- add threshold hysteresis
- add separate blink and prolonged-closure filtering
- add event counting
- add event logging
- add driver-specific calibration
- add PERCLOS
- add head-pose gating
- add gaze-away duration
- add confidence values
- validate against annotated sequences
- compare rule-based and ML-based temporal models

---

# 20. Next Validation

The next validation will focus on Head Pose Estimation.

Milestone 5 validation should include:

- frontal head pose
- left head rotation
- right head rotation
- upward pitch
- downward pitch
- roll behavior
- pose stability
- landmark-loss behavior
- webcam input
- recorded-video input
- different camera distances
- different face orientations

The output should remain geometric:

```text
yaw
pitch
roll
```

Temporal distraction interpretation should be added only after the pose measurements are validated.

---

# Validation Completion Checklist

- [x] Validation executed
- [x] Compilation completed
- [x] Deterministic smoke test completed
- [x] Normal state verified
- [x] Blink candidate verified
- [x] Blink display hold verified
- [x] Blink expiration verified
- [x] Prolonged eye closure verified
- [x] Sustained mouth opening verified
- [x] Prolonged face loss verified
- [x] Source timestamp behavior verified
- [x] Invalid timestamp rejection verified
- [x] Webcam integration verified
- [x] Recorded-video integration verified
- [x] DMD local validation completed
- [x] State colors verified
- [x] Overlay readability verified
- [x] Local annotated video recorded
- [x] Local screenshots captured
- [x] Results documented
- [x] Known issues documented
- [x] Engineering assessment completed
- [x] Ready for README update