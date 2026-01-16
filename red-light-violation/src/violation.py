class ViolationDetector:
    def __init__(self, slope, intercept):
        self.slope = slope
        self.intercept = intercept
        self.prev_centers = {}
        self.violated_ids = set()

    def check(self, track_id, cx, cy, signal):
        if track_id not in self.prev_centers:
            self.prev_centers[track_id] = cy
            return False

        prev_y = self.prev_centers[track_id]
        line_y = self.slope * cx + self.intercept

        self.prev_centers[track_id] = cy

        if (
            signal == "RED"
            and prev_y < line_y
            and cy > line_y
            and track_id not in self.violated_ids
        ):
            self.violated_ids.add(track_id)
            return True

        return False
