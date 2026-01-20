# Smooth Video Preview in Streamlit - Technical Guide

## The Challenge

You want **smooth 30 FPS video** in Streamlit, similar to a video player. However, Streamlit faces architectural limitations:

| Component | Speed | Limitation |
|-----------|-------|------------|
| **Backend Processing** | 30 FPS | ✅ No limits - processes at full speed |
| **Streamlit UI** | ~0.5-2 FPS | ❌ Page refresh required for updates|
| **True Video Player** | 30+ FPS | ✅ But can't add real-time YOLO overlays |

---

## Our Solution: Optimized Refresh Rate

We've implemented a **balanced approach** that works for deployment:

### Current Implementation

```python
# Backend: Processes at 30 FPS
processor.process_frame()  # Full speed, all detections

# Frontend: Updates at 2 FPS (every 0.5 seconds)
time.sleep(0.5)
st.rerun()  # Show latest frame with YOLO boxes
```

### What You Get

✅ **Smooth-looking video** (~2 FPS preview)  
✅ **All detections** processed at full 30 FPS  
✅ **All events logged** in real-time  
✅ **Progress bar** and stats update  
✅ **Deployment-ready** - works for remote users  
✅ **Minimal flickering** - optimized refresh rate  

---

## Performance Modes

You can adjust the refresh rate in **Settings** tab:

| Mode | Refresh | FPS Preview | Use When |
|------|---------|-------------|----------|
| **Ultra Smooth** | 0.1s | ~10 FPS | Powerful server, few users |
| **Smooth** | 0.2s | ~5 FPS | Good balance |
| **Default** | 0.5s | ~2 FPS | ✅ **Recommended** |
| **Stable** | 1.0s | ~1 FPS | Many concurrent users |
| **Conservative** | 2.0s | ~0.5 FPS | Low-end servers |
| **Minimal** | 5.0s | ~0.2 FPS | Just check progress |

### How to Change

1. Go to **⚙️ Settings** tab
2. Scroll to **🎥 Preview Settings**
3. Adjust **Preview Refresh Rate** slider
4. Preview will update at new rate

---

## Why Not True 30 FPS?

### Streamlit's Architecture

```
User Request → Server Processing → HTML Response → Browser Render
     ↓              ↓                    ↓              ↓
  100ms          50ms                100ms          50ms
                                                      
Total: ~300ms per update = 3 FPS maximum possible
```

### If We Try 30 FPS Auto-Refresh

- ❌ Page flickers uncontrollably  
- ❌ Browser freezes/crashes  
- ❌ Server overload with multiple users  
- ❌ Events lost due to rapid refreshes  
- ❌ Unusable interface  

---

## Comparison with Alternatives

### Option A: Current Solution (Recommended )
```
✅ 2 FPS smooth preview in browser
✅ Works for remote deployment
✅ All events logged
✅ Scalable for multiple users
❌ Not true 30 FPS video
```

### Option B: Hybrid (OpenCV + Streamlit  )
```
✅ True 30 FPS in OpenCV window
✅ Analytics in Streamlit
❌ Separate windows
❌ Won't work for remote deployment
❌ Users need VNC/Remote Desktop to see OpenCV
```

### Option C: WebRTC Streaming (Advanced)
```
✅ True 30 FPS video stream
✅ Works in browser
✅ Deployment-ready
❌ Complex setup (requires streamlit-webrtc)
❌ Encoding/decoding overhead
❌ Network bandwidth intensive
```

### Option D: Pre-process + Playback
```
✅ Smooth 30 FPS playback
✅ Simple video player
❌ Not real-time - process first, view later
❌ No live monitoring
```

---

## Our Final Implementation

### What Happens:

1. **Upload video** → Stored temporarily
2. **Start processing** → Backend runs at 30 FPS
3. **Auto-refresh** → Frontend updates every 0.5s
4. **Show frame** → Latest detection with YOLO boxes
5. **Update metrics** → Progress, FPS, events
6. **Log events** → All 30 FPS detections saved

### User Experience:

- Sees **smooth video-like preview** (2 FPS)
- Gets **all detections** (30 FPS backend)
- Can **adjust smoothness** in settings
- Works **remotely** via web browser
- **No flickering** annoyance
- **Scalable** for production

---

## Technical Details

### Frame Buffer Strategy

```python
# UnifiedVideoProcessor
self.frame_queue = queue.Queue(maxsize=30)

# Producer (30 FPS)
while processing:
    frame = process_with_yolo(frame)
    queue.put(frame)  # Buffer latest frame

# Consumer (2 FPS)
def get_latest_frame():
    return queue.get_nowait()  # Get newest frame
```

### Smart Refresh

```python
# Only refresh when processing
if status.is_processing:
    time.sleep(0.5)  # Configurable
    st.rerun()  # Update UI
else:
    # Idle - no refresh
    pass
```

---

## Deployment Considerations

### Single User
- Use **0.2s** refresh (5 FPS) for best experience

### Multiple Users (< 10)
- Use **0.5s** refresh (default) for balance

### Many Users (10+)
- Use **1.0s** refresh for stability
- Consider caching and optimization

### Production Scale (50+)
- Use **2.0s** refresh minimum
- Implement rate limiting
- Consider WebRTC streaming solution

---

## WebRTC Solution (Future/Advanced)

If you need **true 30 FPS** for deployment, consider implementing WebRTC:

### Installation
```bash
pip install streamlit-webrtc av
```

### Implementation
```python
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

class YOLOProcessor(VideoProcessorBase):
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        # YOLO detection here
        result = yolo_detect(img)
        return av.VideoFrame.from_ndarray(result, format="bgr24")

webrtc_streamer(
    key="yolo",
    video_processor_factory=YOLOProcessor,
    media_stream_constraints={"video": True}
)
```

**Pros:** True 30 FPS, deployment-ready  
**Cons:** Complex, requires STUN/TURN servers, bandwidth intensive

---

## Recommendations

### For Development/Testing:
Use **0.2s refresh** (5 FPS) for smoother development experience

### For Demo/Presentation:
Use **0.5s refresh** (2 FPS) - looks smooth enough, stable

### For Production Deployment:
- Start with **0.5s** refresh
- Monitor server load
- Adjust based on user count and feedback
- Consider WebRTC if budget allows

---

## Bottom Line

**Current solution (2 FPS preview)** is the sweet spot for:
- Deployment to remote users ✅
- Minimal server load ✅
- Smooth-looking experience ✅
- Full 30 FPS detection ✅
- Scalability ✅

It's not true 30 FPS video, but it's the **best practical solution** for a production Streamlit deployment without major architectural changes.

---

## Need True 30 FPS?

If you absolutely need smooth 30 FPS for deployment:

1. **Implement WebRTC** (streamlit-webrtc)
2. **Use external video player** (process video, output MP4, play in HTML5)
3. **Switch to different framework** (Flask + Socket.IO + Canvas streaming)
4. **Use commercial solution** (Cloud-based video analytics platforms)

Each has trade-offs in complexity, cost, and features.
