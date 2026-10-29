# Path 1 — Milestone 8 Validation: Hand Activity Analysis

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 8 |
| Validation Date | 2026-10-29 |
| Status | Live geometry/spatial integration PASSED at prototype scope; deterministic regression PENDING; temporal identity refinement OPEN |
| Author | Bassem Soliman |
| Python | 3.11 |
| Operating System | Windows 11 development workstation |
| Live Source | RGB webcam |
| Recorded Evidence | Private self-collected screen/video recordings |
| Repository Branch | feat/hand-activity-analysis |

---

# 1. Validation Objective

Evaluate whether the M8 implementation can provide usable prototype-level hand detection, hand geometry, coarse spatial context and temporal measurements while preserving the previously implemented M1–M7 perception pipeline.

The validation is deliberately separated into:

1. frame-level hand detection and geometry;
2. coarse spatial-region behavior;
3. temporal tracking behavior;
4. integrated M1–M8 runtime behavior;
5. deterministic regression testing.

The available evidence supports prototype functionality. It does not establish behavioral recognition accuracy, tracking identity accuracy, generalization or safety performance.

---

# 2. Test Environment

The milestone was exercised on a Windows development workstation using a frontal RGB webcam and the existing Path 1 Python environment.

The perception stack includes OpenCV, MediaPipe Face Mesh, MediaPipe Pose and MediaPipe Hands. The same source-independent acquisition architecture remains available for webcam and recorded-file input.

No depth camera, calibrated cabin model, steering-wheel detector, motion-capture system or independently labeled hand-activity dataset was used.

---

# 3. Prototype Configuration

Representative M8 prototype settings include:

| Parameter | Setting |
|---|---:|
| Maximum detected hands | 2 |
| CLOSED mean-extension threshold | approximately 1.45 |
| OPEN mean-extension threshold | approximately 2.05 |
| Near-face normalized-distance threshold | approximately 1.10 |
| Torso lateral margin | approximately 0.65 × shoulder width |
| Lower-region start | approximately 0.65 of shoulder–hip vertical span |
| Lower-region extension | approximately 0.80 × torso length |
| Temporal maximum match distance | approximately 320 px in latest refinement |
| Temporary missing tolerance | approximately 0.60 s |
| Handedness mismatch penalty | approximately 50 px-equivalent score |

These are prototype development parameters, not universal thresholds.

---

# 4. M8.1 Hand Detection and Geometry

## 4.1 One-Hand Detection

A controlled webcam test showed a single detected hand with the frame-level visibility state:

```text
SINGLE_HAND
```

The detector returned selected hand landmarks, handedness metadata and valid palm geometry.

## 4.2 Two-Hand Detection

A controlled two-hand test produced:

```text
TWO_HANDS
```

Both hands were processed independently by the geometry extractor.

## 4.3 Coarse Hand Shape

The initial OPEN threshold of approximately 2.15 classified a visually open hand with mean normalized extension around 2.13 as `INTERMEDIATE`.

The OPEN threshold was therefore refined to approximately 2.05 during prototype tuning.

Observed examples included:

- a clearly closed hand with mean normalized extension around 1.44 → `CLOSED`;
- visually open hands around 2.0–2.13 → `OPEN` after threshold refinement;
- intermediate configurations retained `INTERMEDIATE`.

These observations demonstrate the implemented threshold behavior. They do not establish person-independent gesture recognition accuracy.

---

# 5. M8.2 Spatial Region Validation

The spatial estimator was exercised with controlled hand placement.

Observed region states included:

```text
NEAR_FACE
TORSO_REGION
LOWER_REGION
OUTSIDE_BODY_REGION
```

A near-face example produced normalized hand-to-face distance around `0.65`, below the current threshold of approximately `1.10`.

Early body-region testing showed that the original lateral margin was too narrow for practical hand positions. The torso lateral margin was widened to approximately `0.65 × shoulder_width`.

Subsequent controlled observations demonstrated:

- hand clearly near the face → `NEAR_FACE`;
- hand over chest / upper abdomen → `TORSO_REGION`;
- hand around lap / lower torso → `LOWER_REGION`;
- hand clearly lateral to the body band → `OUTSIDE_BODY_REGION`.

Boundary variability was observed and is expected because the current implementation uses simple 2D partitions and frame-level landmarks.

M8.2 was therefore accepted at prototype scope without indefinite threshold tuning.

---

# 6. M8.3 Temporal Tracking Validation

## 6.1 Implemented Temporal Outputs

The temporal smoke test displayed:

```text
T1 / T2 / ...
VISIBLE
TEMPORARILY_MISSING
LOST
region dwell time
image-space speed
missing duration
```

This confirmed that the temporal code path and visualization were active.

## 6.2 Observed Identity Failure

Repeated live recordings exposed significant track-ID proliferation.

Instead of maintaining stable long-term identities such as only `T1` and `T2`, the tracker created new IDs after ordinary detection interruptions and hand motion.

Observed sequences progressed through multiple identifiers, including IDs substantially beyond `T2`.

A first refinement increased the matching gate, reduced the handedness penalty, added short-term motion prediction and pruned stale LOST tracks. Cleanup improved, but persistent identity remained unstable.

## 6.3 Validation Assessment

The following temporal capabilities are considered implemented:

- track lifecycle state;
- missing duration;
- track age;
- spatial dwell;
- displacement;
- image-space speed.

The following capability is **not validated**:

- stable long-term physical-hand identity.

The current temporal layer is therefore retained as an experimental prototype. A persistent two-slot tracker is identified as a future refinement.

This limitation is explicitly documented and does not block continuation of the fast-prototype research path because higher-level behavior interpretation is not yet being claimed.

---

# 7. M8.4 Integrated M1–M8 Validation

After integration into `main.py` and `visualization.py`, a private integrated recording of approximately one minute was reviewed.

The recording showed the following modules operating together:

```text
Face landmark processing
EAR / MAR
Face-level temporal state
Head pose
Gaze
M7 body pose / posture panel
M8 hand detection
M8 hand shape
M8 spatial region
M8 temporal-track measurements
```

The application remained active throughout the reviewed recording without an obvious runtime crash.

The hand panel responded to changes in hand count and hand position.

M7 remained visible in the integrated application. In this particular recording, sagittal posture remained `NOT_CALIBRATED` because neutral calibration was not initiated during the session. This is expected M7 behavior and is not an M8 integration failure.

The integrated recording therefore supports:

**M8.4 full-pipeline integration — PASS at prototype scope.**

---

# 8. Deterministic Regression Validation

Deterministic M8 regression tests are **pending** at the time this validation report was prepared.

They should be implemented without webcam inference so that geometric and temporal rules can be checked reproducibly using synthetic dataclass inputs.

The recommended test suite is:

| Test | Purpose | Expected result |
|---|---|---|
| `test_open_hand_geometry` | Synthetic fingertip geometry clearly above OPEN threshold | valid geometry + `OPEN` |
| `test_closed_hand_geometry` | Synthetic fingertips close to wrist | valid geometry + `CLOSED` |
| `test_intermediate_hand_geometry` | Synthetic mean extension between thresholds | `INTERMEDIATE` |
| `test_invalid_missing_landmarks` | Required landmark omitted | invalid geometry + `UNKNOWN` |
| `test_near_face_region` | Palm center within normalized face threshold | `NEAR_FACE` |
| `test_torso_region` | Palm inside body band and upper torso span | `TORSO_REGION` |
| `test_lower_region` | Palm inside body band below torso split | `LOWER_REGION` |
| `test_outside_body_region` | Palm far outside body band | `OUTSIDE_BODY_REGION` |
| `test_unknown_without_reference_geometry` | No usable face/body reference | `UNKNOWN` |
| `test_temporal_visible_track` | Repeated nearby observations | same track remains `VISIBLE` |
| `test_temporarily_missing` | No observation for less than missing tolerance | `TEMPORARILY_MISSING` |
| `test_lost_after_timeout` | No observation beyond tolerance | `LOST` |
| `test_region_dwell_reset` | Track changes spatial region | dwell resets near zero |
| `test_speed_and_displacement` | Known two-position movement over known time | expected displacement and speed |
| `test_tracker_reset` | Reset after active tracking | no previous track state retained |

Because stable long-term identity is a known limitation, the deterministic suite should **not** include a claim that the current algorithm reliably preserves identity through arbitrary long occlusion or hand crossing.

---

# 9. Recommended Deterministic Test Procedure

From:

```text
paths/01_fast_prototype/
```

first compile the source:

```bash
python -m compileall src
```

Then create:

```text
src/tests/test_m8_hand_activity_regression.py
```

Use synthetic `HandLandmark`, `DetectedHand`, face-landmark, body-geometry and `HandObservation` objects. Do not instantiate the webcam detector for these tests.

Run only M8:

```bash
PYTHONPATH=src python -m unittest discover   -s src/tests   -p "test_m8_hand_activity_regression.py"   -v
```

If all M8 tests pass, run the full deterministic regression set:

```bash
PYTHONPATH=src python -m unittest discover   -s src/tests   -p "test_*.py"   -v
```

The final M8 report should record the exact test count and terminal result only after the user actually runs the suite.

---

# 10. Recorded-File Regression Still Required

After deterministic tests pass, run the integrated program on a controlled private video:

```bash
PYTHONPATH=src python -m main   --source file   --video-path "<PRIVATE_TEST_VIDEO>"
```

If the opening sequence is independently known to be neutral and M7 calibration is desired:

```bash
PYTHONPATH=src python -m main   --source file   --video-path "<PRIVATE_TEST_VIDEO>"   --auto-calibrate-file
```

Verify:

- source opens;
- face/head/gaze remain active;
- body path remains active;
- hand count changes appropriately;
- M8 dashboard updates;
- no exception occurs;
- end-of-file is detected;
- detector resources close;
- application prints clean completion.

This test validates the integrated execution path, not algorithmic accuracy.

---

# 11. Known Issues

## Issue 1 — Temporal Track-ID Proliferation

**Observation:** new IDs can appear after ordinary hand interruptions.

**Current handling:** document the limitation; do not treat track ID as stable anatomical identity.

**Future improvement:** persistent two-slot tracker and controlled identity evaluation.

## Issue 2 — Spatial Boundary Jitter

**Observation:** hands near torso/lower/outside boundaries can change region with small landmark motion.

**Current handling:** accept at prototype scope.

**Future improvement:** temporal hysteresis and cabin-coordinate modeling.

## Issue 3 — Coarse Hand Shape

**Observation:** fingertip-distance geometry does not distinguish many articulated hand configurations.

**Current handling:** only OPEN/CLOSED/INTERMEDIATE/UNKNOWN is reported.

**Future improvement:** joint-angle features or learned hand-state models when justified by task requirements.

## Issue 4 — Handedness Is a Soft Cue

**Observation:** MediaPipe handedness may change with viewpoint, mirroring and detector uncertainty.

**Current handling:** handedness must not be used as guaranteed physical identity.

---

# 12. Scientific Assessment

The available evidence supports the feasibility of adding a hand-perception branch to the existing Path 1 system without collapsing hand geometry directly into a behavioral or safety decision.

Frame-level detection, geometry and coarse spatial context are sufficiently functional for the fast-prototype path. Temporal lifecycle measurements are also available, but stable identity is not yet reliable.

Therefore the milestone should be described as:

**hand activity geometry and temporal prototype integrated, with temporal identity refinement pending.**

It should not be described as validated driver hand-behavior recognition.

---

# 13. Privacy / Evidence Handling

The reviewed webcam and screen recordings contain private human imagery and should remain outside the public repository unless explicit consent and redistribution rights are established.

Validation documentation should contain derived observations and test results rather than private raw video.

Before commit:

```bash
git status
git diff --cached
```

Confirm that no private MP4, screenshots or generated personal-media artifacts are staged.

---

# 14. Validation Completion Checklist

## M8.1 Frame-Level Detection / Geometry

- [x] Single-hand detection observed
- [x] Two-hand detection observed
- [x] Palm geometry observed
- [x] OPEN / CLOSED / INTERMEDIATE states exercised
- [x] Invalid/UNKNOWN behavior implemented
- [ ] Deterministic geometry regression tests passed

## M8.2 Spatial Regions

- [x] NEAR_FACE observed
- [x] TORSO_REGION observed
- [x] LOWER_REGION observed
- [x] OUTSIDE_BODY_REGION observed
- [x] Prototype boundary limitation documented
- [ ] Deterministic spatial-region tests passed

## M8.3 Temporal Layer

- [x] VISIBLE state observed
- [x] TEMPORARILY_MISSING / LOST lifecycle implemented
- [x] Dwell and speed displayed
- [x] Track-ID proliferation reproduced
- [x] Temporal identity limitation documented
- [ ] Deterministic lifecycle / dwell / speed tests passed
- [ ] Persistent long-term identity refinement (future work; not current milestone exit criterion)

## M8.4 Integration

- [x] M8 integrated with M1–M7
- [x] Integrated webcam/dashboard recording reviewed
- [x] No obvious runtime crash in reviewed integrated session
- [ ] Final controlled recorded-file regression passed
- [ ] Full deterministic M1–M8 regression suite passed

## Repository Closure

- [x] M8 implementation report prepared
- [x] M8 validation report prepared
- [x] README update prepared
- [ ] Final Git diff / privacy review completed
- [ ] Feature branch committed and pushed
- [ ] Pull request reviewed and merged
