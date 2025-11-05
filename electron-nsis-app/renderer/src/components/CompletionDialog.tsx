import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store/store';
import { hideCompletion } from '../store/slices/ui-slice';
import './CompletionDialog.css';

const CompletionDialog: React.FC = () => {
  const dispatch = useDispatch();
  const { showCompletionDialog, completionMessage } = useSelector((state: RootState) => state.ui);

  if (!showCompletionDialog) return null;

  const handleClose = () => {
    dispatch(hideCompletion());
  };

  return (
    <div className="completion-overlay">
      <div className="completion-dialog glass-panel">
        <div className="completion-icon success-icon">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="30" stroke="#10B981" strokeWidth="4" className="success-circle" />
            <path d="M20 32L28 40L44 24" stroke="#10B981" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" className="success-check" />
          </svg>
        </div>

        <h2 className="completion-title">Elaborazione Completata</h2>

        <p className="completion-message">{completionMessage}</p>

        <button className="completion-button" onClick={handleClose}>
          OK
        </button>
      </div>
    </div>
  );
};

export default CompletionDialog;
