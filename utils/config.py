# YOLO model
model_path = "./models/yolov10b.pt"
class_name = 0
confidence = 0.5

# Tracker
tracker_model_path = "./models/mars-small128.pb"
cosine = 0.7
max_age = 50

# 1000/25 40

# Video original resolution
width = 1920
height = 2560
original_fps = 25
max_fps = 50

# GPU
device_ios = "mps"
device_windows = "cuda"
device_cpu = "cpu"

# In/Out frames
in_frame = ""
out_frame = ""
