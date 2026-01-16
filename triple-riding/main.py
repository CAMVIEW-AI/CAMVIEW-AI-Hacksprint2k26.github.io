import cv2
import numpy as np

from src.video_reader import VideoReader
from src.helmet_detector import HelmetDetector
from sort.sort import Sort

# =========================
# CONFIG
# =========================
VIDEO_PATH = "input/demo.mp4"

# =========================
# INIT
# =========================
reader = VideoReader(VIDEO_PATH)
detector = HelmetDetector()

# 🔥 Track ONLY bikes
bike_tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

# 🔥 Store violated bike IDs (one-time trigger)
violated_bike_ids = set()

delay = int(1000 / reader.fps)

print("[INFO] Triple Riding - Step 3 started")

# =========================
# MAIN LOOP
# =========================
while True:
    frame = reader.read()
    if frame is None:
        break

    persons, bikes = detector.detect(frame)

    # -----------------------
    # PREPARE BIKE DETECTIONS
    # -----------------------
    bike_dets = []
    for bx1, by1, bx2, by2, conf in bikes:
        bike_dets.append([bx1, by1, bx2, by2, conf])

    bike_dets = np.array(bike_dets) if len(bike_dets) else np.empty((0, 5))
    tracked_bikes = bike_tracker.update(bike_dets)

    # -----------------------
    # DRAW PERSONS
    # -----------------------
    for px1, py1, px2, py2, _ in persons:
        cv2.rectangle(frame, (px1, py1), (px2, py2), (255, 0, 0), 2)

    # -----------------------
    # PROCESS EACH BIKE
    # -----------------------
    for b in tracked_bikes:
        bx1, by1, bx2, by2, bike_id = map(int, b)

        # ---- find persons inside bike ----
        riders = []
        for px1, py1, px2, py2, _ in persons:
            cx = (px1 + px2) // 2
            cy = (py1 + py2) // 2

            if bx1 <= cx <= bx2 and by1 <= cy <= by2:
                riders.append((px1, py1, px2, py2))

        rider_count = len(riders)

        # ---- draw bike ----
        color = (0, 255, 255)
        label = f"BIKE ID {bike_id} | Riders {rider_count}"

        # 🔥 TRIPLE RIDING LOGIC
        if rider_count >= 3:
            color = (0, 0, 255)
            label = f"TRIPLE RIDING | ID {bike_id}"

            if bike_id not in violated_bike_ids:
                violated_bike_ids.add(bike_id)
                print(f"[TRIPLE RIDING] Bike ID={bike_id} | Riders={rider_count}")

        cv2.rectangle(frame, (bx1, by1), (bx2, by2), color, 3)
        cv2.putText(
            frame,
            label,
            (bx1, by1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

        # ---- highlight riders ----
        for rx1, ry1, rx2, ry2 in riders:
            cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), color, 2)

    # -----------------------
    # DISPLAY
    # -----------------------
    cv2.imshow(
        "Triple Riding - Step 3",
        reader.resize_for_display(frame)
    )

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

# =========================
# CLEANUP
# =========================
reader.release()
print("[INFO] Step 3 finished")
