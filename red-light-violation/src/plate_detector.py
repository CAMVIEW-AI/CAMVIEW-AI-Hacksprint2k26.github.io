from ultralytics import YOLO
import cv2

class PlateDetector:
    def __init__(self, model_path="models/license_plate.pt"):
        self.model = YOLO(model_path)

    def detect_and_crop(self, car_img, save_path):
        results = self.model(car_img, conf=0.4, verbose=False)[0]

        if results.boxes is None:
            return None

        # Take best plate
        box = results.boxes[0]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        plate_img = car_img[y1:y2, x1:x2]
        cv2.imwrite(save_path, plate_img)

        return plate_img
