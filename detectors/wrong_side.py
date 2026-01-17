import cv2
from detectors.yolo_wrapper import BaseDetector
from core.events import Event
from config import settings
from typing import List
import math

class WrongSideDetector(BaseDetector):
    def __init__(self):
        super().__init__()
        # History format: {track_id: [(x, y), ...]}  -> Store list of positions for smoothing
        self.history: Dict[int, List[tuple]] = {}
        
        # Violations state: {track_id: {"frames": int, "last_alert": float}}
        self.violation_state: Dict[int, Dict] = {}

    def process(self, frame, frame_id: int) -> List[Event]:
        events = []
        height, width = frame.shape[:2]
        mid_x = width // 2
        
        # Define Ignore Zone (Vertical Center Strip)
        ignore_y_min = int(height * 0.45)
        ignore_y_max = int(height * 0.65)

        # Use YOLO tracking; removing classes filter to allow "all object" visualization as requested previously, 
        # BUT for violation logic we should probably stick to vehicles if possible. 
        # For now, we keep detecting all but filter logic applies to anything moving fast.
        results = self.model.track(frame, persist=True, verbose=False) 
        
        if not results or not results[0].boxes or results[0].boxes.id is None:
            return []

        boxes = results[0].boxes.xywh.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().numpy()
        classes = results[0].boxes.cls.int().cpu().numpy()
        confs = results[0].boxes.conf.cpu().numpy()

        current_time = frame_id / 30.0 # Approximate seconds if 30fps, or just use time.time() if real

        for box, track_id, cls_id, conf in zip(boxes, track_ids, classes, confs):
            x, y, w, h = box
            center_x, center_y = x, y
            label = self.model.names[cls_id]

            # Default Visualization (Safe/Green)
            color = (0, 255, 0) 
            text = f"{label}"
            
            # --- Analysis Logic ---
            should_analyze = True

            # 1. Update History
            if track_id not in self.history:
                self.history[track_id] = []
            self.history[track_id].append((center_x, center_y))
            if len(self.history[track_id]) > settings.DIRECTION_SMOOTHING_FRAMES:
                self.history[track_id].pop(0)

            # Need history to calculate vector
            if len(self.history[track_id]) < 2:
                should_analyze = False

            # 2. Calculate Vector
            avg_dx, avg_dy = 0, 0
            start_x, start_y = center_x, center_y
            end_x, end_y = center_x, center_y

            if should_analyze:
                start_x, start_y = self.history[track_id][0]
                end_x, end_y = self.history[track_id][-1]
                avg_dx = end_x - start_x
                avg_dy = end_y - start_y
                
                speed = math.hypot(avg_dx, avg_dy)
                if speed < 5: # Stationary object
                    should_analyze = False

            # 3. Check Ignore Zone
            if ignore_y_min < center_y < ignore_y_max:
                should_analyze = False
                color = (255, 255, 0) # Cyan/Yellow for ignored zone to indicate tracked but ignored

            # 4. Wrong Side Logic
            is_confirmed_violation = False
            state_frames = 0
            
            if should_analyze:
                is_wrong_side = False
                lane_status = "Unknown"
                
                # Determine lane index using configurable boundaries
                lane_idx = None
                if settings.LANE_BOUNDARIES:
                    # Find first boundary greater than center_x
                    for i, bound in enumerate(settings.LANE_BOUNDARIES):
                        if center_x < bound:
                            lane_idx = i
                            break
                    if lane_idx is None:
                        lane_idx = len(settings.LANE_BOUNDARIES)
                else:
                    # Fallback to simple two‑lane split
                    lane_idx = 0 if center_x < mid_x else 1

                # Expected direction alternates per lane: even lanes -> DOWN (+dy), odd lanes -> UP (-dy)
                expected_down = (lane_idx % 2 == 0)
                if expected_down:
                    if avg_dy < -5:
                        is_wrong_side = True
                        lane_status = f"Lane {lane_idx} (expected DOWN)"
                else:
                    if avg_dy > 5:
                        is_wrong_side = True
                        lane_status = f"Lane {lane_idx} (expected UP)"

                # Update State
                if track_id not in self.violation_state:
                    self.violation_state[track_id] = {"frames": 0, "last_alert": 0}

                if is_wrong_side and conf > settings.WRONG_SIDE_CONFIDENCE:
                    self.violation_state[track_id]["frames"] += 1
                else:
                    self.violation_state[track_id]["frames"] = 0
                
                state_frames = self.violation_state[track_id]["frames"]
                
                # Check for Violation Trigger
                if state_frames >= settings.WRONG_SIDE_MIN_FRAMES:
                    if (current_time - self.violation_state[track_id]["last_alert"]) > settings.WRONG_SIDE_COOLDOWN:
                        is_confirmed_violation = True
                        self.violation_state[track_id]["last_alert"] = current_time

                # Update Colors based on logic
                if is_wrong_side:
                    color = (0, 165, 255) # Orange (Potential)
                    text = f"{label} PO:{state_frames}"
                
                if is_confirmed_violation:
                    color = (0, 0, 255) # Red (Confirmed)
                    text = f"{label} WRONG WAY"
                    
                    # Emit Event
                    events.append(Event(
                        event_type="WRONG_SIDE",
                        camera_id="CAM_01",
                        severity="WARNING",
                        metadata={
                            "track_id": int(track_id),
                            "speed_vector": float(avg_dy),
                            "conf": float(conf),
                            "frame_id": frame_id
                        }
                    ))
                    # Overlay frame number for debugging
                    cv2.putText(frame, f"Frame:{frame_id}", (int(x), int(y)-30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

            # --- DRAWING (Always runs for every object) ---
            cv2.rectangle(frame, (int(x-w/2), int(y-h/2)), (int(x+w/2), int(y+h/2)), color, 2)
            cv2.putText(frame, text, (int(x), int(y)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            if should_analyze:
                 cv2.arrowedLine(frame, (int(start_x), int(start_y)), (int(end_x), int(end_y)), color, 2)

        # Draw Detect Lines

        cv2.line(frame, (int(mid_x), 0), (int(mid_x), height), (255, 255, 0), 1)
        # Draw Ignore Zone
        cv2.line(frame, (0, ignore_y_min), (width, ignore_y_min), (100, 100, 100), 1)
        cv2.line(frame, (0, ignore_y_max), (width, ignore_y_max), (100, 100, 100), 1)

        return events
