"""
CAMVIEW.AI - Enterprise Traffic Safety Monitoring Dashboard  
Professional Streamlit application with advanced analytics and visualizations
"""

import streamlit as st
import pandas as pd
import json
import os
import time
import cv2
import tempfile
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import base64
from PIL import Image
import numpy as np
import io

# Import project modules
from core.unified_processor import get_processor, ProcessingStatus
from modules.logger import EventLogger
from config import settings

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="CAMVIEW.AI - Traffic Safety Monitoring",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ENTERPRISE STYLING ====================
def apply_professional_theme():
    """Apply clean, professional enterprise CSS styling"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Main theme variables - Corporate Palette */
        :root {
            --primary: #2563eb;       /* Royal Blue */
            --primary-dark: #1e3a8a;  /* Dark Blue */
            --secondary: #64748b;     /* Slate Gray */
            --bg-color: #f8fafc;      /* Light Gray/Blue tint */
            --surface: #ffffff;       /* Pure White */
            --text-main: #0f172a;     /* Very Dark Blue/Black */
            --text-sec: #475569;      /* Dark Gray */
            --border: #e2e8f0;        /* Light Border */
        }
        
        /* Font */
        * {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            color: var(--text-main);
        }
        
        /* Clean Background */
        .stApp {
            background-color: var(--bg-color);
            background-image: none;
        }
        
        /* Professional header */
        .main-header {
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border-left: 6px solid var(--primary);
        }
        
        .main-header h1 {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--primary-dark);
            margin: 0;
            padding: 0;
            background: none;
            -webkit-text-fill-color: initial;
            text-shadow: none;
        }
        
        .main-header p {
            color: var(--text-sec);
            font-size: 1.1rem;
            margin-top: 0.5rem;
            font-weight: 400;
        }
        
        /* Metric cards - Clean & Sharp */
        .stMetric {
            background: var(--surface) !important;
            padding: 1.25rem !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
            border: 1px solid var(--border) !important;
        }
        
        .stMetric:hover {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            border-color: var(--primary) !important;
            transform: translateY(-2px);
            transition: all 0.2s ease;
        }
        
        .stMetric label {
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            color: var(--secondary) !important;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: var(--text-main) !important;
        }
        
        /* Professional buttons */
        .stButton > button {
            background-color: var(--primary);
            color: white;
            border: 1px solid var(--primary);
            border-radius: 6px;
            padding: 0.6rem 1.25rem;
            font-weight: 500;
            transition: all 0.15s ease-in-out;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }
        
        .stButton > button:hover {
            background-color: var(--primary-dark);
            border-color: var(--primary-dark);
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            color: white;
        }
        
        /* Secondary buttons (Clear/Stop etc) */
        button[kind="secondary"] {
            background-color: white;
            color: var(--text-sec);
            border-color: var(--border);
        }
        
        /* Tabs - Clean underline style */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent;
            box-shadow: none;
            border-bottom: 2px solid var(--border);
            padding: 0;
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            border: none;
            background: transparent;
            padding: 1rem 0;
            font-weight: 500;
            color: var(--secondary);
            border-bottom: 3px solid transparent;
            border-radius: 0;
            margin-bottom: -2px;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: var(--primary);
            border-bottom: 3px solid var(--primary);
            background: transparent;
            box-shadow: none;
        }
        
        /* Sidebar - Professional Dark Blue */
        [data-testid="stSidebar"] {
            background-color: #0f172a; /* Slate 900 */
            border-right: 1px solid #1e293b;
        }
        
        /* Force ALL sidebar text to be white */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] small,
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMetricValue,
        [data-testid="stSidebar"] .stMetricLabel,
        [data-testid="stSidebar"] div[data-testid="stCaptionContainer"] {
            color: #ffffff !important;
            opacity: 1 !important;
        }
        
        /* Fix logo background (remove black box) */
        [data-testid="stSidebar"] img {
            mix-blend-mode: lighten;
            opacity: 0.9;
        }
        
        [data-testid="stSidebar"] hr {
            background-color: #334155;
        }
         
         /* Status indicators in sidebar */
        [data-testid="stSidebar"] .stMetric {
            background-color: #1e293b !important; /* Slate 800 */
            border: 1px solid #334155 !important;
        }
        
        /* Info/Success/Warning boxes - Clean flat style */
        .stAlert {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-left-width: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        /* File uploader - Clean dashed area */
        .stFileUploader {
            background-color: #f8fafc;
            border: 2px dashed #cbd5e1;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
        }
        
        /* Remove extra animations to reduce "circus" feel */
        @keyframes none {}
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
    </style>
    """, unsafe_allow_html=True)

# ==================== SESSION STATE ====================
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'processor': None,
        'detectors_loaded': False,
        'logger_initialized': False,
        'video_uploaded': False,
        'video_path': None,
        'processing': False,
        'refresh_counter': 0,
        'preview_refresh_rate': 0.2  # 5 FPS preview (changed from 0.5)
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ====================COMPONENT INITIALIZATION ====================
@st.cache_resource
def initialize_logger():
    """Initialize event logger (cached)"""
    try:
        logger = EventLogger()
        return logger
    except Exception as e:
        st.error(f"Failed to initialize logger: {e}")
        return None

def initialize_processor():
    """Initialize unified video processor (Gold Standard Architecture)"""
    if st.session_state.processor is None:
        # New UnifiedVideoProcessor handles all specialists internally
        processor = get_processor()
        st.session_state.processor = processor
        st.session_state.detectors_loaded = True  # Always true with new architecture
        
        if not st.session_state.logger_initialized:
            initialize_logger()
            st.session_state.logger_initialized = True

# ==================== DATA LOADING ====================
def load_events():
    """Load events from JSONL file"""
    if not os.path.exists(settings.EVENT_LOG_FILE):
        return []
    
    events = []
    try:
        with open(settings.EVENT_LOG_FILE, 'r') as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except:
                    continue
    except Exception as e:
        st.warning(f"Could not load events: {e}")
    
    return events

# ==================== MONITORING TAB ====================
def render_monitoring_tab():
    """Main monitoring dashboard"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🚦 CAMVIEW.AI Traffic Safety Monitor</h1>
        <p>Enterprise-grade AI-powered real-time traffic violation detection system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status metrics
    col1, col2, col3, col4 = st.columns(4)
    
    status = st.session_state.processor.get_status() if st.session_state.processor else ProcessingStatus()
    events = load_events()
    
    with col1:
        st.metric(
            "System Status",
            "🟢 Active" if status.is_processing else "⚪ Idle",
            f"Frame {status.current_frame}/{status.total_frames}" if status.total_frames > 0 else "Ready"
        )
    
    with col2:
        critical_count = len([e for e in events if e.get('severity') == 'CRITICAL'])
        st.metric("Critical Events", critical_count, f"{len(events)} total")
    
    with col3:
        st.metric("Processing FPS", f"{status.fps:.1f}", f"{status.processing_time:.1f}s elapsed")
    
    with col4:
        detection_rate = (status.events_detected / max(status.current_frame, 1)) * 100 if status.current_frame > 0 else 0
        st.metric("Detection Rate", f"{detection_rate:.1f}%", f"{status.events_detected} detected")
    
    st.divider()
    
    # Main content
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.subheader("📹 Video Processing")
        
        uploaded_file = st.file_uploader(
            "Upload Video File",
            type=['mp4', 'mov', 'avi', 'mkv'],
            help="Upload a traffic video for AI-powered safety analysis"
        )
        
        if uploaded_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(uploaded_file.read())
            st.session_state.video_path = tfile.name
            st.session_state.video_uploaded = True
            
            if st.session_state.processor and not status.is_processing:
                if st.session_state.processor.load_video(tfile.name):
                    st.success(f"✅ Video loaded: {uploaded_file.name}")
                    st.info(f"📊 Total Frames: {status.total_frames} | FPS: {status.fps:.1f}")
        
        # Controls
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("▶️ Start Processing", disabled=not st.session_state.video_uploaded or status.is_processing):
                if st.session_state.processor:
                    st.session_state.processor.start_processing()
                    st.session_state.processing = True
                    st.success("Processing started!")
        
        with col_btn2:
            if st.button("⏹️ Stop", disabled=not status.is_processing):
                if st.session_state.processor:
                    st.session_state.processor.stop_processing()
                    st.session_state.processing = False
                    st.info("Processing stopped")
        
        with col_btn3:
            if st.button("🔄 Reset"):
                st.session_state.video_uploaded = False
                st.session_state.video_path = None
                st.session_state.processing = False
                st.rerun()
        
        # Live Preview
        st.subheader("🎯 Live Detection Preview")
        
        if status.is_processing:
            progress = status.current_frame / max(status.total_frames, 1) if status.total_frames > 0 else 0
            
            col_prog, col_info = st.columns([3, 1])
            with col_prog:
                st.progress(progress, text=f"Frame {status.current_frame}/{status.total_frames}")
            with col_info:
                st.metric("FPS", f"{status.fps:.1f}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Events", status.events_detected)
            with col2:
                elapsed = time.time() - status.processing_time if status.processing_time > 0 else 0
                st.metric("Elapsed", f"{elapsed:.1f}s")
            with col3:
                remaining = (status.total_frames - status.current_frame) / max(status.fps, 1) if status.fps > 0 else 0
                st.metric("Remaining", f"{remaining:.0f}s")
        
        preview_placeholder = st.empty()
        
        if status.is_processing and st.session_state.processor:
            frame = st.session_state.processor.get_frame()
            
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                with preview_placeholder.container():
                    st.image(frame_rgb, channels="RGB", width='stretch', caption=f"Live Detection - Frame {status.current_frame}")
            else:
                preview_placeholder.info("⏳ Initializing detection...")
        elif st.session_state.video_uploaded and not status.is_processing:
            preview_placeholder.success("✅ Video loaded. Click 'Start Processing'")
        else:
            preview_placeholder.info("📤 Upload a video file to enable detection")
    
    with col_right:
        st.subheader("📋 Live Event Feed")
        
        if events:
            df = pd.DataFrame(events)
            recent_df = df[['time_fmt', 'type', 'severity']].tail(10).copy()
            recent_df.columns = ['Time', 'Event Type', 'Severity']
            
            st.dataframe(recent_df, width='stretch', height=400)
            
            st.metric("Total Events", len(df))
            severity_counts = df['severity'].value_counts()
            for sev, count in severity_counts.items():
                st.metric(f"{sev}", count)
        else:
            st.info("No events yet. Process a video to see detections.")

# ==================== ANALYTICS TAB ====================
def render_analytics_tab():
    """Advanced analytics with comprehensive visualizations"""
    
    st.markdown("""
    <div class="main-header">
        <h1>📊 Advanced Analytics Dashboard</h1>
        <p>Comprehensive insights with interactive visualizations</p>
    </div>
    """, unsafe_allow_html=True)
    
    events = load_events()
    
    if not events:
        st.warning("⚠️ No data available. Process videos first.")
        return
    
    df = pd.DataFrame(events)
    
    # Prepare data
    if 'time' in df.columns:
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        df['hour'] = df['datetime'].dt.hour
        df['day'] = df['datetime'].dt.day_name()
    
    # KPIs
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total = len(df)
    critical = len(df[df['severity'] == 'CRITICAL'])
    warnings = len(df[df['severity'] == 'WARNING'])
    types = df['type'].nunique() if 'type' in df.columns else 0
    
    with col1:
        st.metric("Total Events", total)
    with col2:
        st.metric("Critical", critical, f"{critical/total*100:.1f}%")
    with col3:
        st.metric("Warnings", warnings, f"{warnings/total*100:.1f}%")
    with col4:
        st.metric("Event Types", types)
    with col5:
        if 'datetime' in df.columns:
            span = (df['datetime'].max() - df['datetime'].min()).total_seconds() / 3600
            st.metric("Time Span", f"{span:.1f}h")
    
    st.divider()
    
    # Charts Row 1
    st.subheader("🎯 Distribution Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Event Types (Donut)**")
        if 'type' in df.columns:
            fig = px.pie(df, names='type', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    with col2:
        st.markdown("**Severity Bars**")
        severity_counts = df['severity'].value_counts()
        colors = {'CRITICAL': '#ef4444', 'WARNING': '#f59e0b', 'INFO': '#3b82f6'}
        fig = px.bar(x=severity_counts.index, y=severity_counts.values, color=severity_counts.index, color_discrete_map=colors)
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    with col3:
        st.markdown("**Treemap View**")
        if 'type' in df.columns:
            type_sev = df.groupby(['type', 'severity']).size().reset_index(name='count')
            fig = px.treemap(type_sev, path=['type', 'severity'], values='count', color='severity', color_discrete_map=colors)
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    st.divider()
    
    # Time Series
    st.subheader("⏰ Temporal Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Events Over Time**")
        if 'datetime' in df.columns:
            hourly = df.groupby(df['datetime'].dt.floor('h')).size().reset_index(name='Events')
            hourly.columns = ['Time', 'Events']
            fig = px.area(hourly, x='Time', y='Events', color_discrete_sequence=['#3b82f6'])
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    with col2:
        st.markdown("**Severity Timeline**")
        if 'datetime' in df.columns:
            sev_time = df.groupby([df['datetime'].dt.floor('h'), 'severity']).size().reset_index(name='Count')
            sev_time.columns = ['Time', 'Severity', 'Count']
            fig = px.line(sev_time, x='Time', y='Count', color='Severity', markers=True, color_discrete_map=colors)
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    st.divider()
    
    # Heatmaps
    st.subheader("🔥 Heatmap Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Hourly Pattern**")
        if 'hour' in df.columns and 'day' in df.columns:
            pivot = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
            fig = px.imshow(pivot, labels=dict(x="Hour", y="Day", color="Events"), color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    with col2:
        st.markdown("**Type by Hour**")
        if 'hour' in df.columns and 'type' in df.columns:
            pivot2 = df.groupby(['type', 'hour']).size().unstack(fill_value=0)
            fig = px.imshow(pivot2, labels=dict(x="Hour", y="Type", color="Count"), color_continuous_scale='Viridis')
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    st.divider()
    
    # Advanced
    st.subheader("📉 Advanced Visualizations")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Risk Gauge**")
        risk_score = (critical * 3 + warnings * 1.5) / max(total, 1) * 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': "Risk Score"},
            gauge={'axis': {'range': [0, 100]},
                  'bar': {'color': "darkred" if risk_score > 70 else "orange" if risk_score > 40 else "green"},
                  'steps': [
                      {'range': [0, 40], 'color': "lightgreen"},
                      {'range': [40, 70], 'color': "yellow"},
                      {'range': [70, 100], 'color': "lightcoral"}
                  ]}
        ))
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    with col2:
        st.markdown("**Histogram**")
        if 'datetime' in df.columns:
            fig = px.histogram(df, x='hour', nbins=24, color_discrete_sequence=['#8b5cf6'])
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    with col3:
        st.markdown("**Cumulative**")
        if 'datetime' in df.columns:
            df_sorted = df.sort_values('datetime')
            df_sorted['cumulative'] = range(1, len(df_sorted) + 1)
            fig = px.line(df_sorted, x='datetime', y='cumulative', color_discrete_sequence=['#10b981'])
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    
    st.divider()
    
    # Export
    st.subheader("📥 Export Data")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        csv = df.to_csv(index=False)
        st.download_button("📄 CSV", csv, f"events_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    
    with col2:
        json_str = df.to_json(orient='records', indent=2)
        st.download_button("📦 JSON", json_str, f"events_{datetime.now().strftime('%Y%m%d')}.json", "application/json")
    
    with col3:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📊 Excel", buffer.getvalue(), f"events_{datetime.now().strftime('%Y%m%d')}.xlsx", 
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    with col4:
        report = f"""CAMVIEW.AI Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Total: {total}
Critical: {critical} ({critical/total*100:.1f}%)
Warnings: {warnings} ({warnings/total*100:.1f}%)
Types: {types}
"""
        st.download_button("📝 Report", report, f"report_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain")

# ==================== SETTINGS TAB ====================
def render_settings_tab():
    """System configuration"""
    
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ System Settings</h1>
        <p>Configure detection parameters</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Detection Settings")
        st.slider("Confidence Threshold", 0.0, 1.0, settings.YOLO_CONF_THRESHOLD, 0.05)
        st.slider("Wrong-Side Confidence", 0.0, 1.0, settings.WRONG_SIDE_CONFIDENCE, 0.05)
        st.slider("Cooldown (s)", 1, 30, int(settings.WRONG_SIDE_COOLDOWN))
        
        st.subheader("🎥 Preview Settings")
        refresh = st.select_slider("Refresh Rate (s)", options=[0.1, 0.2, 0.5, 1.0, 2.0], value=0.2)
        if refresh != st.session_state.preview_refresh_rate:
            st.session_state.preview_refresh_rate = refresh
            st.success(f"✅ Preview: {1/refresh:.1f} FPS")
    
    with col2:
        st.subheader("📊 System Info")
        st.markdown(f"**Detectors**: {'✅ Loaded' if st.session_state.detectors_loaded else '❌ Not Loaded'}")
        st.markdown(f"**Logger**: {'✅ Active' if st.session_state.logger_initialized else '❌ Inactive'}")
        st.markdown(f"**Processor**: {'✅ Ready' if st.session_state.processor else '❌ Not Ready'}")
        
        st.subheader("🗑️ Data Management")
        if st.button("Clear Event History", type="secondary"):
            try:
                with open(settings.EVENT_LOG_FILE, 'w') as f:
                    pass
                st.success("✅ Cleared!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ==================== MAIN APP ====================
def render_setup_tab():
    """Render the Setup & Configuration tab"""
    st.header("🛠️ Setup & Configuration")
    
    tabs = st.tabs(["🔥 Firebase Config", "💾 Data Management", "📚 User Guide"])
    
    # --- Tab 1: Firebase ---
    with tabs[0]:
        st.subheader("☁️ Firebase Integration")
        st.markdown("""
        Upload your `firebase_service_account.json` to enable cloud data syncing.
        This allows events to be stored in Firestore for remote monitoring.
        """)
        
        # Check current status
        current_creds_path = "firebase_service_account.json"
        has_creds = os.path.exists(current_creds_path)
        
        if has_creds:
            st.success("✅ Firebase is currently configured")
            try:
                with open(current_creds_path) as f:
                    data = json.load(f)
                st.code(f"Project ID: {data.get('project_id')}\nClient Email: {data.get('client_email')}")
            except:
                st.error("Error reading current credentials file")
        else:
            st.warning("⚠️ No credential file found. System runs in local-only mode.")
            
        st.divider()
        
        # Upload new credentials
        uploaded_file = st.file_uploader("Upload Service Account JSON", type=['json'], key="firebase_uploader")
        
        if uploaded_file:
            try:
                creds = json.load(uploaded_file)
                if "project_id" in creds and "private_key" in creds:
                    # Save the file
                    with open(current_creds_path, "w") as f:
                        json.dump(creds, f)
                    
                    st.success(f"✅ Credentials saved for project: {creds.get('project_id')}")
                    st.info("Please restart the application for changes to take full effect.")
                    
                    # Attempt simple reload
                    if st.button("🔄 Reload Page"):
                        st.rerun()
                else:
                    st.error("Invalid JSON: Missing 'project_id' or 'private_key'")
            except Exception as e:
                st.error(f"Error processing file: {e}")

    # --- Tab 2: Data Management ---
    with tabs[1]:
        st.subheader("📂 Local Data Management")
        
        log_file = "data/logs/events.jsonl"
        
        # 1. Event Logs
        st.markdown("### 📋 Event Logs")
        if os.path.exists(log_file):
            size_kb = os.path.getsize(log_file) / 1024
            st.info(f"Current Log Size: **{size_kb:.2f} KB**")
            
            col1, col2 = st.columns(2)
            with col1:
                with open(log_file, "r") as f:
                    st.download_button(
                        label="📥 Download events.jsonl",
                        data=f,
                        file_name="events.jsonl",
                        mime="application/x-jsonlines"
                    )
            with col2:
                if st.button("🗑️ Clear Log File", type="primary"):
                    os.remove(log_file)
                    st.success("Log file cleared successfully!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.info("No events logged locally yet.")
            
        st.divider()
        
        # 2. Database Status
        st.markdown("### 🗄️ Database Status")
        st.markdown(f"""
        - **Local Path**: `{os.path.abspath(log_file)}`
        - **Cloud Sync**: {'Enabled' if has_creds else 'Disabled'}
        """)

    # --- Tab 3: Guide ---
    with tabs[2]:
        st.subheader("📚 Quick Start Guide")
        st.markdown("""
        ### 1. ☁️ Setup Cloud (Optional)
        - Go to **Firebase Config** tab
        - Upload your `firebase_service_account.json`
        - This enables real-time cloud database syncing
        
        ### 2. 🎥 Monitoring
        - Go to **Monitoring** tab
        - Upload a video file (MP4, AVI, etc.)
        - Click 'Start Processing'
        - Events are detected automatically
        
        ### 3. 📊 Analytics
        - Go to **Analytics** tab
        - View real-time charts and insights
        - Export data to Excel/CSV
        
        ### 4. ⚙️ Settings
        - Adjust detection sensitivity
        - Toggle debug mode
        - Change video preview speed
        """)

def main():
    """Main application"""
    apply_professional_theme()
    init_session_state()
    initialize_processor()
    
    # Sidebar
    with st.sidebar:
        if os.path.exists("download.jpeg"):
            st.image("download.jpeg", width=100)
        st.title("CAMVIEW.AI")
        st.markdown('<p style="color: white; opacity: 0.8; font-size: 0.8rem; margin-top: -10px;">v2.0 Enterprise</p>', unsafe_allow_html=True)
        st.divider()
        st.metric("Detectors", "✅" if st.session_state.detectors_loaded else "❌")
        st.metric("Logger", "✅" if st.session_state.logger_initialized else "❌")
        st.divider()
        st.markdown('<p style="color: white; opacity: 0.8; font-size: 0.8rem;">© 2026 CAMVIEW.AI</p>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Monitoring", "📊 Analytics", "⚙️ Settings", "🛠️ Setup & Guide"])
    
    with tab1:
        render_monitoring_tab()
    
    with tab2:
        render_analytics_tab()
    
    with tab3:
        render_settings_tab()

    with tab4:
        render_setup_tab()
    
    # Auto-refresh
    if st.session_state.processing and st.session_state.processor:
        status = st.session_state.processor.get_status()
        if status.is_processing:
            refresh_interval = st.session_state.get('preview_refresh_rate', 0.5)
            time.sleep(refresh_interval)
            st.rerun()

if __name__ == "__main__":
    main()
