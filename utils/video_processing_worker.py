import cv2
import numpy as np
from typing import List, Tuple
import cvzone
from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot, QObject
from db.db import get_record_by_id, get_object_by_id, update_record_status
from utils.constants import STANDARD_WIDTH
from utils.model import Model
from paths import Paths
import logging


class VideoProcessorSignals(QObject):
    progress_updated = pyqtSignal(int, int, int)
    finished = pyqtSignal(int, int)

class VideoProcessingWorker(QRunnable):

    def __init__(self, object_id, record_id, visual=False):
        super().__init__()
        self.signals = VideoProcessorSignals()
        self.object_id = object_id
        self.record_id = record_id
        self.visual = visual
        self.model = Model()
        self.count = 0
        self._is_canceled = False

        object = get_object_by_id(object_id)
        self._set_polygons(object["in_frame"], object["out_frame"])
        record = get_record_by_id(record_id)
        self._set_video(record["file_path"])

    def cancel(self):
        """Cancel the current process"""
        self._is_canceled = True
    
    def _set_polygons(self, in_polygon: List[List[Tuple[int, int]]], out_polygon: List[List[Tuple[int, int]]]) -> None:
        """
        Initialize the polygons and other properties
        """
        try:

            self.n_inside_polygons = len(in_polygon)
            self.n_outside_polygons = len(out_polygon)
            self.visitors = [0 for _ in range(self.n_inside_polygons)]
            self.entry_times = [{} for _ in range(self.n_inside_polygons)]
            self.time_spent = [[] for _ in range(self.n_inside_polygons)]
            self.inside = [set() for _ in range(self.n_inside_polygons)]

            self.inside_polygons = np.array(in_polygon, dtype=np.int32)
            self.outside_polygons = np.array(out_polygon, dtype=np.int32)
            logging.info("Polygons have been set successfully.")
        except TypeError as te:
            logging.error(f"Type error while setting polygons: {te}")
        except ValueError as ve:
            logging.error(f"Value error while setting polygons: {ve}")
        except Exception as e:
            logging.error(f"Unexpected error occurred while setting polygons: {e}")

    def _set_video(self, video_path: str) -> None:
        """
        Access and initialize the video the set its properties
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("ERROR_NO_VIDEO: Unable to open the video file.")
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.video = cap

            if self.visual:
                self.out = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"XVID"), self.fps, (width, height))

            modified_width = STANDARD_WIDTH
            aspect_ratio = height / width
            modified_height = int(modified_width * aspect_ratio)
            height_aspect = height / modified_height
            width_aspect = width / modified_width
            
            self.inside_polygons = self._scale_polygons(
                self.inside_polygons, width_aspect, height_aspect
            )

            self.outside_polygons = self._scale_polygons(
                self.outside_polygons, width_aspect, height_aspect
            )

            logging.info("Video has been set successfully.")
        except ValueError as ve:
            logging.error(f"Value error while setting video: {ve}")
        except Exception as e:
            logging.error(f"Unexpected error occurred while setting video: {e}")

    def _scale_polygons(self, polygons: np.ndarray, width_aspect: float, height_aspect: float) -> np.ndarray:
        """
        Scale polygons based on width and height aspect ratios.
        """
        try:
            scaled_polygons = []
            for polygon in polygons:
                scaled_polygon = [
                    (
                        int(point[0] * width_aspect),
                        int(point[1] * height_aspect),
                    )
                    for point in polygon
                ]
                scaled_polygons.append(scaled_polygon)
            return np.array(scaled_polygons, dtype=np.int32)
        except Exception as e:
            logging.error(f"Error while scaling polygons: {e}")
            raise

    @pyqtSlot()
    def run(self) -> None:
        try:
            if self.video is None:
                raise ValueError("No video has been loaded: video is None")
            if self.inside_polygons is None or self.outside_polygons is None:
                raise ValueError("Polygons have not been set: either inside_polygons or outside_polygons is None.")
            while True:
                if self._is_canceled:
                    break
                ret, frame = self.video.read()
                if not ret:
                    break # Exit if no more frames

                self.count += 1
                if self.count % 4 != 0:
                    continue # Skip processing most frames for efficiency

                results = self.model.predict(frame)
                if results is None:
                    continue # Skip if no results from the model
                
                boxes = results[0].boxes.xywh.cpu()
                if not results[0].boxes.is_track:
                    continue # Skip if no track ids
        
                track_ids = results[0].boxes.id.int().cpu().tolist()

                for box, track_id in zip(boxes, track_ids):
                    x, y, w, h = (int(box[0].item()), int(box[1].item()), int(box[2].item()), int(box[3].item()))
                    self._check_for_intersections((int(x - w/2), int(y + h/2)), (int(x + w/2), int(y + h/2)), track_id)

                self.signals.progress_updated.emit(
                    self.object_id,
                    self.record_id,
                    int(self.count / self.video.get(cv2.CAP_PROP_FRAME_COUNT) * 100),
                )
                if self.visual:
                    self._visualize_frame(results[0].plot())

                if cv2.waitKey(1) & 0xFF == 27:
                    break

            if not self._is_canceled:
                self._finalize_tracking()

        except ValueError as ve:
            logging.error(f"Validation error in run: {ve}")
        except Exception as e:
            logging.error(f"Unexpected error during processing: {e}")
        finally:
            self._cleanup()

    def _check_for_intersections(self, left_corner: Tuple[int, int], right_corner: Tuple[int, int], obj_id: int) -> None:
        """
        Detect collisions between tracked objects and polygons, updating visitor counts 
        and time spent inside polygons.
        
        Args:
            left_corner (int): coordinates of the tracked object's bottom-left corner.
            right_corner (int): coordinates of the tracked object's bottom-right corner.
            obj_id (int): Unique ID of the tracked object.
        """
        try:
            is_lcorner_inside = False # False if left corner lies inside of any in-polygon, True if otherwise
            is_rcorner_inside = False # False if right corner lies inside of any in-polygon, True if otherwise
            for i in range(self.n_inside_polygons):
                is_lcorner_inside = is_lcorner_inside or cv2.pointPolygonTest(self.inside_polygons[i], left_corner, False) >= 0
                is_rcorner_inside = is_rcorner_inside or cv2.pointPolygonTest(self.inside_polygons[i], right_corner, False) >= 0
                if is_lcorner_inside and is_rcorner_inside:
                    if obj_id not in self.inside[i]:
                        self.inside[i].add(obj_id)
                        self.entry_times[i][obj_id] = self.count
                        break

            for i in range(self.n_outside_polygons):
                if cv2.pointPolygonTest(self.outside_polygons[i], left_corner, False) >= 0 and not is_rcorner_inside \
                    or cv2.pointPolygonTest(self.outside_polygons[i], right_corner, False) >= 0 and not is_lcorner_inside:
                    if obj_id in self.inside[i]:
                        self.visitors[i] += 1
                        self.time_spent[i].append((self.count - self.entry_times[i][obj_id]) / self.fps)
                        self.inside[i].discard(obj_id)
                        self.entry_times[i].pop(obj_id, None)
        except Exception as e:
            logging.error(f"Error in checking for intersections: {e}")

    def _visualize_frame(self, frame):
        """Visualize frames if self.visual == True."""
        cvzone.putTextRect(frame, f"VISITED: {self.visitors}", (50, 60), 2, 2)
        cvzone.putTextRect(frame, f"INSIDE: {self.inside}", (50, 160), 2, 2)
        for polygon in self.inside_polygons:
            cv2.polylines(frame, [polygon], True, (0, 255, 0), 2)
        for polygon in self.outside_polygons:
            cv2.polylines(frame, [polygon], True, (0, 0, 255), 2)
        self.out.write(frame)

    def _finalize_tracking(self) -> None:
        """Finalize visitor and time tracking."""
        self.visitors = np.array(self.visitors, dtype=object)
        self.time_spent = np.array(self.time_spent, dtype=object)

        np.savez(
            Paths.record_data(self.record_id),
            visitors=self.visitors,
            time_spent=self.time_spent,
        )

        update_record_status(self.record_id)

        self.signals.finished.emit(self.object_id, self.record_id)

    def _cleanup(self) -> None:
        """Release resources and clean up."""
        if self.video:
            self.video.release()
        if self.visual and hasattr(self, "out"):
            self.out.release()
        cv2.destroyAllWindows()