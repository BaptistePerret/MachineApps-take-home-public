import React, { useState } from 'react';
import { StatusResponse } from '../types';
import { api } from '../api';
import './CommandButtons.css';

interface Props {
  status: StatusResponse | null;
  onCommandExecuted: () => void;
}

export const CommandButtons: React.FC<Props> = ({ status, onCommandExecuted }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleHomeRobot = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.homeRobot();
      onCommandExecuted();
    } catch (err) {
      setError('Failed to home robot');
    } finally {
      setLoading(false);
    }
  };

  const handleStartSequence = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.startSequence();
      onCommandExecuted();
    } catch (err) {
      setError('Failed to start sequence');
    } finally {
      setLoading(false);
    }
  };

  const isHome = status?.state_machine_state === 'Running_home';
  const isMoving = status?.is_moving;

  return (
    <div className="command-buttons">
      <h2>Controls</h2>

      {error && <div className="error-message">{error}</div>}

      <div className="button-group">
        <button
          onClick={handleHomeRobot}
          disabled={loading || isMoving}
          className="command-btn home-btn"
        >
          {loading ? 'Processing...' : 'Home Robot'}
        </button>

        <button
          onClick={handleStartSequence}
          disabled={loading || !isHome || isMoving}
          title={!isHome ? 'Robot must be in Home state' : ''}
          className="command-btn start-btn"
        >
          {loading ? 'Processing...' : 'Start Sequence'}
        </button>
      </div>

      <div className="button-info">
        <p className="info-text">
          💡 Start Sequence requires the robot to be in <strong>Home</strong> state.
        </p>
        {isHome && (
          <p className="success-text">✓ Robot is ready to start sequence</p>
        )}
        {isMoving && (
          <p className="warning-text">🔴 Robot is currently moving, please wait</p>
        )}
      </div>
    </div>
  );
};
