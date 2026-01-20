import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Header } from '../components/Header';
import { Sidebar } from '../components/EnterpriseSidebar';
import { LiveFeed } from '../components/LiveFeed';
import { Analytics } from '../components/Analytics';
import { Events } from '../components/Events';
import { AboutPage } from './AboutPage';
import { useApi } from '../hooks/useApi';
import '../styles/EnterpriseSidebar.css';

const DashboardPage = () => {
  const [activeView, setActiveView] = useState('about');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { getSystemStatus } = useApi();

  const [systemStatus, setSystemStatus] = useState({
    fps: 0,
    status: 'idle',
    uptime: 0,
    totalFrames: 0,
    detections: 0
  });

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getSystemStatus();
        setSystemStatus(prev => ({
          ...prev,
          ...status,
          fps: status.fps || 0,
          status: status.status || 'idle',
          uptime: status.uptime || 0
        }));
      } catch (error) {
        console.error('Status fetch failed:', error);
        // Mock status for demo
        setSystemStatus({
          fps: 28.4,
          status: 'active',
          uptime: 3.2,
          totalFrames: 45678,
          detections: 1247
        });
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, [getSystemStatus]);

  const renderActiveView = () => {
    switch (activeView) {
      case 'about':
        return <AboutPage />;
      case 'live':
        return <LiveFeed />;
      case 'analytics':
        return <Analytics />;
      case 'events':
        return <Events />;
      default:
        return <AboutPage />;
    }
  };

  return (
    <div className="dashboard-page">
      <motion.div 
        className="page-wrapper"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        {/* Header */}
        <Header 
          systemStatus={systemStatus}
          isLoading={false}
          onMenuToggle={() => setIsSidebarOpen(!isSidebarOpen)}
          className={isSidebarOpen ? 'blurred' : ''}
        />

        {/* Main Content */}
        <div 
          className={`main-content ${isSidebarOpen ? 'sidebar-open blurred' : ''}`}
          onClick={() => isSidebarOpen && setIsSidebarOpen(false)}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={activeView}
              className="content-area"
              initial={{ opacity: 0, x: activeView === 'live' ? 0 : 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: activeView === 'live' ? 0 : -20 }}
              transition={{ duration: 0.4 }}
            >
              {renderActiveView()}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Sidebar Overlay */}
        <AnimatePresence>
          {isSidebarOpen && (
            <motion.div
              className="sidebar-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsSidebarOpen(false)}
            />
          )}
        </AnimatePresence>

        {/* Sidebar */}
        <Sidebar 
          activeView={activeView}
          onViewChange={setActiveView}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />
      </motion.div>
    </div>
  );
};

export default DashboardPage;
