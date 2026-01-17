import cv2
from ultralytics import YOLO
import os

# CONFIG
MODEL_PATH = r"C:\Users\ahadd\OneDrive\Desktop\CAMVIEW-INTEGRATED\best.pt"
TEST_FOLDER = r"C:\Users\ahadd\OneDrive\Desktop\CAMVIEW-INTEGRATED\dataset\RDD2022_India-potholes\India\test\images" # User's dataset path
OUTPUT_FOLDER = r"pothole_test_results"

def main():
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        return

    model = YOLO(MODEL_PATH)
    print(f"Loaded model: {MODEL_PATH}")
    print(f"Classes: {model.names}")

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # If test folder doesn't exist, use a single dummy image or ask for input
    image_paths = []
    if os.path.exists(TEST_FOLDER):
        image_paths = [os.path.join(TEST_FOLDER, f) for f in os.listdir(TEST_FOLDER) if f.lower().endswith(('.jpg','.png','.jpeg'))]
    else:
        print(f"Test folder {TEST_FOLDER} not found.")
        single_img = input("Enter path to a single image to test: ").strip('"')
        if os.path.exists(single_img):
            image_paths = [single_img]

    if not image_paths:
        print("No images found to test.")
        return

    print(f"Processing {len(image_paths)} images...")

    for img_path in image_paths:
        frame = cv2.imread(img_path)
        if frame is None: continue
        
        # Inference
        results = model.predict(frame, conf=0.15) # Very low conf to see everything
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = model.names[cls]
                
                # Draw
                color = (0, 0, 255) if label == 'D40' else (0, 255, 0) # Red for Pothole
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Save
        fname = os.path.basename(img_path)
        save_path = os.path.join(OUTPUT_FOLDER, "pred_" + fname)
        cv2.imwrite(save_path, frame)
        print(f"Saved: {save_path}")

    print("Done! Check 'pothole_test_results' folder.")

if __name__ == "__main__":
    main()
