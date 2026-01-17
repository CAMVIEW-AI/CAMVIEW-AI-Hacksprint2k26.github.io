import cv2
import time
import threading
from typing import List, Optional
from core.events import Event
from core.event_bus import bus
from detectors.yolo_wrapper import BaseDetector
from config import settings

class TrafficSafetyEngine:
    def __init__(self, video_source=0, detectors: List[BaseDetector] = None):
        self.video_source = video_source
        self.detectors = detectors or []
        self.running = False
        self.frame_id = 0
        self.cap = None

    def start(self):
        """Start the processing loop in a separate thread (optional) or blocking."""
        self.running = True
        self._process_loop()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

    def _process_loop(self):
        print(f"[ENGINE] Opening video source: {self.video_source}")
        self.cap = cv2.VideoCapture(self.video_source)
        
        if not self.cap.isOpened():
            print(f"[ERROR] Could not open video source {self.video_source}")
            return

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("[ENGINE] Video ended or failed to read.")
                break

            self.frame_id += 1
            
            # 1. Run Detectors
            for detector in self.detectors:
                try:
                    events = detector.process(frame, self.frame_id)
                    # 2. Publish Events
                    for event in events:
                        bus.publish(event)
                        
                        # VISUALIZATION (Simple: Draw on frame for now)
                        # In a real app, this should be decoupled, but for debugging/demo we draw here.
                        # Note: `detector.process` doesn't currently return bbox, so we need to rely on the detector to draw 
                        # OR change the detector to return bbox in metadata.
                        # For this quick fix, I will ask the detectors to draw on the frame directly or we trust the visual output implementation.
                        
                        # Let's modify the detectors to return 'yolo_results' or draw themselves? 
                        # Simpler: Just overlay the event text.
                        cv2.putText(frame, f"{event.event_type} {event.severity}", (20, 40 + (len(events)*30)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                except Exception as e:
                    print(f"[ERROR] Detector failed: {e}")

            # 3. Show Video Feed (Debug View)
            # Add some info
            cv2.putText(frame, f"Frame: {self.frame_id}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Resize for screen if too large
            # display_frame = cv2.resize(frame, (1024, 768))

            cv2.namedWindow("CAMVIEW AI - Debug Feed", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("CAMVIEW AI - Debug Feed", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("CAMVIEW AI - Debug Feed", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
                break

            # Optional: Sleep to simulate realtime if processing is too fast on prerecorded
            # time.sleep(0.01)

        self.cap.release()
        cv2.destroyAllWindows()
        print("[ENGINE] Stopped.")
