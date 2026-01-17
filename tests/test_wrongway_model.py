import cv2
import time
from detectors.wrong_way_specialist import WrongWaySpecialist
from config import settings

VIDEO_PATH = "data/test_video-1.mp4" # Default
OUTPUT_PATH = "wrongway_test_output.mp4"

def main():
    # Ask for video path
    video_path = input(f"Enter video path (default: {VIDEO_PATH}): ").strip('"')
    if not video_path: video_path = VIDEO_PATH

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height))

    specialist = WrongWaySpecialist()
    frame_id = 0

    print("Running Wrong-Way Test... Press 'q' to stop.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame_id += 1
        
        # Run Specialist
        events = specialist.process(frame, frame_id)
        
        for e in events:
             print(f"[ALERT] {e.event_type}: {e.description}")

        out.write(frame)
        
        # Progress indicator
        if frame_id % 30 == 0:
            print(f"Processing frame {frame_id}...")

    cap.release()
    out.release()
    print(f"Done. Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
