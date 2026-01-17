# 🌊 CAMVIEW.AI - System Architecture & Data Flow

This document outlines the end-to-end data flow of the CAMVIEW.AI system, detailing how video frames are transformed into actionable safety intelligence.

## 1. High-Level System Architecture

The system operates on a **Producer-Consumer** model decoupled by an **Event Bus**.

```mermaid
graph TD
    subgraph "Input Layer"
        VS[Video Source] -->|Raw Frames| UP[Unified Processor]
    end

    subgraph "Core Processing Engine (Background Thread)"
        UP -->|Frame + ID| YW[YOLOv8 Wrapper]
        YW -->|Tracks & Boxes| DL{Detection Logic}
        
        DL -->|Checking Direction| WSD[Wrong-Side Detector]
        DL -->|Classifying Vehicle| EVD[Emergency Vehicle Detector]
        DL -->|Analyzing Surface| PHD[Pothole Detector]
    end

    subgraph "Event Distribution"
        WSD -->|Publish Event| EB((Event Bus))
        EVD -->|Publish Event| EB
        PHD -->|Publish Event| EB
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
    2.  Passes frame to all Detectors sequentially.
    3.  Updates the shared `ProcessingStatus` (FPS, Frame Count).
    4.  Pushes the annotated frame to a `queue.Queue` for the UI to consume.

### B. The Detectors (`detectors/`)
Independent modules that implement specific safety rules.
*   **Wrong-Side Detector**:
    *   *Input*: Track IDs & Bounding Boxes.
    *   *State*: Keeps a history buffer of past positions `[(x1,y1), (x2,y2)...]`.
    *   *Logic*: Calculates vector `(dx, dy)`. If `dy` opposes the lane direction -> **VIOLATION**.
*   **Emergency Detector**:
    *   *Input*: Class IDs.
    *   *Logic*: Checks for high-confidence `ambulance`/`fire truck`. Enforces Cooldown (10s) to avoid spam.
*   **Pothole Detector**:
    *   *Input*: Object Detection.
    *   *Logic*: Measures Bounding Box Area -> Determines Severity (Low/Med/High).

### C. The Event Bus (`core/event_bus.py`)
A lightweight Pub/Sub (Observer Pattern) implementation.
*   **Decoupling**: Detectors don't know about the Logger. Key for scalability.
*   **Events**: Standardized data objects (`event_type`, `severity`, `metadata`, `timestamp`).

---

## 3. Detailed Data Sequence (Wrong-Side Driving Example)

This sequence diagram illustrates exactly what happens when a vehicle drives on the wrong side.

```mermaid
sequenceDiagram
    participant Cam as Camera/Video
    participant Engine as UnifiedProcessor
    participant YOLO as YOLOv8 Model
    participant Det as WrongSideDetector
    participant Bus as EventBus
    participant Log as EventLogger
    participant UI as Streamlit App

    Note over Engine: Background Thread Loop
    Cam->>Engine: Read Frame (N)
    Engine->>YOLO: Track Objects
    YOLO-->>Engine: ID:101, Box:[x,y,w,h]
    
    Engine->>Det: process(frame, ID:101)
    
    Note over Det: 1. Update Position History
    Note over Det: 2. Calculate Vector (dy = -15)
    Note over Det: 3. Check Lane Rule (Left Lane needs +dy)
    Note over Det: 4. DETECT VIOLATION!
    
    Det->>Bus: publish(Event: WRONG_SIDE, ID:101)
    
    par Handling Event
        Bus->>Log: handle_event()
        Log->>Log: Write to events.jsonl
        Log->>Log: Push to Firebase
    and Updating UI
        Engine->>UI: Update Frame Queue
    end
    
    Note over UI: Main Thread (Refresh Loop)
    UI->>UI: Check Frame Queue
    UI->>UI: Render Frame with Red Box
    UI->>Log: Read events.jsonl
    UI->>UI: Update Alert Sidebar & Charts
```

---

## 4. Folder Structure Map

Understanding where the code lives for each part of the flow.

```mermaid
graph LR
    subgraph Root
        APP[app.py]:::ui
        MAIN[main.py]:::cli
    end

    subgraph Core Logic
        UP[core/unified_processor.py]:::core
        BUS[core/event_bus.py]:::core
    end

    subgraph Detectors
        WS[detectors/wrong_side.py]:::logic
        EV[detectors/emergency.py]:::logic
        PH[detectors/pothole.py]:::logic
    end

    subgraph Data
        LOG[modules/logger.py]:::data
        FILE[(data/logs/events.jsonl)]:::file
    end

    APP --> UP
    UP --> WS
    UP --> EV
    UP --> PH
    WS --> BUS
    BUS --> LOG
    LOG --> FILE
    APP -.-> FILE

    classDef ui fill:#e1f5fe,stroke:#01579b,color:black
    classDef cli fill:#e0f2f1,stroke:#004d40,color:black
    classDef core fill:#fff3e0,stroke:#e65100,color:black
    classDef logic fill:#fce4ec,stroke:#880e4f,color:black
    classDef data fill:#f3e5f5,stroke:#4a148c,color:black
    classDef file fill:#eeeeee,stroke:#212121,color:black,stroke-dasharray: 5 5
```

## 5. Technology Stack Flow

| Stage | Tech Stack | Role |
| :--- | :--- | :--- |
| **Ingestion** | **OpenCV (`cv2`)** | High-performance frame grabbing and pre-processing (resizing/color conversion). |
| **Inference** | **Ultralytics YOLOv8** | PyTorch-based Deep Learning for object detection and object tracking (BoT-SORT/ByteTrack). |
| **Logic** | **Python 3.10+** | NumPy for vector math, threading for concurrency. |
| **Visualization**| **Streamlit** | React-based reactive UI framework for Python. |
| **Analytics** | **Pandas & Plotly** | Data aggregation and interactive HTML5 charting. |
