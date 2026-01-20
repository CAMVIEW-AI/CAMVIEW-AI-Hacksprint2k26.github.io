from detectors.yolo_wrapper import BaseDetector
from core.events import Event
from config import settings
from typing import List

class PotholeDetector(BaseDetector):
    def __init__(self):
        # In reality, load a different model, e.g. "pothole_v8.pt"
        # super().__init__(model_path="pothole_v8.pt")
        super().__init__() 
        # Using standard model for compilation, but logic requires pothole class.
        # We will scan for class 'bowl' (45) or 'potted plant' (58) as proxies if using standard COCO for demo,
        # or expect class 'pothole' (0) if user provides a custom model.
        
        # Let's write generic logic assuming class name contains 'pothole' or we use a proxy.
        self.pothole_keywords = ['pothole', 'hole', 'bowl'] # 'bowl' is a proxy for demo w/ stock model

    def process(self, frame, frame_id: int) -> List[Event]:
        events = []
        results = self.model(frame, verbose=False) # Run on all classes
        
        if not results:
            return []

        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]
            
            if any(k in label.lower() for k in self.pothole_keywords):
                x, y, w, h = box.xywh[0]
                area = float(w * h)
                
                # Severity Logic
                severity = "LOW"
                if area > settings.POTHOLE_MIN_AREA * 2:
                    severity = "HIGH"
                elif area > settings.POTHOLE_MIN_AREA:
                    severity = "MEDIUM"
                
                events.append(Event(
                    event_type="POTHOLE_DETECTED",
                    camera_id="CAM_01",
                    severity=severity,
                    metadata={
                        "location_x": float(x),
                        "location_y": float(y),
                        "area": area,
                        "tagged_frame": frame_id
                    }
                ))
        
        return events
