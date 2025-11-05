import React, { useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { clearLogs, toggleLogs } from '../store/slices/ui-slice';
import './LogArea.css';

const LogArea: React.FC = () => {
  const dispatch = useDispatch();
  const { logs, showLogs } = useSelector((state: RootState) => state.ui);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (showLogs && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, showLogs]);

  const handleToggleLogs = () => {
    dispatch(toggleLogs());
  };

  const handleClearLogs = () => {
    dispatch(clearLogs());
  };

  const formatTimestamp = (log: string) => {
    const now = new Date();
    const time = now.toLocaleTimeString('it-IT', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
    return `[${time}]`;
  };

  const getLogType = (log: string): 'info' | 'warning' | 'error' | 'success' => {
    const lowerLog = log.toLowerCase();
    if (lowerLog.includes('errore') || lowerLog.includes('error') || lowerLog.includes('fallito')) {
      return 'error';
    }
    if (lowerLog.includes('warning') || lowerLog.includes('attenzione')) {
      return 'warning';
    }
    if (lowerLog.includes('completato') || lowerLog.includes('successo') || lowerLog.includes('caricato')) {
      return 'success';
    }
    return 'info';
  };

  return (
    <div className="log-area">
      <div className="log-header">
        <h3 className="log-title">Log Operazioni</h3>
        <div className="log-controls">
          <button
            className="btn-icon"
            onClick={handleClearLogs}
            disabled={logs.length === 0}
            title="Cancella log"
          >
            <span className="icon">🗑️</span>
          </button>
          <button
            className="btn-icon"
            onClick={handleToggleLogs}
            title={showLogs ? 'Nascondi log' : 'Mostra log'}
          >
            <span className="icon">{showLogs ? '▼' : '▲'}</span>
          </button>
        </div>
      </div>

      {showLogs && (
        <div className="log-container glass-panel-dark">
          <div className="log-content">
            {logs.length === 0 ? (
              <div className="log-empty">Nessun log disponibile</div>
            ) : (
              logs.map((log, index) => {
                const logType = getLogType(log);
                return (
                  <div key={index} className={`log-entry log-${logType}`}>
                    <span className="log-timestamp">{formatTimestamp(log)}</span>
                    <span className="log-message">{log}</span>
                  </div>
                );
              })
            )}
            <div ref={logEndRef} />
          </div>
        </div>
      )}
    </div>
  );
};

export default LogArea;
