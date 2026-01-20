import React from 'react';
import { motion } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faVideo, 
  faChartLine, 
  faBell, 
  faTimes,
  faInfoCircle,
  faHome,
  faCog
} from '@fortawesome/free-solid-svg-icons';

/**
 * Enterprise Sidebar Component
 * Professional, minimal, and scalable navigation
 */
export const Sidebar = ({ 
  activeView, 
  onViewChange, 
  isOpen, 
  onClose 
}) => {
  const menuItems = [
    { 
      id: 'about', 
      icon: faInfoCircle, 
      label: 'About',
      description: 'System Overview'
    },
    { 
      id: 'live', 
      icon: faVideo, 
      label: 'Monitoring',
      description: 'Live Video Stream'
    },
    { 
      id: 'events', 
      icon: faBell, 
      label: 'Events',
      description: 'Event Intelligence'
    },
    { 
      id: 'analytics', 
      icon: faChartLine, 
      label: 'Analytics',
      description: 'Traffic Insights'
    },
  ];

  return (
    <motion.div 
      className={`enterprise-sidebar ${isOpen ? 'open' : ''}`}
      initial={false}
      animate={{ x: isOpen ? 0 : '-100%' }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside sidebar
    >
      {/* Header */}
      <div className="enterprise-sidebar__header">
        <div className="enterprise-sidebar__brand">
          <div className="enterprise-sidebar__logo">
            <span className="enterprise-sidebar__logo-text">CAMVIEW</span>
            <span className="enterprise-sidebar__logo-subtitle">AI</span>
          </div>
        </div>
        <motion.button 
          className="enterprise-sidebar__close"
          onClick={onClose} 
          whileTap={{ scale: 0.95 }}
          whileHover={{ scale: 1.05 }}
          aria-label="Close menu"
        >
          <FontAwesomeIcon icon={faTimes} />
        </motion.button>
      </div>

      {/* Navigation */}
      <nav className="enterprise-sidebar__nav">
        <div className="enterprise-sidebar__nav-section">
          <div className="enterprise-sidebar__nav-title">Navigation</div>
          {menuItems.map((item, index) => (
            <motion.button
              key={item.id}
              className={`enterprise-sidebar__nav-item ${activeView === item.id ? 'active' : ''}`}
              onClick={() => {
                onViewChange(item.id);
                onClose();
              }}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="enterprise-sidebar__nav-icon">
                <FontAwesomeIcon icon={item.icon} />
              </div>
              <div className="enterprise-sidebar__nav-content">
                <div className="enterprise-sidebar__nav-label">{item.label}</div>
                <div className="enterprise-sidebar__nav-description">{item.description}</div>
              </div>
            </motion.button>
          ))}
        </div>

        {/* Footer */}
        <div className="enterprise-sidebar__footer">
          <div className="enterprise-sidebar__status">
            <div className="enterprise-sidebar__status-indicator"></div>
            <span>System Online</span>
          </div>
          <div className="enterprise-sidebar__copyright">
            © 2026 CAMVIEW.AI
          </div>
        </div>
      </nav>
    </motion.div>
  );
};
