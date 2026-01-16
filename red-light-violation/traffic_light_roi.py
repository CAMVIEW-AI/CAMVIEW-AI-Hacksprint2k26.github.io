import cv2

VIDEO_PATH = "input/video.mp4"
DISPLAY_WIDTH = 1280

points = []
scale = 1.0

def mouse(event, x, y, flags, param):
    global scale, points
    if event == cv2.EVENT_LBUTTONDOWN:
        ox = int(x / scale)
        oy = int(y / scale)
        points.append((ox, oy))
        print(f"Point added: ({ox}, {oy})")

cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)
delay = int(1000 / fps)

cv2.namedWindow("Stop Line Calibration - LIVE")
cv2.setMouseCallback("Stop Line Calibration - LIVE", mouse)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]

    if w > DISPLAY_WIDTH:
        scale = DISPLAY_WIDTH / w
        display = cv2.resize(frame, (int(w * scale), int(h * scale)))
    else:
        display = frame.copy()
        scale = 1.0

    # Draw already clicked points
    for (px, py) in points:
        dx = int(px * scale)
        dy = int(py * scale)
        cv2.circle(display, (dx, dy), 5, (0, 0, 255), -1)

    cv2.putText(
        display,
        "LEFT CLICK: add point | S: save | Q: quit",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.imshow("Stop Line Calibration - LIVE", display)

    key = cv2.waitKey(delay) & 0xFF

    if key == ord('q'):
        print("\nExited without saving.")
        break

    if key == ord('s'):
        print("\nSAVED POINTS:")
        for p in points:
            print(p)
        break

cap.release()
cv2.destroyAllWindows()
