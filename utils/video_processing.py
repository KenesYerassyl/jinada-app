import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import Tracker
import cvzone
import time
import os
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot
import torch

import numpy as np


class VideoProcessorSignals(QObject):
    progress = pyqtSignal(int)
    maximum = pyqtSignal(int)
    finished = pyqtSignal()
    result = pyqtSignal(dict, int)


class VideoProcessor(QRunnable):
    model = YOLO("./models/yolov10b.pt")

    def __init__(self, file_path, areas, new_name, current_id):
        super(VideoProcessor, self).__init__()
        self.file_path = file_path
        self.areas = areas
        self.new_name = new_name
        self.signals = VideoProcessorSignals()
        self.current_id = current_id

        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {device}")
        self.model.to(device)

    @pyqtSlot()
    def run(self):
        self.process_video()

    def RGB(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            point = [x, y]
            # print(point)

    def process_video(self):
        # cv2.namedWindow("RGB")
        # cv2.setMouseCallback("RGB", self.RGB)
        cap = cv2.VideoCapture(self.file_path)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(f"{self.new_name}.mp4", fourcc, fps, (1020, 500))
        my_file = open("./coco.txt", "r")
        data = my_file.read()
        class_list = data.split("\n")

        frame_counter = 0

        tracker = Tracker()

        inside = {}
        statistics = {}
        entry_times = {}
        counter = 0
        time_spent = 0

        detection_threshold = 0.5
        frame_count = 0

        while cap.isOpened():
            frame_counter += 1
            self.signals.progress.emit(frame_counter)  # frame counter for progress bar
            ret, frame = cap.read()
            if not ret:
                print("End of video!")
                break
            if frame_count == 0:
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.signals.maximum.emit(frame_count)  # set max val for progress bar
            if frame_counter % 2 != 0:
                continue
            frame = cv2.resize(frame, (1020, 500))

            results = self.model(frame, verbose=False)
            for result in results:
                detections = []
                for r in result.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = r
                    x1 = int(x1)
                    y1 = int(y1)
                    x2 = int(x2)
                    y2 = int(y2)
                    class_id = int(class_id)
                    if score > detection_threshold and class_id == 0:
                        detections.append([x1, y1, x2, y2, score])
                tracker.update(frame, detections)

            for track in tracker.tracks:
                x3, y3, x4, y4 = track.bbox
                x3 = int(x3)
                y3 = int(y3)
                x4 = int(x4)
                y4 = int(y4)
                id = track.track_id
                cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 255, 255), 2)
                cv2.circle(frame, (x4, y4), 7, (255, 0, 255), -1)
                cvzone.putTextRect(frame, f"Person-{id}", (x3, y3), 1, 1)
                outside_check = cv2.pointPolygonTest(
                    np.array(self.areas[0], np.int32), ((x4, y4)), False
                )
                inside_check = cv2.pointPolygonTest(
                    np.array(self.areas[1], np.int32), ((x4, y4)), False
                )
                if outside_check >= 0 and (id in inside):
                    counter += 1
                    exit_time = time.time()
                    time_spent = exit_time - entry_times[id]
                    if id not in statistics:
                        statistics[id] = []
                    statistics[id].append(time_spent)
                    del inside[id]
                    del entry_times[id]
                elif inside_check >= 0 and (id not in inside):
                    inside[id] = (x4, y4)
                    entry_times[id] = time.time()

            cvzone.putTextRect(frame, f"Number of visitors: {counter}", (50, 60), 2, 2)
            cvzone.putTextRect(frame, f"Time: {round(time_spent, 1)}", (50, 260), 2, 2)
            cv2.polylines(
                frame, [np.array(self.areas[0], np.int32)], True, (0, 255, 0), 2
            )
            cv2.polylines(
                frame, [np.array(self.areas[1], np.int32)], True, (0, 255, 0), 2
            )
            out.write(frame)
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        self.signals.result.emit(statistics, self.current_id)  # send results
        self.signals.finished.emit()  # notify about the end
