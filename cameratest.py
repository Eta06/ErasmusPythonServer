import cv2

def test_cameras():
    """Tests all connected cameras and prints their availability status."""

    # Start with camera index 0 and iterate
    camera_index = 0
    while True:
        cap = cv2.VideoCapture(camera_index)

        # Check if the camera opened successfully
        if not cap.isOpened():
            break  # No more cameras

        # Check if we can read a frame (indicates camera functionality)
        ret, frame = cap.read()
        if ret:
            print(f"Camera {camera_index} is available.")
        else:
            print(f"Camera {camera_index} is connected but not accessible.")

        # Release resources for this camera
        cap.release()
        camera_index += 1

if __name__ == "__main__":
    test_cameras()
