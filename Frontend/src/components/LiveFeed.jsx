import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faPlay, 
  faPause, 
  faExpand, 
  faSpinner,
  faEye,
  faEyeSlash,
  faTruckMedical,
  faWarning
} from '@fortawesome/free-solid-svg-icons';
import { useApi } from '../hooks/useApi';

/**
 * LiveFeed Component
 * Displays real-time video stream with minimal visual noise and event overlays
 */
export const LiveFeed = () => {
  const [isPlaying, setIsPlaying] = useState(true);
  const [frameData, setFrameData] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [frameError, setFrameError] = useState(false);
  const [showOverlays, setShowOverlays] = useState(false);
  const [lastEvent, setLastEvent] = useState(null);
  const videoRef = useRef(null);
  const { getLiveFrame, getEvents } = useApi();

  /**
   * Convert base64 to data URL for image display
   */
  const getImageUrl = useCallback((base64Data) => {
    if (!base64Data) return null;
    return `data:image/jpeg;base64,${base64Data}`;
  }, []);

  /**
   * Fetch latest frame from backend
   */
  const fetchFrame = useCallback(async () => {
    if (!isPlaying) return;
    
    try {
      setFrameError(false);
      setIsConnecting(true);
      const frame = await getLiveFrame();
      
      // Map API response to component state
      if (frame && frame.base64) {
        setFrameData({
          url: getImageUrl(frame.base64),
          timestamp: frame.timestamp
        });
      } else if (frame && frame.url) {
        setFrameData({
          url: frame.url,
          timestamp: frame.timestamp
        });
      } else {
        setFrameError(true);
      }
    } catch (error) {
      console.error('[LiveFeed] Frame fetch failed:', error);
      setFrameError(true);
    } finally {
      setIsConnecting(false);
    }
  }, [isPlaying, getLiveFrame, getImageUrl]);

  /**
   * Fetch latest critical event for overlay
   */
  const fetchLatestEvent = useCallback(async () => {
    try {
      const events = await getEvents({ limit: 1 });
      if (events && events.length > 0) {
        const event = events[0];
        setLastEvent({
          type: event.type || event.event_type || 'UNKNOWN',
          severity: event.severity || 'INFO',
          timestamp: event.time_fmt || new Date(event.time * 1000).toISOString(),
          vehicleId: event.metadata?.vehicleId || 'N/A'
        });
      }
    } catch (error) {
      console.error('[LiveFeed] Event fetch failed:', error);
    }
  }, [getEvents]);

  /**
   * Auto-refresh frame and events at regular intervals
   */
  useEffect(() => {
    if (isPlaying) {
      fetchFrame();
      fetchLatestEvent();
      const frameInterval = setInterval(fetchFrame, 500); // 2 FPS
      const eventInterval = setInterval(fetchLatestEvent, 2000); // Check for new events every 2s
      return () => {
        clearInterval(frameInterval);
        clearInterval(eventInterval);
      };
    }
  }, [isPlaying, fetchFrame, fetchLatestEvent]);

  /**
   * Toggle play/pause
   */
  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  /**
   * Toggle visual overlays (bounding boxes)
   */
  const toggleOverlays = () => {
    setShowOverlays(!showOverlays);
  };

  /**
   * Toggle fullscreen
   */
  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        videoRef.current.requestFullscreen().catch(err => {
          console.error('[LiveFeed] Fullscreen error:', err);
        });
      }
    }
  };

  /**
   * Get event severity color
   */
  const getSeverityColor = (severity) => {
    const sev = (severity || 'INFO').toUpperCase();
    switch(sev) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f59e0b';
      case 'MEDIUM': return '#10b981';
      default: return '#3b82f6';
    }
  };

  /**
   * Format event type for display
   */
  const formatEventType = (type) => {
    return (type || 'UNKNOWN')
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  const isEmergency = lastEvent?.severity === 'CRITICAL' || lastEvent?.type.toUpperCase().includes('EMERGENCY');

  return (
    <div className="live-feed">
      <motion.div 
        className="video-container"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="video-overlay">
          <motion.div
            ref={videoRef}
            className="live-video-wrapper"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {frameData ? (
              <motion.img 
                src={frameData.url}
                alt="Live Traffic Feed"
                className="live-video"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.1 }}
                onError={() => setFrameError(true)}
              />
            ) : (
              <div className="video-placeholder">
                <div className="placeholder-text">
                  <FontAwesomeIcon icon={faSpinner} spin size="2x" />
                  <p>Initializing video stream...</p>
                </div>
              </div>
            )}
            
            {frameError && (
              <div className="video-error">
                <p>Unable to load video stream</p>
                <small>Check backend connection</small>
              </div>
            )}
            
            {isConnecting && !frameData && (
              <motion.div 
                className="loading-overlay"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <FontAwesomeIcon icon={faSpinner} spin size="2x" />
                <span>Connecting to stream...</span>
              </motion.div>
            )}

            {/* System Status Overlay */}
            <div className="system-overlay">
              <div className="overlay-top-left">
                <div className="overlay-stat">
                  <span className="label">STREAM</span>
                  <span className="value">{isPlaying ? 'LIVE' : 'PAUSED'}</span>
                </div>
              </div>

              <div className="overlay-top-right">
                <div className="overlay-stat">
                  <span className="label">Overlays</span>
                  <span className="value">{showOverlays ? 'ON' : 'OFF'}</span>
                </div>
              </div>

              {/* Event Alert Overlay */}
              {lastEvent && (
                <motion.div
                  className={`event-alert ${isEmergency ? 'emergency' : 'warning'}`}
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <FontAwesomeIcon icon={isEmergency ? faTruckMedical : faWarning} />
                  <div className="event-info">
                    <span className="event-type">{formatEventType(lastEvent.type)}</span>
                    <span className="event-vehicle">Vehicle: {lastEvent.vehicleId}</span>
                  </div>
                </motion.div>
              )}
            </div>

            <div className="video-controls">
              <motion.button
                onClick={togglePlay}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                className="play-btn"
                title={isPlaying ? 'Pause' : 'Play'}
                aria-label={isPlaying ? 'Pause' : 'Play'}
              >
                <FontAwesomeIcon icon={isPlaying ? faPause : faPlay} />
              </motion.button>

              <motion.button
                onClick={toggleOverlays}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                className={`overlays-btn ${showOverlays ? 'active' : ''}`}
                title={showOverlays ? 'Hide Overlays' : 'Show Overlays'}
                aria-label={showOverlays ? 'Hide Overlays' : 'Show Overlays'}
              >
                <FontAwesomeIcon icon={showOverlays ? faEye : faEyeSlash} />
              </motion.button>
              
              <motion.button 
                className="fullscreen-btn" 
                whileHover={{ rotate: 360, scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                onClick={toggleFullscreen}
                title="Fullscreen"
                aria-label="Fullscreen"
              >
                <FontAwesomeIcon icon={faExpand} />
              </motion.button>
            </div>
          </motion.div>
        </div>

        <div className="video-stats">
          <div className="stat-item">
            <span className="label">Status:</span>
            <span className={`value ${isPlaying ? 'active' : 'paused'}`}>
              {isPlaying ? '🔴 LIVE' : '⏸ PAUSED'}
            </span>
          </div>
          {frameData && frameData.timestamp && (
            <div className="stat-item">
              <span className="label">Updated:</span>
              <span className="value">{new Date(frameData.timestamp).toLocaleTimeString()}</span>
            </div>
          )}
          {lastEvent && (
            <div className="stat-item">
              <span className="label">Last Event:</span>
              <span className="value" style={{ color: getSeverityColor(lastEvent.severity) }}>
                {formatEventType(lastEvent.type)}
              </span>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

