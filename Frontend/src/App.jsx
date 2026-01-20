import React from 'react';
import { Routes, Route } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import ErrorBoundary from './components/ErrorBoundary';
import { ThemeProvider } from './context/ThemeContext';
import './App.css';

/**
 * Main App Component
 * Entry point for the React application with error handling and theme support
 */
function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <div className="app">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/live" element={<DashboardPage />} />
            <Route path="/events" element={<DashboardPage />} />
            <Route path="/analytics" element={<DashboardPage />} />
          </Routes>
        </div>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;

