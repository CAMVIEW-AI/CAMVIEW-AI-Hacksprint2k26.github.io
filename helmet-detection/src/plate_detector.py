from ultralytics import YOLO
import cv2

class PlateDetector:
    def __init__(self, model_path="models/license_plate.pt", conf=0.4):
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, image):
        if image is None or image.size == 0:
            return None, None

        h, w = image.shape[:2]
        results = self.model(image, conf=self.conf, verbose=False)[0]

        if results.boxes is None:
            return None, None

        best_box = None
        best_conf = 0

        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            if conf > best_conf:
                best_conf = conf
                best_box = (x1, y1, x2, y2)

        if best_box is None:
            return None, None

        x1, y1, x2, y2 = best_box

        # 🔥 CLAMP VALUES (VERY IMPORTANT)
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w - 1, x2)
        y2 = min(h - 1, y2)

        if x2 <= x1 or y2 <= y1:
            return None, None

        plate_crop = image[y1:y2, x1:x2]

        if plate_crop.size == 0:
            return None, None

        return plate_crop, (x1, y1, x2, y2)
