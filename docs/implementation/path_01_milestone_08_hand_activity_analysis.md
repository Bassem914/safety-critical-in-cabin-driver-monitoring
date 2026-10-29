# Path 1 — Milestone 8: Hand Activity Analysis

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 8 |
| Status | Prototype implemented and integrated; deterministic regression validation pending |
| Date | 2026-10-29 |
| Author | Bassem Soliman |
| Repository | safety-critical-in-cabin-driver-monitoring |
| Branch | feat/hand-activity-analysis |
| Python | 3.11 |
| Primary CV Stack | OpenCV + MediaPipe |

---

# 1. Objective

Extend the existing source-independent in-cabin perception prototype with interpretable hand-level geometry, coarse spatial context and an experimental temporal tracking layer, while preserving the previously implemented facial geometry, face-level temporal rules, head pose, gaze and body-posture modules.

Milestone 8 is intentionally limited to **observable geometric and temporal hand states**. It does not infer phone use, hands-off-wheel behavior, distraction, engagement, impairment, driver intent or safety-critical intervention.

---

# 2. Implemented Scope

Milestone 8 is divided into four prototype stages:

| Stage | Capability | Status |
|---|---|---|
| M8.1 | Hand detection and basic geometry | Implemented |
| M8.2 | Spatial hand-region estimation | Implemented |
| M8.3 | Temporal hand tracking | Implemented as prototype; identity refinement pending |
| M8.4 | Integration into the full M1–M8 pipeline | Integrated and visually exercised |

Current outputs include:

```text
Hand count
Hand visibility state
Selected hand landmarks
Palm center
Palm width / palm length
Normalized finger-extension geometry
OPEN / CLOSED / INTERMEDIATE / UNKNOWN
NEAR_FACE / TORSO_REGION / LOWER_REGION / OUTSIDE_BODY_REGION / UNKNOWN
Temporal track ID
VISIBLE / TEMPORARILY_MISSING / LOST
Spatial dwell time
Image-space displacement
Image-space speed
```

These outputs remain prototype measurements and labels.

---

# 3. Software Components

Milestone 8 introduces or extends the following components:

| Module | Responsibility |
|---|---|
| `src/perception/hand_features.py` | MediaPipe Hands wrapper, selected landmarks, hand geometry, coarse hand-shape state and spatial-region estimation |
| `src/perception/hand_tracking.py` | Experimental temporal association, track lifecycle, dwell time, displacement and image-space speed |
| `src/experiments/hand_activity_smoke_test.py` | Isolated M8 webcam experiment for detection, geometry, spatial regions and temporal tracking |
| `src/main.py` | Full M1–M8 integration using the existing source-independent `VideoSource` abstraction |
| `src/perception/visualization.py` | Integrated hand-landmark, temporal-track and M8 dashboard visualization |
| `src/tests/test_m8_hand_activity_regression.py` | Planned deterministic regression suite for geometry, spatial rules and temporal lifecycle |

The hand detector is independent from the face and body detectors. The full application therefore combines three perception branches: Face Mesh, Pose and Hands.

---

# 4. Selected Hand Landmarks

The prototype retains a compact subset of MediaPipe Hands landmarks:

```text
wrist          = 0
thumb_tip      = 4
index_mcp      = 5
index_tip      = 8
middle_mcp     = 9
middle_tip     = 12
ring_mcp       = 13
ring_tip       = 16
pinky_mcp      = 17
pinky_tip      = 20
```

The retained landmarks are sufficient for the current palm-scale and finger-extension baseline without introducing unnecessary feature complexity at this stage.

MediaPipe handedness is stored as a **model-provided label and confidence score**. It is not treated as guaranteed anatomical identity.

---

# 5. Hand Visibility State

The frame-level detector reports:

```text
NOT_DETECTED
SINGLE_HAND
TWO_HANDS
```

The prototype supports at most two detected hands per frame.

The current-frame detection identifiers `D1` and `D2` are visualization labels only. They are not persistent temporal identities.

---

# 6. Hand Geometry

For each detected hand, the geometry extractor computes a palm center from the MCP landmarks and two palm-scale measures:

```text
palm_width  = distance(index_mcp, pinky_mcp)
palm_length = distance(wrist, middle_mcp)
palm_scale  = max(palm_width, palm_length)
```

Finger-extension features are normalized by `palm_scale`:

```text
normalized_extension =
    distance(wrist, fingertip) / palm_scale
```

The mean normalized extension is calculated over index, middle, ring and pinky fingers.

The current prototype thresholds are approximately:

```text
mean extension <= 1.45  -> CLOSED
mean extension >= 2.05  -> OPEN
otherwise               -> INTERMEDIATE
```

Invalid or insufficient geometry produces `UNKNOWN`.

These thresholds are development settings derived from controlled prototype observations. They are not anatomical, clinical, ergonomic or production DMS thresholds.

---

# 7. Spatial Hand Regions

Milestone 8.2 adds coarse image-space context using the existing face and body modules.

The available region states are:

```text
NEAR_FACE
TORSO_REGION
LOWER_REGION
OUTSIDE_BODY_REGION
UNKNOWN
```

## 7.1 Near-Face Geometry

The face center is estimated from the selected forehead and chin landmarks. Face scale is the pixel distance between forehead and chin.

The hand-to-face measure is:

```text
normalized_face_distance =
    distance(palm_center, face_center) / face_scale
```

The current prototype near-face threshold is approximately:

```text
normalized_face_distance <= 1.10 -> NEAR_FACE
```

## 7.2 Body-Referenced Regions

When valid M7 body geometry exists, the body-referenced region logic uses:

- shoulder midpoint
- hip midpoint
- shoulder width
- torso length

The horizontal body band is expanded using a lateral margin of approximately `0.65 × shoulder_width`.

The lower-region split begins approximately `0.65` of the shoulder-to-hip vertical span below the shoulder midpoint. The lower region extends beyond the hip line by approximately `0.80 × torso_length`.

These are simple 2D geometric partitions. Boundary changes between adjacent regions can occur because of landmark jitter, perspective and natural motion.

---

# 8. Temporal Hand Tracking

Milestone 8.3 introduces an experimental temporal layer.

The track lifecycle is:

```text
VISIBLE
TEMPORARILY_MISSING
LOST
```

Tracked quantities include:

```text
track ID
track age
missing duration
spatial region
region dwell time
frame-to-frame displacement
image-space speed
```

The tracker uses palm-center proximity as its primary association signal and MediaPipe handedness only as a soft cue.

Current prototype association parameters have included approximately:

```text
maximum match distance: 320 px
temporary missing tolerance: 0.60 s
handedness mismatch penalty: 50 px-equivalent score
```

These values are implementation parameters rather than validated physical motion limits.

---

# 9. Known Temporal-Identity Limitation

Continuous live testing exposed a clear limitation in the current temporal association strategy: ordinary detection interruptions can cause new track identifiers to be created even when the physical hand is the same.

During development, repeated IDs such as `T1`, `T2`, `T3`, ... were observed instead of maintaining only two stable long-term hand identities.

Several refinements improved cleanup but did not fully solve persistent identity.

This issue is explicitly retained as a **future refinement** rather than hidden by relabeling the output.

A likely future architecture is a persistent two-slot tracker because the cabin prototype expects at most two hands. Such a tracker can retain `T1` / `T2` lifecycle state through temporary loss and use spatial continuity plus handedness for reactivation.

For the current milestone:

- temporal lifecycle measurements are available;
- dwell and image-space speed are available;
- long-term identity persistence is **not validated**;
- track ID must not be used as reliable biometric or anatomical identity.

---

# 10. Full-Pipeline Integration

Milestone 8.4 integrates the hand branch with the existing pipeline:

```text
WebcamVideoSource / FileVideoSource
                  |
              FramePacket
                  |
      +-----------+-----------+
      |           |           |
 Face Mesh      Pose        Hands
      |           |           |
 EAR/MAR       M7 body     M8 geometry
 head pose     geometry     hand shape
 gaze          posture      spatial region
 temporal                    temporal track
      +-----------+-----------+
                  |
          Integrated dashboard
```

The integrated application preserves:

- source-independent webcam/file acquisition;
- facial geometry and face-level temporal state;
- geometric head pose;
- gaze estimation;
- M7 body geometry and calibration;
- M8 hand geometry, regions and temporal outputs;
- clean shutdown of face, body and hand detector resources.

A recorded integrated M1–M8 webcam session of approximately one minute was visually reviewed after integration. Face/head/gaze, body pose and hand activity were simultaneously present without an observed application crash. The body sagittal state remained uncalibrated in that particular session because M7 neutral calibration was not initiated; this is not an M8 failure.

---

# 11. Visualization

The integrated dashboard presents separate channels rather than collapsing them into a behavioral label.

The M8 panel displays:

```text
number of hands
visibility state
model handedness label / confidence
coarse hand shape
spatial region
normalized face distance when available
temporal track state
region dwell time
image-space speed
```

The image overlay also distinguishes:

```text
D* = current-frame detection
T* = temporal prototype track
```

The dashboard explicitly states that the outputs are geometric only and that temporal identity persistence requires refinement.

---

# 12. Scientific Interpretation

Milestone 8 does **not** equate a geometric state with a driver behavior.

Examples:

```text
NEAR_FACE != phone use
LOWER_REGION != hands off steering wheel
CLOSED != gripping an object
TEMPORARILY_MISSING != unsafe hand state
LOST != driver impairment
```

A future behavioral layer would require temporal context, object evidence, steering-wheel/vehicle context, task definition and independent validation.

---

# 13. Validation Status

Evidence completed before documentation closure:

- isolated one-hand detection;
- isolated two-hand detection;
- OPEN / CLOSED / INTERMEDIATE geometry observations;
- `NEAR_FACE` observation;
- `TORSO_REGION` observation;
- `LOWER_REGION` observation;
- `OUTSIDE_BODY_REGION` observation;
- temporal lifecycle visualization;
- temporal dwell and speed visualization;
- identification of temporal-ID instability;
- full M1–M8 integrated webcam/dashboard run.

Still pending at the time of this report:

- deterministic M8 regression suite;
- final recorded-file regression through integrated `main.py`;
- formal Git diff / privacy review;
- final commit, pull request and merge.

---

# 14. Limitations

## 14.1 2D image-space geometry

Spatial regions are camera-view dependent and do not represent metric cabin coordinates.

## 14.2 Hand shape is coarse

The OPEN/CLOSED/INTERMEDIATE state is based on normalized fingertip distance, not articulated finger-joint reconstruction or object-aware grasp recognition.

## 14.3 Region boundaries are heuristic

Near-face and body-region thresholds are provisional and can fluctuate near boundaries.

## 14.4 Dependency on M7 geometry

Torso and lower-body regions require valid body geometry. Missing shoulders/hips can reduce spatial classification to `UNKNOWN` when the hand is not near the face.

## 14.5 Temporal identity instability

The current tracker can generate new IDs after interruptions or association failures. Persistent two-hand identity remains future work.

## 14.6 MediaPipe handedness

The handedness output is model-reported and camera/mirroring dependent. It must not be interpreted as guaranteed anatomical identity.

## 14.7 No object semantics

The prototype does not detect phones, steering wheels, food, drinks, controls or other objects.

## 14.8 No safety-performance claim

No false-positive rate, recall, behavioral accuracy, driver-risk metric, functional-safety qualification or production DMS performance is established.

---

# 15. Future Refinements

Future M8 research may include:

- persistent two-slot temporal tracking;
- stronger motion association and re-identification;
- temporal smoothing / hysteresis for spatial regions;
- steering-wheel geometry;
- object-aware hand interaction;
- 3D or cabin-coordinate hand localization;
- hand/body occlusion studies;
- annotated driver-hand activity datasets;
- quantitative tracking and region-classification metrics.

These are future research tasks rather than completion claims for the present prototype.

---

# 16. Next Step

Complete deterministic M8 regression tests and a final source-independent recorded-file regression. After repository closure, proceed to **Milestone 9 — Unified Temporal Feature Layer**, where hand, gaze, head and body channels can begin to be synchronized into higher-level temporal features without prematurely assigning driver-behavior or safety semantics.

---

# Milestone Completion Checklist

## Implementation

- [x] MediaPipe Hands wrapper implemented
- [x] Up to two hands supported
- [x] Selected hand landmarks extracted
- [x] Palm geometry implemented
- [x] OPEN / CLOSED / INTERMEDIATE / UNKNOWN prototype states implemented
- [x] Face/body-referenced spatial regions implemented
- [x] Temporal lifecycle, dwell, displacement and speed implemented
- [x] M1–M8 full-pipeline integration implemented
- [x] Integrated hand dashboard implemented

## Validation

- [x] One-hand and two-hand live detection observed
- [x] Coarse hand-shape states observed
- [x] Near-face / torso / lower / outside-body regions observed
- [x] Temporal lifecycle visualization exercised
- [x] Integrated M1–M8 webcam/dashboard run completed
- [x] Temporal identity instability reproduced and documented
- [ ] Deterministic M8 regression suite passed
- [ ] Final integrated recorded-file regression completed

## Documentation / Repository Closure

- [x] M8 implementation report prepared
- [x] M8 validation report prepared
- [x] README prepared for M8 status
- [ ] Final private-media exclusion and Git diff reviewed
- [ ] Commit, pull request and merge completed
