import cv2
import numpy as np

class StopLineDetector:
    def __init__(self):
        # 🔥 HARD CALIBRATED STOP LINE (from your points)
        self.x1, self.y1 = 291, 735
        self.x2, self.y2 = 1918, 733

        # Precompute slope & intercept
        self.slope = (self.y2 - self.y1) / (self.x2 - self.x1)
        self.intercept = self.y1 - self.slope * self.x1

    def detect(self, frame, signal_color):
        h, w = frame.shape[:2]
        frame_org = frame.copy()

        # -----------------------------
        # DRAW STOP LINE (ALWAYS)
        # -----------------------------
        color = {
            "RED": (0, 0, 255),
            "GREEN": (0, 255, 0),
            "YELLOW": (0, 255, 255),
            "UNKNOWN": (255, 255, 255)
        }[signal_color]

        cv2.line(
            frame,
            (self.x1, self.y1),
            (self.x2, self.y2),
            color,
            4
        )

        # -----------------------------
        # MASK ABOVE STOP LINE
        # -----------------------------
        mask_line = frame_org.copy()

        for x in range(w):
            y = int(self.slope * x + self.intercept)
            if 0 <= y < h:
                mask_line[:y, x] = 0

        stop_line = ((self.x1, self.y1), (self.x2, self.y2))
        return frame, stop_line, mask_line
