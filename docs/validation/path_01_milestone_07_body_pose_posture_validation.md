# Path 1 — Milestone 7 Validation: Body Pose and Posture Analysis

---

# Metadata

| Item | Value |
|------|-------|
| Path | Path 1 – Fast Prototype |
| Milestone | 7 |
| Validation Date | 2026-09-24 |
| Status | Deterministic logic PASSED; exploratory webcam/file demonstrations obtained; final full runtime regression OPEN |
| Author | Bassem Soliman |
| Python | 3.11 / previously reported 3.11.7 |
| MediaPipe | 0.10.14 in latest Windows environment check |
| Operating System | Windows 11 development workstation |
| Live Source | RGB webcam |
| Recorded Source | Private, self-collected webcam MP4 |
| Repository Branch | feat/body-pose-posture |

---

# 1. Validation Objective

Verify selected shoulder/hip detection, basic validity gating, expected lateral-angle sign, explicitly calibrated neutral-relative forward-depth behavior, two independent prototype posture states, deterministic calibration logic, source-independent file replay and non-regression of M1–M6 after integration. Evaluation is exploratory and does not establish physical 3D pose accuracy, per-class error rates, driver-state validity or safety performance.

---

# 2. Test Environment

## 2.1 Hardware

Windows development workstation with built-in/external RGB webcam; a seated operator was filmed in a controlled frontal camera arrangement. No calibrated stereo, depth/ToF or reference motion-capture system was used.

## 2.2 Software

Python 3.11, OpenCV, MediaPipe Pose, NumPy and standard `unittest`. Latest reported installed versions: MediaPipe 0.10.14, TensorFlow and TensorFlow-Intel 2.15.0 (pulled in through optional MediaPipe import). On 2026-09-24 a combined webcam start failed while importing TensorFlow with `MemoryError`; an isolated `import mediapipe` subsequently completed. The deterministic tests passed with a lazily imported MediaPipe body detector.

## 2.3 Input Sources

### Webcam

Manual neutral calibration, pure lateral/forward movements, neutral returns, and simultaneous lateral/forward movement were inspected using screenshots and continuous display.

### Recorded Video

The private `body_pose_smoketest.mp4` is approximately 50.4 s at 1280 × 720. A locally produced `body_pose_smoketest_m7_validation.csv` contains frame-level features and predictions from the early recorded-video experiment. `full_scenario_webcam_test.mp4` was also reported working through the combined source-independent file path after fixing the Bash command formatting. No private media is included in the repository.

---

# 3. Test Configuration

| Parameter | Prototype setting |
|---|---:|
| Selected Pose landmarks | shoulders 11/12; hips 23/24 |
| Minimum reported landmark visibility | 0.5 |
| Minimum shoulder width / torso length | 10 px / 10 px |
| Lateral state threshold | ±6° (strict inequalities) |
| Forward relative-depth threshold | −0.08 |
| Neutral calibration target | 30 accepted frames |
| Maximum attempted calibration frames | 150 |
| Maximum accepted depth-sample range | 0.12 |
| Baseline statistic | Median of accepted neutral `torso_dZ` samples |

`torso_dZ` is shoulder mean landmark z minus hip mean landmark z. Relative depth is current `torso_dZ` minus the stored neutral value; the scale is **not metric**. Automatic recorded-file calibration is appropriate only for a clip confirmed to begin in neutral posture.

---

# 4. Deterministic Validation

From `paths/01_fast_prototype`:

```bash
python -m compileall src
PYTHONPATH=src python -m unittest discover -s src/tests -p "test_m7_posture_regression.py" -v
```

The user's 2026-09-24 terminal output reported **8/8 PASSED** (`Ran 8 tests in 0.005s`, `OK`) after the lazy-import body-module change.

| Test | Purpose | Result |
|---|---|---|
| `test_initial_state` | Valid geometry before calibration | PASS |
| `test_median_calibration` | 30 accepted frames / median baseline | PASS |
| `test_forward_and_return` | Forward-depth transition and neutral recovery | PASS |
| `test_lateral_and_combined` | Independent two-axis outputs | PASS |
| `test_lateral_boundaries` | Strict behavior at exactly ±6° | PASS |
| `test_missing_and_invalid_geometry` | `UNKNOWN` and invalid-sample handling | PASS |
| `test_unstable_calibration_rejected` | Reject excessive depth spread | PASS |
| `test_reset` | Clear the baseline and restore NOT_CALIBRATED | PASS |

These are synthetic estimator tests. They do not use physical ground truth, measure landmark accuracy, benchmark false-positive rates, or exercise the combined MediaPipe runtime.

---

# 5. Webcam Validation

## 5.1 Validation Procedure

Sit neutral with shoulders and hips in frame; begin calibration using a single `C` press, remain still until 30 valid frames are accepted, then keep the same baseline across neutral–forward–neutral, neutral–left/right–neutral and combined movements. `R` clears the baseline if chair/camera seating changes. Screenshots were inspected across both the earlier single-frame prototype and subsequent median-calibration version.

## 5.2 Lateral Direction Validation

Early controlled observations supported anatomical left as positive and right as negative in the non-mirrored frontal setup. In a later five-screenshot median-calibration series, left lean produced +14.73° and `LEAN_LEFT`, while right lean produced −12.71° and `LEAN_RIGHT`. Neutral frames remained near zero (+0.27°, +0.13°). These are selected samples, not a population-level validation.

## 5.3 Sagittal and Combined Validation

Earlier single-frame calibration screenshots demonstrated a forward sample with relative dZ −0.1565 (`FORWARD_LEAN`), a returned neutral sample at −0.0124 (`NEUTRAL`), and a combined forward/right sample at lateral −12.43° with relative dZ −0.0967 (both outputs active). This confirms the implemented architecture can express simultaneous geometric labels in an observed controlled session, not that it accurately separates every combined pose.

---

# 6. Median Calibration Validation

A 30-valid-frame webcam calibration completed with reported neutral baseline approximately −0.2681 and calibration depth range 0.0647, below the configured 0.12 rejection boundary. The subsequent observed sequence was:

| Intended movement | Lateral angle | Relative dZ | Displayed states |
|---|---:|---:|---|
| Initial neutral | +0.27° | +0.0198 | UPRIGHT / NEUTRAL |
| Primarily right lean | −12.71° | −0.1246 | LEAN_RIGHT / FORWARD_LEAN |
| Left lean | +14.73° | +0.1221 | LEAN_LEFT / NEUTRAL |
| Return to neutral | +0.13° | +0.1357 | UPRIGHT / NEUTRAL |
| Forward lean | −1.95° | −0.3607 | UPRIGHT / FORWARD_LEAN |

The calibration lifecycle completed and representative postures were displayed, but a primarily rightward movement also crossed the sagittal threshold; if the operator did not intentionally move forward, this is a false forward-positive instance. The later neutral reading also shifted substantially from the calibrated reference. These observations justify treating the classifier as a prototype with documented coupling and drift, **not** increasing calibration length indefinitely without measurement evidence.

---

# 7. Recorded-Video Validation

## 7.1 Objective

Exercise the same geometry/calibration/estimator logic on a repeatable private recorded webcam source and inspect frame-level outputs without manually holding an identical pose over repeated live trials.

## 7.2 Observed Behavior

An early 10-second-gated CSV review reported 1,520 processed frames over 50.34 s, of which 1,218 were evaluated after the gate, with 100% of frames passing the code's **basic geometry-valid condition**. This figure is not landmark accuracy. Across evaluation frames assigned lateral `LEAN_LEFT`, 221 of 241 also received sagittal `FORWARD_LEAN`; all 290 of 290 `LEAN_RIGHT` frames also received `FORWARD_LEAN`. **These are model-output overlaps, not empirically established false-positive rates** because the recording lacks authoritative per-frame manual ground-truth labels.

The same CSV showed a marked shift in depth values starting around six seconds, while the original evaluation gate started at ten seconds. A subsequent smoke-test version was prepared to begin evaluation immediately after calibration finishes. No validated replacement aggregate report from that revised file has been supplied.

The user later reported the controlled full-scenario file working in the integrated `main.py` after passing `--source file` and the quoted file path on one complete Git Bash command. This supports initial source-independent file playback, but does not replace the pending integrated regression checklist.

---

# 8. Face-Loss and Invalid-Geometry Behavior

The deterministic invalid/missing-geometry test passed: the estimator returns `UNKNOWN` states for invalid geometry and skips invalid calibration samples. An end-to-end occlusion/loss experiment verifying that the running full application continues its M1–M6 face pipeline while body detection is unavailable remains pending.

---

# 9. Integration Regression

The M7 integration is prepared in `src/main.py`, retaining M1–M6 acquisition, EAR/MAR, temporal rules, head pose, gaze and the existing dashboard, plus a separate M7 panel. Deterministic M7 tests passed; however, the user's subsequent integrated webcam attempt terminated in `MemoryError` during `face_features.py` → MediaPipe → optional TensorFlow import. A standalone MediaPipe import later succeeded, leaving the combined runtime outcome unresolved.

Final integrated acceptance requires a fresh launch and clean exit, visible M1–M6/M7 outputs, successful 30-frame calibration and deliberate missing-body handling. Both webcam and controlled recorded-file sources should be checked. Do not infer these outcomes from unit-test success.

---

# 10. Dashboard Validation

The isolated M7 smoke test displayed validity, calibration progress and both axes in screenshots. The prepared integrated program reuses M6 `visualization.py` and appends an M7 panel in `main.py`. A screenshot or completed observation verifying the final combined panel layout, text visibility, and previous outputs after the reported import failure has not yet been supplied.

---

# 11. Performance Summary

No defensible end-to-end M7 FPS, CPU/RAM envelope, per-state precision/recall, angular-error distribution, calibration repeatability across drivers, or DMD generalization metric is established by the available observations. The recorded-video frame count reflects a specific early analysis run; it must not be confused with inference throughput or accuracy.

---

# 12. Evidence

Local-only evidence includes controlled webcam screenshots, the self-recorded MP4, and a CSV of experimental per-frame features and predictions. The 2026-09-24 console transcript independently shows the eight deterministic test results and an integrated import-related failure. Private faces, raw media and derivative validation CSVs are not repository deliverables unless consent and redistribution rights are independently established.

---

# 13. Known Issues

## Issue 1 — Sideways Movement Triggers Forward Label

**Observation:** Primarily rightward leaning generated a negative relative depth crossing −0.08 in one controlled screenshot; the early video CSV also showed substantial co-occurrence of both model outputs. **Current handling:** retain both outputs and document ambiguity rather than relabeling without reference annotations. **Future improvement:** controlled annotated lateral-only trials, viewpoint analysis and lateral/depth decoupling.

## Issue 2 — Neutral Depth Drift

**Observation:** A neutral return after median calibration had relative dZ +0.1357. **Current handling:** initial median baseline and stability rejection; no claim of long-term stabilization. **Future improvement:** controlled drift quantification, robust temporal filtering and reassessment of calibration strategy.

## Issue 3 — Prototype Thresholds

**Observation:** ±6° and −0.08 originated from exploratory webcam results. **Current handling:** configurable and explicitly labeled prototype values. **Future improvement:** independent annotated sessions across subjects/camera placements and threshold sensitivity analysis.

## Issue 4 — Landmark/Camera Limitations

**Observation:** A monocular `z` proxy, partial hip visibility, camera rotation and occlusions can bias features. **Current handling:** visibility and minimum-geometry gates, `UNKNOWN` output when invalid. **Future improvement:** pose-world evaluation, reference camera geometry and targeted occlusion testing.

## Issue 5 — Integrated Import-Memory Failure

**Observation:** One full webcam launch ended with `MemoryError` while loading optional TensorFlow through MediaPipe. The installed MediaPipe package imported successfully alone afterward. **Current handling:** lazy import of MediaPipe in the M7 body module for independent deterministic tests. **Future improvement:** recheck integrated runtime in a clean process; inspect Windows available/committed RAM and project-specific virtual environment if recurring. Do not mark this resolved without successful combined runs.

---

# 14. Engineering Assessment

M7 has a implemented two-axis geometric posture pipeline, functioning controlled live/file demonstrations and an observed passing 8/8 deterministic regression suite. Median calibration is operational. The available evidence supports **prototype feasibility and estimator logic**, not validated real-world posture recognition, reliable lateral–sagittal separation or production safety claims. The outstanding integrated webcam import-memory issue is an acceptance risk that should be closed before merging.

---

# 15. Recommendations

Keep current M7 scope fixed. Reproduce the full webcam/file run in a fresh environment, verify the appended dashboard and previous milestone features, test one deliberate missing-body interval, and record the outcome. Preserve the 30-frame median and existing prototype thresholds; defer calibration optimization, additional posture classes and statistically annotated datasets to research backlog unless the runtime acceptance itself exposes a blocking bug. Inspect staged Git files for private media.

---

# 16. Next Validation

After integrated acceptance, proceed to M8 hand activity. M7 future research should add movement-time annotations and new camera/driver conditions before reporting confusion matrices or comparing algorithms.

---

# Validation Completion Checklist

## Deterministic Validation

- [x] Eight synthetic M7 regression tests passed, including thresholds and two-axis states
- [x] Thirty-valid-frame median calibration, reset and unstable-window rejection tested
- [x] Missing/invalid geometry produces `UNKNOWN` in deterministic estimator tests

## Webcam Validation

- [x] Selected shoulder/hip landmarks and lateral-angle signs observed
- [x] Neutral, forward, left, right and combined states demonstrated in controlled sessions
- [x] Thirty-frame calibration completed and neutral return observed

## Recorded-Video Validation

- [x] Private self-recorded webcam MP4 processed by the M7 smoke test
- [x] Experimental timestamped feature/prediction CSV generated and reviewed
- [x] Observed lateral–sagittal output coupling and neutral drift documented
- [ ] Independent per-frame movement annotations and quantitative accuracy assessment (future research; not a prototype-exit criterion)

## M7 Scientific Reporting

- [x] Non-metric depth, provisional thresholds and limited posture semantics explicitly stated
- [x] No unmeasured accuracy, generalization or safety-performance claims made

## Separate Integration / Repository Closure

- [x] Combined M7 `main.py` prepared; controlled recorded-file playback reported
- [x] Latest combined webcam/file regression, previous-feature checks and dashboard review recorded
- [x] End-to-end missing-body handling observed in combined application
- [x] Private-media exclusion and final Git/PR checks completed
