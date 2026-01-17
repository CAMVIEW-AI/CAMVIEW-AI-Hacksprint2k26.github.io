# CAMVIEW.AI Dashboard - User Guide

## 🎯 Overview

The new enterprise-level dashboard provides a professional interface for real-time traffic safety monitoring with AI-powered YOLO detection.

---

## ✨ Key Features

### 1. **Live YOLO Detection Preview**
- Real-time visualization of object detection as the video processes
- Bounding boxes and labels directly on the video feed
- Frame-by-frame detection updates

### 2. **Three-Tab Interface**

#### 🎯 Monitoring Tab
-  **Video upload and processing controls**
- **Live detection preview** with YOLO bounding boxes
- **Real-time event feed** showing latest detections
- **System status metrics** (FPS, frame count, detection rate)

#### 📊 Analytics Tab
- Event type distribution charts
- Severity breakdown visualization
- Timeline analysis
- Data export (CSV/JSON)

#### ⚙️ Settings Tab
- Detection parameter configuration
- Model settings
- Data management tools
- System component status

### 3. **Professional UI**
- Clean, modern enterprise design
- Gradient headers and metric cards
- Responsive layout
- Color-coded severity indicators

---

## 🚀 How to Use

### Starting the Dashboard

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Run Streamlit
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Processing a Video

1. **Upload Video**
   - Click "Browse files" under "Video Processing"
   - Select your traffic video file (MP4, MOV, AVI, MKV)
   - Wait for upload and loading confirmation

2. **Start Detection**
   - Click "▶️ Start Processing"
   - Watch the live YOLO detection preview
   - Events will appear in the right panel in real-time

3. **Monitor Results**
   - View live detection preview with bounding boxes
   - Check event feed for detected violations
   - Monitor system metrics (FPS, frame count, etc.)

4. **Stop/Reset**
   - Click "⏹️ Stop" to pause processing
   - Click "🔄 Reset" to clear and start over

### Viewing Analytics

1. Navigate to the **📊 Analytics** tab
2. View charts and statistics
3. Filter data by type, severity, or date range
4. Export data using CSV or JSON buttons

### Adjusting Settings

1. Go to the **⚙️ Settings** tab
2. Modify detection parameters:
   - Confidence thresholds
   - Wrong-side detection settings
   - Cooldown periods
3. Manage data:
   - Clear event history
   - Reload detectors
   - Configure storage paths

---

## 📊 Understanding the Interface

### Status Indicators

| Icon | Meaning |
|------|---------|
| 🟢 Active | System is processing video |
| ⚪ Idle | System is ready but not processing |
| 🎯 | Live YOLO detection running |

### Event Severity Colors

| Color | Severity | Description |
|-------|----------|-------------|
| 🔴 Red | CRITICAL | Emergency vehicles, severe violations |
| 🟡 Yellow | WARNING | Wrong-side driving, potential hazards |
| 🔵 Blue | INFO | General detections, non-critical events |

### Metrics Explained

- **System Status**: Current processing state and frame position
- **Critical Events**: Number of high-priority detections
- **Processing FPS**: Frames processed per second
- **Detection Rate**: Percentage of frames with detections

---

## 🎥 Live Detection Preview

The live preview shows:

- **Bounding Boxes**: Colored rectangles around detected objects
- **Labels**: Object type and confidence score
- **Frame Information**: Current frame number
- **Event Count**: Number of events in current frame

Colors indicate detection type:
- Green: Normal traffic/objects
- Orange: Potential violations (being monitored)
- Red: Confirmed violations
- Cyan: Emergency vehicles

---

## 💾 Event Logging

All detected events are automatically saved to:
- **Local File**: `data/logs/events.jsonl`
- **Firebase**: Synced to cloud (if configured)

Each event includes:
- Timestamp
- Event type (WRONG_SIDE, EMERGENCY_VEHICLE, POTHOLE)
- Severity level
- Frame number
- Confidence score
- Additional metadata

---

## 🔧 Performance Tips

### For Faster Processing:
1. Use smaller video resolutions (720p recommended)
2. Process every 2nd or 3rd frame (adjust in settings)
3. Use GPU if available (automatic detection)
4. Close other applications to free resources

### For Better Accuracy:
1. Use high-quality video files
2. Ensure good lighting conditions
3. Adjust confidence thresholds based on your needs
4. Process full video without skipping frames

---

## 📁 File Structure

```
CAMVIEW.AI/
├── app.py                    # Main Streamlit dashboard (NEW)
├── app_old.py               # Backup of previous version
├── main.py                  # CLI processing engine
├── config/
│   └── settings.py          # Configuration
├── core/
│   ├── unified_processor.py # Video processing engine
│   ├── events.py            # Event definitions
│   └── firebase_client.py   # Cloud sync
├── detectors/
│   ├── wrong_side.py        # Wrong-side detection
│   ├── emergency.py         # Emergency vehicle detection
│   └── pothole.py           # Pothole detection
├── modules/
│   └── logger.py            # Event logging
└── data/
    └── logs/
        └── events.jsonl     # Event storage
```

---

## 🐛 Troubleshooting

### Dashboard won't start
```powershell
# Reinstall dependencies
pip install -r requirements.txt

# Clear Streamlit cache
streamlit cache clear
```

### No live preview showing
- Ensure video is uploaded and processing has started
- Check that UnifiedVideoProcessor is running
- Verify detector models are loaded

### Events not appearing
- Check `data/logs/events.jsonl` exists
- Verify logger is initialized (green indicator in sidebar)
- Ensure confidence thresholds aren't too high

### Slow processing
- Reduce video resolution
- Enable frame skip in settings
- Check GPU utilization
- Close unnecessary applications

---

## 🆕 What's New in V2.0

### Improvements Over Previous Version

1. **✅ Cleaner Code Structure**
   - Removed duplicate/unused code
   - Organized into logical sections
   - Better separation of concerns

2. **✅ Live YOLO Preview**
   - Real-time detection visualization
   - Integrated with UnifiedVideoProcessor
   - Smooth frame updates

3. **✅ Professional UI**
   - Enterprise-grade styling
   - Responsive design
   - Better visual hierarchy

4. **✅ Improved Performance**
   - Optimized frame handling
   - Better memory management
   - Reduced unnecessary re-renders

5. **✅ Better Organization**
   - Clear tab structure
   - Intuitive navigation
   - Consistent design language

---

## 📞 Support

For issues or questions:
1. Check the `DEPLOYMENT_GUIDE.md` for deployment help
2. Review `FIREBASE_SETUP.md` for cloud configuration
3. Examine `data/logs/events.jsonl` for raw event data

---

## 📝 License & Credits

**CAMVIEW.AI** - Enterprise Traffic Safety Monitoring System  
© 2026 | Powered by YOLOv11 + Streamlit

Built with:
- YOLOv11 (Object Detection)
- Streamlit (Dashboard)
- OpenCV (Video Processing)
- Plotly (Analytics)
- Firebase (Cloud Sync)
