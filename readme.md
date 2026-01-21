<div align="center">

# 🌊 CAMVIEW.AI - System Architecture & Data Flow
### Enterprise-Grade Intelligent Traffic Safety Intelligence System (Gold Standard Edition)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-v1.32-FF4B4B.svg)](https://streamlit.io/)
[![YOLOv11](https://img.shields.io/badge/Ultralytics-YOLOv11-green)](https://docs.ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red)](https://opencv.org/)
[![Status](https://img.shields.io/badge/Status-Gold%20Standard%20Active-gold)](https://github.com/)

**Real-Time Event Reasoning for Safer Roads | One Frame → One Base Detection**

[Features](#-core-features) • [Architecture](#1-high-level-system-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Dashboard](#-real-time-dashboard)

</div>

---

## 1. High-Level System Architecture

The Gold Standard architecture operates on a **Single-Scan Producer-Consumer** model coupled with a **Centralized Registry**.

```mermaid
graph TD
    subgraph "Input Layer"
        VS[Video Source] -->|Raw Frames| UP[Unified Processor]
    end

    subgraph "Core Processing Engine (Background Thread)"
        UP -->|Shared Inference| YOLO[YOLOv11 Base Model]
        YOLO -->|Detections| TR[DeepSort Tracker]
        TR -->|Tracks| VR[Vehicle Registry]
        
        VR -->|State| SS[Speed Specialist]
        VR -->|State| WS[WrongWay Specialist]
        VR -->|State| ES[Emergency Specialist]
        VR -->|State| RE[ReID Specialist]
        
        subgraph "Rule Engine"
            VR -->|Validation| RULE{Rule Engine}
        end
    end

    subgraph "Event Distribution"
        RULE -->|Valid Event| EB((Event Bus))
    end

    subgraph "Data Persistence & Action"
        EB -->|Subscribe| EL[Event Logger]
        EL -->|Write| JSON[events.jsonl]
        EL -->|Sync| FB[Firebase Cloud]
        EL -->|Print| T[Terminal/Console]
    end

    subgraph "Presentation Layer (Streamlit)"
        JSON -->|Read Polling| DB[Dashboard UI]
        UP -->|Get Latest Frame| DB
        DB -->|Render| V[Live Preview]
        DB -->|Render| C[Analytics Charts]
    end
```

---

## 2. Component Interaction Breakdown

### A. The Core Engine (`core/`)
The `UnifiedVideoProcessor` is the heart of the system.
*   **Threading**: Runs in a separate `threading.Thread` to prevent blocking the UI.
*   **Responsibility**:
    1.  Captures frame from OpenCV.
    2.  Runs **ONE** YOLO inference per frame (Efficiency).
    3.  Updates the `VehicleRegistry` with new track data.
    4.  Pushes the annotated frame to a `queue.Queue` for the UI.

### B. The Vehicle Registry (`core/vehicle_registry.py`)
The "Brain" that maintains persistent state for every vehicle.
*   **Responsibility**:
    *   Tracks Speed, Lane, Class, and Violation history.
    *   **Rule Engine**: Validates events (e.g., "Is this vehicle exempt?").
    *   **Cooldowns**: Enforces 5-second silence period to prevent spam.

### C. The Specialists (`detectors/`)
Pure logic units that consume data from the Registry.
*   **Emergency Specialist**:
    *   *Input*: Vehicle Crops.
    *   *Logic*: Custom YOLOv11 + Visual Logic (Blue/Red Lights). **95% Confidence Required**.
    *   *Effect*: Marks vehicle as `is_emergency`, bypassing all violations.
*   **Wrong-Way Specialist**:
    *   *Input*: Track Trajectories.
    *   *Logic*: Dynamic vector analysis relative to center divider.
*   **Speed Specialist**:
    *   *Input*: Centroid movement.
    *   *Logic*: 2-Line Virtual Loop calculation.

---

## 3. Detailed Data Sequence (Emergency Override Example)

This sequence diagram illustrates how the system prioritizes emergency vehicles.

```mermaid
sequenceDiagram
    participant Cam as Camera
    participant Engine as UnifiedProcessor
    participant YOLO as YOLOv11
    participant Reg as VehicleRegistry
    participant EmSpec as EmergencySpecialist
    participant Bus as EventBus
    participant UI as Streamlit

    Note over Engine: Background Thread Loop
    Cam->>Engine: Read Frame (N)
    Engine->>YOLO: Detect Objects
    YOLO-->>Engine: 3 Cars Detected
    Engine->>Reg: Update Tracks
    
    Engine->>EmSpec: Verify Vehicle crops
    EmSpec->>EmSpec: Check Visuals + Confidence > 0.95
    EmSpec-->>Reg: Mark ID:101 as AMBULANCE
    
    Note over Reg: Rule Engine Check
    Reg->>Reg: Check ID:101 Speed (120km/h)
    Reg->>Reg: IS_EMERGENCY = True -> IGNORE VIOLATION
    Reg->>Reg: Generate PRIORITY Event
    
    Reg->>Bus: publish(Event: EMERGENCY_VEHICLE)
    Bus->>UI: Update Dashboard (Red Alert)
```

---

## 4. Folder Structure Map

Understanding where the code lives for each part of the flow.

```mermaid
graph LR
    subgraph Root
        APP[app.py]:::ui
    end

    subgraph Core Logic
        UP[core/unified_processor.py]:::core
        REG[core/vehicle_registry.py]:::core
    end

    subgraph Specialists
        ES[detectors/emergency_specialist.py]:::logic
        SS[detectors/speed_specialist.py]:::logic
        WS[detectors/wrong_way_specialist.py]:::logic
    end

    subgraph Data
        LOG[modules/logger.py]:::data
        FILE[(output_results/events.jsonl)]:::file
    end

    APP --> UP
    UP --> REG
    REG --> ES
    REG --> SS
    REG --> WS
    REG --> LOG
    LOG --> FILE
    APP -.-> FILE

    classDef ui fill:#e1f5fe,stroke:#01579b,color:black
    classDef core fill:#fff3e0,stroke:#e65100,color:black
    classDef logic fill:#fce4ec,stroke:#880e4f,color:black
    classDef data fill:#f3e5f5,stroke:#4a148c,color:black
    classDef file fill:#eeeeee,stroke:#212121,color:black,stroke-dasharray: 5 5
```

---

## 5. Technology Stack Flow

| Stage | Tech Stack | Role |
| :--- | :--- | :--- |
| **Ingestion** | **OpenCV (`cv2`)** | High-performance frame grabbing. |
| **Inference** | **YOLOv11 + DeepSort** | Single-shot detection with robust multi-object tracking. |
| **Logic** | **Python 3.10** | `VehicleRegistry` state machine and Rule Engine. |
| **Visualization**| **Streamlit** | React-based reactive UI framework. |
| **Analytics** | **Pandas & Plotly** | Data aggregation and interactive HTML5 charting. |

---

## 6. Installation & Usage

### Installation
```bash
git clone https://github.com/your-username/CAMVIEW.AI.git
cd CAMVIEW-INTEGRATED
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install deep-sort-realtime
```

### ▶️ Run Dashboard
```bash
streamlit run app.py
```

### Notion file
```bash
https://flash-helmet-d0e.notion.site/CAMVIEW-AI-Enterprise-Traffic-Intelligence-Platform-2eb3e53d4a2c800787bdcfcd2d451c0e
```

<div align="center">

**© 2026 CAMVIEW.AI** • *Engineering Safety Intelligence by TEAM Unkown Coders*

</div>
