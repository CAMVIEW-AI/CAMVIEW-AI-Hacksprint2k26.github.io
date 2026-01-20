// API Configuration
const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000';
const API_PREFIX = '/api';

/**
 * API endpoint definitions
 * All endpoints use the Flask backend server at /api/*
 */
export const api = {
  // Health & Status
  health: () => `${API_BASE}${API_PREFIX}/health`,
  status: () => `${API_BASE}${API_PREFIX}/status`,
  processingStatus: () => `${API_BASE}${API_PREFIX}/processing/status`,
  
  // Frame/Video
  liveFrame: () => `${API_BASE}${API_PREFIX}/frame/latest`,
  videoUpload: () => `${API_BASE}${API_PREFIX}/video/upload`,
  videoStop: () => `${API_BASE}${API_PREFIX}/video/stop`,
  
  // Events
  events: (params = {}) => {
    const queryParams = new URLSearchParams(params).toString();
    return `${API_BASE}${API_PREFIX}/events${queryParams ? '?' + queryParams : ''}`;
  },
  eventStats: () => `${API_BASE}${API_PREFIX}/events/stats`,
  
  // Analytics & Statistics
  analytics: () => `${API_BASE}${API_PREFIX}/analytics`,
  vehicleStats: () => `${API_BASE}${API_PREFIX}/stats/vehicles`,
  violationStats: () => `${API_BASE}${API_PREFIX}/stats/violations`,
};

export default api;
