# Webcam Smoke Test Validation

## Test Objective

Confirm that the video acquisition layer works before adding MediaPipe.

## Acceptance Criteria

- Webcam opens successfully
- Live video is displayed
- FPS is shown on the frame
- Pressing `q` closes the window cleanly
- No terminal error appears

## Result

Status: Passed

The webcam opened successfully, FPS was displayed, and the application closed cleanly using `q`.

## Next Step

Integrate MediaPipe Face Mesh for face landmark detection.