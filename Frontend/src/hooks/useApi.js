import { useState, useCallback } from 'react';
import { api } from '../utils/api';

/**
 * useApi Hook
 * Provides a unified interface for all API calls with error handling and loading states
 */
export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Generic request handler with error management
   */
  const request = useCallback(async (url, options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...options.headers,
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'API request failed';
      setError(errorMessage);
      console.error('[API Error]', errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * System Status - Get current system status
   */
  const getSystemStatus = useCallback(async () => {
    try {
      return await request(api.status());
    } catch (err) {
      // Return mock data on error for resilience
      return {
        status: 'offline',
        fps: 0,
        currentFrame: 0,
        totalFrames: 0,
        eventsDetected: 0,
        uptime: 0,
      };
    }
  }, [request]);

  /**
   * Processing Status - Get detailed processing status
   */
  const getProcessingStatus = useCallback(async () => {
    try {
      return await request(api.processingStatus());
    } catch (err) {
      return {
        isProcessing: false,
        currentFrame: 0,
        totalFrames: 0,
        fps: 0,
        eventsDetected: 0,
        progress: 0,
      };
    }
  }, [request]);

  /**
   * Live Frame - Get latest video frame
   */
  const getLiveFrame = useCallback(async () => {
    try {
      return await request(api.liveFrame());
    } catch (err) {
      return {
        base64: null,
        timestamp: new Date().toISOString(),
        message: 'Unable to fetch frame',
      };
    }
  }, [request]);

  /**
   * Get Events - Fetch events with optional filtering
   */
  const getEvents = useCallback(async (params = {}) => {
    try {
      const response = await request(api.events(params));
      return response.events || [];
    } catch (err) {
      return [];
    }
  }, [request]);

  /**
   * Get Event Statistics
   */
  const getEventStats = useCallback(async () => {
    try {
      const response = await request(api.eventStats());
      return response.stats || {};
    } catch (err) {
      return {
        total: 0,
        critical: 0,
        warning: 0,
        info: 0,
        by_type: {},
        by_severity: {},
      };
    }
  }, [request]);

  /**
   * Get Analytics Data
   */
  const getAnalytics = useCallback(async () => {
    try {
      return await request(api.analytics());
    } catch (err) {
      return {
        totalVehicles: 0,
        violations: 0,
        potholes: 0,
        emergencyVehicles: 0,
        peakHour: 'N/A',
        avgSpeed: 0,
        violationTrend: [],
        vehicleTypes: {},
      };
    }
  }, [request]);

  /**
   * Get Vehicle Statistics
   */
  const getVehicleStats = useCallback(async () => {
    try {
      return await request(api.vehicleStats());
    } catch (err) {
      return {
        total: 0,
        byType: {},
      };
    }
  }, [request]);

  /**
   * Get Violation Statistics
   */
  const getViolationStats = useCallback(async () => {
    try {
      return await request(api.violationStats());
    } catch (err) {
      return {
        total: 0,
        critical: 0,
        warning: 0,
        byType: {},
        bySeverity: {},
      };
    }
  }, [request]);

  /**
   * Upload Video File
   */
  const uploadVideo = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(api.videoUpload(), {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Stop Video Processing
   */
  const stopVideoProcessing = useCallback(async () => {
    try {
      return await request(api.videoStop(), { method: 'POST' });
    } catch (err) {
      return { error: 'Failed to stop processing' };
    }
  }, [request]);

  /**
   * Check API Health
   */
  const checkHealth = useCallback(async () => {
    try {
      return await request(api.health());
    } catch (err) {
      return { status: 'unhealthy', error: true };
    }
  }, [request]);

  return {
    loading,
    error,
    request,
    checkHealth,
    getSystemStatus,
    getProcessingStatus,
    getLiveFrame,
    getEvents,
    getEventStats,
    getAnalytics,
    getVehicleStats,
    getViolationStats,
    uploadVideo,
    stopVideoProcessing,
  };
};

