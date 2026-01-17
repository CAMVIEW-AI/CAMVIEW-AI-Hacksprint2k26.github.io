import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Any
from config import settings

class BaseDetector:
    def __init__(self, model_path=settings.YOLO_MODEL_PATH):
        print(f"[SYSTEM] Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)
    
    def detect(self, frame):
        """
        Raw YOLO detection
        """
        results = self.model(frame, verbose=False, conf=settings.CONFIDENCE_THRESHOLD)
        return results[0]  # Return first result (single image/frame)

    def process(self, frame, frame_id: int):
        """
        To be implemented by subclasses.
        Should return a list of Event objects or triggering side effects.
        """
        raise NotImplementedError
