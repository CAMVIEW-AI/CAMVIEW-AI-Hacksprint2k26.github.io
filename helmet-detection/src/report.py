import os
import json
import cv2
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class HelmetReportManager:
    def __init__(self, base_dir="reports"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.counter = 1

    def create_report(self, bike_img, plate_img, plate_text):
        folder = f"helmet_violation_{self.counter:03d}"
        path = os.path.join(self.base_dir, folder)
        os.makedirs(path, exist_ok=True)

        bike_path = os.path.join(path, "bike.jpg")
        plate_path = os.path.join(path, "plate.jpg")
        json_path = os.path.join(path, "report.json")
        pdf_path = os.path.join(path, "report.pdf")

        cv2.imwrite(bike_path, bike_img)
        if plate_img is not None:
            cv2.imwrite(plate_path, plate_img)

        data = {
            "violation_type": "NO_HELMET",
            "plate_number": plate_text,
            "timestamp": datetime.now().isoformat()
        }

        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

        self._make_pdf(pdf_path, bike_path, plate_path, plate_text)

        self.counter += 1
        print(f"[REPORT SAVED] {path}")

    def _make_pdf(self, pdf_path, bike_path, plate_path, plate_text):
        c = canvas.Canvas(pdf_path, pagesize=A4)
        w, h = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, h - 50, "Helmet Violation Report")

        c.setFont("Helvetica", 12)
        c.drawString(50, h - 90, f"Violation: NO HELMET")
        c.drawString(50, h - 120, f"Plate Number: {plate_text}")

        c.drawImage(bike_path, 50, h - 400, width=250, preserveAspectRatio=True)
        if os.path.exists(plate_path):
            c.drawImage(plate_path, 320, h - 400, width=200, preserveAspectRatio=True)

        c.showPage()
        c.save()
