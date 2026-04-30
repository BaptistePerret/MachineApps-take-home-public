import React from 'react';
import { StatusResponse } from '../types';
import './StateDisplay.css';

interface Props {
  status: StatusResponse | null;
}

const getStateColor = (state: string): string => {
  const stateColors: Record<string, string> = {
    'Running_home': 'home',
    'Running_moveToCube': 'moving',
    'Running_lowerToPick': 'moving',
    'Running_closeGripper': 'gripper',
    'Running_liftCube': 'moving',
    'Running_moveToDest': 'moving',
    'Running_lowerToPlace': 'moving',
    'Running_openGripper': 'gripper',
    'Running_liftFromPlace': 'moving',
    'Running_complete': 'complete',
  };
  return stateColors[state] || 'unknown';
};

const getStateLabel = (state: string): string => {
  const labels: Record<string, string> = {
    'Running_home': 'Homing',
    'Running_moveToCube': 'Moving to Cube',
    'Running_lowerToPick': 'Lowering to Pick',
    'Running_closeGripper': 'Closing Gripper',
    'Running_liftCube': 'Lifting Cube',
    'Running_moveToDest': 'Moving to Destination',
    'Running_lowerToPlace': 'Lowering to Place',
    'Running_openGripper': 'Opening Gripper',
    'Running_liftFromPlace': 'Lifting from Place',
    'Running_complete': 'Sequence Complete',
  };
  return labels[state];
};

export const StateDisplay: React.FC<Props> = ({ status }) => {
  if (!status) {
    return <div className="state-display">Loading...</div>;
  }

  const stateColor = getStateColor(status.state_machine_state);
  const stateLabel = getStateLabel(status.state_machine_state);
  console.log("Current state:", status.state_machine_state);
  return (
    <div className="state-display">
      <h2>State Machine Status</h2>

      <div className="state-sequence">
        <h3>Pick & Place Sequence</h3>
        <div className="state-steps">
          {['Running_home', 'Running_moveToCube', 'Running_lowerToPick', 'Running_closeGripper', 'Running_liftCube', 
            'Running_moveToDest', 'Running_lowerToPlace', 'Running_openGripper', 'Running_liftFromPlace', 'Running_complete'].map((step, idx) => (
            <div
              key={step}
              className={`state-step ${status.state_machine_state === step ? `active state-${stateColor}` : ''}`}
              title={stateLabel}
            >
              <div className="step-name">{getStateLabel(step)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
