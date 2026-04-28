import React from 'react';
import { StatusResponse } from '../types';
import './ErrorBanner.css';

interface Props {
  status: StatusResponse | null;
}

export const ErrorBanner: React.FC<Props> = ({ status }) => {
  if (!status?.error) {
    return null;
  }

  return (
    <div className="error-banner">
      <div className="error-icon">⚠️</div>
      <div className="error-content">
        <div className="error-title">Error Detected</div>
        <div className="error-message">{status.error}</div>
      </div>
      <div className="error-close">×</div>
    </div>
  );
};
