# OpenCV Webcam Module

---

# 1. Objective

The objective of this module is to establish the **video acquisition layer** of the Driver Monitoring System (DMS).

This module verifies that the software can successfully communicate with the camera before any perception model (MediaPipe, RTMPose, etc.) is integrated.

---

# 2. System Context

Current system architecture:

Camera
↓

OpenCV VideoCapture
↓

Video Frame
↓

Display Window

↓

Future Perception Modules

This module is the foundation of the complete perception pipeline.

---

# 3. Software Perspective

### Responsibility

This module is responsible for:

- opening the camera
- acquiring frames
- calculating FPS
- displaying the live image
- releasing camera resources safely

### Inputs

USB Webcam

### Outputs

RGB video frames

---

# 4. Computer Vision Perspective

This module performs **no perception**.

No AI model is running.

No face is detected.

No landmarks are extracted.

The objective is only to verify that image acquisition works correctly.

The acquired RGB frames will later become the input for:

- MediaPipe Face Mesh
- MediaPipe Holistic
- MediaPipe Hands

---

# 5. Python Perspective

Main concepts introduced:

- imports
- functions
- type hints (`-> None`)
- while loop
- variables
- OpenCV objects
- function calls

---

# 6. Implementation Details

The application performs the following steps:

1. Open camera
2. Verify camera availability
3. Read video frames
4. Calculate FPS
5. Overlay FPS
6. Display frame
7. Exit when user presses **q**
8. Release all resources

---

# 7. Data Flow

USB Camera

↓

VideoCapture()

↓

Frame

↓

FPS Overlay

↓

Display Window

---

# 8. Validation

Acceptance Criteria

✅ Webcam opens

✅ Video stream displayed

✅ FPS displayed

✅ Exit using q

---

# 9. Limitations

Current implementation cannot:

- detect faces
- detect eyes
- estimate pose
- estimate driver state

---

# 10. Future Scalability

Next milestone:

Camera

↓

OpenCV

↓

MediaPipe Face Mesh

↓

468 Face Landmarks

↓

Feature Extraction

---

# 11. Lessons Learned

The video acquisition layer should always be validated before integrating perception algorithms.

This modular approach simplifies debugging and enables incremental system development.
