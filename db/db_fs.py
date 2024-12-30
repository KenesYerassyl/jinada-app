import cv2
import os
from datetime import datetime
from utils.constants import Error
from paths import Paths

# DB File System Handler


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def save_first_frame(file_path):
    # Add validation, make sure it is video
    result = ()
    file_name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_image_path = os.path.join(Paths.OBJECT_FRAMES, f"{file_name}.jpg")
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{Error().ERROR_NO_VIDEO_FILE} {file_path}")

        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            raise IOError(f"{Error().ERROR_CANNOT_OPEN_FILE}  {file_path}")

        success, frame = cap.read()
        if not success:
            raise ValueError(Error().ERROR_CANNOT_READ_FRAME)

        cv2.imwrite(output_image_path, frame)
        result = (1, output_image_path)

    except FileNotFoundError as fnf_error:
        result = (0, repr(fnf_error))
    except IOError as io_error:
        result = (0, repr(io_error))
    except ValueError as val_error:
        result = (0, repr(val_error))
    except Exception as e:
        result = (0, repr(f"{Error().ERROR_WHILE_SAVING_FRAME} {e}"))
    finally:
        if "cap" in locals() and cap.isOpened():
            cap.release()
    return result

def shutdown():
    import shutil
    import paths
    shutil.rmtree(paths.SECURE_PATH)