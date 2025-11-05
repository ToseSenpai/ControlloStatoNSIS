import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { FileText, Loader2 } from 'lucide-react';
import { RootState } from '../store/store';
import { setFilePath, setExcelData } from '../store/slices/data-slice';
import { setProcessing, addLog } from '../store/slices/ui-slice';
import { useIpc } from '../hooks/useIpc';
import './FileSection.css';

const FileSection: React.FC = () => {
  const dispatch = useDispatch();
  const ipc = useIpc();

  const { selectedFilePath, excel } = useSelector((state: RootState) => state.data);
  const { progress } = useSelector((state: RootState) => state.ui);

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

  // Estrai solo il nome del file dal percorso completo
  const getFileName = (path: string | null) => {
    if (!path) return null;
    return path.split('\\').pop() || path.split('/').pop() || path;
  };

  const fileName = getFileName(selectedFilePath);

  return (
    <div className="file-section">
      <h3 className="section-title">File Excel</h3>

      <button
        className="btn-select-file"
        onClick={handleSelectFile}
        disabled={progress.isProcessing}
        title={fileName || 'Seleziona file Excel'}
      >
        {progress.isProcessing ? (
          <Loader2 size={16} className="spinning" />
        ) : (
          <FileText size={16} />
        )}
        <span className="file-button-text">
          {fileName || 'Seleziona file Excel'}
        </span>
      </button>

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
    </div>
  );
};

export default FileSection;
