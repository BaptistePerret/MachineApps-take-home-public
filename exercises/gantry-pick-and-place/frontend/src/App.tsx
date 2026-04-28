import React, { useState, useEffect } from 'react';
import { StatusResponse } from './types';
import { api } from './api';
import {
  RobotTelemetryCard,
  PositionConfigurationForm,
  CommandButtons,
  StateDisplay,
  ErrorBanner,
} from './components';
import './App.css';

function App() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Subscribe to status stream
  useEffect(() => {
    let isMounted = true;

    const subscribeToStatus = async () => {
      try {
        for await (const statusUpdate of api.statusStream()) {
          if (!isMounted) break;
          setStatus(statusUpdate);
          setLoading(false);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          console.error('Failed to connect to status stream:', err);
          setError('Failed to connect to backend');
          setLoading(false);
        }
      }
    };

    subscribeToStatus();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleCommandExecuted = () => {
    // Commands return updated status, but stream will also update
    // This is just for immediate feedback if needed
  };

  if (loading && !status) {
    return (
      <div className="app-loading">
        <h1>Gantry Pick & Place Dashboard</h1>
        <p>Connecting to backend...</p>
        {error && <p className="error-text">Error: {error}</p>}
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Gantry Pick & Place Dashboard</h1>
        <div className="connection-status">
          {status ? (
            <>
              <span className="status-indicator connected"></span>
              <span>Connected (Live Stream)</span>
            </>
          ) : (
            <>
              <span className="status-indicator disconnected"></span>
              <span>Disconnected</span>
            </>
          )}
        </div>
      </header>

      <main className="app-main">
        {status && <ErrorBanner status={status} />}

        <div className="dashboard-grid">
          <section className="dashboard-section full-width">
            <RobotTelemetryCard status={status} />
          </section>

          <section className="dashboard-section">
            <StateDisplay status={status} />
          </section>

          <section className="dashboard-section">
            <CommandButtons
              status={status}
              onCommandExecuted={handleCommandExecuted}
            />
          </section>

          <section className="dashboard-section full-width">
            <PositionConfigurationForm
              status={status}
              onPositionUpdate={handleCommandExecuted}
            />
          </section>
        </div>
      </main>

      <footer className="app-footer">
        <p>Live streaming from backend</p>
      </footer>
    </div>
  );
}

export default App;
