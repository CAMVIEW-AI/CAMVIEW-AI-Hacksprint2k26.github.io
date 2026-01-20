"""
Wrong-Way Specialist - Pure Logic Unit (Gold Standard)
Consumes VehicleState from Registry, detects wrong-way driving using center divider.
NO internal YOLO or tracking.
"""
import cv2
import numpy as np
import time
from detectors.base_specialist import BaseSpecialist, Event
from config import settings

class WrongWaySpecialist(BaseSpecialist):
    def __init__(self):
        """
        Center divider-based wrong-way detection.
        Works with VehicleRegistry in integrated mode.
        """
        self.previous_y = {}  # track_id -> {'history': [], 'alert_count': int, 'last_alert': float}
        
    def load_model(self):
        """No model needed - pure logic"""
        pass
    
    def compute_dynamic_divider(self, tracks, frame_width):
        """
        Estimate divider X-coordinate using vehicle clustering.
        """
        if len(tracks) < 6:
            return frame_width // 2  # fallback
        
        xs = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            cx = (x1 + x2) // 2
            xs.append(cx)
        
        if not xs:
            return frame_width // 2
        
        left = [v for v in xs if v < frame_width // 2]
        right = [v for v in xs if v >= frame_width // 2]
        
        if not left or not right:
            return frame_width // 2
        
        divider_x = (max(left) + min(right)) // 2
        return divider_x
    
    def process(self, frame, frame_id=0, registry=None, tracks=None):
        """
        Process frame with pre-computed tracks and registry.
        
        Args:
            frame: Video frame for visualization
            frame_id: Current frame number
            registry: VehicleRegistry instance (integrated mode)
            tracks: List of Track objects (integrated mode)
        
        Returns:
            List of Event objects
        """
        if frame is None:
            return []
        
        events = []
        h, w, _ = frame.shape
        
        # Process tracks (if provided by integrated mode)
        if tracks is None or registry is None:
            return []
        
        # Compute dynamic divider
        divider_x = self.compute_dynamic_divider(tracks, w)
        
        # Draw divider
        cv2.line(frame, (divider_x, 0), (divider_x, h), (255, 0, 0), 3)
        cv2.putText(frame, "MEDIAN", (divider_x + 5, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Track & decide wrong way
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            w_box, h_box = x2 - x1, y2 - y1
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            
            is_right_side = cx > divider_x
            
            # Initialize tracking history
            if track_id not in self.previous_y:
                self.previous_y[track_id] = {
                    "history": [],
                    "alert_count": 0,
                    "last_alert": 0,
                }
            
            history = self.previous_y[track_id]["history"]
            history.append((cx, cy))
            if len(history) > 30:
                history.pop(0)
            
            # Draw trajectory
            if len(history) > 1:
                cv2.polylines(frame, [np.array(history)], False, (0, 165, 255), 2)
            
            # Need at least 6 points to determine direction
            if len(history) < 6:
                continue
            
            # Calculate direction (dy)
            dy = history[-1][1] - history[-6][1]
            
            # Wrong-way logic (divided road)
            is_wrong = False
            lane = "LEFT" if not is_right_side else "RIGHT"
            
            # LEFT side → should move towards camera (dy > 0)
            if not is_right_side and dy < -10:
                is_wrong = True
            
            # RIGHT side → should move away from camera (dy < 0)
            if is_right_side and dy > 10:
                is_wrong = True
            
            # Update registry
            registry.update_wrong_way(track_id, is_wrong, lane)
            
            # Visualization
            color = (0, 0, 255) if is_wrong else (0, 255, 0)
            label = "WRONG!" if is_wrong else "OK"
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Event debounce
            if is_wrong:
                self.previous_y[track_id]["alert_count"] += 1
                if self.previous_y[track_id]["alert_count"] > 5:
                    if time.time() - self.previous_y[track_id]["last_alert"] > 5:
                        events.append(Event(
                            event_type="WRONG_WAY_DRIVING",
                            severity="CRITICAL",
                            description=f"Vehicle #{track_id} wrong-way in {lane} lane",
                            camera_id="CAM_01",
                            source="wrong_way_specialist",
                            metadata={
                                "vehicle_id": track_id,
                                "lane": lane,
                                "bbox": [x1, y1, w_box, h_box],
                            },
                        ))
                        self.previous_y[track_id]["last_alert"] = time.time()
            else:
                self.previous_y[track_id]["alert_count"] = max(
                    0, self.previous_y[track_id]["alert_count"] - 1
                )
        
        return events
