import React, { useState, useEffect } from 'react';
import { Position, StatusResponse } from '../types';
import { api } from '../api';
import './PositionConfigurationForm.css';

interface Props {
  status: StatusResponse | null;
  onPositionUpdate: () => void;
}

export const PositionConfigurationForm: React.FC<Props> = ({ status, onPositionUpdate }) => {
  const [cubePosition, setCubePosition] = useState<Position>({ x: 0, y: 0, z: 0 });
  const [destPosition, setDestPosition] = useState<Position>({ x: 0, y: 0, z: 0 });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (status) {
      setCubePosition(status.cube_start_position);
      setDestPosition(status.destination_position);
    }
  }, [status]);

  const handleCubePositionChange = (axis: keyof Position, value: string) => {
    setCubePosition(prev => ({
      ...prev,
      [axis]: parseFloat(value) || 0,
    }));
  };

  const handleDestPositionChange = (axis: keyof Position, value: string) => {
    setDestPosition(prev => ({
      ...prev,
      [axis]: parseFloat(value) || 0,
    }));
  };

  const handleSetCubePosition = async () => {
    setLoading(true);
    try {
      await api.setCubePosition(cubePosition);
      setMessage({ type: 'success', text: 'Cube position updated successfully' });
      onPositionUpdate();
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update cube position' });
    } finally {
      setLoading(false);
    }
  };

  const handleSetDestPosition = async () => {
    setLoading(true);
    try {
      await api.setDestinationPosition(destPosition);
      setMessage({ type: 'success', text: 'Destination position updated successfully' });
      onPositionUpdate();
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update destination position' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="config-form">
      <h2>Position Configuration</h2>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="form-section">
        <h3>Cube Start Position</h3>
        <div className="position-inputs">
          <div className="input-group">
            <label>X</label>
            <input
              type="number"
              value={cubePosition.x}
              onChange={e => handleCubePositionChange('x', e.target.value)}
              step="10"
            />
          </div>
          <div className="input-group">
            <label>Y</label>
            <input
              type="number"
              value={cubePosition.y}
              onChange={e => handleCubePositionChange('y', e.target.value)}
              step="10"
            />
          </div>
          <div className="input-group">
            <label>Z</label>
            <input
              type="number"
              value={cubePosition.z}
              onChange={e => handleCubePositionChange('z', e.target.value)}
              step="10"
            />
          </div>
        </div>
        <button 
          onClick={handleSetCubePosition}
          disabled={loading}
          className="set-button"
        >
          Set Cube Position
        </button>
      </div>

      <div className="form-section">
        <h3>Destination Position</h3>
        <div className="position-inputs">
          <div className="input-group">
            <label>X</label>
            <input
              type="number"
              value={destPosition.x}
              onChange={e => handleDestPositionChange('x', e.target.value)}
              step="10"
            />
          </div>
          <div className="input-group">
            <label>Y</label>
            <input
              type="number"
              value={destPosition.y}
              onChange={e => handleDestPositionChange('y', e.target.value)}
              step="10"
            />
          </div>
          <div className="input-group">
            <label>Z</label>
            <input
              type="number"
              value={destPosition.z}
              onChange={e => handleDestPositionChange('z', e.target.value)}
              step="10"
            />
          </div>
        </div>
        <button 
          onClick={handleSetDestPosition}
          disabled={loading}
          className="set-button"
        >
          Set Destination Position
        </button>
      </div>
    </div>
  );
};
