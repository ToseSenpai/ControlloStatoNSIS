import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import './ProgressOverlay.css';

const ProgressOverlay: React.FC = () => {
  const { progress } = useSelector((state: RootState) => state.ui);

  // Don't show overlay if not processing OR if progress is still at 0%
  // (wait until actual processing starts before showing the dialog)
  if (!progress.isProcessing || progress.current === 0) return null;

  return (
    <div className="progress-overlay">
      <div className="progress-container glass-panel-dark">
        <div className="loading-header">
          <div className="loading-spinner"></div>
          <h2>Elaborazione in Corso</h2>
        </div>

        <div className="progress-bar-container">
          <div
            className="progress-bar-fill"
            style={{ width: `${progress.percentage}%` }}
          />
        </div>

        <p className="progress-info">{progress.percentage}%</p>
        <p className="progress-status">{progress.status}</p>
        <p className="progress-count">{progress.current} / {progress.total}</p>
      </div>
    </div>
  );
};

export default ProgressOverlay;
