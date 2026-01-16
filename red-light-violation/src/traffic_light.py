import cv2
import numpy as np
from collections import deque

class TrafficLightDetector:
    def __init__(self, roi, history=5):
        """
        roi = (x, y, w, h)  traffic light bounding box
        history = smoothing window
        """
        self.x, self.y, self.w, self.h = roi
        self.state_history = deque(maxlen=history)

    def detect(self, frame):
        roi = frame[self.y:self.y+self.h, self.x:self.x+self.w]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # RED ranges (two ranges in HSV)
        red1 = cv2.inRange(hsv, (0, 120, 70), (10, 255, 255))
        red2 = cv2.inRange(hsv, (170, 120, 70), (180, 255, 255))
        red_mask = red1 | red2

        # GREEN
        green_mask = cv2.inRange(hsv, (36, 50, 70), (89, 255, 255))

        # YELLOW
        yellow_mask = cv2.inRange(hsv, (20, 100, 100), (30, 255, 255))

        red_count = cv2.countNonZero(red_mask)
        green_count = cv2.countNonZero(green_mask)
        yellow_count = cv2.countNonZero(yellow_mask)

        if red_count > green_count and red_count > yellow_count:
            state = "RED"
        elif green_count > red_count and green_count > yellow_count:
            state = "GREEN"
        elif yellow_count > 0:
            state = "YELLOW"
        else:
            state = "UNKNOWN"

        self.state_history.append(state)
        return self._stable_state()

    def _stable_state(self):
        if not self.state_history:
            return "UNKNOWN"
        return max(set(self.state_history), key=self.state_history.count)

    def draw(self, frame, state):
        color = {
            "RED": (0, 0, 255),
            "GREEN": (0, 255, 0),
            "YELLOW": (0, 255, 255),
            "UNKNOWN": (255, 255, 255)
        }[state]

        cv2.rectangle(
            frame,
            (self.x, self.y),
            (self.x + self.w, self.y + self.h),
            color,
            2
        )

        cv2.putText(
            frame,
            f"Signal: {state}",
            (self.x, self.y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2
        )
