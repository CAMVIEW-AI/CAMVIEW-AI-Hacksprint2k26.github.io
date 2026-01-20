import cv2
import numpy as np
import math
from config import settings

class RoadAnalytics:
    """
    Analyzes road geometry to provide dynamic calibration for:
    1. Vanishing Point (VP) -> Perspective Transform (Speed)
    2. Lane Dividers -> Wrong Way Detection boundaries
    """
    def __init__(self):
        self.vanishing_point = None
        self.lane_lines = []
        self.center_polyline = [] 
        self.smoothed_polyline = [] # Weighted average for stability
        self.frame_count = 0
        self.src_points = np.array(settings.SPEED_SOURCE_POINTS, dtype=np.float32)

    def analyze(self, frame):
        self.frame_count += 1
        if self.frame_count % 30 != 1: return
             
        height, width, _ = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Curve Detection (Segmentation)
        num_strips = 10
        strip_h = height // num_strips
        points = []
        
        # Bottom 60%
        for i in range(num_strips - 1, 3, -1):
            y_start = i * strip_h
            y_end = (i + 1) * strip_h
            strip = gray[y_start:y_end, :]
            edges = cv2.Canny(strip, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=20, minLineLength=20, maxLineGap=10)
            
            if lines is not None:
                strip_centers = []
                img_center_x = width // 2
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    angle = math.atan2(y2-y1, x2-x1) * 180 / np.pi
                    # Steep lines only
                    if 45 < abs(angle) < 135:
                        avg_x = (x1 + x2) // 2
                        if abs(avg_x - img_center_x) < width * 0.4:
                            strip_centers.append(avg_x)
                
                if strip_centers:
                    points.append((int(np.median(strip_centers)), (y_start + y_end)//2))
        
        new_polyline = []
        if len(points) > 2:
            try:
                ys = [p[1] for p in points]
                xs = [p[0] for p in points]
                fit = np.polyfit(ys, xs, 2)
                
                new_polyline = []
                for y in range(height, int(height*0.35), -20): # Go higher (35%)
                    x = int(fit[0]*y**2 + fit[1]*y + fit[2])
                    
                    # ALIGNMENT FIX: Shift slightly right (+20px) to hit barrier center
                    x += 20 
                    
                    x = max(0, min(width, x))
                    new_polyline.append((x, y))
            except:
                new_polyline = points

        # 2. Temporal Smoothing (EMA)
        if new_polyline:
            if not self.smoothed_polyline or len(self.smoothed_polyline) != len(new_polyline):
                self.smoothed_polyline = new_polyline
            else:
                # Ultra-Smooth: 90% Old, 10% New
                temp = []
                for old, new in zip(self.smoothed_polyline, new_polyline):
                    avg_x = int(old[0] * 0.90 + new[0] * 0.10)
                    temp.append((avg_x, new[1]))
                self.smoothed_polyline = temp
        
        self.center_polyline = self.smoothed_polyline
        
        # 3. Perspective-Correct Speed Zone
        if self.center_polyline:
            zone_points = []
            
            top_y = self.center_polyline[-1][1]
            bottom_y = height
            
            # Widen the zone slightly more
            max_w = width * 0.95 
            min_w = width * 0.20 
            
            left_edge = []
            right_edge = []
            
            for pt in self.center_polyline:
                cx, cy = pt
                progress = (bottom_y - cy) / (bottom_y - top_y + 1e-5)
                current_w = max_w - (max_w - min_w) * progress
                
                lx = int(cx - current_w / 2)
                rx = int(cx + current_w / 2)
                
                left_edge.append((lx, cy))
                right_edge.append((rx, cy))
            
            bl = left_edge[0]
            br = right_edge[0]
            tl = left_edge[-1]
            tr = right_edge[-1]
            
            self.src_points = np.array([bl, br, tr, tl], dtype=np.float32)

    def get_dynamic_source_points(self, width, height):
        return self.src_points
    
    def get_lane_polyline(self):
        return self.center_polyline
