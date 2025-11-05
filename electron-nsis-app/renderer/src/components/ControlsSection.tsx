import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { setState } from '../store/slices/app-slice';
import { setProcessing, addLog, resetBadges } from '../store/slices/ui-slice';
import { useIpc } from '../hooks/useIpc';
import './ControlsSection.css';

const ControlsSection: React.FC = () => {
  const dispatch = useDispatch();
  const ipc = useIpc();

  const { state } = useSelector((state: RootState) => state.app);
  const { excel } = useSelector((state: RootState) => state.data);
  const { progress } = useSelector((state: RootState) => state.ui);

  const canStart = excel && excel.codes && excel.codes.length > 0 && !progress.isProcessing;

  const handleStart = () => {
    if (!excel?.codes) return;

    dispatch(setState('PROCESSING'));
    dispatch(setProcessing(true));
    dispatch(resetBadges());
    dispatch(addLog(`Avvio elaborazione di ${excel.codes.length} codici...`));

    ipc.startProcessing(excel.codes);
  };

  const handleStop = () => {
    dispatch(addLog('Interruzione elaborazione...'));
    ipc.stopProcessing();
    dispatch(setProcessing(false));
    dispatch(setState('IDLE'));
  };

  return (
    <div className="controls-section">
      <h3 className="section-title">Controlli</h3>

      <div className="controls-buttons">
        {!progress.isProcessing ? (
          <button
            className="btn-control btn-start"
            onClick={handleStart}
            disabled={!canStart}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M3 2l10 6-10 6V2z" />
            </svg>
            <span>Avvia Elaborazione</span>
          </button>
        ) : (
          <button
            className="btn-control btn-stop"
            onClick={handleStop}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <rect x="3" y="3" width="10" height="10" />
            </svg>
            <span>Ferma</span>
          </button>
        )}
      </div>

      <div className="controls-status">
        <div className={`status-indicator status-${state.toLowerCase()}`}>
          <span className="status-dot"></span>
          <span className="status-text">{getStatusText(state)}</span>
        </div>
      </div>
    </div>
  );
};

function getStatusText(state: string): string {
  switch (state) {
    case 'IDLE': return 'Pronto';
    case 'LOADING': return 'Caricamento...';
    case 'PROCESSING': return 'Elaborazione in corso';
    case 'COMPLETED': return 'Completato';
    case 'ERROR': return 'Errore';
    default: return state;
  }
}

export default ControlsSection;
