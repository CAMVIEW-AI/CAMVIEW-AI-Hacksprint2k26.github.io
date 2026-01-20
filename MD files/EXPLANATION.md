# Viva Explanation Points

## 1. System Architecture
**Q: Why Event-Driven?**
A: Instead of a monolithic loop, an event-driven approach decouples the *Detection* (Computer Vision) from the *Decision* (Business Logic).
- **Benefit**: We can add new detectors (e.g., Helmet Detection) without changing the logging or dashboard code. We just emit a new `Event` type.

**Q: proper Event Schema?**
A: We standardized the output. Every event has a `type`, `time`, `camera_id`, and flexible `metadata`. This allows uniform logging and analytics.

## 2. Detection Logic

### Wrong-Side Driving
- **Method**: We don't just look at static position. We track the *vector* (movement) of the vehicle over time using a Tracking algorithm (YOLO Track).
- **Rule**: If a vehicle is in the LEFT lane but moving UP (against flow), it's a violation.

### Emergency Vehicle
- **Method**: Object Detection for specific classes (Bus/Truck) combined with visual classifiers (or simulated for demo).
- **Priority**: System tags these events as CRITICAL, which can trigger traffic light preemption.

### Potholes
- **Method**: Object detection to find the pothole.
- **Severity**: Calculated based on the bounding box `area`. Larger area = Higher Severity.

## 3. Technology Choices
- **YOLOv8**: State-of-the-art speed/accuracy trade-off.
- **Streamlit**: Lightweight, data-centric UI perfect for engineering prototypes.
- **JSONL**: Robust logging format for appending data without corruption.
