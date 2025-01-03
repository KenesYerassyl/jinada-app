import cv2
import numpy as np
from typing import List, Tuple
import cvzone
from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot, QObject
from db.db import get_record_by_id, get_object_by_id, update_record_status
from utils.constants import STANDARD_WIDTH, Error
from utils.tracker_utility import TrackerUtility, convert_detections
from paths import Paths
import numpy as np


class VideoProcessorSignals(QObject):
    progress_updated = pyqtSignal(int, int, int)
    finished = pyqtSignal(int, int)

class VideoProcessingWorker(QRunnable):

    def __init__(self, object_id, record_id, model, tracker, visual=False):
        super().__init__()
        self.signals = VideoProcessorSignals()
        self.object_id = object_id
        self.record_id = record_id
        self.visual = visual
        self.model = model
        self.model.gpu_init()
        self.tracker: TrackerUtility = tracker
        self.count = 0

        object = get_object_by_id(object_id)
        self.set_polygons(object["in_frame"], object["out_frame"])
        record = get_record_by_id(record_id)
        self.set_video(record["file_path"])

    def set_polygons(
        self,
        in_polygon: List[List[Tuple[int, int]]],
        out_polygon: List[List[Tuple[int, int]]],
    ):
        try:
            self.n_inside_polygons = len(in_polygon)
            self.n_outside_polygons = len(out_polygon)
            self.visitors = [0 for _ in range(self.n_inside_polygons)]
            self.entry_times = [{} for _ in range(self.n_inside_polygons)]
            self.time_spent = [[] for _ in range(self.n_inside_polygons)]
            self.inside = [set() for _ in range(self.n_inside_polygons)]
            self.inside_polygons = np.int32(in_polygon)
            self.outside_polygons = np.int32(out_polygon)
        except Exception as e:
            print(f"{Error().ERROR_WHILE_SETTING_POLYGONS} {e}")

    def set_video(self, video_path):
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(Error().ERROR_NO_VIDEO)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.video = cap

            if self.visual:
                fourcc = cv2.VideoWriter_fourcc(*"XVID")
                self.out = cv2.VideoWriter(
                    "output.avi", fourcc, self.fps, (width, height)
                )

            modified_width = STANDARD_WIDTH
            aspect_ratio = height / width
            modified_height = int(modified_width * aspect_ratio)
            height_aspect = height / modified_height
            width_aspect = width / modified_width
            for polygon_i in range(len(self.inside_polygons)):
                for point_i in range(len(self.inside_polygons[polygon_i])):
                    self.inside_polygons[polygon_i][point_i][0] = int(
                        self.inside_polygons[polygon_i][point_i][0] * width_aspect
                    )
                    self.inside_polygons[polygon_i][point_i][1] = int(
                        self.inside_polygons[polygon_i][point_i][1] * height_aspect
                    )

            for polygon_i in range(len(self.outside_polygons)):
                for point_i in range(len(self.outside_polygons[polygon_i])):
                    self.outside_polygons[polygon_i][point_i][0] = int(
                        self.outside_polygons[polygon_i][point_i][0] * width_aspect
                    )
                    self.outside_polygons[polygon_i][point_i][1] = int(
                        self.outside_polygons[polygon_i][point_i][1] * height_aspect
                    )
        except Exception as e:
            print(f"{Error().ERROR_WHILE_SETTING_VIDEO} {e}")

    def visualize_frame(self, frame):
        cvzone.putTextRect(frame, f"VISITED: {self.visitors}", (50, 60), 2, 2)
        # cvzone.putTextRect(frame, f"CURRENTLY INSIDE: {len(self.inside)}", (50, 160), 2, 2)
        cvzone.putTextRect(frame, f"TIME SPENT: {self.time_spent}", (50, 260), 2, 2)
        for polygon in self.inside_polygons:
            cv2.polylines(frame, [polygon], True, (0, 255, 0), 2)
        for polygon in self.outside_polygons:
            cv2.polylines(frame, [polygon], True, (0, 0, 255), 2)
        self.out.write(frame)

    def draw_bboxes(self, frame, x3, y3, x4, y4, id):
        cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 255, 255), 2)
        cv2.circle(frame, (x3, y4), 7, (255, 0, 255), -1)
        cv2.circle(frame, (x4, y4), 7, (255, 0, 255), -1)
        cvzone.putTextRect(frame, f"Person-{id}", (x3, y3), 1, 1)

    def detect_collisions(self, x3, y4, id):
        for i in range(self.n_inside_polygons):
            inside_check = cv2.pointPolygonTest(
                self.inside_polygons[i], (x3, y4), False
            )
            if inside_check >= 0 and (id not in self.inside[i]):
                self.visitors[i] += 1
                self.inside[i].add(id)
                self.entry_times[i][id] = self.count
        for i in range(self.n_outside_polygons):
            outside_check = cv2.pointPolygonTest(
                self.outside_polygons[i], (x3, y4), False
            )
            if outside_check >= 0 and (id in self.inside[i]):
                self.time_spent[i].append(
                    (self.count - self.entry_times[i][id]) / self.fps
                )
                self.inside[i].discard(id)
                self.entry_times[i].pop(id)

    @pyqtSlot()
    def run(self):
        if self.video is None:
            raise Exception(Error().ERROR_NO_VIDEO)
        if self.inside_polygons is None or self.outside_polygons is None:
            raise Exception(Error().ERROR_NO_POLYGONS)
        # try:
        while True:
            ret, frame = self.video.read()
            if not ret:
                break
            self.count += 1
            if self.count % 10 != 0:
                continue
            results = self.model.predict(frame)
            if results is None:
                continue
            for result in results:
                detections = []
                for r in result.boxes.data.tolist():
                    x1, y1, x2, y2, score, _ = r
                    if score > 0.8:
                        detections.append(([x1, y1, x2 - x1, y2 - y1], score, "person"))
                self.tracker.update(detections, frame)

            for track in self.tracker.tracks:
                x3, y3, x4, y4 = track.to_ltrb()
                x3 = int(x3)
                y3 = int(y3)
                x4 = int(x4)
                y4 = int(y4)
                id = track.track_id
                if self.visual:
                    self.draw_bboxes(frame, x3, y3, x4, y4, id)
                self.detect_collisions(x3, y4, id)
            if self.visual:
                self.visualize_frame(frame)

            self.signals.progress_updated.emit(
                self.object_id,
                self.record_id,
                int(self.count / self.video.get(cv2.CAP_PROP_FRAME_COUNT) * 100),
            )

            if cv2.waitKey(1) & 0xFF == 27:
                break
        for i in range(len(self.visitors)):
            self.visitors[i] -= len(self.inside[i])
        self.video.release()
        if self.visual:
            self.out.release()
        cv2.destroyAllWindows()
        self.visitors = np.array(self.visitors, dtype=object)
        self.time_spent = np.array(self.time_spent, dtype=object)
        np.savez(
            Paths.record_data(self.record_id),
            visitors=self.visitors,
            time_spent=self.time_spent,
        )
        update_record_status(self.record_id)
        self.signals.finished.emit(self.object_id, self.record_id)
        # except Exception as e:
        #     print(f"{Error().ERROR_WHILE_PROCESSING_VIDEO} {self.record_id}. {e}")
