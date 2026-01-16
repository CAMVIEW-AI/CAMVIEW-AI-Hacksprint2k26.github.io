import easyocr
import cv2
import re

class PlateOCR:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def read(self, plate_img):
        if plate_img is None or plate_img.size == 0:
            return ""

        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)

        results = self.reader.readtext(gray)

        text = ""
        for (_, t, conf) in results:
            if conf > 0.4:
                text += t + " "

        text = text.upper().strip()
        text = re.sub(r'[^A-Z0-9]', '', text)

        return text
