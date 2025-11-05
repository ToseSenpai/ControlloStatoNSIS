import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { FileText, Loader2 } from 'lucide-react';
import { RootState } from '../store/store';
import { setFilePath, setExcelData } from '../store/slices/data-slice';
import { setState } from '../store/slices/app-slice';
import { setProcessing, addLog, resetBadges } from '../store/slices/ui-slice';
import { useIpc } from '../hooks/useIpc';
import './ControlsSection.css';

const ControlsSection: React.FC = () => {
  const dispatch = useDispatch();
  const ipc = useIpc();

  const { state } = useSelector((state: RootState) => state.app);
  const { selectedFilePath, excel } = useSelector((state: RootState) => state.data);
  const { progress } = useSelector((state: RootState) => state.ui);

  const canStart = excel && excel.codes && excel.codes.length > 0 && !progress.isProcessing;

  // File selection handler
  const handleSelectFile = async () => {
    try {
      dispatch(setProcessing(true));
      dispatch(addLog('Apertura dialog selezione file...'));

      const filePath = await ipc.selectFile();

      if (filePath) {
        dispatch(setFilePath(filePath));
        dispatch(addLog(`File selezionato: ${filePath}`));

        // Carica il file Excel
        dispatch(addLog('Caricamento file Excel...'));
        const excelData = await ipc.loadExcel(filePath);

        dispatch(setExcelData(excelData));
        dispatch(addLog(`File caricato: ${excelData.codes?.length || 0} codici trovati`));
      } else {
        dispatch(addLog('Selezione file annullata'));
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Errore sconosciuto';
      dispatch(addLog(`Errore: ${message}`));
      console.error('Errore selezione file:', error);
    } finally {
      dispatch(setProcessing(false));
    }
  };

  // Start processing handler
  const handleStart = () => {
    if (!excel?.codes) return;

    dispatch(setState('PROCESSING'));
    dispatch(setProcessing(true));
    dispatch(resetBadges());
    dispatch(addLog(`Avvio elaborazione di ${excel.codes.length} codici...`));

    ipc.startProcessing(excel.codes);
  };

  // Stop processing handler
  const handleStop = () => {
    dispatch(addLog('Interruzione elaborazione...'));
    ipc.stopProcessing();
    dispatch(setProcessing(false));
    dispatch(setState('IDLE'));
  };

  // Estrai solo il nome del file dal percorso completo
  const getFileName = (path: string | null) => {
    if (!path) return null;
    return path.split('\\').pop() || path.split('/').pop() || path;
  };

  const fileName = getFileName(selectedFilePath);

  return (
    <div className="controls-section">
      <h3 className="section-title">Controlli</h3>

      <div className="controls-buttons">
        {/* Button 1: Seleziona file Excel */}
        <button
          className="btn-control btn-select-file"
          onClick={handleSelectFile}
          disabled={progress.isProcessing}
          title={fileName || 'Seleziona file Excel'}
        >
          {progress.isProcessing ? (
            <Loader2 size={16} className="spinning" />
          ) : (
            <FileText size={16} />
          )}
          <span className="button-text">
            {fileName || 'Seleziona file Excel'}
          </span>
        </button>

        {/* Button 2/3: Avvia Elaborazione OR Ferma (conditional) */}
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

      {/* File info display (when loaded) */}
      {excel && (
        <div className="file-info">
          <div className="info-item">
            <span className="info-label">Codici trovati:</span>
            <span className="info-value">{excel.codes?.length || 0}</span>
          </div>
          {excel.columns && excel.columns.length > 0 && (
            <div className="info-item">
              <span className="info-label">Colonne:</span>
              <span className="info-value">{excel.columns.length}</span>
            </div>
          )}
        </div>
      )}

      {/* Status indicator */}
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
