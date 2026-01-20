# 📂 CAMVIEW-INTEGRATED Project Structure (Gold Standard)

This document reflects the updated **Gold Standard Architecture** directory structure.

## 🏗️ Directory Hierarchy

```text
CAMVIEW-INTEGRATED/
├── app.py                      # 🚀 Main Streamlit Dashboard (Entry Point)
├── main.py                     # Legacy Terminal Entry Point
├── requirements.txt            # Python Dependencies
├── MD files/                   # 📚 Project Documentation
│   ├── README.md
│   ├── task.md
│   └── walkthrough.md
│
├── core/                       # 🧠 Core System Logic
│   ├── unified_processor.py    # Main Engine (YOLO + DeepSort)
│   ├── vehicle_registry.py     # MASTER STATE & Rule Engine
│   └── adapters/               # Backward Compatibility Adapters
│
├── detectors/                  # 🧩 Specialists (Pure Logic Units)
│   ├── base_specialist.py      # Abstract Base Class
│   ├── speed_specialist.py     # Speed Logic (Virtual Loops)
│   ├── wrong_way_specialist.py # Lane Logic (Center Divider)
│   ├── emergency_specialist.py # Emergency Logic (Custom YOLOv11)
│   ├── reid_specialist.py      # ReID Logic (Color Embeddings)
│   └── pothole_specialist.py   # Pothole Model Wrapper
│
├── tests/                      # 🧪 Test Suite
│   ├── test_gold_standard.py   # Main Integration Test
│   └── test_integrated_system.py
│
├── output_results/             # 🎥 Generated Video Outputs
│   ├── gold_standard_output.mp4
│   └── emergency_test_output.mp4
│
├── scripts/                    # 🛠️ Utility & Training Scripts
│   ├── train_emergency_model.py
│   └── create_colab_notebook.py
│
├── models/                     # 🤖 AI Models (Optional location)
│   └── ... (usually root)
│
├── modules/                    # 📦 Legacy/Foreign Modules
│   └── logger.py               # Event Logger
│
└── config/                     # ⚙️ Configuration Files
    └── settings.py
```

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `core/vehicle_registry.py` | **The Brain.** Tracks every vehicle, enforces cooldowns, decides if an event is valid. |
| `core/unified_processor.py` | **The Heart.** centralized loop that runs YOLO once, updates Tracker, and tickles the Registry. |
| `app.py` | **The Face.** Visualizes the Registry state in real-time. |
