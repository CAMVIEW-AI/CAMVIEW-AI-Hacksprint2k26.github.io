import cv2
from detectors.reid_specialist import ReIDSpecialist
from config import settings

VIDEO_PATH = "data/test_video.mp4"
OUTPUT_PATH = "reid_test_output.mp4"

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

    specialist = ReIDSpecialist()
    frame_id = 0

    print("Running ReID Test... Processing video.")
    print("ReID tracks vehicles across frames and re-identifies them if they disappear and reappear.")

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
    print("\nReID Specialist tracks vehicle IDs persistently.")
    print("Check the output video to see consistent ID numbers even when vehicles are occluded.")

if __name__ == "__main__":
    main()
