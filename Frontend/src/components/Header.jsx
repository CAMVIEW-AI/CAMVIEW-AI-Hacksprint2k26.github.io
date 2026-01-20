import React from 'react';
import { motion } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faBars, 
  faVideo, 
  faCog, 
  faClock,
  faEye,
  faSignal,
  faMoon,
  faSun
} from '@fortawesome/free-solid-svg-icons';
import { useTheme } from '../context/ThemeContext';

/**
 * Header Component
 * Professional command-center header with system health indicators and theme toggle
 */
export const Header = ({ 
  systemStatus, 
  isLoading, 
  onMenuToggle,
  className 
}) => {
  const { theme, toggleTheme } = useTheme();
  const isOnline = systemStatus?.status === 'active';

  return (
    <motion.header 
      className={`header ${className || ''}`} 
      initial={{ y: -100 }} 
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      <div className="header-content">
        <motion.button
          className="menu-toggle"
          onClick={onMenuToggle}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          aria-label="Toggle menu"
        >
          <FontAwesomeIcon icon={faBars} />
        </motion.button>

        <div className="logo">
          <FontAwesomeIcon icon={faVideo} />
          <span>CAMVIEW.AI</span>
          <span className="logo-subtitle">Traffic Intelligence</span>
        </div>

        <div className="header-right">
          <div className="health-section">
            {/* System Status */}
            <motion.div 
              className={`health-indicator ${isOnline ? 'online' : 'offline'}`}
              animate={{ opacity: [0.8, 1, 0.8] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <div className="status-dot"></div>
              <span className="status-text">
                {isOnline ? 'ACTIVE' : 'OFFLINE'}
              </span>
            </motion.div>

            {/* Processing Stats */}
            <div className="stat-group">
              <div className="stat">
                <FontAwesomeIcon icon={faEye} className="stat-icon" />
                <span className="stat-label">FPS</span>
                <span className="stat-value">{systemStatus?.fps?.toFixed(1) || '0'}</span>
              </div>
              <div className="stat">
                <FontAwesomeIcon icon={faClock} className="stat-icon" />
                <span className="stat-label">Uptime</span>
                <span className="stat-value">{systemStatus?.uptime?.toFixed(1) || '0'}h</span>
              </div>
            </div>

            {/* Processing Quality */}
            <div className="quality-indicator">
              <FontAwesomeIcon icon={faSignal} className="signal-icon" />
              <span className="quality-text">Signal OK</span>
            </div>
          </div>

          <div className="action-buttons">
            <motion.button 
              className="theme-toggle-btn" 
              onClick={toggleTheme}
              whileHover={{ scale: 1.08 }} 
              whileTap={{ scale: 0.95 }}
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
              aria-label="Toggle theme"
            >
              <motion.div
                key={theme} // Key triggers re-render animation
                initial={{ rotate: -180, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                transition={{ 
                  duration: 0.3, 
                  ease: "easeInOut"
                }}
              >
                <FontAwesomeIcon icon={theme === 'dark' ? faSun : faMoon} />
              </motion.div>
            </motion.button>
          </div>
        </div>
      </div>
    </motion.header>
  );
};
