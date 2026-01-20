"""
Unified Video Processing Service
Handles video processing with Optimized Architecture (Shared Detection)
"""
import cv2
import time
import threading
import queue
from typing import List, Optional, Callable
from dataclasses import dataclass
from core.events import Event
from core.event_bus import bus
from core.vehicle_registry import VehicleRegistry
from config import settings
from ultralytics import YOLO

# Detectors
from detectors.speed_specialist import SpeedSpecialist
from detectors.wrong_way_specialist import WrongWaySpecialist
from detectors.emergency_specialist import EmergencySpecialist
from detectors.reid_specialist import ReIDSpecialist
from detectors.pothole_specialist import PotholeSpecialist
from detectors.base_specialist import BaseSpecialist

# Tracker
# Using a simple SORT/DeepSort wrapper logic here for demonstration 
# or importing existing tracking logic if available.
# To allow "One Frame One Detection", we integrate tracking here.
from deep_sort_realtime.deepsort_tracker import DeepSort

@dataclass
class ProcessingStatus:
    is_processing: bool = False
    current_frame: int = 0
    total_frames: int = 0
    fps: float = 30.0
    events_detected: int = 0
    processing_time: float = 0.0
    last_update: float = 0.0

class UnifiedVideoProcessor:
    def __init__(self):
        self.status = ProcessingStatus()
        self.registry = VehicleRegistry()
        
        # 1. Base Detector (YOLO) - The "Eye"
        print("[Processor] Loading Base YOLO Model...")
        self.base_model = YOLO("yolo11n.pt") 
        
        # 2. Base Tracker
        self.tracker = DeepSort(max_age=30, n_init=3)
        
        # 3. Specialists
        self.specialists = {
            "speed": SpeedSpecialist(),
            "wrong_way": WrongWaySpecialist(),
            "emergency": EmergencySpecialist(), 
            "reid": ReIDSpecialist(),
            "pothole": PotholeSpecialist()
        }
        
        self.cap = None
        self.stop_event = threading.Event()
        self.frame_queue = queue.Queue(maxsize=30)
        self.processing_thread = None
        self.stats_lock = threading.Lock()
        
    def load_video(self, source):
        try:
            if isinstance(source, str):
                self.cap = cv2.VideoCapture(source)
                if self.cap.isOpened():
                    self.status.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    return True
        except Exception as e:
            print(f"[ERROR] Load Video: {e}")
        return False
    
    def start_processing(self):
        if not self.cap or not self.cap.isOpened(): return False
        self.stop_event.clear()
        self.status.is_processing = True
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        return True
    
    def stop_processing(self):
        self.stop_event.set()
        if self.processing_thread: self.processing_thread.join(timeout=2)
        if self.cap: self.cap.release()
            
    def _processing_loop(self):
        while not self.stop_event.is_set() and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
            
            self.status.current_frame += 1
            start = time.time()
            
            # --- LEVEL 1: BASE DETECTION (Run ONCE) ---
            # Detect vehicles (2=Car, 3=Motorcycle, 5=Bus, 7=Truck)
            results = self.base_model(frame, classes=[2,3,5,7], verbose=False, conf=0.4)[0]
            
            # Format for Tracker: [[left, top, w, h], conf, detection_class]
            detections = []
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w, h = x2-x1, y2-y1
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                detections.append([[x1, y1, w, h], conf, cls])
                
            # --- LEVEL 2: TRACKING ---
            tracks = self.tracker.update_tracks(detections, frame=frame)
            
            # Update Registry with all tracks
            for track in tracks:
                if not track.is_confirmed(): continue
                
                track_id = track.track_id
                ltrb = track.to_ltrb()
                x1, y1, x2, y2 = map(int, ltrb)
                w, h = x2 - x1, y2 - y1
                
                # Update vehicle state in registry
                self.registry.update_vehicle(track_id, [x1, y1, w, h])
            
            # --- LEVEL 3: SPECIALISTS (Pure Logic Units) ---
            active_events = []
            
            # 3.1 Speed Specialist
            try:
                speed_events = self.specialists['speed'].process(
                    frame, self.status.current_frame, 
                    registry=self.registry, tracks=tracks
                )
                active_events.extend(speed_events)
            except Exception as e:
                print(f"[ERROR] SpeedSpecialist: {e}")
            
            # 3.2 WrongWay Specialist
            try:
                wrongway_events = self.specialists['wrong_way'].process(
                    frame, self.status.current_frame,
                    registry=self.registry, tracks=tracks
                )
                active_events.extend(wrongway_events)
            except Exception as e:
                print(f"[ERROR] WrongWaySpecialist: {e}")
            
            # 3.3 Emergency Specialist
            try:
                emergency_events = self.specialists['emergency'].process(
                    frame, self.status.current_frame,
                    registry=self.registry, tracks=tracks
                )
                active_events.extend(emergency_events)
            except Exception as e:
                print(f"[ERROR] EmergencySpecialist: {e}")
            
            # 3.4 ReID Specialist
            try:
                reid_events = self.specialists['reid'].process(
                    frame, self.status.current_frame,
                    registry=self.registry, tracks=tracks
                )
                active_events.extend(reid_events)
            except Exception as e:
                print(f"[ERROR] ReIDSpecialist: {e}")
            
            # --- LEVEL 4: POTHOLE (Async / N-th frame) ---
            if self.status.current_frame % 5 == 0:
                try:
                    pothole_events = self.specialists['pothole'].process(frame, self.status.current_frame)
                    active_events.extend(pothole_events)
                except Exception as e:
                    print(f"[ERROR] PotholeSpecialist: {e}")
            
            # --- LEVEL 5: RULE ENGINE (Emergency Override) ---
            # Get rule-based events from Registry
            # Only check vehicles that haven't been checked this frame
            checked_vehicles = set()
            for track_id in list(self.registry.vehicles.keys()):
                if track_id in checked_vehicles:
                    continue
                checked_vehicles.add(track_id)
                
                rule_events = self.registry.check_rules_and_get_events(track_id)
                for e_dict in rule_events:
                    evt = Event(
                        event_type=e_dict['type'],
                        severity=e_dict['severity'],
                        description=e_dict['description'],
                        timestamp=self.status.current_frame,
                        metadata=e_dict.get('metadata', {})
                    )
                    active_events.append(evt)
                    bus.publish(evt)
            
            # Cleanup old vehicles
            self.registry.cleanup()
            
            # Update Stats
            with self.stats_lock:
                self.status.events_detected += len(active_events)
            
            # Queue frame
            try:
                self.frame_queue.put_nowait(frame)
            except: pass
            
            # FPS Control
            time.sleep(max(0, 1/30 - (time.time() - start)))

    def get_frame(self):
        try: return self.frame_queue.get_nowait()
        except: return None
    
    def get_status(self):
        with self.stats_lock:
             return self.status

_processor_instance = None
def get_processor():
    global _processor_instance
    if not _processor_instance: _processor_instance = UnifiedVideoProcessor()
    return _processor_instance
