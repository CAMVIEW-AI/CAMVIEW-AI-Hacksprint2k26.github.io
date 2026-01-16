import cv2
import numpy as np
import os
from datetime import datetime

from src.video_reader import VideoReader
from src.traffic_light import TrafficLightDetector
from src.stop_line import StopLineDetector
from src.vehicle_detector import VehicleDetector
from src.violation import ViolationDetector
from src.plate_detector import PlateDetector
from src.ocr import read_plate
from src.reporter import generate_report

from sort.sort import Sort

# =========================
# CONFIG
# =========================
VIDEO_PATH = "input/video.mp4"

TRAFFIC_LIGHT_ROI = (75, 46, 93, 266)

STOP_X1, STOP_Y1 = 291, 735
STOP_X2, STOP_Y2 = 1918, 733

SLOPE = (STOP_Y2 - STOP_Y1) / (STOP_X2 - STOP_X1)
INTERCEPT = STOP_Y1 - SLOPE * STOP_X1

REPORTS_DIR = "reports"

# =========================
# INIT
# =========================
os.makedirs(REPORTS_DIR, exist_ok=True)

reader = VideoReader(VIDEO_PATH)
traffic_light = TrafficLightDetector(TRAFFIC_LIGHT_ROI)
stop_line = StopLineDetector()

vehicle_detector = VehicleDetector("models/yolov8n.pt")
plate_detector = PlateDetector("models/license_plate.pt")

tracker = Sort(max_age=15, min_hits=3, iou_threshold=0.3)
violation_checker = ViolationDetector(SLOPE, INTERCEPT)

delay = int(1000 / reader.fps)

violation_count = 0
reported_ids = set()

print("[INFO] Traffic AI started")

# =========================
# MAIN LOOP
# =========================
while True:
    frame = reader.read()
    if frame is None:
        break

    # 1. Traffic light
    signal = traffic_light.detect(frame)
    traffic_light.draw(frame, signal)

    # 2. Stop line
    frame, stop_line_pts, mask_line = stop_line.detect(frame, signal)

    # 3. Vehicle detection + tracking
    detections = vehicle_detector.detect(frame)
    tracks = tracker.update(detections) if len(detections) else []

    # 4. Violation logic
    for t in tracks:
        x1, y1, x2, y2, track_id = map(int, t)

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        violated = violation_checker.check(
            track_id=track_id,
            cx=cx,
            cy=cy,
            signal=signal
        )

        color = (0, 0, 255) if violated else (0, 255, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.circle(frame, (cx, cy), 4, color, -1)

        cv2.putText(
            frame,
            f"ID {track_id}",
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

        # =========================
        # 🚨 ON VIOLATION (ONCE)
        # =========================
        if violated and track_id not in reported_ids:
            reported_ids.add(track_id)
            violation_count += 1

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            folder = os.path.join(REPORTS_DIR, f"violation_{violation_count:03d}")
            os.makedirs(folder, exist_ok=True)

            print(
                f"[VIOLATION] ID={track_id} | Time={timestamp} | "
                f"Center=({cx},{cy}) | Signal=RED"
            )

            # --------- CAR CROP ---------
            car_img = frame[y1:y2, x1:x2]
            car_path = os.path.join(folder, "car.jpg")
            cv2.imwrite(car_path, car_img)

            # --------- PLATE DETECTION ---------
            plate_path = os.path.join(folder, "plate.jpg")
            plate_img = plate_detector.detect_and_crop(car_img, plate_path)

            plate_text = "NOT_DETECTED"
            if plate_img is not None:
                plate_text = read_plate(plate_img)

            # --------- REPORT DATA ---------
            report_data = {
                "violation_type": "Red Light Violation",
                "vehicle_id": track_id,
                "signal": signal,
                "time": timestamp,
                "number_plate": plate_text,
            }

            # --------- GENERATE REPORT ---------
            generate_report(report_data, folder)

            print(f"[REPORT GENERATED] {folder}")

            cv2.putText(
                frame,
                "RED LIGHT VIOLATION",
                (x1, y2 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

    # DISPLAY
    display = reader.resize_for_display(frame)
    cv2.imshow("Traffic AI - Live", display)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

# =========================
# CLEANUP
# =========================
reader.release()
print("[INFO] Traffic AI stopped")
