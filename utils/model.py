from ultralytics import YOLO
from paths import Paths
import torch


class Model:
    def __init__(self):
        self.model = YOLO(Paths.YOLO_MODEL_PATH)
        self.class_name = 0
        self.confidence = 0.4
        self.gpu_init()

    def gpu_init(self):
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
        self.model.to(device)

    def predict(self, frame):
        predictions = self.model(
            frame, verbose=False, classes=self.class_name, conf=self.confidence
        )
        if predictions[0].boxes.data.numel() == 0:
            return None
        return predictions
