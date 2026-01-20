"""
Emergency Vehicle Specialist - Pure Logic Unit (Gold Standard)
Consumes vehicle crops from tracks, runs custom YOLOv11 model.
Updates VehicleRegistry with emergency status.
"""
import cv2
import numpy as np
from detectors.base_specialist import BaseSpecialist, Event
from ultralytics import YOLO
import os

class EmergencySpecialist(BaseSpecialist):
    def __init__(self, model_name='models/emergency_best.pt'):
        """
        Detects Emergency Vehicles using Custom Trained YOLOv11 Model.
        Runs inference on vehicle crops only (not full frame).
        """
        # Ensure model exists
        if not os.path.exists(model_name):
            print(f"[Warning] Custom model not found at {model_name}. Falling back to 'yolo11n.pt'")
            model_name = 'yolo11n.pt'
            
        self.model = self.load_model(model_name)
        
        # Dynamically determine target classes from model names
        self.target_indices = []
        self.class_mapping = {}
        
        # Keywords to look for in class names
        target_keywords = ['ambulance', 'fire', 'police', 'emergency', 'truck', 'bus']
        
        print(f"[EmergencySpecialist] Loading classes from {model_name}...")
        for idx, name in self.model.names.items():
            lower_name = name.lower()
            if any(k in lower_name for k in target_keywords):
                self.target_indices.append(idx)
                self.class_mapping[idx] = name
                print(f"  - Found Target Class [{idx}]: {name}")
                
        # If no custom classes found (fallback to standard COCO), map standard IDs
        if not self.target_indices and 'yolo' in model_name:
             # Fallback to COCO: 2=Car (often used for Police), 5=Bus, 7=Truck
             self.target_indices = [2, 5, 7]
             print("  - Using Standard COCO Fallback Classes [2, 5, 7]")

        self.confidence_threshold = 0.95  # Extremely high threshold to eliminate false positives

    def load_model(self, model_name):
        return YOLO(model_name)
    
    def verify_emergency_features(self, crop):
        """
        Visual verification: Check for emergency vehicle features.
        Returns: (has_features, confidence_boost)
        """
        if crop is None or crop.size == 0:
            return False, 0.0
        
        h, w = crop.shape[:2]
        if h < 50 or w < 50:
            return False, 0.0
        
        # Convert to HSV for color analysis
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        
        # Check for bright blue/red lights (emergency lights)
        # Blue lights (police)
        blue_mask = cv2.inRange(hsv, np.array([100, 150, 200]), np.array([130, 255, 255]))
        blue_ratio = np.count_nonzero(blue_mask) / (h * w)
        
        # Red lights (fire/ambulance)
        red_mask1 = cv2.inRange(hsv, np.array([0, 150, 200]), np.array([10, 255, 255]))
        red_mask2 = cv2.inRange(hsv, np.array([170, 150, 200]), np.array([180, 255, 255]))
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        red_ratio = np.count_nonzero(red_mask) / (h * w)
        
        # Check for white body (common in emergency vehicles)
        white_mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 30, 255]))
        white_ratio = np.count_nonzero(white_mask) / (h * w)
        
        # Check top portion for light bars (emergency vehicles have lights on top)
        top_portion = crop[:int(h*0.3), :]
        top_hsv = cv2.cvtColor(top_portion, cv2.COLOR_BGR2HSV)
        top_bright = cv2.inRange(top_hsv, np.array([0, 0, 220]), np.array([180, 50, 255]))
        top_bright_ratio = np.count_nonzero(top_bright) / (top_portion.shape[0] * top_portion.shape[1])
        
        # Scoring logic
        has_features = False
        confidence_boost = 0.0
        
        # Strong indicators
        if blue_ratio > 0.02 and white_ratio > 0.3:  # Blue lights + white body
            has_features = True
            confidence_boost = 0.15
        elif red_ratio > 0.02 and white_ratio > 0.3:  # Red lights + white body
            has_features = True
            confidence_boost = 0.15
        elif top_bright_ratio > 0.2:  # Bright top (light bar)
            has_features = True
            confidence_boost = 0.10
        
        return has_features, confidence_boost
    
    def classify_vehicle_crop(self, crop):
        """
        Run emergency model on vehicle crop with visual verification.
        Returns: (is_emergency, emergency_type, confidence)
        """
        if crop is None or crop.size == 0:
            return False, "None", 0.0
        
        try:
            results = self.model(crop, verbose=False, imgsz=640)[0]
        except:
            results = self.model(crop, verbose=False)[0]
        
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            if cls_id in self.target_indices:
                class_name = self.model.names[cls_id]
                
                # Primary check: Model confidence
                if conf > self.confidence_threshold:
                    return True, class_name, conf
                
                # Secondary check: Visual verification (if confidence is close)
                if conf > 0.70:  # Lower threshold for visual verification
                    has_features, boost = self.verify_emergency_features(crop)
                    if has_features:
                        adjusted_conf = min(1.0, conf + boost)
                        if adjusted_conf > self.confidence_threshold:
                            return True, class_name, adjusted_conf
        
        return False, "None", 0.0

    def process(self, frame, frame_id=0, registry=None, tracks=None):
        """
        Process frame with pre-computed tracks and registry.
        Runs emergency detection on vehicle crops.
        
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
        
        # Process tracks (if provided by integrated mode)
        if tracks is None or registry is None:
            return []
        
        h_img, w_img, _ = frame.shape
        
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            w, h = x2 - x1, y2 - y1
            
            # Boundary checks
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_img, x2), min(h_img, y2)
            
            # SIZE FILTER: Emergency vehicles are typically larger
            # Reject small vehicles (likely sedans/compact cars)
            MIN_WIDTH = 100   # Increased from 80
            MIN_HEIGHT = 100  # Increased from 80
            MIN_AREA = 12000  # Increased from 8000 pixels²
            
            vehicle_area = w * h
            
            if w < MIN_WIDTH or h < MIN_HEIGHT or vehicle_area < MIN_AREA:
                continue  # Skip small vehicles
            
            # Extract vehicle crop
            vehicle_crop = frame[y1:y2, x1:x2]
            
            # Classify crop
            is_emergency, em_type, conf = self.classify_vehicle_crop(vehicle_crop)
            
            if is_emergency:
                # Update registry (this is the source of truth)
                registry.mark_emergency(track_id, em_type)
                
                # Determine color for UI
                color = (0, 0, 255)  # Default Red
                if "ambulance" in em_type.lower():
                    color = (255, 255, 0)  # Cyan
                elif "police" in em_type.lower():
                    color = (255, 0, 0)  # Blue
                elif "fire" in em_type.lower():
                    color = (0, 0, 255)  # Red
                
                # Visualize
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                cv2.putText(frame, f"{em_type} {conf:.0%}", (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # NOTE: Events are generated by Registry's rule engine
                # We don't create events here to avoid bypassing cooldown logic
        
        return events  # Empty - Registry handles event generation
