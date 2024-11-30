import cv2
import os

# DB File System Handler


def save_first_frame(file_path):
    # Add validation, make sure it is video
    result = ()
    file_name, _ = os.path.splitext(os.path.basename(file_path))
    output_image_path = os.path.join("./local_db/object_frames/", f"{file_name}.jpg")
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")

        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            raise IOError(f"Error: Cannot open video file: {file_path}")

        success, frame = cap.read()
        if not success:
            raise ValueError("Error: Could not read the first frame of the video")

        cv2.imwrite(output_image_path, frame)
        result = (1, output_image_path)

    except FileNotFoundError as fnf_error:
        result = (0, repr(fnf_error))
    except IOError as io_error:
        result = (0, repr(io_error))
    except ValueError as val_error:
        result = (0, repr(val_error))
    except Exception as e:
        result = (0, repr(f"An unexpected error occurred: {e}"))
    finally:
        if "cap" in locals() and cap.isOpened():
            cap.release()
    return result
