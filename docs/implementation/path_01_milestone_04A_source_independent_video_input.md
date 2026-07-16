# Path 1 — Milestone 4A: Source-Independent Video Input

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 4A |
| Status | Completed |
| Date | 2026-07-16 |
| Author | Bassem Soliman |
| Repository | safety-critical-in-cabin-driver-monitoring |

---

# 1. Objective

The objective of this milestone is to decouple the perception pipeline from direct webcam acquisition and introduce a source-independent video input architecture.

The milestone adds support for:

- live webcam input
- local video-file input
- recorded cabin videos
- dataset sample videos
- source timestamps
- source frame indices
- configurable horizontal mirroring

The same facial perception and geometry pipeline can now operate without knowing whether frames originate from a live camera or a recorded video.

---

# 2. Motivation

The previous implementation was directly coupled to:

```python
cv2.VideoCapture(0)
```

This was sufficient for early webcam validation but created an architectural limitation.

The project is intended to process:

- live cabin-sensing cameras
- local MP4 files
- recorded experimental sessions
- DMD dataset samples
- future RGB, IR and NIR streams
- future synchronized multi-camera recordings

A webcam-specific implementation would require repeated refactoring when additional sources are introduced.

This milestone therefore introduces a common video-source interface before temporal reasoning, head-pose estimation, gaze analysis, body pose and hand activity are added.

The source-independent architecture also prepares the project for reproducible offline experiments.

---

# 3. Software Perspective

This milestone introduces a dedicated acquisition package.

New package:

```text
src/acquisition/
├── __init__.py
└── video_source.py
```

Updated modules:

- `src/main.py`
- `src/perception/visualization.py`
- `.gitignore`

The acquisition layer provides a shared interface through the abstract `VideoSource` class.

Concrete source implementations include:

- `WebcamVideoSource`
- `FileVideoSource`

Both implementations return the same `FramePacket` structure.

This separation allows `main.py` to execute one shared perception pipeline independently of the selected input source.

---

# 4. Computer Vision Perspective

The computer vision pipeline remains unchanged after frame acquisition.

Updated pipeline:

Input Source

↓

Source-Independent Frame Acquisition

↓

Frame Packet

↓

Optional Horizontal Mirroring

↓

BGR-to-RGB Conversion

↓

MediaPipe Face Mesh

↓

Selected Facial Landmarks

↓

EAR / MAR Feature Extraction

↓

Visualization

The main computer vision improvement is not a new detection algorithm.

The improvement is that the existing perception stack can now be validated on both live and recorded visual data.

This is important because computer vision algorithms must be tested under reproducible sequences, not only through interactive webcam demonstrations.

---

# 5. Python Perspective

This milestone introduces object-oriented abstraction for input sources.

The implementation uses:

- abstract base classes
- dataclasses
- type hints
- pathlib
- command-line argument parsing
- monotonic timing
- modular class-based design

The main data structure is:

```python
FramePacket
```

It contains:

- image frame
- frame index
- source timestamp
- source name

The abstract `VideoSource` interface defines:

- `source_name`
- `fps`
- `is_opened()`
- `read()`
- `release()`

The two source implementations follow the same interface, which reduces branching and duplicated logic inside `main.py`.

---

# 6. Engineering Perspective

This milestone introduces an explicit separation between:

```text
acquisition
perception
visualization
```

The engineering goal is:

```text
input source changes
perception pipeline remains unchanged
```

This separation is important for future scalability.

Without it, each new source type would require changes throughout the perception code.

The design also separates:

```text
source timestamp
processing FPS
```

The source timestamp represents the original or live source timeline.

Processing FPS represents how quickly the current computer processes frames.

Temporal reasoning must later use source timestamps rather than processing speed.

This ensures consistent temporal behavior during:

- real-time webcam operation
- slow offline processing
- fast offline processing
- dataset replay
- experiments on different computers

---

# 7. Implemented Components

## `src/acquisition/__init__.py`

Introduced package-level documentation for source-independent acquisition.

The package is intended to support:

- webcams
- local video files
- recorded cabin videos
- dataset videos
- future synchronized camera streams

---

## `src/acquisition/video_source.py`

Implemented:

- `FramePacket`
- `VideoSource`
- `WebcamVideoSource`
- `FileVideoSource`
- source FPS access
- source identification
- frame indexing
- source timestamps
- resource release

### `FramePacket`

The frame packet provides a common representation for downstream modules.

Fields:

```text
frame
frame_index
timestamp_seconds
source_name
```

### `WebcamVideoSource`

Implemented:

- configurable camera index
- live frame acquisition
- monotonic elapsed timestamps
- increasing frame index
- webcam source identification
- camera resource release

### `FileVideoSource`

Implemented:

- local video-file loading
- path normalization using `pathlib`
- source FPS extraction
- video timeline timestamps
- frame-index fallback timing
- file source identification
- end-of-file handling
- video resource release

---

## `src/main.py`

Updated:

- command-line argument parsing
- input-source selection
- webcam source creation
- file source creation
- optional mirroring
- shared perception execution
- source metadata display
- error handling for missing video paths
- error handling for unavailable sources

The main loop no longer directly constructs `cv2.VideoCapture`.

Instead, it receives a `VideoSource`.

---

## `src/perception/visualization.py`

Updated:

- source-time overlay
- frame-index overlay
- source-name overlay

The graphical code was moved out of `main.py` to preserve separation between orchestration and visualization.

---

## `.gitignore`

Updated to protect:

- external datasets
- private recordings
- local MP4 files
- AVI files
- MOV files
- MKV files

This prevents accidental publication of:

- DMD video samples
- private cabin recordings
- dataset-derived video evidence
- large local media files

---

# 8. Command-Line Interface

The pipeline now supports command-line source selection.

## Webcam input

```bash
python src/main.py --source webcam --camera-index 0
```

## Webcam input with mirroring

```bash
python src/main.py --source webcam --camera-index 0 --mirror
```

## Local video-file input

```bash
python src/main.py \
  --source file \
  --video-path "/path/to/video.mp4"
```

## Available arguments

```text
--source
--camera-index
--video-path
--mirror
```

### `--source`

Supported values:

```text
webcam
file
```

### `--camera-index`

Defines the OpenCV webcam index.

Default:

```text
0
```

### `--video-path`

Defines the local path used by `FileVideoSource`.

This argument is required when:

```text
--source file
```

### `--mirror`

Horizontally flips the frame.

This option is intended mainly for user-friendly webcam visualization.

---

# 9. Mirroring Policy

Horizontal mirroring is now configurable.

Recommended usage:

```text
Live webcam:
optional mirroring

Recorded videos:
no mirroring by default

Datasets:
no mirroring unless explicitly required
```

Mirroring changes left-right orientation.

This may affect:

- driver hand side
- head-turn direction
- gaze direction
- body orientation
- annotation correspondence
- future camera calibration

The milestone therefore removes unconditional mirroring from the shared pipeline.

---

# 10. Project Architecture Impact

Previous architecture:

Webcam

↓

OpenCV `VideoCapture(0)`

↓

Face Mesh

↓

EAR / MAR

↓

Visualization

Updated architecture:

Webcam Source or File Source

↓

Common `VideoSource` Interface

↓

`FramePacket`

↓

Shared Perception Pipeline

↓

Face Mesh

↓

EAR / MAR

↓

Source and Perception Visualization

Future architecture:

Live Camera / Recorded Video / Dataset / Sensor Stream

↓

Acquisition Layer

↓

Timestamped Frame Packet

↓

Multimodal Perception

↓

Temporal Feature Analysis

↓

Behavior Modeling

↓

Driver-State Estimation

↓

Explainable Decision Output

---

# 11. System Interfaces

## Inputs

### Webcam source

```text
camera index
```

### File source

```text
local video path
```

## Acquisition outputs

Each source returns:

```text
FramePacket
```

containing:

- OpenCV BGR frame
- zero-based frame index
- timestamp in seconds
- readable source name

## Downstream consumers

The frame packet is consumed by:

- `main.py`
- MediaPipe Face Mesh
- facial geometry extraction
- visualization
- future temporal state analysis
- future experiment logging

## Dependencies

- Python
- OpenCV
- NumPy
- MediaPipe
- pathlib
- argparse

---

# 12. Validation Summary

Manual validation was performed using:

- live webcam
- mirrored live webcam
- local MP4 video
- DMD face-camera sample
- missing video-path input
- invalid file path

The following behavior was verified:

- webcam input opens correctly
- file-video input opens correctly
- DMD video is processed through the shared pipeline
- source time increases
- frame index increases
- Face Mesh remains functional
- EAR and MAR remain functional
- mirroring works only when requested
- missing file-path arguments are handled
- invalid sources are handled
- the application exits cleanly using `q`

Validation details are documented in:

```text
docs/validation/path_01_milestone_04A_source_independent_video_input_validation.md
```

Planned validation evidence:

```text
paths/01_fast_prototype/outputs/figures/
path_01_milestone_04A_source_independent_video_input.png
```

---

# 13. Limitations

Current limitations:

- only one video stream is processed at a time
- no multi-camera synchronization
- no IR-specific preprocessing
- no depth-video input
- no automatic output-video recording yet
- no experiment CSV logger
- no automated unit tests for acquisition classes
- end-of-file and frame-read failure use the same simplified return value
- no playback-speed control
- no pause or seek controls
- source metadata remains limited to basic fields

These limitations are acceptable for Milestone 4A.

---

# 14. Future Scalability

The source-independent architecture prepares the system for:

- recorded cabin experiments
- DMD dataset evaluation
- RGB camera input
- IR and NIR camera input
- synchronized face, body and hand cameras
- ROS image topics
- network or IP cameras
- annotated output-video generation
- experiment logging
- temporal signal analysis
- reproducible benchmark execution

The `FramePacket` structure can later be extended with:

```text
camera_id
modality
session_id
subject_id
sequence_id
source_fps
synchronization_timestamp
```

The current abstraction also allows new source classes to be introduced without changing the perception modules.

---

# 15. Research / Technology Notes

Live webcam validation is useful for rapid prototyping but is not sufficient for scientific evaluation.

Recorded video input enables:

- reproducible experiments
- repeated evaluation on identical frames
- controlled comparisons
- event-level analysis
- deterministic temporal validation
- dataset benchmarking

The DMD sample was used locally as an external dataset input source.

Dataset-derived videos remain local and are not distributed through the public repository.

Public evidence should focus on:

- plots
- screenshots
- architecture figures
- quantitative results
- approved recordings
- privacy-preserving demonstrations

---

# 16. Lessons Learned

This milestone demonstrated that acquisition should be separated before adding additional perception and temporal modules.

The same Face Mesh and EAR/MAR pipeline now works with both live and recorded data.

The milestone also showed the importance of distinguishing source timing from processing performance.

A source-independent architecture reduces future refactoring and makes the project more suitable for research experiments, dataset evaluation and multimodal expansion.

Moving source overlays into the visualization module also improved separation of responsibilities.

---

# 17. Next Milestone

The next milestone is:

**Path 1 — Milestone 4B: Face-Level Temporal State Baseline**

The goal will be to transform frame-level features into time-dependent event candidates.

Planned temporal features include:

- EAR smoothing
- MAR smoothing
- blink duration
- prolonged eye-closure duration
- sustained mouth-opening duration
- face-loss duration

Planned output candidates include:

```text
BLINK_CANDIDATE
PROLONGED_EYE_CLOSURE
SUSTAINED_MOUTH_OPENING
PROLONGED_FACE_LOSS
```

The milestone will not yet claim final drowsiness, distraction or unresponsive-driver classifications.

---

# Milestone Completion Checklist

- [x] Software implementation completed
- [x] Computer vision functionality verified
- [x] Webcam input validated
- [x] Mirrored webcam input validated
- [x] Local video input validated
- [x] DMD sample input validated
- [x] Private-data protection added
- [x] Architecture separation completed
- [x] Documentation completed
- [x] Validation documentation completed
- [x] Evidence stored
- [x] README updated
- [x] Git commit completed
- [x] GitHub updated
- [x] Ready for final milestone closure