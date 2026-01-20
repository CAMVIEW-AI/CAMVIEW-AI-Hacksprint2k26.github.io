import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faCar, 
  faRoad, 
  faExclamationTriangle, 
  faTruckMedical,
  faChartLine,
  faArrowUp,
  faArrowDown,
  faSpinner,
  faClock,
  faGaugeHigh
} from '@fortawesome/free-solid-svg-icons';
import { useApi } from '../hooks/useApi';

/**
 * Analytics Component
 * Displays traffic intelligence summary and operational insights
 */
export const Analytics = () => {
  const [stats, setStats] = useState({
    totalVehicles: 0,
    violations: 0,
    potholes: 0,
    emergencyVehicles: 0,
    peakHour: 'N/A',
    avgSpeed: 0,
    violationTrend: [],
    vehicleTypes: {},
    violationDist: {},
    emergencyFreq: 0
  });
  const [loading, setLoading] = useState(false);
  const { getAnalytics } = useApi();

  /**
   * Fetch analytics data from backend
   */
  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const data = await getAnalytics();
        
        // Map API response to component format
        setStats({
          totalVehicles: data.totalVehicles || 0,
          violations: data.violations || 0,
          potholes: data.potholes || 0,
          emergencyVehicles: data.emergencyVehicles || 0,
          peakHour: data.peakHour || 'N/A',
          avgSpeed: data.avgSpeed || 0,
          violationTrend: data.violationTrend || [],
          vehicleTypes: data.vehicleTypes || {},
          violationDist: data.violationDist || {},
          emergencyFreq: data.emergencyFreq || 0
        });
      } catch (error) {
        console.error('[Analytics] Fetch failed:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, [getAnalytics]);

  /**
   * Intelligence Metric Card Component
   */
  const MetricCard = ({ icon, value, label, insight, color = '#3b82f6', trend = null }) => (
    <motion.div 
      className="metric-card"
      whileHover={{ translateY: -2, boxShadow: '0 8px 16px rgba(0,0,0,0.1)' }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="metric-icon-wrapper" style={{ backgroundColor: color + '15' }}>
        <FontAwesomeIcon icon={icon} style={{ color }} size="lg" />
      </div>
      <div className="metric-content">
        <div className="metric-value">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </div>
        <div className="metric-label">{label}</div>
        {insight && (
          <div className="metric-insight">{insight}</div>
        )}
      </div>
      {trend !== null && (
        <div className={`metric-trend ${trend > 0 ? 'up' : 'down'}`}>
          <FontAwesomeIcon icon={trend > 0 ? faArrowUp : faArrowDown} />
          <span>{Math.abs(trend)}%</span>
        </div>
      )}
    </motion.div>
  );

  /**
   * Simple Bar Chart Component
   */
  const SimpleBarChart = ({ data, title, subtitle }) => {
    if (!data || Object.keys(data).length === 0) {
      return (
        <div className="chart-placeholder">
          <p>No data available</p>
        </div>
      );
    }

    const entries = Object.entries(data).slice(0, 5);
    const maxValue = Math.max(...entries.map(([_, v]) => v));

    return (
      <div className="simple-chart">
        <h4>{title}</h4>
        {subtitle && <p className="chart-subtitle">{subtitle}</p>}
        <div className="bar-chart">
          {entries.map(([label, value], idx) => (
            <div key={idx} className="bar-item">
              <div className="bar-label">{label}</div>
              <div className="bar-container">
                <motion.div
                  className="bar-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${(value / maxValue) * 100}%` }}
                  transition={{ delay: idx * 0.1, duration: 0.6 }}
                />
              </div>
              <div className="bar-value">{value}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  /**
   * Stat Grid Item
   */
  const StatGridItem = ({ icon, label, value, unit = '', color }) => (
    <motion.div 
      className="stat-grid-item"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="stat-grid-icon" style={{ color }}>
        <FontAwesomeIcon icon={icon} size="lg" />
      </div>
      <div className="stat-grid-content">
        <div className="stat-grid-value">{value}</div>
        <div className="stat-grid-label">{label}</div>
        {unit && <div className="stat-grid-unit">{unit}</div>}
      </div>
    </motion.div>
  );

  return (
    <div className="analytics-container">
      {/* Page Title */}
      <motion.div 
        className="analytics-header"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <div className="header-content">
          <h1>Analytics & Insights</h1>
          <p className="header-subtitle">Traffic intelligence summary and operational trends</p>
        </div>
        {loading && <FontAwesomeIcon icon={faSpinner} spin className="header-spinner" />}
      </motion.div>

      {/* Key Metrics Section */}
      <section className="section">
        <h2 className="section-title">Key Performance Indicators</h2>
        
        <div className="metrics-grid">
          <MetricCard 
            icon={faCar}
            value={stats.totalVehicles}
            label="Vehicles Tracked"
            insight="Active in last hour"
            color="#3b82f6"
            trend={12}
          />
          <MetricCard 
            icon={faExclamationTriangle}
            value={stats.violations}
            label="Traffic Violations"
            insight="Detected & validated"
            color="#f59e0b"
            trend={-3}
          />
          <MetricCard 
            icon={faRoad}
            value={stats.potholes}
            label="Road Damages"
            insight="Identified locations"
            color="#8b5cf6"
            trend={2}
          />
          <MetricCard 
            icon={faTruckMedical}
            value={stats.emergencyVehicles}
            label="Emergency Vehicles"
            insight="System priority: HIGH"
            color="#ef4444"
            trend={null}
          />
        </div>
      </section>

      {/* Traffic Intelligence Section */}
      <section className="section">
        <h2 className="section-title">Traffic Intelligence</h2>
        
        <div className="intelligence-grid">
          <motion.div 
            className="intelligence-card"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
          >
            <div className="card-icon">
              <FontAwesomeIcon icon={faClock} size="lg" />
            </div>
            <h3>Peak Activity</h3>
            <div className="card-value">{stats.peakHour}</div>
            <p className="card-description">Highest violation rate</p>
          </motion.div>

          <motion.div 
            className="intelligence-card"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="card-icon">
              <FontAwesomeIcon icon={faGaugeHigh} size="lg" />
            </div>
            <h3>Average Speed</h3>
            <div className="card-value">{stats.avgSpeed.toFixed(1)}</div>
            <p className="card-description">km/h across all lanes</p>
          </motion.div>

          <motion.div 
            className="intelligence-card"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="card-icon">
              <FontAwesomeIcon icon={faTruckMedical} size="lg" />
            </div>
            <h3>Emergency Services</h3>
            <div className="card-value">{stats.emergencyFreq}</div>
            <p className="card-description">Detected in last 24h</p>
          </motion.div>
        </div>
      </section>

      {/* Distribution Analysis */}
      <section className="section">
        <h2 className="section-title">Violation Distribution</h2>
        
        <div className="charts-grid">
          <motion.div 
            className="chart-container"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
          >
            <SimpleBarChart 
              data={stats.violationDist}
              title="By Violation Type"
              subtitle="24-hour analysis"
            />
          </motion.div>

          <motion.div 
            className="chart-container"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <SimpleBarChart 
              data={stats.vehicleTypes}
              title="Vehicle Distribution"
              subtitle="Fleet composition"
            />
          </motion.div>
        </div>
      </section>

      {/* Fleet Summary */}
      <section className="section">
        <h2 className="section-title">Fleet Summary</h2>
        
        <div className="fleet-grid">
          <StatGridItem 
            icon={faCar}
            label="Total Count"
            value={stats.totalVehicles}
            color="#3b82f6"
          />
          <StatGridItem 
            icon={faExclamationTriangle}
            label="Violations"
            value={stats.violations}
            unit="flagged"
            color="#f59e0b"
          />
          <StatGridItem 
            icon={faRoad}
            label="Road Issues"
            value={stats.potholes}
            unit="detected"
            color="#8b5cf6"
          />
          <StatGridItem 
            icon={faTruckMedical}
            label="Priority"
            value={stats.emergencyVehicles}
            unit="active"
            color="#ef4444"
          />
        </div>
      </section>
    </div>
  );
};
