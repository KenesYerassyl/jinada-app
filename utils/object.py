import cv2
import os


class Object:
    def __init__(self, file_path="", name="", frame_path=""):
        self.__file_path = file_path
        self.__name = name
        self.__frame_path = frame_path

    def set_file_path(self, file_path):
        self.__file_path = file_path

    def set_name(self, name):
        self.__name = name

    def set_frame_path(self, frame_path):
        self.__frame_path = frame_path

    def get_file_path(self):
        return self.__file_path

    def get_name(self):
        return self.__name

    def get_frame_path(self):
        return self.__frame_path

    def save_first_frame(self):
        result = ()
        file_name, _ = os.path.splitext(os.path.basename(self.__file_path))
        output_image_path = os.path.join(
            os.path.dirname(self.__file_path), f"{file_name}.jpg"
        )
        try:
            if not os.path.exists(self.__file_path):
                raise FileNotFoundError(f"Video file not found: {self.__file_path}")

            cap = cv2.VideoCapture(self.__file_path)
            if not cap.isOpened():
                raise IOError(f"Error: Cannot open video file: {self.__file_path}")

            success, frame = cap.read()
            if not success:
                raise ValueError("Error: Could not read the first frame of the video")

            cv2.imwrite(output_image_path, frame)
            self.set_frame_path(output_image_path)
            result = (1, f"First frame saved successfully to {output_image_path}")

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


default_object = Object(
    file_path="/Users/Yerassyl/Desktop/violette/samples/sample3.MOV",
    name="sample3",
    frame_path="/Users/Yerassyl/Desktop/violette/samples/sample3.jpg",
)
