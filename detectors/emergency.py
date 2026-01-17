import cv2
from detectors.yolo_wrapper import BaseDetector
from core.events import Event
from typing import List, Dict

class EmergencyVehicleDetector(BaseDetector):
    def __init__(self):
        super().__init__()
        # COCO IDs: 
        # format: {track_id: last_alert_timestamp}
        self.alert_cooldowns: Dict[int, float] = {}
        self.COOLDOWN_SECONDS = 10.0

    def process(self, frame, frame_id: int) -> List[Event]:
        events = []
        # Use existing YOLO model (already loaded in BaseDetector)
        # We need to run inference if not already run? 
        # BaseDetector doesn't store previous results. 
        # Ideally we share results across detectors for efficiency, but for now we run track again 
        # OR we assume the Engine passes results? 
        # The Engine calls detectors sequentially. 
        # To avoid double-inference, we should really share results, but current architecture runs independent.
        # Check if we can just re-use tracking from wrong_side if it ran? No, independent.
        
        # We'll run inference again (overhead, but safe for now) or rely on what's better.
        # Actually, let's keep it simple.
        results = self.model.track(frame, persist=True, verbose=False)
        
        if not results or not results[0].boxes or results[0].boxes.id is None:
            return []

        boxes = results[0].boxes
        track_ids = boxes.id.int().cpu().numpy()
        current_time = frame_id / 30.0

        for box, track_id, cls_id, conf in zip(boxes, track_ids, boxes.cls, boxes.conf):
            label = self.model.names[int(cls_id)]
            
            # Filter for heavy vehicles
            if label not in ['bus', 'truck', 'car']: # Include car for police cars?
                continue
                
            # If it's a car, we need VERY specific confidence or model (skip for now to avoid false positives)
            if label == 'car': 
                continue

            # Heuristic for demo:
            if conf > 0.85:
                # Check Cooldown
                last_alert = self.alert_cooldowns.get(track_id, 0)
                if (current_time - last_alert) < self.COOLDOWN_SECONDS:
                    # Draw but don't log event
                    x, y, w, h = box.xywh[0].cpu().numpy()
                    color = (0, 165, 255)
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2)), (int(x+w/2), int(y+h/2)), color, 3)
                    cv2.putText(frame, f"PRIORITY (Sent)", (int(x), int(y)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    continue

                # Log Event
                self.alert_cooldowns[track_id] = current_time
                
                x, y, w, h = box.xywh[0].cpu().numpy()
                # Visualization
                color = (0, 165, 255)
                cv2.rectangle(frame, (int(x-w/2), int(y-h/2)), (int(x+w/2), int(y+h/2)), color, 3)
                cv2.putText(frame, f"EMERGENCY PRIORITY", (int(x), int(y)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                events.append(Event(
                    event_type="EMERGENCY_VEHICLE",
                    camera_id="CAM_01",
                    severity="CRITICAL",
                    metadata={
                        "vehicle_type": label,
                        "confidence": float(conf),
                        "action": "PRIORITY_SIGNAL_REQUESTED"
                    }
                ))
            else:
                # Debug: Show we checked it
                x, y, w, h = box.xywh[0].cpu().numpy()
                # Visual feed of what is being rejected
                cv2.putText(frame, f"Priority Check: {conf:.2f}", (int(x), int(y)-35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                pass
        
        return events
