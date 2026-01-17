import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_VIDEO_DIR = os.path.join(DATA_DIR, "raw")
LOG_DIR = os.path.join(DATA_DIR, "logs")
EVENT_LOG_FILE = os.path.join(LOG_DIR, "events.jsonl")

# Detection Config
YOLO_MODEL_PATH = "yolo11n.pt" 
YOLO_CONF_THRESHOLD = 0.3      # Lowered from 0.5 to catch far objects
YOLO_INFERENCE_SIZE = 1280     # Increased from default 640 to catch small/far objects

# Lane boundaries (x‑coordinates). Empty list means auto‑split into two equal lanes.
LANE_BOUNDARIES = []  # e.g. [300, 600] for three‑lane road

WRONG_SIDE_COOLDOWN = 6.0  # Increased cooldown to reduce spam
WRONG_SIDE_MIN_FRAMES = 5  # Require 5 consecutive frames of "wrong way" before multiple alerts
WRONG_SIDE_CONFIDENCE = 0.65 # Higher threshold for violation detection
DIRECTION_SMOOTHING_FRAMES = 5 # Average vector over N frames

POTHOLE_MIN_AREA = 500  # Pixels

# Pothole Settings
POTHOLE_MIN_AREA = 500

# Wrong Way Specialist Settings
WRONG_WAY_ALLOWED_DIRECTION = "UP"  # Default for single lane. For Highway, uses ROAD_CENTER_X logic.
ROAD_CENTER_X = 960 # X-Coordinate to split road (e.g., 1920/2). 
# If DUAL_MODE: Left of Center expects DOWN, Right of Center expects UP (or vice versa)
WRONG_WAY_TRACKER_MAX_DIST = 50     # Max pixels to track object between frames
WRONG_WAY_MIN_CONFIDENCE = 0.5      # Minimum YOLO confidence for vehicles

# SPEED DETECTION (Multi-Segment Virtual Loops)
SPEED_NUM_SEGMENTS = 4  # Number of segments (will create 5 lines)
SPEED_SEGMENT_START_Y = 0.20  # Start position (0.0 to 1.0 of height) - moved higher
SPEED_SEGMENT_END_Y = 0.95    # End position - moved lower
SPEED_METERS_PER_SEGMENT = 5.0  # Real-world meters between each line
MAX_SPEED_LIMIT = 100 # km/h

# Pothole Detection
POTHOLE_MODEL_PATH = "best.pt"

# Speed Estimation Settings (Calibration)
# Source Points: [Bottom-Left, Bottom-Right, Top-Right, Top-Left]
SPEED_SOURCE_POINTS = [(18, 550), (1852, 608), (1335, 370), (534, 343)] 
SPEED_REAL_WIDTH = 30   # Width of the road section in meters
SPEED_REAL_LENGTH = 100 # Length of the road section in meters
SPEED_LIMIT = 80        # Speed limit in km/h for events

# Firebase Configuration
FIREBASE_CREDENTIALS = os.path.join(BASE_DIR, "firebase_service_account.json")
FIREBASE_EVENT_COLLECTION = "traffic_safety_events"

# User Configurable Settings (will be overridden by UI)
USER_EVENT_LOG_FILE = EVENT_LOG_FILE
USER_FIREBASE_CREDENTIALS = FIREBASE_CREDENTIALS

