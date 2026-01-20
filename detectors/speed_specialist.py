"""
Speed Specialist - Pure Logic Unit (Gold Standard)
Consumes VehicleState from Registry, calculates speed using 2-line virtual loop.
NO internal YOLO or tracking.
"""
import cv2
import time
from detectors.base_specialist import BaseSpecialist, Event
from config import settings

class SpeedSpecialist(BaseSpecialist):
    def __init__(self):
        """
        Simple 2-line speed detection (Virtual Loop)
        Works with VehicleRegistry in integrated mode.
        """
        self.line1_y = None
        self.line2_y = None
        self.vehicle_timings = {}  # track_id -> {'entry_time': float, 'speed': float}
        self.alerted = set()
        
    def load_model(self):
        """No model needed - pure logic"""
        pass
    
    def calculate_speed(self, track_id, cy, current_time):
        """
        Calculate speed using 2-line crossing method.
        Returns: speed_kmh or None
        """
        if track_id not in self.vehicle_timings:
            self.vehicle_timings[track_id] = {'entry_time': None, 'speed': None}
        
        vehicle = self.vehicle_timings[track_id]
        
        # Check line 1 crossing (entry)
        if vehicle['entry_time'] is None and abs(cy - self.line1_y) < 25:
            vehicle['entry_time'] = current_time
            return None
        
        # Check line 2 crossing (exit)
        if vehicle['entry_time'] is not None and vehicle['speed'] is None:
            if abs(cy - self.line2_y) < 25:
                time_elapsed = current_time - vehicle['entry_time']
                if time_elapsed > 0.2:  # Minimum time threshold
                    # Distance between lines = 20m (configurable)
                    speed_mps = 20.0 / time_elapsed
                    speed_kmh = speed_mps * 3.6
                    
                    # Sanity check
                    if 10 < speed_kmh < 200:
                        vehicle['speed'] = speed_kmh
                        return speed_kmh
        
        return vehicle.get('speed')
    
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
        height, width, _ = frame.shape
        
        # Initialize virtual loop lines
        if self.line1_y is None:
            self.line1_y = int(height * 0.50)
            self.line2_y = int(height * 0.80)
        
        # Draw virtual loop lines
        cv2.line(frame, (0, self.line1_y), (width, self.line1_y), (0, 255, 255), 2)
        cv2.line(frame, (0, self.line2_y), (width, self.line2_y), (0, 255, 255), 2)
        cv2.putText(frame, "SPEED ZONE", (10, self.line1_y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        current_time = time.time()
        
        # Process tracks (if provided by integrated mode)
        if tracks is not None and registry is not None:
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                track_id = track.track_id
                ltrb = track.to_ltrb()
                x1, y1, x2, y2 = map(int, ltrb)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                # Calculate speed
                speed_kmh = self.calculate_speed(track_id, cy, current_time)
                
                # Update registry
                if speed_kmh is not None:
                    registry.update_speed(track_id, speed_kmh)
                    
                    # Visualization
                    color = (0, 255, 0)
                    label = f"{speed_kmh:.0f} km/h"
                    
                    if speed_kmh > settings.MAX_SPEED_LIMIT:
                        color = (0, 0, 255)
                        label = f"⚠️ {speed_kmh:.0f} km/h"
                        
                        # Generate event (only once per vehicle)
                        if track_id not in self.alerted:
                            events.append(Event(
                                event_type="OVERSPEEDING",
                                severity="WARNING",
                                description=f"Vehicle #{track_id} at {speed_kmh:.0f} km/h",
                                camera_id="CAM_01",
                                source="speed_specialist",
                                metadata={"bbox": [x1, y1, x2-x1, y2-y1], "speed": speed_kmh}
                            ))
                            self.alerted.add(track_id)
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return events
