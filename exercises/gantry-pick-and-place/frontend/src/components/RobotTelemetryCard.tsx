import React from 'react';
import { StatusResponse } from '../types';
import './RobotTelemetryCard.css';

interface Props {
  status: StatusResponse | null;
}

export const RobotTelemetryCard: React.FC<Props> = ({ status }) => {
  if (!status) {
    return <div className="telemetry-card">Loading...</div>;
  }

  const formatPosition = (x: number, y: number, z: number) => 
    `(${x.toFixed(2)}, ${y.toFixed(2)}, ${z.toFixed(2)})`;

  return (
    <div className="telemetry-card">
      <h2>Robot Telemetry</h2>
      <div className="telemetry-grid">
        <div className="telemetry-item">
          <label>Current Robot Position</label>
          <div className="position-value">
            {formatPosition(
              status.robot_position.x,
              status.robot_position.y,
              status.robot_position.z
            )}
          </div>
        </div>

        <div className="telemetry-item">
          <label>Home Position</label>
          <div className="position-value">
            {formatPosition(
              status.home_position.x,
              status.home_position.y,
              status.home_position.z
            )}
          </div>
        </div>

        <div className="telemetry-item">
          <label>Cube Start Position</label>
          <div className="position-value">
            {formatPosition(
              status.cube_start_position.x,
              status.cube_start_position.y,
              status.cube_start_position.z
            )}
          </div>
        </div>

        <div className="telemetry-item">
          <label>Destination Position</label>
          <div className="position-value">
            {formatPosition(
              status.destination_position.x,
              status.destination_position.y,
              status.destination_position.z
            )}
          </div>
        </div>

        <div className="telemetry-item">
          <label>Gripper State</label>
          <div className={`gripper-state ${status.gripper_state.toLowerCase()}`}>
            {status.gripper_state}
          </div>
        </div>

        <div className="telemetry-item">
          <label>Moving</label>
          <div className={`moving-status ${status.is_moving ? 'active' : 'idle'}`}>
            {status.is_moving ? '🔴 Moving' : '⚪ Idle'}
          </div>
        </div>
      </div>
    </div>
  );
};
