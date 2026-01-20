import cv2
import time
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.unified_processor import UnifiedVideoProcessor
from detectors.wrong_way_specialist import WrongWaySpecialist
from detectors.emergency_specialist import EmergencySpecialist
from detectors.pothole_specialist import PotholeSpecialist
from detectors.speed_specialist import SpeedSpecialist
from detectors.reid_specialist import ReIDSpecialist
from config import settings

def main():
    print("🚦 CAMVIEW.AI - Integrated System Test")
    print("========================================")
    
    # 1. Initialize Processor
    print("[System] Initializing Processor...")
    processor = UnifiedVideoProcessor()
    
    # 2. Initialize Specialists
    print("[System] Loading Specialists...")
    detectors = []
    
    # Pothole (Infrastructure)
    try:
        if os.path.exists("best.pt"):
            detectors.append(PotholeSpecialist(model_path="best.pt"))
            print("  ✅ PotholeSpecialist Loaded")
        else:
            print("  ⚠️ PotholeSpecialist Skipped (best.pt not found)")
    except Exception as e:
        print(f"  ❌ PotholeSpecialist Failed: {e}")

    # WrongWay (Violation)
    try:
        detectors.append(WrongWaySpecialist())
        print("  ✅ WrongWaySpecialist Loaded")
    except Exception as e:
        print(f"  ❌ WrongWaySpecialist Failed: {e}")
        
    # Emergency (Priority)
    try:
        detectors.append(EmergencySpecialist()) # Auto-loads models/emergency_best.pt
        print("  ✅ EmergencySpecialist Loaded")
    except Exception as e:
        print(f"  ❌ EmergencySpecialist Failed: {e}")
        
    # Speed (Analytics)
    try:
        detectors.append(SpeedSpecialist())
        print("  ✅ SpeedSpecialist Loaded")
    except Exception as e:
         print(f"  ❌ SpeedSpecialist Failed: {e}")
         
    # ReID (Tracking)
    try:
        detectors.append(ReIDSpecialist())
        print("  ✅ ReIDSpecialist Loaded")
    except Exception as e:
         print(f"  ❌ ReIDSpecialist Failed: {e}")

    # Register them
    processor.set_detectors(detectors)
    print(f"[System] {len(detectors)} Specialists Active.")
    
    # 3. Load Video
    video_path = input("Enter video path (default: data/test_video.mp4): ").strip().strip('"').strip("'")
    if not video_path:
        video_path = "data/test_video.mp4"
        
    # Search for video if not found
    if not os.path.exists(video_path):
        # Try finding any mp4 in root
        mp4s = [f for f in os.listdir('.') if f.endswith('.mp4')]
        if mp4s:
            print(f"Video not found. Using first available: {mp4s[0]}")
            video_path = mp4s[0]
        else:
            print("[Error] No video found.")
            return

    if not processor.load_video(video_path):
        print("[Error] Failed to load video.")
        return

    # 4. Process Loop with Recording
    output_path = "integrated_output.mp4"
    cap = processor.cap
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    print(f"\n[Processing] Started... Saving to {output_path}")
    print("Press Ctrl+C to stop early.")
    
    print(f"\n[Processing] Started... Saving to {output_path}")
    print("Press Ctrl+C to stop early.")
    
    try:
        while True:
            # Manually read frame since Processor is threaded design
            ret, frame = processor.cap.read()
            
            if not ret:
                break
                
            processor.status.current_frame += 1
            
            # Process frame through all detectors
            events = []
            processed_frame = frame.copy()
            
            for detector in detectors:
                try:
                    # Direct call to detector
                    detector_events = detector.process(processed_frame, processor.status.current_frame)
                    events.extend(detector_events)
                except Exception as e:
                    pass # Ignore individual detector failures during loop
            
            # Overlay Info
            cv2.putText(processed_frame, f"Frame: {processor.status.current_frame}", 
                       (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if events:
                 cv2.putText(processed_frame, f"Events: {len(events)}", 
                            (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Update stats
            processor.status.events_detected += len(events)
            processor.status.fps = 30.0 # Placeholder
                
            # Write to file
            writer.write(processed_frame)
            
            # Progress
            if processor.status.current_frame % 10 == 0:
                print(f"\rFrame: {processor.status.current_frame} | Events: {processor.status.events_detected}", end="")
                
    except KeyboardInterrupt:
        print("\n[Stopped] User interrupted.")
    finally:
        writer.release()
        processor.stop_processing()
        
    print(f"\n\n✅ Done! Output saved to: {os.path.abspath(output_path)}")
    print("Events Summary:")
    # We can't easily access the logger from here unless passing it, but console output verified visually.

if __name__ == "__main__":
    main()
