import cv2
import time



def main() -> None:
    """
    OpenCV webcam smoke test.

    Purpose:
    - Verify that Python can access the webcam.
    - Verify that OpenCV can read frames.
    - Display the live video stream.
    - Show FPS on the frame.
    - Exit cleanly when pressing 'q'.
    """

    camera_index = 0
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"ERROR: Could not open webcam with camera index {camera_index}.")
        print("Try changing camera_index to 1 or 2.")
        return

    previous_time = time.time()
    fps = 0.0

    print("Webcam smoke test started.")
    print("Press 'q' inside the video window to quit.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("ERROR: Could not read frame from webcam.")
            break

        current_time = time.time()
        elapsed_time = current_time - previous_time

        if elapsed_time > 0:
            fps = 1.0 / elapsed_time

        previous_time = current_time

        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            frame,
            "Press q to quit",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        cv2.imshow("Cabin Sensing - Webcam Smoke Test", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("Quit requested by user.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Webcam smoke test finished cleanly.")


if __name__ == "__main__":
    main()
