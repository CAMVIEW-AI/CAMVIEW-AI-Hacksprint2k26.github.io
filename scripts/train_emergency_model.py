import os
from ultralytics import YOLO
import yaml

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Dataset Path (Standard YOLO format)
# Ensure you have 'data.yaml' inside this folder
DATASET_DIR = "datasets/emergency-vehicles"
DATA_YAML = os.path.join(DATASET_DIR, "data.yaml")

# Model Selection
# 'yolo11n.pt' is the latest, fastest nano model. 
# You can change to 'yolo11s.pt' for better accuracy (slower).
MODEL_NAME = "yolo11n.pt" 

# Training Parameters
EPOCHS = 50
IMG_SIZE = 640
BATCH_SIZE = 16

def main():
    print(f"🚀 Starting Training for Emergency Vehicles using {MODEL_NAME}...")
    
    # 1. Check for Dataset
    if not os.path.exists(DATA_YAML):
        print(f"\n[ERROR] Dataset not found at: {DATA_YAML}")
        print("Please download an 'Emergency Vehicle' dataset (YOLO format) from Roboflow Universe.")
        print("1. Go to: https://universe.roboflow.com/search?q=emergency+vehicle")
        print("2. Download dataset in 'YOLOv8' format.")
        print(f"3. Extract it to: {os.path.abspath(DATASET_DIR)}")
        print("4. Ensure 'data.yaml' is present inside.")
        return

    # 2. Fix data.yaml paths (common issue with downloaded datasets)
    # Roboflow sometimes puts absolute paths in data.yaml that don't match your PC.
    # We will rewrite it to use relative paths.
    try:
        with open(DATA_YAML, 'r') as f:
            data_config = yaml.safe_load(f)
        
        # Force relative paths
        data_config['train'] = os.path.join(os.path.abspath(DATASET_DIR), "train/images")
        data_config['val'] = os.path.join(os.path.abspath(DATASET_DIR), "valid/images")
        data_config['test'] = os.path.join(os.path.abspath(DATASET_DIR), "test/images")
        
        # Save fixed config
        with open(DATA_YAML, 'w') as f:
            yaml.dump(data_config, f)
        print("✅ validated data.yaml paths.")
        
    except Exception as e:
        print(f"⚠️ Warning checking data.yaml: {e}")

    # 3. Load Model
    model = YOLO(MODEL_NAME)

    # 4. Train
    print("\nStarting Fine-tuning...")
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH_SIZE,
        plots=True,
        project="runs/detect",
        name="emergency_vehicle_custom",
        exist_ok=True # Overwrite existing run
    )

    print("\n✅ Training Complete!")
    print(f"Best model saved at: runs/detect/emergency_vehicle_custom/weights/best.pt")
    print("You can now update 'detectors/emergency_specialist.py' to use this path.")

if __name__ == "__main__":
    main()
