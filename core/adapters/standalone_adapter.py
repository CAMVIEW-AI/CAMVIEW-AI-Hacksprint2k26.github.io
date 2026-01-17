"""
Standalone Adapter for Backward Compatibility
Allows old test scripts to work with refactored specialists by providing
a YOLO + Tracker layer that feeds into VehicleRegistry.
"""
import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from core.vehicle_registry import VehicleRegistry
from config import settings

class StandaloneAdapter:
    """
    Adapter that runs YOLO + Tracking for standalone specialist tests.
    Feeds results into VehicleRegistry so specialists can work unchanged.
    """
    def __init__(self, model_path="yolo11n.pt"):
        self.model = YOLO(model_path)
        self.tracker = DeepSort(max_age=30, n_init=3)
        self.registry = VehicleRegistry()
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
    def process_frame(self, frame):
        """
        Process frame through YOLO + Tracker, update Registry.
        Returns: (frame, tracks, registry)
        """
        # Run YOLO
        results = self.model(frame, classes=self.vehicle_classes, verbose=False, conf=0.4)[0]
        
        # Format detections for tracker
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            w, h = x2 - x1, y2 - y1
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            detections.append(([x1, y1, w, h], conf, cls))
        
        # Update tracker
        tracks = self.tracker.update_tracks(detections, frame=frame)
        
        # Update registry
        for track in tracks:
            if not track.is_confirmed():
                continue
                
            track_id = track.track_id
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            w, h = x2 - x1, y2 - y1
            
            # Update vehicle state in registry
            self.registry.update_vehicle(track_id, [x1, y1, w, h])
        
        return frame, tracks, self.registry
