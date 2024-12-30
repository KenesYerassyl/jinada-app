COCO_91_CLASSES = ['__background__', 'person']

import torch
import torchvision
import cv2
import os
import time
import argparse
import numpy as np
 
 
from torchvision.transforms import ToTensor
from deep_sort_realtime.deepsort_tracker import DeepSort
 
# Define a function to convert detections to SORT format.
def convert_detections(detections):
    # Get the bounding boxes, labels and scores from the detections dictionary.
    threshold = 0.7
    classes = ['person']
    boxes = detections["boxes"].cpu().numpy()
    labels = detections["labels"].cpu().numpy()
    scores = detections["scores"].cpu().numpy()
    lbl_mask = np.isin(labels, classes)
    scores = scores[lbl_mask]
    # Filter out low confidence scores and non-person classes.
    mask = scores > threshold
    boxes = boxes[lbl_mask][mask]
    scores = scores[mask]
    labels = labels[lbl_mask][mask]
 
 
    # Convert boxes to [x1, y1, w, h, score] format.
    final_boxes = []
    for i, box in enumerate(boxes):
        # Append ([x, y, w, h], score, label_string).
        final_boxes.append(
            (
                [box[0], box[1], box[2] - box[0], box[3] - box[1]],
                scores[i],
                str(labels[i])
            )
        )
 
 
    return final_boxes

# Function for bounding box and ID annotation.
def annotate(tracks, frame, resized_frame, frame_width, frame_height, colors):
    for track in tracks:
        if not track.is_confirmed():
            continue
        track_id = track.track_id
        track_class = track.det_class
        x1, y1, x2, y2 = track.to_ltrb()
        p1 = (int(x1/resized_frame.shape[1]*frame_width), int(y1/resized_frame.shape[0]*frame_height))
        p2 = (int(x2/resized_frame.shape[1]*frame_width), int(y2/resized_frame.shape[0]*frame_height))
        # Annotate boxes.
        color = colors[int(track_class)]
        cv2.rectangle(
            frame,
            p1,
            p2,
            color=(int(color[0]), int(color[1]), int(color[2])),
            thickness=2
        )
        # Annotate ID.
        cv2.putText(
            frame, f"ID: {track_id}",
            (p1[0], p1[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
            lineType=cv2.LINE_AA
        )
    return frame


class TrackerUtility:

    def __init__(self):
        self.tracks = []
        self.tracker = DeepSort(max_age=50, embedder="torchreid", max_cosine_distance=0.7)
    
    def update(self, detections, frame):
        self.tracks = []
        tracks = self.tracker.update_tracks(detections, frame=frame)
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            self.tracks.append(track)



"""

ready to use detection models with torchvision.models.detection

'fasterrcnn_resnet50_fpn_v2',
'fasterrcnn_resnet50_fpn',
'fasterrcnn_mobilenet_v3_large_fpn',
'fasterrcnn_mobilenet_v3_large_320_fpn',
'fcos_resnet50_fpn',
'ssd300_vgg16',
'ssdlite320_mobilenet_v3_large',
'retinanet_resnet50_fpn',
'retinanet_resnet50_fpn_v2'

feature extractors 

"mobilenet",
"torchreid",
"clip_RN50",
"clip_RN101",
"clip_RN50x4",
"clip_RN50x16",
"clip_ViT-B/32",
"clip_ViT-B/16"
"""