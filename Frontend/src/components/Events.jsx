import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faExclamationTriangle, 
  faCarSide,
  faRoad,
  faTruckMedical,
  faFilter,
  faSpinner,
  faCheckCircle,
  faClock,
  faImage
} from '@fortawesome/free-solid-svg-icons';
import { useApi } from '../hooks/useApi';

/**
 * Events Component
 * Displays validated traffic events as intelligent timeline
 */
export const Events = () => {
  const [events, setEvents] = useState([]);
  const [filterType, setFilterType] = useState('ALL');
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [loading, setLoading] = useState(false);
  const { getEvents } = useApi();

  /**
   * Fetch events from backend
   */
  const fetchEvents = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filterType !== 'ALL') params.type = filterType;
      
      const data = await getEvents(params);
      
      // Map API response to component format
      const mappedEvents = (data || []).map((event, idx) => ({
        id: event.id || event.event_id || idx,
        type: event.type || event.event_type || 'UNKNOWN',
        severity: event.severity || 'INFO',
        timestamp: event.time_fmt || new Date((event.time || 0) * 1000).toISOString(),
        metadata: event.metadata || {},
        description: event.description || '',
        snapshot: event.snapshot || null
      }));
      
      setEvents(mappedEvents);
    } catch (error) {
      console.error('[Events] Fetch failed:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Auto-refresh events
   */
  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 3000); // Update every 3 seconds
    return () => clearInterval(interval);
  }, [filterType, filterSeverity]);

  /**
   * Get appropriate icon for event type
   */
  const getEventIcon = (type) => {
    const typeStr = (type || 'UNKNOWN').toUpperCase();
    
    if (typeStr.includes('EMERGENCY')) return faTruckMedical;
    if (typeStr.includes('POTHOLE')) return faRoad;
    if (typeStr.includes('WRONG') || typeStr.includes('SIDE')) return faCarSide;
    return faExclamationTriangle;
  };

  /**
   * Get color for severity level
   */
  const getSeverityColor = (severity) => {
    const sev = (severity || 'INFO').toUpperCase();
    
    switch(sev) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f59e0b';
      case 'MEDIUM': return '#10b981';
      case 'WARNING': return '#f59e0b';
      case 'INFO': return '#3b82f6';
      default: return '#6b7280';
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

  /**
   * Get metadata display text
   */
  const getMetadataText = (event) => {
    const meta = event.metadata || {};
    
    if (meta.vehicleId) return `Vehicle ID: ${meta.vehicleId}`;
    if (meta.vehicleType) return `${meta.vehicleType}`;
    if (meta.speed) return `Speed: ${meta.speed} km/h`;
    
    return event.description || 'Traffic violation detected';
  };

  /**
   * Filtered events based on current filters
   */
  const filteredEvents = useMemo(() => {
    let filtered = events;
    
    if (filterType !== 'ALL') {
      filtered = filtered.filter(e => e.type.toUpperCase() === filterType.toUpperCase());
    }
    
    if (filterSeverity !== 'ALL') {
      filtered = filtered.filter(e => e.severity.toUpperCase() === filterSeverity.toUpperCase());
    }
    
    return filtered;
  }, [events, filterType, filterSeverity]);

  /**
   * Event Card Component
   */
  const EventCard = ({ event, index }) => {
    const timeAgo = new Date(event.timestamp);
    const now = new Date();
    const diffMs = now - timeAgo;
    const diffMins = Math.floor(diffMs / 60000);
    const diffSecs = Math.floor((diffMs % 60000) / 1000);
    const timeStr = diffMins > 0 ? `${diffMins}m ago` : `${diffSecs}s ago`;

    return (
      <motion.div
        className={`event-card ${event.severity.toLowerCase()}`}
        initial={{ opacity: 0, x: -30, y: 0 }}
        animate={{ opacity: 1, x: 0, y: 0 }}
        exit={{ opacity: 0, x: -30 }}
        transition={{ delay: index * 0.05 }}
        whileHover={{ x: 4, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}
      >
        <div className="event-card-icon" style={{ backgroundColor: getSeverityColor(event.severity) + '20' }}>
          <FontAwesomeIcon 
            icon={getEventIcon(event.type)} 
            style={{ color: getSeverityColor(event.severity) }}
            size="lg"
          />
        </div>

        <div className="event-card-content">
          <div className="event-card-header">
            <h3 className="event-title">{formatEventType(event.type)}</h3>
            <span 
              className="severity-badge"
              style={{ 
                backgroundColor: getSeverityColor(event.severity) + '20',
                color: getSeverityColor(event.severity),
                borderLeft: `3px solid ${getSeverityColor(event.severity)}`
              }}
            >
              {event.severity}
            </span>
          </div>

          <p className="event-metadata">{getMetadataText(event)}</p>

          <div className="event-card-footer">
            <div className="event-time">
              <FontAwesomeIcon icon={faClock} size="sm" />
              <span>{timeStr}</span>
            </div>
            
            {event.snapshot && (
              <div className="event-snapshot-indicator">
                <FontAwesomeIcon icon={faImage} size="sm" />
                <span>Snapshot</span>
              </div>
            )}

            <div className="event-validation">
              <FontAwesomeIcon icon={faCheckCircle} size="sm" style={{ color: '#10b981' }} />
              <span>Validated</span>
            </div>
          </div>

          {event.description && (
            <p className="event-description">{event.description}</p>
          )}
        </div>
      </motion.div>
    );
  };

  return (
    <div className="events-container">
      <motion.div 
        className="events-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="header-title">
          <h2>Event Intelligence</h2>
          <p className="subtitle">Validated traffic events timeline</p>
        </div>

        <div className="filter-section">
          <div className="filter-group">
            <label className="filter-label">Event Type</label>
            <div className="filter-buttons">
              <motion.button 
                className={`filter-btn ${filterType === 'ALL' ? 'active' : ''}`}
                onClick={() => setFilterType('ALL')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                All Events
              </motion.button>
              <motion.button 
                className={`filter-btn ${filterType === 'WRONG_SIDE_DRIVING' ? 'active' : ''}`}
                onClick={() => setFilterType('WRONG_SIDE_DRIVING')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <FontAwesomeIcon icon={faCarSide} /> Wrong Side
              </motion.button>
              <motion.button 
                className={`filter-btn ${filterType === 'EMERGENCY_VEHICLE' ? 'active' : ''}`}
                onClick={() => setFilterType('EMERGENCY_VEHICLE')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <FontAwesomeIcon icon={faTruckMedical} /> Emergency
              </motion.button>
              <motion.button 
                className={`filter-btn ${filterType === 'POTHOLE_DETECTED' ? 'active' : ''}`}
                onClick={() => setFilterType('POTHOLE_DETECTED')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <FontAwesomeIcon icon={faRoad} /> Potholes
              </motion.button>
            </div>
          </div>

          <div className="filter-group">
            <label className="filter-label">Severity Level</label>
            <div className="filter-buttons">
              <motion.button 
                className={`filter-btn severity ${filterSeverity === 'ALL' ? 'active' : ''}`}
                onClick={() => setFilterSeverity('ALL')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                All Levels
              </motion.button>
              <motion.button 
                className={`filter-btn severity critical ${filterSeverity === 'CRITICAL' ? 'active' : ''}`}
                onClick={() => setFilterSeverity('CRITICAL')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Critical
              </motion.button>
              <motion.button 
                className={`filter-btn severity high ${filterSeverity === 'HIGH' ? 'active' : ''}`}
                onClick={() => setFilterSeverity('HIGH')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                High
              </motion.button>
              <motion.button 
                className={`filter-btn severity medium ${filterSeverity === 'MEDIUM' ? 'active' : ''}`}
                onClick={() => setFilterSeverity('MEDIUM')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Medium
              </motion.button>
            </div>
          </div>
        </div>
      </motion.div>

      {loading && filteredEvents.length === 0 && (
        <motion.div 
          className="loading-state"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <FontAwesomeIcon icon={faSpinner} spin size="2x" />
          <p>Loading events...</p>
        </motion.div>
      )}

      <div className="events-timeline">
        <AnimatePresence mode="popLayout">
          {filteredEvents.map((event, index) => (
            <EventCard key={event.id} event={event} index={index} />
          ))}
        </AnimatePresence>
      </div>

      {filteredEvents.length === 0 && !loading && (
        <motion.div 
          className="no-events"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <FontAwesomeIcon icon={faFilter} size="4x" />
          <h3>No events detected</h3>
          <p>
            {filterType === 'ALL' 
              ? 'No events yet. The system will show validated traffic violations here.' 
              : `No ${filterType.replace(/_/g, ' ').toLowerCase()} events found with current filters.`}
          </p>
        </motion.div>
      )}
    </div>
  );
};
