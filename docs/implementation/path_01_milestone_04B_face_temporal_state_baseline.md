# Path 1 — Milestone 4B: Face-Level Temporal State Baseline

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 4B |
| Status | Completed |
| Date | 2026-07-26 |
| Author | Bassem Soliman |
| Repository | safety-critical-in-cabin-driver-monitoring |

---

# 1. Objective

The objective of this milestone is to extend the frame-level facial feature pipeline with timestamp-based temporal reasoning.

Milestone 3 introduced frame-level facial geometry features:

- Eye Aspect Ratio
- Mouth Aspect Ratio

Milestone 4A introduced source-independent video acquisition and source timestamps.

Milestone 4B combines these components to detect interpretable face-level temporal event candidates.

The milestone introduces:

- EAR moving-average processing
- MAR moving-average processing
- eye-closure duration tracking
- mouth-opening duration tracking
- face-loss duration tracking
- blink candidate detection
- prolonged eye-closure detection
- sustained mouth-opening detection
- prolonged face-loss detection
- state-priority logic
- blink-state display hold
- deterministic temporal-rule testing
- webcam and recorded-video integration

The resulting states are prototype temporal candidates and are not final medical diagnoses or production safety classifications.

---

# 2. Motivation

Single-frame facial features are insufficient for reliable driver-state reasoning.

A low EAR value in one frame may represent:

- a normal blink
- landmark noise
- temporary occlusion
- head movement
- a partially closed eye
- prolonged eye closure

Similarly, a high MAR value in one frame may represent:

- speech
- temporary mouth movement
- a short mouth opening
- a sustained mouth-opening event
- landmark instability

A Driver Monitoring System must therefore reason about feature behavior over time.

Milestone 4B introduces temporal logic so the pipeline can distinguish short events from sustained events.

Examples:

```text
Short eye closure
→ blink candidate

Long eye closure
→ prolonged eye-closure candidate

Short mouth opening
→ no sustained event

Long mouth opening
→ sustained mouth-opening candidate

Short face loss
→ temporary detection loss

Long face loss
→ prolonged face-loss candidate
```

The system intentionally avoids directly labeling these events as:

```text
DROWSY
YAWNING
UNRESPONSIVE
```

Those conclusions require additional signals, calibration, validation, and multimodal reasoning.

---

# 3. Software Perspective

This milestone extends the existing modular architecture.

Updated modules:

```text
src/decision/__init__.py
src/decision/temporal_rules.py
src/experiments/temporal_rules_smoke_test.py
src/main.py
src/perception/visualization.py
```

The decision layer is responsible for converting frame-level measurements into time-dependent event candidates.

The implementation introduces:

- `TemporalState`
- `TemporalRuleConfig`
- `TemporalDecisionResult`
- `TemporalRuleEngine`

The perception layer remains responsible for:

- face landmark detection
- EAR computation
- MAR computation

The acquisition layer remains responsible for:

- frame acquisition
- frame index
- source timestamp
- source identification

The decision layer receives measurements from perception and timestamps from acquisition.

This separation prevents temporal logic from becoming mixed with landmark detection or video acquisition.

---

# 4. Computer Vision Perspective

The computer vision pipeline now includes a temporal interpretation layer.

Updated pipeline:

Video Source

↓

Timestamped Frame Acquisition

↓

MediaPipe Face Mesh

↓

Selected Facial Landmarks

↓

EAR / MAR Feature Extraction

↓

Temporal Smoothing

↓

Continuous Duration Tracking

↓

Temporal Candidate Selection

↓

Visualization

The temporal layer uses three primary observations:

```text
EAR
MAR
face visibility
```

EAR is used as an estimate of eye openness.

MAR is used as an estimate of mouth openness.

Face visibility determines whether valid facial measurements are currently available.

The temporal engine does not operate directly on image pixels. It operates on measurements produced by the perception layer.

This allows the temporal logic to remain independent of the landmark-detection backend.

---

# 5. Python Perspective

This milestone introduces several Python concepts.

## Enum

`TemporalState` is implemented as an enum.

It defines a fixed set of valid temporal candidates:

```text
NORMAL
BLINK_CANDIDATE
PROLONGED_EYE_CLOSURE
SUSTAINED_MOUTH_OPENING
PROLONGED_FACE_LOSS
```

Using an enum avoids inconsistent free-text state names.

---

## Frozen dataclasses

The following structures use frozen dataclasses:

```text
TemporalRuleConfig
TemporalDecisionResult
```

`TemporalRuleConfig` stores the thresholds and timing parameters.

`TemporalDecisionResult` represents one immutable temporal output.

Frozen dataclasses reduce accidental runtime modification.

---

## Optional values

EAR and MAR may be unavailable when:

- no face is detected
- required landmarks are unavailable
- feature extraction fails

The implementation therefore uses:

```python
Optional[float]
```

---

## Deques

Moving-average histories use:

```python
collections.deque
```

The deque has a configurable maximum length.

When the history reaches its maximum size, the oldest value is removed automatically.

---

## Type hints

Type hints are used for:

- configuration values
- timestamps
- feature measurements
- return values
- history containers
- internal event timers

This improves readability and static analysis.

---

# 6. Engineering Perspective

The key engineering decision is to calculate event duration using source timestamps rather than frame count or processing FPS.

The system uses:

```python
frame_packet.timestamp_seconds
```

This ensures that temporal behavior remains consistent across:

- live webcam processing
- real-time recorded-video playback
- slow offline processing
- fast offline processing
- computers with different performance
- videos with different frame rates

A frame-count-based implementation would produce different event durations when the source FPS changes.

A processing-FPS-based implementation would incorrectly connect driver-state timing to computer performance.

Source timestamps represent the correct temporal reference.

---

# 7. Implemented Components

## `src/decision/__init__.py`

The decision package contains temporal and rule-based driver-state components.

The package is separated from perception because it interprets measurements rather than extracting them.

---

## `src/decision/temporal_rules.py`

Implemented:

- temporal state enum
- configurable thresholds
- moving-average histories
- eye-closure timer
- mouth-opening timer
- face-loss timer
- blink detection
- blink-state display hold
- state-priority selection
- source-timestamp validation
- configuration validation
- reset behavior

---

## `src/experiments/temporal_rules_smoke_test.py`

Implemented deterministic tests for:

- normal state
- blink candidate
- blink display hold
- blink display expiration
- prolonged eye closure
- sustained mouth opening
- prolonged face loss
- decreasing timestamp rejection

The smoke test uses artificial timestamps and artificial EAR/MAR values.

This allows the temporal logic to be tested independently of:

- webcam behavior
- MediaPipe variability
- lighting
- head orientation
- landmark noise
- dataset content

---

## `src/main.py`

Updated:

- initializes `TemporalRuleEngine`
- reads EAR and MAR from the feature dictionary
- passes source timestamps to the temporal engine
- passes face-detection state to the temporal engine
- receives `TemporalDecisionResult`
- sends temporal results to visualization
- updates the milestone label to Milestone 4B

---

## `src/perception/visualization.py`

Updated:

- temporal state display
- smoothed EAR display
- smoothed MAR display
- eye-closure duration display
- mouth-opening duration display
- face-loss duration display
- state-dependent colors
- compact non-overlapping text layout

State colors:

```text
NORMAL
→ green

BLINK_CANDIDATE
→ yellow

PROLONGED_EYE_CLOSURE
→ red

SUSTAINED_MOUTH_OPENING
→ orange

PROLONGED_FACE_LOSS
→ magenta
```

---

# 8. Temporal State Model

The temporal state model currently supports five states.

## `NORMAL`

Returned when no higher-priority temporal event is active.

Examples:

- face visible
- eyes open
- mouth not sustained open
- no completed blink pulse
- face loss below the configured duration

---

## `BLINK_CANDIDATE`

Returned after a completed eye closure whose duration falls within the configured blink interval.

A blink requires this sequence:

```text
eyes open
↓
EAR below threshold
↓
closure duration within blink interval
↓
eyes reopen
↓
BLINK_CANDIDATE
```

The state is generated after reopening the eyes.

---

## `PROLONGED_EYE_CLOSURE`

Returned when EAR remains below the configured threshold for longer than the configured prolonged-closure duration.

This remains an interpretable event candidate.

It is not directly classified as drowsiness.

---

## `SUSTAINED_MOUTH_OPENING`

Returned when MAR remains above the configured threshold for longer than the configured mouth-opening duration.

This remains a sustained mouth-opening candidate.

It is not directly classified as yawning because speech and other behaviors may also increase MAR.

---

## `PROLONGED_FACE_LOSS`

Returned when the face remains undetected longer than the configured face-loss duration.

Possible causes include:

- driver moving outside the camera field of view
- face occlusion
- poor lighting
- severe head rotation
- detector failure
- camera obstruction

It is not automatically interpreted as an unresponsive driver.

---

# 9. Temporal Configuration

The default temporal configuration contains:

```text
eye_closed_ear_threshold
mouth_open_mar_threshold
blink_min_duration_seconds
blink_max_duration_seconds
blink_display_hold_seconds
prolonged_eye_closure_seconds
sustained_mouth_opening_seconds
prolonged_face_loss_seconds
smoothing_window_size
```

Prototype defaults:

```text
Eye-closed EAR threshold: 0.20
Mouth-open MAR threshold: 0.60

Minimum blink duration: 0.08 seconds
Maximum blink duration: 0.50 seconds
Blink display hold: 0.40 seconds

Prolonged eye closure: 1.50 seconds
Sustained mouth opening: 1.00 second
Prolonged face loss: 1.00 second
```

The live validation used a smoothing window of one frame to preserve short blink visibility.

These values are prototype settings.

They require later calibration across:

- different drivers
- face shapes
- eyewear
- camera positions
- lighting conditions
- RGB and IR cameras
- head orientations
- cabin datasets

---

# 10. Moving-Average Processing

The temporal engine supports a simple moving average for EAR and MAR.

The moving average reduces frame-level variation caused by:

- landmark jitter
- image noise
- small head movements
- detector instability

However, smoothing creates a trade-off.

A large smoothing window improves stability but may suppress short blink events.

A small smoothing window preserves fast events but provides less noise reduction.

For the current live prototype, a smoothing window of one was used during blink validation.

A future implementation may use separate signals:

```text
raw EAR
→ blink detection

smoothed EAR
→ prolonged eye-closure detection
```

This would better separate rapid and sustained events.

---

# 11. Blink Display Hold

The true `blink_detected` event is generated for one update after the eyes reopen.

At approximately 30 FPS, this may be visible for only around one frame.

This is too brief for a human observer to recognize reliably.

The milestone therefore introduces:

```text
blink_display_hold_seconds
```

When a blink is detected, the visible `BLINK_CANDIDATE` state is held for a short period.

This improves human observability without changing the actual blink duration.

The implementation distinguishes between:

```text
blink event pulse
```

and:

```text
displayed blink candidate state
```

The actual `blink_detected` flag remains true only on the detection update.

---

# 12. Duration Tracking

The temporal engine tracks three continuous durations.

## Eye-closure duration

Begins when:

```text
smoothed EAR < eye-closed threshold
```

Resets when the eyes reopen.

---

## Mouth-opening duration

Begins when:

```text
smoothed MAR > mouth-open threshold
```

Resets when MAR falls below the threshold.

---

## Face-loss duration

Begins when:

```text
face_detected = False
```

Resets when the face is detected again.

When the face is lost:

- EAR history is cleared
- MAR history is cleared
- eye-closure timing is reset
- mouth-opening timing is reset

This prevents stale measurements from continuing during face loss.

---

# 13. State Priority

Only one primary temporal state is displayed at a time.

The current priority is:

```text
1. PROLONGED_EYE_CLOSURE
2. SUSTAINED_MOUTH_OPENING
3. BLINK_CANDIDATE
4. NORMAL
```

Face-loss handling is processed separately because EAR and MAR are unavailable when no face is detected.

When prolonged face loss becomes active, the result is:

```text
PROLONGED_FACE_LOSS
```

The priority prevents multiple states from competing for the primary visualization output.

Future systems may return multiple simultaneous flags in addition to one primary state.

---

# 14. System Interfaces

## Inputs

`TemporalRuleEngine.update()` receives:

```text
timestamp_seconds
face_detected
ear
mar
```

### `timestamp_seconds`

Timestamp from the source timeline.

### `face_detected`

Boolean indicating whether the face is available.

### `ear`

Frame-level Eye Aspect Ratio.

### `mar`

Frame-level Mouth Aspect Ratio.

---

## Outputs

The engine returns:

```text
TemporalDecisionResult
```

containing:

```text
primary_state
smoothed_ear
smoothed_mar
eye_closure_duration_seconds
mouth_open_duration_seconds
face_loss_duration_seconds
blink_detected
```

---

## Consumers

The result is consumed by:

- the visualization layer
- future event logging
- future behavior models
- future evaluation tools
- future explainability modules

---

# 15. Integration into the Main Pipeline

The shared pipeline now performs:

```text
1. Read FramePacket
2. Optionally mirror frame
3. Detect selected facial landmarks
4. Compute EAR and MAR
5. Read source timestamp
6. Update TemporalRuleEngine
7. Receive TemporalDecisionResult
8. Draw perception overlay
9. Draw source metadata
10. Draw temporal-state overlay
11. Display the frame
```

The same logic is used for:

- webcam input
- local video input
- local DMD sample validation

No source-specific temporal logic is implemented.

---

# 16. Validation Summary

Validation was performed using:

- deterministic artificial sequences
- live webcam input
- mirrored webcam input
- local recorded video
- local DMD sample video
- repeated state activation
- recorded output video
- local screenshots

The following states were verified:

```text
NORMAL
BLINK_CANDIDATE
PROLONGED_EYE_CLOSURE
SUSTAINED_MOUTH_OPENING
PROLONGED_FACE_LOSS
```

The following behavior was also verified:

- blink display hold
- blink display expiration
- source timestamp usage
- decreasing timestamp rejection
- face-loss history reset
- state-dependent colors
- clean recorded-video processing
- clean application shutdown

Validation details are documented in:

```text
docs/validation/path_01_milestone_04B_face_temporal_state_baseline_validation.md
```

Local evidence includes:

- an annotated video containing all temporal states
- screenshots of the temporal states
- webcam output
- recorded-video output

The video and screenshots are currently stored locally and are not yet published in the repository.

---

# 17. Limitations

Current limitations:

- prototype thresholds are not calibrated per driver
- one EAR threshold is used for both eyes
- no per-eye blink interpretation
- no adaptive baseline
- no head-pose compensation
- no gaze information
- no speech discrimination
- sustained mouth opening is not equivalent to yawning
- prolonged eye closure is not equivalent to drowsiness
- face loss has multiple possible causes
- smoothing configuration is shared between EAR and MAR
- blink display hold is part of visual observability
- no event history or event counter
- no structured CSV logging
- no automated video-level benchmark
- no ground-truth annotation comparison
- no confidence values
- no hysteresis around thresholds

These limitations are expected for the fast prototype.

---

# 18. Future Scalability

The temporal architecture can later support:

- independent left-eye and right-eye closure
- blink frequency
- blink rate
- PERCLOS
- eye-closure percentage
- yawn-duration estimation
- repeated-yawn analysis
- adaptive driver baselines
- threshold hysteresis
- head-pose gating
- gaze-away duration
- hands-off-wheel duration
- phone-use duration
- unsafe-posture duration
- unresponsive-driver candidate logic
- multimodal sensor fusion
- event logging
- ML-based temporal models
- explainable state decisions

Future temporal models may include:

- finite-state machines
- hidden Markov models
- temporal convolutional networks
- recurrent neural networks
- LSTM models
- transformers
- probabilistic graphical models

The current rule-based baseline will provide an interpretable reference for comparison.

---

# 19. Research / Technology Notes

Rule-based temporal logic is useful as an early baseline because it is:

- interpretable
- deterministic
- lightweight
- fast
- easy to debug
- suitable for real-time execution
- suitable for comparison with later ML models

However, a production Driver Monitoring System requires broader validation.

The current event candidates should be treated as observable facial events rather than final driver-state conclusions.

A stronger system should combine:

- eye behavior
- head pose
- gaze
- facial activity
- body posture
- hand activity
- steering behavior
- vehicle context
- physiological information

The rule engine can later support explainability by reporting which measurements and durations activated each state.

---

# 20. Lessons Learned

This milestone demonstrated that temporal reasoning changes isolated feature values into more meaningful event candidates.

It also showed that:

- source timestamps are essential
- processing FPS must not define event duration
- smoothing introduces responsiveness trade-offs
- short blink events require different treatment from sustained states
- human-visible overlays may need display logic separate from event logic
- deterministic tests are important before webcam integration
- face loss must reset unavailable feature histories
- temporal states should remain cautious and interpretable

The architecture now provides a foundation for additional driver-behavior dimensions.

---

# 21. Next Milestone

The next milestone is:

**Path 1 — Milestone 5: Head Pose Estimation**

The goal will be to estimate driver head orientation using facial landmarks.

Planned outputs include:

```text
yaw
pitch
roll
```

The milestone will support later analysis of:

- head-turn direction
- prolonged head deviation
- forward-road attention
- distraction candidates
- face orientation quality
- EAR/MAR interpretation under non-frontal pose

Head pose will remain a geometric measurement before being converted into temporal distraction logic.

---

# Milestone Completion Checklist

- [x] Temporal state enum implemented
- [x] Temporal configuration implemented
- [x] Temporal result model implemented
- [x] EAR moving-average support implemented
- [x] MAR moving-average support implemented
- [x] Blink candidate implemented
- [x] Blink display hold implemented
- [x] Prolonged eye closure implemented
- [x] Sustained mouth opening implemented
- [x] Prolonged face loss implemented
- [x] State-priority logic implemented
- [x] Timestamp validation implemented
- [x] Deterministic smoke tests completed
- [x] Webcam integration completed
- [x] Recorded-video integration completed
- [x] DMD local validation completed
- [x] Colored visualization completed
- [x] Local output video recorded
- [x] Local screenshots captured
- [x] Implementation documentation completed
- [x] Ready for validation documentation