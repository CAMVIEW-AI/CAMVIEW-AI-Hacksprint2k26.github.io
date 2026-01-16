from ultralytics import YOLO

class HelmetDetector:
    def __init__(
        self,
        person_bike_model="models/yolov8n.pt",
        helmet_model="models/helmet.pt",
        conf=0.4
    ):
        # Models
        self.pb_model = YOLO(person_bike_model)
        self.helmet_model = YOLO(helmet_model)
        self.conf = conf

        # COCO classes
        self.PERSON = 0
        self.MOTORCYCLE = 3

        # Helmet model classes
        self.WITH_HELMET = 0
        self.WITHOUT_HELMET = 1

    def detect(self, frame):
        persons = []
        bikes = []
        helmets = []  # (x1, y1, x2, y2, label, conf)

        # -------------------------
        # 1. PERSON + BIKE DETECTION
        # -------------------------
        pb_results = self.pb_model(frame, conf=self.conf, verbose=False)[0]

        for box in pb_results.boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            if cls == self.PERSON:
                persons.append((x1, y1, x2, y2, conf))

            elif cls == self.MOTORCYCLE:
                bikes.append((x1, y1, x2, y2, conf))

        # -------------------------
        # 2. HELMET / NO-HELMET
        # -------------------------
        helmet_results = self.helmet_model(frame, conf=self.conf, verbose=False)[0]

        for box in helmet_results.boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            if cls == self.WITH_HELMET:
                helmets.append((x1, y1, x2, y2, "WITH_HELMET", conf))

            elif cls == self.WITHOUT_HELMET:
                helmets.append((x1, y1, x2, y2, "WITHOUT_HELMET", conf))

        return persons, bikes, helmets
