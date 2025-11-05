import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store/store';
import { showCompletion, setProcessing, updateBadges } from '../store/slices/ui-slice';
import { setState } from '../store/slices/app-slice';
import ControlsSection from './ControlsSection';
import StatisticsSection from './StatisticsSection';
import WebViewSection from './WebViewSection';
import LogArea from './LogArea';
import ProgressOverlay from './ProgressOverlay';
import CompletionDialog from './CompletionDialog';
import SidebarToggle from './SidebarToggle';
import './MainWindow.css';

const MainWindow: React.FC = () => {
  const dispatch = useDispatch();
  const { state } = useSelector((state: RootState) => state.app);
  const { progress } = useSelector((state: RootState) => state.ui);
  const { collapsed } = useSelector((state: RootState) => state.sidebar);

  // Listen for completion dialog event from main process
  useEffect(() => {
    const unsubscribe = window.electronAPI.onShowCompletionDialog((message: string) => {
      console.log('[MainWindow] Showing completion dialog:', message);
      dispatch(showCompletion(message));
    });

    return () => {
      unsubscribe();
    };
  }, [dispatch]);

  // Listen for processing complete event to reset UI state
  useEffect(() => {
    const unsubscribe = window.electronAPI.onProcessingComplete(() => {
      console.log('[MainWindow] Processing completed - resetting UI state');
      dispatch(setProcessing(false));
      dispatch(setState('COMPLETED'));
    });

    return () => {
      unsubscribe();
    };
  }, [dispatch]);

  // Listen for badge updates from main process
  useEffect(() => {
    const unsubscribe = window.electronAPI.onBadgeUpdate((badges: any) => {
      console.log('[MainWindow] Badge update received:', badges);
      dispatch(updateBadges(badges));
    });

    return () => {
      unsubscribe();
    };
  }, [dispatch]);

  const getStatusText = () => {
    if (progress.isProcessing) {
      return `Elaborazione in corso: ${progress.current}/${progress.total} (${progress.percentage}%)`;
    }
    switch (state) {
      case 'IDLE':
        return 'Pronto';
      case 'PROCESSING':
        return 'Elaborazione...';
      case 'COMPLETED':
        return 'Elaborazione completata';
      case 'ERROR':
        return 'Errore durante elaborazione';
      default:
        return 'Pronto';
    }
  };

  return (
    <div className="main-window">
      {/* Main Content */}
      <div className="main-content">
        <div className={`content-grid ${collapsed ? 'sidebar-collapsed' : ''}`}>
          {/* Left Sidebar Column */}
          <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
            <SidebarToggle />

            <div className="sidebar-content">
              <div className={`glass-panel section-panel ${collapsed ? 'compact' : ''}`}>
                <ControlsSection />
              </div>

              <div className={`glass-panel section-panel ${collapsed ? 'compact' : ''}`}>
                <StatisticsSection />
              </div>

              {/* Log Operazioni - temporaneamente nascosto
              <div className={`glass-panel section-panel ${collapsed ? 'compact' : ''}`}>
                <LogArea />
              </div>
              */}
            </div>
          </div>

          {/* Right Column: WebView (spans all rows) */}
          <div className="section-panel-full">
            <WebViewSection />
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <span className="status-text">{getStatusText()}</span>
      </div>

      {/* Progress Overlay */}
      <ProgressOverlay />

      {/* Completion Dialog */}
      <CompletionDialog />
    </div>
  );
};

export default MainWindow;
