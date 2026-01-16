import cv2

class VideoReader:
    def __init__(self, video_path, display_width=1280):
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")

        self.display_width = display_width
        self.frame_index = 0

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print("[INFO] Video loaded")
        print(f"[INFO] Resolution: {self.width}x{self.height}")
        print(f"[INFO] FPS: {self.fps:.2f}")

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        self.frame_index += 1
        return frame

    def resize_for_display(self, frame):
        h, w = frame.shape[:2]

        if w <= self.display_width:
            return frame

        scale = self.display_width / w
        new_w = int(w * scale)
        new_h = int(h * scale)

        return cv2.resize(frame, (new_w, new_h))

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
