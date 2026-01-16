import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_report(data, folder):
    # JSON
    with open(os.path.join(folder, "report.json"), "w") as f:
        json.dump(data, f, indent=4)

    # PDF
    pdf_path = os.path.join(folder, "report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, "Traffic Violation Report")

    c.setFont("Helvetica", 12)
    y = 760
    for k, v in data.items():
        if "image" not in k:
            c.drawString(50, y, f"{k}: {v}")
            y -= 20

    c.drawImage(os.path.join(folder, "car.jpg"), 50, 350, width=250, height=150)
    c.drawImage(os.path.join(folder, "plate.jpg"), 320, 350, width=200, height=100)

    c.save()
