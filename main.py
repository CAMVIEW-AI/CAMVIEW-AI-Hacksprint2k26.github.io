import argparse
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.unified_processor import get_processor
from detectors.wrong_way_specialist import WrongWaySpecialist
from detectors.emergency_specialist import EmergencySpecialist
from detectors.pothole_specialist import PotholeSpecialist
from detectors.speed_specialist import SpeedSpecialist
from detectors.reid_specialist import ReIDSpecialist
from modules.logger import EventLogger
from config import settings

def main():
    parser = argparse.ArgumentParser(description="CAMVIEW.AI Terminal Processing Engine - Video File Analysis Only")
    parser.add_argument("--source", type=str, required=True, help="Video file path (required)")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode with mock events if needed")
    parser.add_argument("--headless", action="store_true", help="Run without GUI (terminal only)")
    args = parser.parse_args()

    # Validate source is a file (not webcam)
    if args.source.isdigit() or args.source == "0":
        print("[ERROR] Webcam processing is not supported in terminal mode. Please provide a video file path.")
        print("Usage: python main.py --source path/to/video.mp4")
        return
    
    if not os.path.exists(args.source):
        print(f"[ERROR] Video file not found: {args.source}")
        return

    # 1. Initialize Logger
    logger = EventLogger()

    # 2. Initialize Detectors
    print("[SYSTEM] Initializing Unified Traffic Safety Processor...")
    detectors = []
    
    try:
        detectors.append(WrongWaySpecialist())
        detectors.append(EmergencySpecialist())
        detectors.append(PotholeSpecialist())
        detectors.append(SpeedSpecialist())
        detectors.append(ReIDSpecialist())
        print(f"[SYSTEM] Loaded {len(detectors)} detection modules")
    except Exception as e:
        print(f"[ERROR] Failed to load detectors: {e}")
        return

    # 3. Initialize Unified Processor
    processor = get_processor()
    processor.set_detectors(detectors)
    
    # Set up callbacks for terminal output
    def frame_callback(frame, events):
        """Handle frame updates (optional for terminal mode)"""
        pass  # No frame display in headless mode
    
    def event_callback(events):
        """Handle event updates"""
        for event in events:
            print(f"[EVENT] {event.event_type} - {event.severity} at {event.time_str}")
    
    processor.set_callbacks(frame_callback, event_callback)

    # 4. Load Video Source
    source = args.source  # Already validated as file path

    print(f"[SYSTEM] Loading video file: {source}")
    
    if not processor.load_video(source):
        print(f"[ERROR] Failed to load video file: {source}")
        return

    # 5. Start Processing
    print("[SYSTEM] Starting video file processing...")
    print("[SYSTEM] Press Ctrl+C to stop")
    
    try:
        processor.start_processing()
        
        # Monitor processing
        while True:
            status = processor.get_status()
            if not status.is_processing:
                print("[SYSTEM] Video processing completed")
                break
            
            # Print status every 10 seconds
            if int(status.current_frame) % 300 == 0:  # Assuming ~30fps
                print(f"[STATUS] Frame: {status.current_frame}, Events: {status.events_detected}, FPS: {status.fps:.1f}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n[SYSTEM] Stopping video processing...")
        processor.stop_processing()
        print("[SYSTEM] Exiting...")

if __name__ == "__main__":
    main()
