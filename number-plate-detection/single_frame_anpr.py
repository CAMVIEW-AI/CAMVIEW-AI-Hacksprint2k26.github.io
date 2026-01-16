from ultralytics import YOLO
import cv2
import easyocr
import numpy as np

# ---------------- LOAD MODELS ----------------
car_model   = YOLO("model/yolov8n.pt")
plate_model = YOLO("model/license_plate.pt")

reader = easyocr.Reader(['en'], gpu=False)

# ---------------- LOAD IMAGE ----------------
img = cv2.imread("input/bike.jpg")
if img is None:
    print("Image not found")
    exit()

img = cv2.resize(img, (1280, 720))

# ---------------- DETECT CARS ----------------
cars = car_model(img, conf=0.25)[0]
car_boxes = []

for d in cars.boxes.data.tolist():
    x1,y1,x2,y2,score,cls = d
    if int(cls) in [2,3,5,7]:   # car, bike, bus, truck
        car_boxes.append([x1,y1,x2,y2])

# ---------------- DETECT PLATES ----------------
plates = plate_model(img, conf=0.1)[0]

plate_id = 0

for p in plates.boxes.data.tolist():
    x1,y1,x2,y2,pscore,_ = p

    plate_crop = img[int(y1):int(y2), int(x1):int(x2)]
    if plate_crop.size == 0:
        continue

    # ---------------- OCR PREPROCESSING ----------------
    gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)

    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )

    # ---------------- OCR ----------------
    ocr = reader.readtext(thresh)
    text = ""
    if ocr:
        best = max(ocr, key=lambda x: x[2])
        text = best[1]

    # ---------------- ASSIGN TO CAR ----------------
    for c in car_boxes:
        cx1,cy1,cx2,cy2 = c
        if x1 > cx1 and y1 > cy1 and x2 < cx2 and y2 < cy2:

            # Draw car
            cv2.rectangle(img,(int(cx1),int(cy1)),(int(cx2),int(cy2)),(0,255,0),2)

            # Draw plate
            cv2.rectangle(img,(int(x1),int(y1)),(int(x2),int(y2)),(0,0,255),2)

            # Draw text
            if text:
                print("Detected Plate:", text) 
                cv2.putText(img, text, (int(cx1), int(cy1)-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

            # Show plate & OCR image
            plate_id += 1
            cv2.imshow(f"Plate_{plate_id}", plate_crop)
            cv2.imshow(f"OCR_{plate_id}", thresh)

# ---------------- SHOW RESULT ----------------
cv2.imshow("ANPR Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()  

