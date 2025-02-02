import cv2
import os
from paths import Paths, SECURE_PATH
import logging
import shutil
from typing import Tuple
import time

# DB File System Handler

def delete_file(file_path: str) -> None:
    """
    Deletes a file at the specified path if it exists.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"File {file_path} deleted successfully.")
        else:
            logging.warning(f"File {file_path} does not exist.")
    except Exception as e:
        logging.error(f"Error deleting file {file_path}: {e}")

def save_first_frame(file_path: str) -> Tuple[int, str]:
    """
    Captures the first frame of the video file and saves it as an image.
    Returns a tuple (status_code, file_path_or_error_message).
    """
    # TODO: Add validation, make sure it is video
    result = ()

    file_name = f"object_frame_{int(time.time())}"
    output_image_path = os.path.join(Paths.OBJECT_FRAMES, f"{file_name}.jpg")

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No video file found at this location {file_path}")

        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            raise IOError(f"Video cannot be opened at this location {file_path}")

        success, frame = cap.read()
        if not success:
            raise ValueError("Frame cannot be read, some error with video file.")

        cv2.imwrite(output_image_path, frame)
        result = (1, output_image_path)
        logging.info(f"First frame saved successfully at {output_image_path}")

    except FileNotFoundError as fnf_error:
        result = (0, repr(fnf_error))
        logging.error(f"File not found: {fnf_error}")
    except IOError as io_error:
        result = (0, repr(io_error))
        logging.error(f"IO error while opening file: {io_error}")
    except ValueError as val_error:
        result = (0, repr(val_error))
        logging.error(f"Error reading frame: {val_error}")
    except Exception as e:
        result = (0, repr(f"Unexpected error while saving frame {e}"))
        logging.error(f"Unexpected error while saving frame: {e}")
    finally:
        if "cap" in locals() and cap.isOpened():
            cap.release()
            logging.debug("Video capture released.")

    return result

def shutdown() -> None:
    """
    Cleans up by deleting secure data and paths.
    """
    try:
        shutil.rmtree(SECURE_PATH)
        logging.info(f"Successfully removed {SECURE_PATH}.")
    except Exception as e:
        logging.error(f"Error during shutdown and cleanup: {e}")