import React from 'react';
import './WindowControls.css';

const WindowControls: React.FC = () => {
  const handleMinimize = () => {
    window.electronAPI?.windowMinimize();
  };

  const handleMaximize = () => {
    window.electronAPI?.windowMaximize();
  };

  const handleClose = () => {
    window.electronAPI?.windowClose();
  };

  return (
    <div className="window-controls">
      <button
        className="window-control-btn minimize-btn"
        onClick={handleMinimize}
        aria-label="Minimize"
        title="Riduci a icona"
      >
        <svg width="12" height="12" viewBox="0 0 12 12">
          <path d="M 2 6 L 10 6" stroke="currentColor" strokeWidth="1.5" fill="none" />
        </svg>
      </button>

      <button
        className="window-control-btn maximize-btn"
        onClick={handleMaximize}
        aria-label="Maximize"
        title="Ingrandisci"
      >
        <svg width="12" height="12" viewBox="0 0 12 12">
          <rect x="2" y="2" width="8" height="8" stroke="currentColor" strokeWidth="1.5" fill="none" />
        </svg>
      </button>

      <button
        className="window-control-btn close-btn"
        onClick={handleClose}
        aria-label="Close"
        title="Chiudi"
      >
        <svg width="12" height="12" viewBox="0 0 12 12">
          <path d="M 2 2 L 10 10 M 10 2 L 2 10" stroke="currentColor" strokeWidth="1.5" />
        </svg>
      </button>
    </div>
  );
};

export default WindowControls;
