"""
CAMVIEW.AI - Integrated System Test (Gold Standard Architecture)
Tests the optimized unified processor with shared detection and VehicleRegistry
"""
import cv2
import os
import sys
import time

sys.path.append(os.getcwd())

from core.unified_processor import UnifiedVideoProcessor

def main():
    print("🚦 CAMVIEW.AI - Gold Standard Architecture Test")
    print("=" * 60)
    print("Features:")
    print("  ✓ Single YOLO inference per frame")
    print("  ✓ Shared DeepSort tracking")
    print("  ✓ VehicleRegistry state management")
    print("  ✓ Emergency override logic")
    print("  ✓ Event cooldown (5s)")
    print("=" * 60)
    
    # Initialize Unified Processor (loads all specialists internally)
    print("\n[System] Initializing Unified Processor...")
    processor = UnifiedVideoProcessor()
    
    # Load Video
    video_path = input("\nEnter video path (default: emergency_test_output.mp4): ").strip().strip('"').strip("'")
    if not video_path:
        # Try to find a video
        if os.path.exists("emergency_test_output.mp4"):
            video_path = "emergency_test_output.mp4"
        elif os.path.exists("data/test_video.mp4"):
            video_path = "data/test_video.mp4"
        else:
            print("[Error] No video found.")
            return
    
    if not os.path.exists(video_path):
        print(f"[Error] Video not found: {video_path}")
        return
        
    print(f"[System] Loading video: {video_path}")
    if not processor.load_video(video_path):
        print("[Error] Failed to load video.")
        return
    
    # Setup output
    output_path = "gold_standard_output.mp4"
    width = int(processor.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(processor.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = processor.cap.get(cv2.CAP_PROP_FPS) or 30.0
    
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    print(f"\n[Processing] Started...")
    print(f"  Output: {output_path}")
    print(f"  Resolution: {width}x{height} @ {fps:.1f} FPS")
    print("\nPress Ctrl+C to stop early.\n")
    
    # Start processing in background thread
    processor.start_processing()
    
    frame_count = 0
    last_frame_time = time.time()
    timeout = 5.0  # 5 seconds without frames = timeout
    
    try:
        while processor.status.is_processing:
            # Get processed frame from queue
            frame = processor.get_frame()
            
            if frame is not None:
                # Write to output
                writer.write(frame)
                frame_count += 1
                last_frame_time = time.time()
                
                # Progress (every 30 frames)
                if frame_count % 30 == 0:
                    status = processor.get_status()
                    print(f"\rFrame: {status.current_frame}/{status.total_frames} | "
                          f"Events: {status.events_detected} | "
                          f"Vehicles: {len(processor.registry.vehicles)}", end="", flush=True)
            else:
                # No frame available, check timeout
                if time.time() - last_frame_time > timeout:
                    print(f"\n[Warning] No frames received for {timeout}s, stopping...")
                    break
                time.sleep(0.01)  # Small sleep to avoid busy waiting
            
            # Check if processing is complete
            status = processor.get_status()
            if not status.is_processing:
                break
                
    except KeyboardInterrupt:
        print("\n[Stopped] User interrupted.")
    finally:
        processor.stop_processing()
        writer.release()
    
    print(f"\n\n✅ Processing Complete!")
    print(f"   Output: {os.path.abspath(output_path)}")
    print(f"   Total Events: {processor.status.events_detected}")
    print(f"   Total Frames Processed: {frame_count}")
    
    # Registry stats
    print(f"\n📊 Vehicle Registry Stats:")
    print(f"   Active Vehicles: {len(processor.registry.vehicles)}")
    
    # Count vehicle types
    emergency_count = sum(1 for v in processor.registry.vehicles.values() if v.is_emergency)
    speeding_count = sum(1 for v in processor.registry.vehicles.values() if v.is_overspeeding)
    wrong_way_count = sum(1 for v in processor.registry.vehicles.values() if v.is_wrong_way)
    
    print(f"   Emergency Vehicles: {emergency_count}")
    print(f"   Speeding Vehicles: {speeding_count}")
    print(f"   Wrong-Way Vehicles: {wrong_way_count}")

if __name__ == "__main__":
    main()
