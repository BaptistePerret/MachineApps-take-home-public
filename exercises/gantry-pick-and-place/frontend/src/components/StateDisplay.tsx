import React from 'react';
import { StatusResponse } from '../types';
import './StateDisplay.css';

interface Props {
  status: StatusResponse | null;
}

const getStateColor = (state: string): string => {
  const stateColors: Record<string, string> = {
    'ready': 'ready',
    'home': 'home',
    'moveToCube': 'moving',
    'lowerToPick': 'moving',
    'closeGripper': 'gripper',
    'liftCube': 'moving',
    'moveToDest': 'moving',
    'lowerToPlace': 'moving',
    'openGripper': 'gripper',
    'liftFromPlace': 'moving',
    'complete': 'complete',
  };
  return stateColors[state] || 'unknown';
};

const getStateLabel = (state: string): string => {
  const labels: Record<string, string> = {
    'ready': 'Ready',
    'home': 'Homing',
    'moveToCube': 'Moving to Cube',
    'lowerToPick': 'Lowering to Pick',
    'closeGripper': 'Closing Gripper',
    'liftCube': 'Lifting Cube',
    'moveToDest': 'Moving to Destination',
    'lowerToPlace': 'Lowering to Place',
    'openGripper': 'Opening Gripper',
    'liftFromPlace': 'Lifting from Place',
    'complete': 'Sequence Complete',
  };
  return labels[state] || state;
};

export const StateDisplay: React.FC<Props> = ({ status }) => {
  if (!status) {
    return <div className="state-display">Loading...</div>;
  }

  const stateColor = getStateColor(status.state_machine_state);
  const stateLabel = getStateLabel(status.state_machine_state);

  return (
    <div className="state-display">
      <h2>State Machine Status</h2>
      
      <div className={`state-badge state-${stateColor}`}>
        <div className="state-label">{stateLabel}</div>
        <div className="state-code">{status.state_machine_state}</div>
      </div>

      <div className="state-sequence">
        <h3>Pick & Place Sequence</h3>
        <div className="state-steps">
          {['ready', 'home', 'moveToCube', 'lowerToPick', 'closeGripper', 'liftCube', 
            'moveToDest', 'lowerToPlace', 'openGripper', 'liftFromPlace', 'complete'].map((step, idx) => (
            <div
              key={step}
              className={`state-step ${status.state_machine_state === step ? 'active' : ''}`}
              title={getStateLabel(step)}
            >
              <div className="step-number">{idx + 1}</div>
              <div className="step-name">{step}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
