import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store/store';
import { showCompletion, setProcessing, updateBadges } from '../store/slices/ui-slice';
import { setState } from '../store/slices/app-slice';
import { setUpdateAvailable, setDownloadProgress, setUpdateDownloaded, setUpdateError } from '../store/slices/update-slice';
import ControlsSection from './ControlsSection';
import StatisticsSection from './StatisticsSection';
import WebViewSection from './WebViewSection';
import LogArea from './LogArea';
import ProgressOverlay from './ProgressOverlay';
import CompletionDialog from './CompletionDialog';
import SidebarToggle from './SidebarToggle';
import UpdateModal from './UpdateModal';
import './MainWindow.css';

const MainWindow: React.FC = () => {
  const dispatch = useDispatch();
  const { state } = useSelector((state: RootState) => state.app);
  const { progress } = useSelector((state: RootState) => state.ui);
  const { collapsed } = useSelector((state: RootState) => state.sidebar);
  const [appVersion, setAppVersion] = useState<string>('');

  // Get app version
  useEffect(() => {
    window.electronAPI.getAppVersion().then(v => setAppVersion(v));
  }, []);

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

  // ===== AUTO-UPDATE EVENT LISTENERS =====
  useEffect(() => {
    // Update available
    const unsubscribeAvailable = window.electronAPI.onUpdateAvailable((info: any) => {
      console.log('[MainWindow] Update available:', info);
      dispatch(setUpdateAvailable(info));
    });

    // Download progress
    const unsubscribeProgress = window.electronAPI.onUpdateDownloadProgress((progress: any) => {
      console.log('[MainWindow] Download progress:', progress.percent + '%');
      dispatch(setDownloadProgress(progress));
    });

    // Update downloaded
    const unsubscribeDownloaded = window.electronAPI.onUpdateDownloaded((info: any) => {
      console.log('[MainWindow] Update downloaded:', info);
      dispatch(setUpdateDownloaded(info));
    });

    // Update error
    const unsubscribeError = window.electronAPI.onUpdateError((error: string) => {
      console.error('[MainWindow] Update error:', error);
      dispatch(setUpdateError(error));
    });

    return () => {
      unsubscribeAvailable();
      unsubscribeProgress();
      unsubscribeDownloaded();
      unsubscribeError();
    };
  }, [dispatch]);

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

      {/* Progress Overlay */}
      <ProgressOverlay />

      {/* Completion Dialog */}
      <CompletionDialog />

      {/* Update Modal */}
      <UpdateModal />

      {/* App Version */}
      {appVersion && <div className="app-version">v{appVersion}</div>}
    </div>
  );
};

export default MainWindow;
