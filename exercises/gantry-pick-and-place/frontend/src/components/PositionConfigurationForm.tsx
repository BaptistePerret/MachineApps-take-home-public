import React, { useState, useEffect } from 'react';
import { Position, StatusResponse } from '../types';
import { api } from '../api';
import './PositionConfigurationForm.css';

interface Props {
  status: StatusResponse | null;
  onPositionUpdate: () => void;
}

export const PositionConfigurationForm: React.FC<Props> = ({ status, onPositionUpdate }) => {
  const [cubePositionText, setCubePositionText] = useState<Record<keyof Position, string>>({ x: '0', y: '0', z: '0' });
  const [destPositionText, setDestPositionText] = useState<Record<keyof Position, string>>({ x: '0', y: '0', z: '0' });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (status) {
      setCubePositionText({
        x: String(status.cube_start_position.x),
        y: String(status.cube_start_position.y),
        z: String(status.cube_start_position.z),
      });
      setDestPositionText({
        x: String(status.destination_position.x),
        y: String(status.destination_position.y),
        z: String(status.destination_position.z),
      });
    }
  }, []);

  const parsePositionValue = (value: string): number => {
    const parsed = parseFloat(value);
    return Number.isNaN(parsed) ? 0 : parsed;
  };

  const handleCubePositionChange = (axis: keyof Position, value: string) => {
    if (Number(value) >= -1000 && Number(value) <= 1000) {
      setCubePositionText(prev => ({
        ...prev,
        [axis]: value,
      }));
    }
  };

  const handleDestPositionChange = (axis: keyof Position, value: string) => {
    if (Number(value) >= -1000 && Number(value) <= 1000) {
      setDestPositionText(prev => ({
        ...prev,
        [axis]: value,
      }));
    }
  };

  const handleSetCubePosition = async () => {
    setLoading(true);
    try {
      await api.setCubePosition({
        x: parsePositionValue(cubePositionText.x),
        y: parsePositionValue(cubePositionText.y),
        z: parsePositionValue(cubePositionText.z),
      });
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
      await api.setDestinationPosition({
        x: parsePositionValue(destPositionText.x),
        y: parsePositionValue(destPositionText.y),
        z: parsePositionValue(destPositionText.z),
      });
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
              value={cubePositionText.x}
              onChange={e => handleCubePositionChange('x', e.target.value)}
              step="10"
            />
          </div>
          <div className="input-group">
            <label>Y</label>
            <input
              type="number"
              value={cubePositionText.y}
              onChange={e => handleCubePositionChange('y', e.target.value)}
              step="10"
            />
          </div>
          <div className="input-group">
            <label>Z</label>
            <input
              type="number"
              value={cubePositionText.z}
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
              value={destPositionText.x}
              onChange={e => handleDestPositionChange('x', e.target.value)}
              step="10"
            />
          </div>
          <div className="input-group">
            <label>Y</label>
            <input
              type="number"
              value={destPositionText.y}
              onChange={e => handleDestPositionChange('y', e.target.value)}
              step="10"
            />
          </div>
          <div className="input-group">
            <label>Z</label>
            <input
              type="number"
              value={destPositionText.z}
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
