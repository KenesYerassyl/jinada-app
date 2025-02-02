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

NULLPOINT = (20000, 20000)

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
        record = get_record_by_id(record_id)
        self._set_attrs(len(object["in_frame"]))
        self._set_polygons(record["file_path"], object["in_frame"], object["out_frame"])

    def cancel(self):
        """Cancel the current process"""
        self._is_canceled = True

    def _set_attrs(self, in_polygon_size: int) -> None:
        """
        Initialize the polygons and other properties
        """
        try:
            self.visitors = [0 for _ in range(in_polygon_size)]
            self.entry_times = [{} for _ in range(in_polygon_size)]
            self.time_spent = [[] for _ in range(in_polygon_size)]
            self.inside = [set() for _ in range(in_polygon_size)]

        except TypeError as te:
            logging.error(f"Type error while setting polygons: {te}")
            raise
        except ValueError as ve:
            logging.error(f"Value error while setting polygons: {ve}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error occurred while setting polygons: {e}")
            raise

    def _set_polygons(self, video_path: str, in_polygon: List[List[Tuple[int, int]]], out_polygon: List[List[Tuple[int, int]]]) -> None:
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
            

            self.inside_polygons = self._preprocess_polygons(in_polygon, width_aspect, height_aspect)
            self.outside_polygons = self._preprocess_polygons(out_polygon, width_aspect, height_aspect)

            logging.info("Polygons have been set successfully.")
        except ValueError as ve:
            logging.error(f"Value error while setting video: {ve}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error occurred while setting video: {e}")
            raise

    def _preprocess_polygons(self, polygons: List[List[Tuple[int, int]]], width_aspect: float, height_aspect: float, pad_value: Tuple[int, int] = NULLPOINT) -> np.ndarray:
        """
        Scale polygons based on width and height aspect ratios.
        """
        try:
            max_len = max(len(polygon) for polygon in polygons)

            processed_polygons = []
            for polygon in polygons:
                processed_polygon = [
                    (
                        int(point[0] * width_aspect),
                        int(point[1] * height_aspect),
                    )
                    for point in polygon
                ]
                padding_needed = max_len - len(processed_polygon)
                processed_polygons.append(processed_polygon + [pad_value] * padding_needed)
                
            return np.array(processed_polygons, dtype=np.int32)
        except Exception as e:
            logging.error(f"Error while processing polygons: {e}")
            raise

    @pyqtSlot()
    def run(self) -> None:
        try:
            if self.video is None:
                raise ValueError("No video has been loaded: video is None")
            if self.inside_polygons is None or self.outside_polygons is None:
                raise ValueError("Polygons have not been set: either inside_polygons or outside_polygons is None.")
            
            frames = []

            while True:
                if self._is_canceled:
                    break
                ret, frame = self.video.read()
                if not ret:
                    break # Exit if no more frames

                self.count += 1

                self.signals.progress_updated.emit(
                    self.object_id,
                    self.record_id,
                    int(self.count / self.video.get(cv2.CAP_PROP_FRAME_COUNT) * 100),
                )

                if self.count % 4 != 0:
                    continue # Skip processing most frames for efficiency

                frames.append(frame)
                if len(frames) == self.model.batch_size:
                    results = self.model.predict(frames)
                    for i in range(self.model.batch_size):
                        if results[i] is None or not results[i].boxes.is_track:
                            continue
                        boxes = results[i].boxes.xyxy.cpu().tolist()
                        track_ids = results[i].boxes.id.int().cpu().tolist()
                        for box, track_id in zip(boxes, track_ids):
                            x1, _, x2, y2 = map(int, box)
                            self._check_for_intersections((x1, y2), (x2, y2), track_id)
                        if self.visual:
                            self._visualize_frame(results[i].plot())
                    frames.clear()

                if cv2.waitKey(1) & 0xFF == 27:
                    break

            if not self._is_canceled:
                self._finalize_tracking()

        except ValueError as ve:
            logging.error(f"Value error in run: {ve}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during processing: {e}")
            raise
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
            for i, polygon in enumerate(self.inside_polygons):
                polygon_trunc = polygon[polygon != NULLPOINT].reshape(-1, 2)

                is_lcorner_inside = cv2.pointPolygonTest(polygon_trunc, left_corner, False) >= 0
                is_rcorner_inside = cv2.pointPolygonTest(polygon_trunc, right_corner, False) >= 0

                if is_lcorner_inside and is_rcorner_inside:
                    if obj_id not in self.inside[i]:
                        self.inside[i].add(obj_id)
                        self.entry_times[i][obj_id] = self.count
                elif not is_lcorner_inside and not is_rcorner_inside:  # Both corners are outside
                    if obj_id in self.inside[i]:  # Ensure obj_id was previously inside
                        self.visitors[i] += 1
                        self.time_spent[i].append((self.count - self.entry_times[i][obj_id]) / self.fps)
                        self.inside[i].discard(obj_id)
                        self.entry_times[i].pop(obj_id, None)
                    
        except Exception as e:
            logging.error(f"Error in checking for intersections: {e}")
            raise

    def _visualize_frame(self, frame):
        """Visualize frames if self.visual == True."""
        cvzone.putTextRect(frame, f"VISITED: {self.visitors}", (50, 60), 2, 2)
        cvzone.putTextRect(frame, f"INSIDE: {self.inside}", (50, 160), 2, 2)
        for polygon in self.inside_polygons:
            polygon_trunc = polygon[polygon != NULLPOINT].reshape(-1, 2)
            cv2.polylines(frame, [polygon_trunc], True, (0, 255, 0), 2)
        for polygon in self.outside_polygons:
            polygon_trunc = polygon[polygon != NULLPOINT].reshape(-1, 2)
            cv2.polylines(frame, [polygon_trunc], True, (0, 0, 255), 2)
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