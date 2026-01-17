import os
import glob
import xml.etree.ElementTree as ET
import shutil
import random
from tqdm import tqdm
import yaml

# --- Configuration ---
# INPUT PATHS (Adjust these if your folder structure is different)
BASE_DIR = r"C:\Users\ahadd\OneDrive\Desktop\CAMVIEW-INTEGRATED"
RAW_IMAGES_DIR = os.path.join(BASE_DIR, "dataset", "RDD2022_India-potholes", "India", "train", "images")
RAW_XML_DIR = os.path.join(BASE_DIR, "dataset", "RDD2022_India-potholes", "India", "train", "annotations", "xmls")

# OUTPUT PATHS
PROCESSED_DIR = os.path.join(BASE_DIR, "dataset", "processed_rdd")
IMAGES_TRAIN_DIR = os.path.join(PROCESSED_DIR, "images", "train")
IMAGES_VAL_DIR = os.path.join(PROCESSED_DIR, "images", "val")
LABELS_TRAIN_DIR = os.path.join(PROCESSED_DIR, "labels", "train")
LABELS_VAL_DIR = os.path.join(PROCESSED_DIR, "labels", "val")

# RDD CLASS MAPPING (Standard Sekilab Classes)
CLASSES = ['D00', 'D01', 'D10', 'D11', 'D20', 'D40', 'D43', 'D44']
CLASS_MAP = {name: i for i, name in enumerate(CLASSES)}

SPLIT_RATIO = 0.8  # 80% Train, 20% Val

def convert_xml_to_yolo(xml_file, output_txt_path):
    """Parses XML and writes YOLO format TXT."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        size = root.find('size')
        w = int(size.find('width').text)
        h = int(size.find('height').text)

        yolo_lines = []
        for obj in root.findall('object'):
            cls_name = obj.find('name').text
            if cls_name not in CLASS_MAP:
                continue # Skip unknown classes if any
            
            cls_id = CLASS_MAP[cls_name]
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), 
                 float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
            
            # YOLO Format: x_center, y_center, width, height (Normalized)
            bb = convert_coordinates((w, h), b)
            yolo_lines.append(f"{cls_id} {bb[0]:.6f} {bb[1]:.6f} {bb[2]:.6f} {bb[3]:.6f}")

        if yolo_lines:
            with open(output_txt_path, 'w') as f:
                f.write('\n'.join(yolo_lines))
            return True
        else:
            return False # No valid objects found
            
    except Exception as e:
        print(f"Error converting {xml_file}: {e}")
        return False

def convert_coordinates(size, box):
    """Converts min/max to center/width/height normalized."""
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def main():
    print(f"🚀 Starting RDD2022 to YOLOv8 Conversion...")
    
    # 1. Create Output Directories
    for d in [IMAGES_TRAIN_DIR, IMAGES_VAL_DIR, LABELS_TRAIN_DIR, LABELS_VAL_DIR]:
        os.makedirs(d, exist_ok=True)
    
    # 2. Get List of XML Files
    xml_files = glob.glob(os.path.join(RAW_XML_DIR, "*.xml"))
    print(f"Found {len(xml_files)} XML annotation files.")
    
    # Pair with images
    dataset = []
    for xml_path in xml_files:
        basename = os.path.splitext(os.path.basename(xml_path))[0]
        jpg_path = os.path.join(RAW_IMAGES_DIR, basename + ".jpg")
        
        if os.path.exists(jpg_path):
            dataset.append((jpg_path, xml_path))
        else:
            # Try other extensions if needed (rare for RDD)
            pass

    print(f"Found {len(dataset)} valid image-label pairs.")
    
    # 3. Shuffle and Split
    random.seed(42) # Reproducibility
    random.shuffle(dataset)
    split_index = int(len(dataset) * SPLIT_RATIO)
    train_set = dataset[:split_index]
    val_set = dataset[split_index:]
    
    print(f"Training Samples: {len(train_set)}")
    print(f"Validation Samples: {len(val_set)}")
    
    # 4. Processing Loop
    def process_subset(subset, img_dest_dir, lbl_dest_dir):
        count = 0
        for img_src, xml_src in tqdm(subset, desc=f"Processing {os.path.basename(img_dest_dir)}"):
            basename = os.path.splitext(os.path.basename(img_src))[0]
            txt_filename = basename + ".txt"
            txt_dest = os.path.join(lbl_dest_dir, txt_filename)
            
            # Convert XML -> TXT
            success = convert_xml_to_yolo(xml_src, txt_dest)
            
            if success:
                # Copy Image
                shutil.copy(img_src, os.path.join(img_dest_dir, os.path.basename(img_src)))
                count += 1
        return count

    train_count = process_subset(train_set, IMAGES_TRAIN_DIR, LABELS_TRAIN_DIR)
    val_count = process_subset(val_set, IMAGES_VAL_DIR, LABELS_VAL_DIR)
    
    # 5. Create data.yaml
    yaml_content = {
        'path': PROCESSED_DIR,
        'train': 'images/train',
        'val': 'images/val',
        'names': {i: name for i, name in enumerate(CLASSES)}
    }
    
    yaml_path = os.path.join(BASE_DIR, "rdd_data.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
        
    print(f"✅ Data Preparation Complete!")
    print(f"Processed {train_count} training and {val_count} validation images.")
    print(f"Dataset location: {PROCESSED_DIR}")
    print(f"Config file created: {yaml_path}")
    print("\nTo train locally, run:")
    print(f"yolo task=detect mode=train model=yolo11n.pt data='{yaml_path}' epochs=50 imgsz=640")

if __name__ == "__main__":
    main()
