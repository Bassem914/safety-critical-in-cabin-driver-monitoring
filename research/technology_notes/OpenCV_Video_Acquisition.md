# Technology Note: OpenCV for Video Acquisition

## Why OpenCV?

OpenCV is used as the first video acquisition tool because it provides a simple and reliable interface for webcam and video input.

## Role in This Project

OpenCV is responsible for:

- opening the webcam
- reading frames
- displaying frames
- overlaying visual information
- supporting later integration with MediaPipe

## Alternatives

Possible alternatives include GStreamer, PyAV, ROS camera drivers, or custom camera SDKs.  
For the fast prototype, OpenCV is preferred because it is simpler and faster to implement.

## Decision

Use OpenCV for Path 1 because the goal is fast prototyping and validation of the perception pipeline.