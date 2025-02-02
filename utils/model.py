from ultralytics import YOLO
from paths import Paths
import torch
import logging

class Model:
    def __init__(self):
        self.model = YOLO(Paths.YOLO_MODEL_PATH)
        self.class_name = 0
        self.confidence = 0.4
        self.batch_size = 16
        self.gpu_init()

    def gpu_init(self):
        if torch.cuda.is_available():
            device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
        
        self.device = device
        self.model.to(self.device)
        logging.info(f"Using device: {self.device}")

    def predict(self, frame):
        predictions = self.model.track(
            frame, persist=True, tracker="bytetrack.yaml", verbose=False, classes=self.class_name, conf=self.confidence
        )
        return predictions
