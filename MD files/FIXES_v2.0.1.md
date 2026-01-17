# Dashboard Fixes - v2.0.1

## Issues Fixed

### 1. ✅ Flickering Problem - RESOLVED
**Problem**: Dashboard was constantly refreshing every 100ms causing severe flickering  
**Root Cause**: Auto-rerun loop at the end of `main()` function  
**Solution**: Removed automatic refresh; added manual "🔄 Refresh Preview" button

**Before:**
```python
if st.session_state.processing:
    time.sleep(0.1)
    st.rerun()  # <- This caused constant page refresh
```

**After:**
```python
# Manual refresh button instead
if st.button("🔄 Refresh Preview", disabled=not status.is_processing):
    st.rerun()
```

### 2. ✅ Deprecation Warnings - RESOLVED
**Problem**: Streamlit warnings about deprecated parameters  
**Fixed**:
- `use_container_width=True` → `width='stretch'` (for charts)
- `use_container_width=True` → `use_column_width=True` (for buttons/images)
- `df.floor('H')` → `df.floor('h')` (pandas hourly freq)

---

## How to Use Now

### Live Preview Updates

The dashboard no longer auto-refreshes to prevent flickering. Instead:

1. **Start Processing** - Click "▶️ Start Processing"
2. **Manual Refresh** - Click "🔄 Refresh Preview" to update the detection view
3. **As Needed** - Refresh as often as you like without auto-flickering

**Benefits:**
- ✅ No more flickering
- ✅ Smooth, stable interface
- ✅ Control when to update
- ✅ Better performance
- ✅ Events still log in real-time (backend continues)

---

## Alternative: Real-Time Preview in Separate Window

If you want **continuous real-time preview** without Streamlit limitations:

### Option 1: Use `realtime_detection.py`
```powershell
python realtime_detection.py --source "path/to/video.mp4"
```

This opens an OpenCV window with:
- True real-time YOLO detection
- No refresh delays
- Smooth 30 FPS preview
- All events still logged to `events.jsonl`

### Option 2: Hybrid Approach (Recommended)
1. Run `realtime_detection.py` for live preview
2. Keep Streamlit open for analytics & monitoring
3. Both share the same event log

---

## Performance Improvements

### Before (v2.0.0):
- Auto-refresh every 100ms
-  Page reloads constantly
- Flickering UI
- High CPU usage

### After (v2.0.1):
- Manual refresh only
- Stable UI
- No flickering
- Lower CPU usage
- Events still logged in real-time

---

## Testing

To verify the fixes:

1. **Upload a video** in the dashboard
2. **Click "Start Processing"**
3. **Observe**: Page should NOT flicker
4. **Click "🔄 Refresh Preview"** to see latest frame
5. **Check logs**: Events still appearing in real-time

---

## Notes

- Backend processing continues uninterrupted
- Events are logged in real-time to `data/logs/events.jsonl` and Firebase
- Detection happens at full speed regardless of UI refresh rate
- You can refresh preview as often as needed without affecting performance

---

## Future Enhancements (Optional)

If you want automatic updates without flickering, consider:

1. **WebSocket streaming** (advanced)
2. **Streamlit fragments** (experimental feature)
3. **Separate preview service** (microservices architecture)

For now, manual refresh is the most stable solution.
