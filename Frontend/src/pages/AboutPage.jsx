import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faCamera,
  faRobot,
  faChartLine,
  faShield,
  faUsers,
  faBullseye,
  faBriefcase,
  faAward
} from '@fortawesome/free-solid-svg-icons';

import ScrambledText from '../styles/ScrambledText';
import MagicBento from '../styles/MagicBento';
import '../styles/MagicBento.css';
import '../styles/AboutPage.css';
import '../styles/EnterpriseSidebar.css';

/**
 * About Page - Introduction to CAMVIEW.AI
 */
export const AboutPage = () => {
  // Custom data for each section
  const featuresData = [
    {
      color: '#0a4d0a',
      title: 'Real-time Monitoring',
      description: 'Continuous video feed processing with intelligent event detection',
      label: 'Core'
    },
    {
      color: '#0a4d0a',
      title: 'AI-Powered Detection',
      description: 'Advanced YOLO model for accurate vehicle and violation recognition',
      label: 'AI'
    },
    {
      color: '#0a4d0a',
      title: 'Analytics & Insights',
      description: 'Comprehensive traffic intelligence and operational trends',
      label: 'Data'
    },
    {
      color: '#0a4d0a',
      title: 'System Reliability',
      description: 'Stable, validated event processing with cooldown policies',
      label: 'Trust'
    }
  ];

  const capabilitiesData = [
    {
      color: '#0a4d0a',
      title: 'Emergency Detection',
      description: 'Identify emergency vehicles instantly',
      label: 'Safety'
    },
    {
      color: '#0a4d0a',
      title: 'Violation Detection',
      description: 'Detect wrong-way driving and violations',
      label: 'Enforcement'
    },
    {
      color: '#0a4d0a',
      title: 'Road Monitoring',
      description: 'Monitor road conditions and damage',
      label: 'Infrastructure'
    },
    {
      color: '#0a4d0a',
      title: 'Real-time Processing',
      description: 'Process events with minimal latency',
      label: 'Performance'
    }
  ];

  const architectureData = [
    {
      color: '#0a4d0a',
      title: 'Video Input',
      description: 'Real-time video stream processing from traffic cameras',
      label: 'Input'
    },
    {
      color: '#0a4d0a',
      title: 'Processing Engine',
      description: 'YOLO-based detection with specialized violation models',
      label: 'Engine'
    },
    {
      color: '#0a4d0a',
      title: 'Business Logic',
      description: 'Event-driven system with stateful vehicle registry',
      label: 'Logic'
    },
    {
      color: '#0a4d0a',
      title: 'Intelligence Interface',
      description: 'Professional command-center dashboard and analytics',
      label: 'Interface'
    }
  ];

  const philosophyData = [
    {
      color: '#0a4d0a',
      title: 'Event-First Design',
      description: 'Prioritize validated events over raw detections',
      label: 'Focus'
    },
    {
      color: '#0a4d0a',
      title: 'Trust & Reliability',
      description: 'De-duplicate events and respect system policies',
      label: 'Quality'
    },
    {
      color: '#0a4d0a',
      title: 'Professional Interface',
      description: 'Clean design focused on actionable intelligence',
      label: 'Design'
    },
    {
      color: '#0a4d0a',
      title: 'Operator-Centric',
      description: 'Built for traffic operations teams',
      label: 'User'
    }
  ];

  return (
    <div className="about-container">
      {/* Hero Section */}
      <motion.section
        className="about-hero"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="hero-content">
          <h1>CAMVIEW.AI</h1>
          <p className="hero-subtitle">Intelligent Traffic Intelligence Command Center</p>
          <ScrambledText
            className="hero-description"
            radius={100}
            duration={1.2}
            speed={0.5}
            scrambleChars={'.:'}
          >
            Transform raw video streams into actionable traffic intelligence. 
            CAMVIEW.AI combines advanced computer vision with intelligent event processing 
            to provide comprehensive traffic monitoring and analytics.
          </ScrambledText>
        </div>
      </motion.section>

      {/* Core Features */}
      <motion.section
        className="about-section"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2>Core Features</h2>
        {console.log('Features Data:', featuresData)}
        <MagicBento 
          textAutoHide={false}
          enableStars
          enableSpotlight
          enableBorderGlow={true}
          enableTilt={false}
          enableMagnetism={false}
          clickEffect
          spotlightRadius={400}
          particleCount={12}
          glowColor="74, 222, 128"
          disableAnimations={false}
          data={featuresData}
        />
      </motion.section>

      {/* System Capabilities */}
      <motion.section
        className="about-section capabilities-section"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2>System Capabilities</h2>
        <MagicBento 
          textAutoHide={false}
          enableStars
          enableSpotlight
          enableBorderGlow={true}
          enableTilt={false}
          enableMagnetism={false}
          clickEffect
          spotlightRadius={400}
          particleCount={8}
          glowColor="74, 222, 128"
          disableAnimations={false}
          data={capabilitiesData}
        />
      </motion.section>

      {/* Architecture Overview */}
      <motion.section
        className="about-section architecture-section"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2>Architecture Overview</h2>
        <MagicBento 
          textAutoHide={false}
          enableStars
          enableSpotlight
          enableBorderGlow={true}
          enableTilt={false}
          enableMagnetism={false}
          clickEffect
          spotlightRadius={400}
          particleCount={15}
          glowColor="74, 222, 128"
          disableAnimations={false}
          data={architectureData}
        />
      </motion.section>

      {/* Design Philosophy */}
      <motion.section
        className="about-section philosophy-section"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2>Design Philosophy</h2>
        <MagicBento 
          textAutoHide={false}
          enableStars
          enableSpotlight
          enableBorderGlow={true}
          enableTilt={false}
          enableMagnetism={false}
          clickEffect
          spotlightRadius={400}
          particleCount={10}
          glowColor="74, 222, 128"
          disableAnimations={false}
          data={philosophyData}
        />
      </motion.section>

      {/* CTA Section */}
      <motion.section
        className="about-section cta-section"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        <h2>Get Started</h2>
        <p>
          Navigate to <a href="/monitoring/live" className="cta-link" target="_blank" rel="noopener noreferrer">Live Monitoring</a> to begin watching the real-time video feed,
          check <a href="/monitoring/events" className="cta-link" target="_blank" rel="noopener noreferrer">Event Intelligence</a> for validated traffic events, 
          or view <a href="/monitoring/analytics" className="cta-link" target="_blank" rel="noopener noreferrer">Analytics & Insights</a> for operational trends.
        </p>
      </motion.section>
    </div>
  );
};