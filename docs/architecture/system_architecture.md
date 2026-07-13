# Safety-Critical In-Cabin Driver Monitoring
## System Architecture

---

| Item | Value |
|---|---|
| Document Status | Draft |
| Architecture Version | 1.0 |
| Active Path | Path 1 — Fast Prototype |
| Last Updated | 2026-07-13 |
| Next Milestone | Milestone 4A — Source-Independent Video Acquisition |

---

## 1. Purpose

This document defines the long-term software, perception, temporal reasoning, behavior modeling and evaluation architecture of the **Safety-Critical In-Cabin Driver Monitoring** project.

The architecture is designed to support:

- live webcam input
- local video files
- recorded cabin videos
- dataset samples such as DMD
- future RGB, IR and NIR camera streams
- frame-level visual perception
- temporal feature analysis
- multimodal behavior modeling
- ML/XAI-oriented driver-state estimation
- reproducible validation and benchmarking
- future HMI and vehicle-system integration

The architecture separates acquisition, timing, perception, feature extraction, temporal reasoning, behavior modeling, explainability, evaluation and application logic.

---

## 2. Architecture Principles

The system follows these engineering principles:

1. Input sources must remain independent from the perception pipeline.
2. Source timestamps must remain independent from processing speed.
3. Frame-level perception must remain separate from temporal reasoning.
4. Temporal events must remain separate from high-level behavior classification.
5. Driver-state outputs must be interpretable and supported by measurable evidence.
6. Dataset files and private recordings must not be committed to the repository.
7. Each module must have a clear responsibility and interface.
8. The architecture must support future multimodal and multi-camera extensions.
9. Dataset replay and experiments must remain reproducible.
10. Safety-relevant outputs must be described as candidates until properly validated.
11. Unknown or low-confidence states must be represented explicitly.
12. The system should evolve incrementally without unnecessary redesign.

---

## 3. High-Level Architecture

```text
Acquisition Layer
        ↓
Frame Metadata and Timing Layer
        ↓
Perception Layer
        ↓
Feature Layer
        ↓
Temporal Feature Layer
        ↓
Behavior Modeling Layer
        ↓
Explainability Layer
        ↓
Driver-State Estimation Layer
        ↓
Evaluation and Application Layer
```

The core architectural separation is:

```text
acquisition ≠ perception
perception ≠ temporal reasoning
temporal reasoning ≠ behavior classification
behavior classification ≠ final safety decision
```

---

## 4. Acquisition Layer

The acquisition layer provides a common interface for all supported video and sensor inputs.

Supported or planned sources include:

- live webcam
- local video files
- recorded cabin videos
- DMD dataset videos
- future RGB camera streams
- future IR and NIR camera streams
- future synchronized multi-camera streams

Planned structure:

```text
src/acquisition/
├── __init__.py
└── video_source.py
```

The initial Milestone 4A implementation will support:

```text
WebcamVideoSource
FileVideoSource
```

Future extensions may support:

```text
DatasetVideoSource
RecordedCabinVideoSource
SynchronizedMultiCameraSource
RGBIRVideoSource
```

The acquisition layer must return a common frame representation rather than only a raw image.

---

## 5. Frame Metadata and Timing Layer

Every acquired frame should be represented by a common frame packet.

Initial structure:

```text
frame
frame_index
timestamp_seconds
source_name
```

Future extensions may include:

```text
camera_id
modality
session_id
subject_id
sequence_id
source_fps
original_resolution
synchronization_timestamp
```

The architecture distinguishes between:

```text
source timestamp
processing timestamp
processing FPS
```

### 5.1 Source Timestamp

The source timestamp represents the original position of a frame in the source timeline.

Examples:

```text
webcam:
elapsed monotonic time since acquisition started

video file:
video timestamp or frame_index / source_fps

dataset:
dataset-provided timestamp or synchronized sequence timeline
```

### 5.2 Processing Time

Processing time represents how long the current computer requires to process each frame.

Temporal state logic must use the **source timestamp**, not the processing speed.

This prevents inconsistent temporal behavior when:

- the same video is processed on different computers
- additional perception modules reduce processing speed
- offline video is processed faster or slower than real time
- the source FPS differs from the runtime FPS

---

## 6. Perception Layer

The perception layer extracts frame-level visual information.

Current and planned modules:

```text
src/perception/
├── face_features.py
├── head_pose.py
├── gaze_features.py
├── body_features.py
├── hand_features.py
└── visualization.py
```

Responsibilities include:

- face landmark detection
- facial geometry extraction
- head-pose estimation
- gaze estimation
- body-pose analysis
- hand-activity analysis
- perception-result visualization

The perception layer processes individual frames.

It must not make final driver-state decisions.

Current implemented perception components:

```text
FaceMeshDetector
FacialGeometryExtractor
selected facial landmarks
Eye Aspect Ratio
Mouth Aspect Ratio
face visibility
```

---

## 7. Feature Layer

The feature layer provides measurable frame-level signals.

Current features:

```text
Eye Aspect Ratio
Mouth Aspect Ratio
face visibility
selected facial landmarks
```

Planned features:

```text
head yaw
head pitch
head roll
gaze direction
gaze-away indicator
torso orientation
shoulder alignment
posture descriptors
hand location
hands-on-wheel indicator
reaching indicator
possible phone-interaction cue
```

Feature outputs should be:

- numerically defined
- timestamped
- traceable to their perception source
- suitable for temporal processing
- interpretable during validation
- independent from final behavior labels

The feature layer must not directly classify the driver as drowsy, distracted or unresponsive.

---

## 8. Temporal Feature Layer

The temporal layer transforms frame-level features into time-dependent events.

Planned structure:

```text
src/temporal/
├── __init__.py
└── facial_state.py
```

Initial Milestone 4B temporal features:

```text
EAR smoothing
MAR smoothing
blink duration
prolonged eye-closure duration
sustained mouth-opening duration
face-loss duration
```

Future temporal features:

```text
gaze-away duration
head-turn duration
head-down duration
posture-state duration
hands-off-wheel duration
reaching duration
multi-event sequence analysis
```

Example:

```text
single-frame low EAR
→ measurement only

low EAR over a short duration
→ blink candidate

low EAR over a prolonged duration
→ prolonged eye-closure candidate
```

The temporal layer should output interpretable event candidates such as:

```text
BLINK_CANDIDATE
PROLONGED_EYE_CLOSURE
SUSTAINED_MOUTH_OPENING
PROLONGED_FACE_LOSS
GAZE_AWAY_EVENT
HEAD_TURN_EVENT
HANDS_OFF_WHEEL_EVENT
```

These outputs are not yet final behavioral diagnoses.

---

## 9. Behavior Modeling Layer

The behavior modeling layer combines temporal events and multimodal features.

Planned approaches:

- interpretable rule-based baseline
- finite-state-machine baseline
- temporal feature fusion
- TCN
- LSTM
- Temporal Transformer
- multimodal fusion

Potential input channels:

```text
facial geometry
face visibility
head pose
gaze
body posture
hand activity
contextual information
```

Potential driver-state candidates:

```text
ATTENTIVE
DROWSINESS_CANDIDATE
DISTRACTION_CANDIDATE
OUT_OF_POSITION_CANDIDATE
UNRESPONSIVE_DRIVER_CANDIDATE
UNKNOWN
```

Example reasoning:

```text
prolonged low EAR
+ head-down orientation
+ reduced gaze stability
→ drowsiness candidate
```

Another example:

```text
gaze away
+ head turned
+ hand reaching
→ distraction candidate
```

The behavior layer must preserve the evidence that caused each state transition.

---

## 10. Explainability Layer

The explainability layer supports both rule-based interpretability and future ML/XAI methods.

Planned outputs:

- triggering features
- temporal evidence
- event duration
- state-transition history
- confidence values
- feature contributions
- model attribution results

Example explanation:

```text
Prolonged eye-closure candidate

Evidence:
- EAR below threshold
- duration: 1.8 seconds
- face visible
- head pose approximately frontal
```

Future ML/XAI-oriented methods may include:

```text
feature importance
temporal saliency
attention visualization
SHAP-style feature attribution
sequence-level explanations
counterfactual analysis
```

The explainability layer is important because the system targets human-state interpretation and safety-relevant perception.

---

## 11. Driver-State Estimation Layer

The driver-state estimation layer produces high-level state candidates from validated temporal and multimodal evidence.

Potential state candidates:

```text
ATTENTIVE
DROWSINESS_CANDIDATE
DISTRACTION_CANDIDATE
OUT_OF_POSITION_CANDIDATE
UNRESPONSIVE_DRIVER_CANDIDATE
UNKNOWN
```

The `UNKNOWN` state should be used when:

- the face is not visible
- required perception channels are unavailable
- confidence is too low
- evidence is contradictory
- the system operates outside validated conditions

The system must avoid forcing a confident state when the available evidence is insufficient.

---

## 12. Evaluation Layer

The evaluation layer supports technical, scientific and safety-oriented validation.

Planned structure:

```text
src/evaluation/
├── __init__.py
└── metrics.py
```

Evaluation modes:

- live webcam validation
- recorded-video replay
- DMD sample evaluation
- dataset benchmarking
- subject-independent evaluation
- controlled scenario testing

Planned metrics:

```text
precision
recall
F1 score
false-positive rate
false-negative rate
event detection delay
event duration error
frame-level accuracy
event-level accuracy
processing FPS
latency
CPU usage
memory usage
```

Evaluation should distinguish between:

```text
frame-level metrics
event-level metrics
subject-level metrics
runtime metrics
```

For behavior modeling, event-level evaluation is often more meaningful than only frame-level accuracy.

---

## 13. Application and HMI Layer

The application layer exposes system outputs to users or external systems.

Planned functions:

- real-time visualization
- event logging
- state timeline visualization
- warning-state visualization
- recorded annotated video
- experiment summaries
- future HMI integration
- future vehicle-system interfaces

The current implementation remains a research and portfolio prototype.

It is not a certified safety system.

---

## 14. Mirroring Policy

Horizontal mirroring must be configurable.

Recommended behavior:

```text
Live webcam:
optional mirror for user-friendly display

Recorded video:
no mirror by default

Datasets:
no mirror unless explicitly required
```

Uncontrolled mirroring can change:

```text
left/right semantics
driver orientation
camera geometry
annotation correspondence
hand-side interpretation
head-pose interpretation
```

Mirroring must never be applied automatically to all sources.

Milestone 4A will introduce a configurable mirror option.

---

## 15. Dataset and Recording Policy

External datasets and private recordings must remain outside Git history.

Recommended local structure:

```text
data/
├── README.md
├── external/
│   └── dmd/
├── private/
│   └── cabin_recordings/
└── samples/
```

Repository policy:

```text
data/external/ must not be committed
data/private/ must not be committed
private cabin recordings must not be committed
dataset videos must not be redistributed
only approved evidence may be published
```

The repository may contain:

- code
- documentation
- configuration
- public metadata
- legally distributable examples
- anonymized or privacy-preserving validation evidence

The repository should not contain:

- private raw recordings
- personal unblurred screenshots
- restricted datasets
- confidential industrial material
- license-restricted video files

---

## 16. Configuration Strategy

Thresholds and temporal parameters must not remain permanently hard-coded.

The initial Milestone 4B implementation may use a Python dataclass.

Example parameters:

```text
eye_closed_threshold
mouth_open_threshold
prolonged_eye_closure_seconds
sustained_mouth_open_seconds
face_loss_seconds
smoothing_window_size
```

Future configuration may move to:

```text
config/path_01.yaml
```

This enables:

- reproducible experiments
- dataset-specific configurations
- subject-specific calibration
- controlled parameter comparison
- cleaner validation reports

A large configuration framework should not be introduced before it is needed.

---

## 17. Logging and Experiment Traceability

Future experiments should record:

```text
source name
configuration
timestamp
software version
Git commit
processing FPS
detected events
state transitions
evaluation results
```

Recommended future output structure:

```text
outputs/
├── figures/
├── logs/
├── videos/
└── experiments/
```

Each experiment should be reproducible from:

```text
source
configuration
Git commit
validation notes
```

---

## 18. Error Handling and Unknown States

The system must handle:

- camera open failure
- end of video
- missing face
- missing feature values
- invalid timestamps
- unsupported video files
- corrupted frames
- low-confidence perception
- inconsistent multimodal evidence

The system should prefer:

```text
UNKNOWN
NOT_AVAILABLE
LOW_CONFIDENCE
```

instead of forcing an incorrect behavioral classification.

---

## 19. Future Multi-Camera and Multimodal Extension

The long-term architecture should support:

```text
face camera
body camera
hand camera
RGB stream
IR stream
depth stream
vehicle signals
physiological signals
```

Possible future modalities include:

```text
EEG
ECG
GSR
SpO2
steering input
vehicle speed
lane position
pedal activity
```

The current frame metadata design should remain extensible for future synchronization and multimodal fusion.

Multi-camera synchronization is not part of Milestone 4A.

---

## 20. Current Implementation Status

Completed:

```text
Milestone 1 — Webcam Smoke Test
Milestone 2 — MediaPipe Face Mesh Landmark Pipeline
Milestone 3 — EAR and MAR Facial Geometry Features
```

Current implemented pipeline:

```text
webcam
  ↓
OpenCV acquisition
  ↓
MediaPipe Face Mesh
  ↓
selected facial landmarks
  ↓
EAR / MAR extraction
  ↓
real-time visualization
```

Next:

```text
Milestone 4A — Source-Independent Video Acquisition
Milestone 4B — Face-Level Temporal State Baseline
```

---

## 21. Milestone 4 Architectural Decisions

### 21.1 Milestone 4A

Milestone 4A will introduce:

- source-independent acquisition
- webcam input
- local file-video input
- common frame packets
- frame index
- deterministic source timestamps
- processing FPS separation
- configurable mirroring

Planned modules:

```text
src/acquisition/
├── __init__.py
└── video_source.py
```

Milestone 4A will validate the existing face and EAR/MAR pipeline using:

```text
live webcam
local MP4 file
recorded cabin video
DMD sample video when available
```

### 21.2 Milestone 4B

Milestone 4B will introduce:

- temporal smoothing
- eye-closure duration
- mouth-opening duration
- face-loss duration
- blink candidates
- prolonged eye-closure candidates
- sustained mouth-opening candidates
- prolonged face-loss candidates

Planned modules:

```text
src/temporal/
├── __init__.py
└── facial_state.py
```

Milestone 4B will not yet introduce:

- final drowsiness classification
- final distraction classification
- multimodal driver-state fusion
- ML sequence models
- full DMD training pipeline

These capabilities will be introduced only after the required perception channels and evaluation protocol are available.

---

## 22. Long-Term Development Roadmap

```text
M1   Webcam acquisition
M2   Face Mesh landmarks
M3   Facial geometry: EAR and MAR

M4A  Source-independent video acquisition
M4B  Face-level temporal state baseline

M5   Head-pose estimation
M6   Gaze estimation
M7   Body-pose features
M8   Hand-activity analysis
M9   Unified temporal feature interface
M10  Multimodal driver-behavior baseline
M11  ML/XAI behavior modeling
M12  Dataset evaluation and benchmarking
```

The roadmap may evolve as validation results and research findings become available.

---

## 23. Current Architectural Boundary

The immediate implementation boundary is:

```text
input abstraction
        ↓
shared frame packet
        ↓
existing face perception
        ↓
EAR / MAR
        ↓
offline and live validation
```

The next boundary is:

```text
timestamped features
        ↓
face-level temporal events
```

High-level multimodal behavior classification remains outside the current milestone.

---

## 24. Architecture Review Checklist

- [x] Acquisition separated from perception
- [x] Source time separated from processing time
- [x] Perception separated from temporal reasoning
- [x] Temporal events separated from behavior classification
- [x] Mirroring policy defined
- [x] Dataset and privacy policy defined
- [x] Future multimodal extension considered
- [x] Milestone 4 scope defined
- [ ] Architecture reviewed after Milestone 4A implementation
- [ ] Architecture version updated after validation