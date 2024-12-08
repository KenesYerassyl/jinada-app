from ultralytics import YOLO
import utils.config as config
import torch


class Model:
    def __init__(self):
        self.model = YOLO(config.model_path)
        self.class_name = config.class_name
        self.confidence = config.confidence
        self.gpu_init()

    def gpu_init(self):
        if torch.cuda.is_available():
            device = config.device_windows
        elif torch.backends.mps.is_available():
            device = config.device_ios
        else:
            device = config.device_cpu
        self.model.to(device)

    def predict(self, frame):
        predictions = self.model(
            frame, verbose=False, classes=self.class_name, conf=self.confidence
        )
        if predictions[0].boxes.data.numel() == 0:
            return None
        return predictions
