# CAMVIEW.AI - Project Analysis & Solution

## 1. Project Overview
**CAMVIEW.AI** is an enterprise-grade intelligent traffic safety monitoring system designed to analyze video feeds in real-time. Unlike simple object detectors that just draw boxes around cars, CAMVIEW uses **event-driven logic** and **temporal tracking** to understand vehicle behavior.

It focuses on three critical safety use cases:
1.  **Wrong-Side Driving Detection** (Preventing accidents).
2.  **Emergency Vehicle Priority** (Clearing traffic).
3.  **Pothole Detection** (Infrastructure maintenance).

The system features a **hybrid architecture** that combines a high-performance backend processing engine (OpenCV + YOLO + Python threading) with a modern frontend dashboard (Streamlit).

---

## 2. System Architecture

The project follows a **Decoupled Event-Driven Architecture**:

1.  **Input Layer (Video Source)**
    -   Captures frames from a webcam (`0`) or video files (`.mp4`).
    -   Managed by `UnifiedVideoProcessor` in a dedicated background thread to ensure non-blocking UI.

2.  **Detection Layer (The Brain)**
    -   **YOLOv8 Wrapper**: Uses Ultralytics YOLO logic for object detection and tracking (`model.track`).
    -   **Specific Detectors**:
        -   `WrongSideDetector`: Analyzes motion vectors over time.
        -   `EmergencyVehicleDetector`: Classifies priority vehicles.
        -   `PotholeDetector`: Identifies road hazards.
    -   *Key Insight*: Detectors operate sequentially on each frame but independently generate events.

3.  **Event Bus (The Nervous System)**
    -   A Publish-Subscribe (`Pub/Sub`) mechanism (`core.event_bus`).
    -   Detectors **Publish** events (e.g., `WRONG_SIDE`, `CRITICAL`).
    -   Consumers **Subscribe** to events without knowing who sent them.

4.  **Action Layer (Consumers)**
    -   **Logger (`modules.logger`)**: Writes events to `data/logs/events.jsonl` (local) and Firebase (cloud).
    -   **Console**: Prints alerts for debugging.
    -   **UI**: Reads the shared state for visualization.

5.  **Presentation Layer (Dashboard)**
    -   **Streamlit App**: Polls the processor for the latest video frame and reads the JSONL log file for analytics.
    -   **Plotly**: Renders real-time graphs and heatmaps.

---

## 3. Deep Dive: Feature Implementation

### A. Wrong-Side Driving Detection
**File**: `detectors/wrong_side.py`

This is the most complex logic in the system. It doesn't just look at a single frame; it tracks movement over time.
*   **Tracking**: Uses YOLO's `track()` mode to assign unique IDs to vehicles.
*   **Vector Calculation**: Maintains a history of `(x, y)` positions for each vehicle (buffer size defined by `DIRECTION_SMOOTHING_FRAMES`).
*   **Lane Logic**:
    *   The screen is divided into two (or more) lanes.
    *   Example: Left lane vehicles *must* move DOWN (`+y`), Right lane vehicles *must* move UP (`-y`).
    *   The system calculates the average vector `(avg_dx, avg_dy)`.
    *   If a vehicle in the Left Lane has a negative `avg_dy` (moving UP), it is flagged.
*   **Confirmation**: To prevent false alarms (jitters), a violation must persist for `WRONG_SIDE_MIN_FRAMES` before a `WARNING` event is triggered.

### B. Emergency Vehicle Priority
**File**: `detectors/emergency.py`

*   **Detection**: Scans for specific classes (e.g., `ambulance`, `fire truck`, `police car`).
*   **filtering**: Uses a high confidence threshold (`> 0.85`) to ensure accuracy.
*   **Heuristic**: Since standard COCO models often just say "car" or "truck", the code includes logic to filter based on specific trained labels if available, or visual confidence.
*   **Cooldown**: Implements a `COOLDOWN_SECONDS` timer (10s) to prevent spamming the system with hundreds of events for the same slowly moving ambulance.

### C. Pothole Detection
**File**: `detectors/pothole.py`

*   **Proxy Logic**: The current code is set up to detect 'pothole', but also accepts 'bowl' (class 45) or 'potted plant' generally found in standard models for demonstration purposes if a custom pothole model isn't loaded.
*   **Severity Grading**:
    *   Calculates the pixel area of the bounding box (`w * h`).
    *   **Low**: Small area.
    *   **Medium**: Area > `POTHOLE_MIN_AREA`.
    *   **High**: Area > `2 * POTHOLE_MIN_AREA`.

---

## 4. File Structure Breakdown

| Path | Purpose |
| :--- | :--- |
| **`app.py`** | **Main Entry Point (UI)**. The Streamlit dashboard. Handles layout, video loading, and charts. |
| **`main.py`** | **Alternative Entry Point (CLI)**. Runs the engine without the web UI for headless operation. |
| **`core/`** | **System Kernel**. |
| `core/unified_processor.py` | Manages the seamless background frame processing loop. |
| `core/event_bus.py` | Handles message passing between components. |
| `core/firebase_client.py` | Syncs data to Google Firebase (if configured). |
| **`detectors/`** | **Business Logic**. |
| `detectors/wrong_side.py` | Logic for direction violation. |
| `detectors/emergency.py` | Logic for priority vehicles. |
| `detectors/pothole.py` | Logic for hazard detection. |
| **`config/`** | **Configuration**. |
| `config/settings.py` | Constants like thresholds, file paths, and lane boundaries. |
| **`modules/`** | **Utilities**. |
| `modules/logger.py` | Handles writing events to JSONL files and the console. |
| **`data/`** | **Storage**. |
| `data/logs/events.jsonl` | The "database" file where all events are stored. |

---

## 5. Critical Workflows

### How Data Flows to the Dashboard
1.  **Capture**: `UnifiedVideoProcessor` reads a frame from `camera`.
2.  **Detect**: `WrongSideDetector` sees a car moving up in the left lane.
    *   *Logic*: `avg_dy < -5` (Moving UP) but Lane 0 expectation is DOWN.
3.  **Publish**: Detector calls `bus.publish(Event(type="WRONG_SIDE"))`.
4.  **Log**: `EventLogger` (listening on bus) catches this info and appends a line to `events.jsonl`.
5.  **Visualize**: `app.py` (which re-runs on a timer) reads `events.jsonl` into a Pandas DataFrame and updates the "Live Event Feed" and Analytics charts.

### How to Run
1.  **Install**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Dashboard**:
    ```bash
    streamlit run app.py
    ```
3.  **Operate**:
    *   Upload a video file via the UI.
    *   Click "Start Processing".
    *   Watch the Live Preview and identifying markers.

---

## 6. Recommendations & Solution

To bring this project to a fully finished "Solution" state:

1.  **Custom Model Weights**:
    *   The `PotholeDetector` currently relies on proxies ('bowl'). For production, train a small YOLOv8n model specifically on a Pothole dataset (e.g., from Kaggle/Roboflow) and update `detectors/pothole.py` to load `pothole_v8.pt` instead of the default.
2.  **Dynamic Lane Configuration**:
    *   Currently, lanes are split by the screen midpoint (`mid_x`). In real-world roads, lanes are rarely perfectly centered.
    *   *Solution*: Add a "Calibration Mode" in the UI where users can draw the lane divider lines on the first frame.
3.  **Performance Optimization**:
    *   The Streamlit app refreshes the whole page to update the image (`st.image`). This ties the UI responsiveness to the refresh rate.
    *   *Solution*: Use WebRTC (via `streamlit-webrtc`) for zero-latency video streaming instead of sending images frame-by-frame.

This analysis covers the project from A to Z, detailing its logic, structure, and execution flow.
