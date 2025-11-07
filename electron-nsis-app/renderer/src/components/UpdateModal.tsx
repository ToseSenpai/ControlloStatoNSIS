import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import './UpdateModal.css';

const UpdateModal: React.FC = () => {
  const { available, downloaded, info, progress } = useSelector(
    (state: RootState) => state.update
  );

  const handleInstall = () => {
    window.electronAPI.installUpdate();
  };

  if (!available) return null;

  return (
    <div className="update-modal-overlay">
      <div className="update-modal">
        <div className="update-header">
          <h2>🚀 Aggiornamento Disponibile</h2>
        </div>

        <div className="update-content">
          {info && (
            <p className="update-version">
              Versione <strong>{info.version}</strong> disponibile!
            </p>
          )}

          {!downloaded && progress && (
            <div className="update-progress">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${progress.percent}%` }}
                />
              </div>
              <div className="progress-text">
                {Math.round(progress.percent)}%
                ({Math.round(progress.transferred / 1024 / 1024)} MB / {Math.round(progress.total / 1024 / 1024)} MB)
              </div>
            </div>
          )}

          {downloaded && (
            <div className="update-ready">
              <p>✅ Aggiornamento scaricato e pronto per l'installazione</p>
              <button className="install-button" onClick={handleInstall}>
                Installa e Riavvia
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UpdateModal;
