import cv2
from typing import List
from detectors.base_specialist import BaseSpecialist
from core.events import Event
from ultralytics import YOLO
import numpy as np

class PotholeSpecialist(BaseSpecialist):
    """
    Wrapper for Road Damage Detection (sekilab standard).
    Target Classes: {D00: Longitudinal Crack, D10: Transverse Crack, D20: Aligator Crack, D40: Pothole}
    """
    
    def __init__(self, model_path=r"C:\Users\ahadd\OneDrive\Desktop\CAMVIEW-INTEGRATED\best.pt"):
        """
        Initialize with path to the Specialist Model.
        """
        self.model_path = model_path
        self.model = None
        self.load_model()
        
        # RDD Classes mappings
        self.DAMAGE_CLASSES = ['D00', 'D10', 'D20', 'D40', 'Repair']

    def load_model(self):
        try:
            print(f"[Specialist] Loading Pothole Model from {self.model_path}...")
            self.model = YOLO(self.model_path)
        except Exception as e:
            print(f"[ERROR] Failed to load Pothole Specialist: {e}")

    def process(self, frame, frame_id: int) -> List[Event]:
        if not self.model: return []
            
        events = []
        # Inference with custom trained model
        results = self.model.predict(frame, verbose=False, conf=0.25)
        
        if not results: return []

        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]
            
            is_damage = False
            damage_type = "Unknown"
            
            # REAL LOGIC (Active)
            # D40 = Pothole, D20 = Alligator Crack
            if label in ['D00', 'D10', 'D20', 'D40']:
                is_damage = True
                damage_type = label
            
            if is_damage:
                x, y, w, h = box.xywh[0].cpu().numpy()
                area = w * h
                
                # Severity Grading
                severity = "INFO"
                if damage_type == "D40": # Pothole
                    if area > (frame.shape[0] * frame.shape[1] * 0.05): # Large
                        severity = "CRITICAL"
                    else:
                        severity = "WARNING"
                elif damage_type == "D20":
                    severity = "WARNING"
                
                # Visualization (Draw on frame - optional, usually UI handles it, but good for debug)
                # Note: passing frame by reference, so drawing here shows up in UI
                color = (0, 0, 255) if severity == "CRITICAL" else (0, 165, 255)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, f"{damage_type} ({severity})", (int(x1), int(y1)-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                events.append(Event(
                    event_type="ROAD_DAMAGE",
                    camera_id="CAM_01",
                    severity=severity,
                    metadata={
                        "type": damage_type,
                        "bbox": [float(x), float(y), float(w), float(h)],
                        "source": "sekilab_wrapper_v1",
                        "frame_id": frame_id
                    }
                ))
                
        return events
