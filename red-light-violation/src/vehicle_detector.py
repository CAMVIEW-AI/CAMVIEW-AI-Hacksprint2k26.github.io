from ultralytics import YOLO
import numpy as np

class VehicleDetector:
    def __init__(self, model_path="models/yolov8n.pt"):
        self.model = YOLO(model_path)
        self.vehicle_classes = [2, 3, 5, 7]  # car, bike, bus, truck

    def detect(self, frame):
        results = self.model(frame, conf=0.4, verbose=False)[0]
        detections = []

        for box in results.boxes:
            cls = int(box.cls[0])
            if cls in self.vehicle_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append([x1, y1, x2, y2, conf])

        return np.array(detections)
