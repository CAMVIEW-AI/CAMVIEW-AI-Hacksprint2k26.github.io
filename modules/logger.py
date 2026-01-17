import json
import os
import logging
from core.events import Event
from core.event_bus import bus
from config import settings
from core import firebase_client

# Configure standard logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EventLogger:
    def __init__(self, log_file: str = None):
        # Use configurable log file or default
        self.log_file = log_file or getattr(settings, 'USER_EVENT_LOG_FILE', settings.EVENT_LOG_FILE)
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Initialize Firebase with configurable credentials
        firebase_path = getattr(settings, 'USER_FIREBASE_CREDENTIALS', settings.FIREBASE_CREDENTIALS)
        
        # Temporarily update settings for Firebase initialization
        original_firebase_path = settings.FIREBASE_CREDENTIALS
        settings.FIREBASE_CREDENTIALS = firebase_path
        
        firebase_client.initialize_firebase()
        
        # Restore original path
        settings.FIREBASE_CREDENTIALS = original_firebase_path
        
        # Subscribe to all events
        bus.subscribe("*", self.handle_event)
        print(f"[SYSTEM] Logger initialized. Writing to {self.log_file}")
        if os.path.exists(firebase_path):
            print(f"[SYSTEM] Firebase configured: {firebase_path}")
        else:
            print("[SYSTEM] Firebase not configured - using local storage only")

    def handle_event(self, event: Event):
        """
        Log event to console, file, and Firebase
        """
        # 1. Console Output (Terminal)
        self._print_terminal(event)
        
        # 2. File Output (JSONL)
        self._write_file(event)
        
        # 3. Firebase Output (Firestore)
        self._write_firebase(event)

    def _print_terminal(self, event: Event):
        if event.severity == "CRITICAL":
            prefix = "[!!! CRITICAL ALERT !!!]"
        elif event.severity == "WARNING":
            prefix = "[WARNING]"
        else:
            prefix = "[INFO]"
            
        print(f"{prefix} {event.event_type} @ {event.time_str} | Camera: {event.camera_id} | {event.metadata}")

    def _write_file(self, event: Event):
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(event.to_dict()) + "\n")
        except Exception as e:
            logging.error(f"Failed to write to log file: {e}")
    
    def _write_firebase(self, event: Event):
        """Write event to Firebase Firestore"""
        try:
            firebase_client.save_event(event.to_dict())
        except Exception as e:
            logging.debug(f"Firebase write skipped: {e}")

# Singleton to be initialized in main
