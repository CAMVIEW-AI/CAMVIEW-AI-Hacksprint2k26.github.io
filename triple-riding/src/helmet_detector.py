from ultralytics import YOLO

class HelmetDetector:
    def __init__(self, model_path="models/yolov8n.pt", conf=0.4):
        self.model = YOLO(model_path)
        self.conf = conf

        # COCO classes
        self.PERSON = 0
        self.BIKE = 3  # motorcycle

    def detect(self, frame):
        results = self.model(frame, conf=self.conf, verbose=False)[0]

        persons = []
        bikes = []

        if results.boxes is None:
            return persons, bikes

        for box in results.boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            if cls == self.PERSON:
                persons.append((x1, y1, x2, y2, conf))

            elif cls == self.BIKE:
                bikes.append((x1, y1, x2, y2, conf))

        return persons, bikes
