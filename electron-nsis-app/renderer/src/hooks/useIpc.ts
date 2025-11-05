import { useEffect } from 'react';

/**
 * Custom hook per gestire la comunicazione IPC con il main process
 * Gestisce automaticamente subscribe/unsubscribe
 */

export const useIpc = () => {
  return {
    // File operations
    selectFile: async (): Promise<string | null> => {
      return window.electronAPI.selectFile();
    },

    loadExcel: async (filePath: string): Promise<any> => {
      return window.electronAPI.loadExcel(filePath);
    },

    saveExcel: async (filePath: string, data: any): Promise<void> => {
      return window.electronAPI.saveExcel(filePath, data);
    },

    // Processing
    startProcessing: (codes: string[]) => {
      window.electronAPI.startProcessing(codes);
    },

    stopProcessing: () => {
      window.electronAPI.stopProcessing();
    },

    // Event listeners with auto-cleanup
    onFileSelected: (callback: (filePath: string) => void) => {
      return window.electronAPI.onFileSelected(callback);
    },

    onExcelLoaded: (callback: (data: any) => void) => {
      return window.electronAPI.onExcelLoaded(callback);
    },

    onProgressUpdate: (callback: (data: { current: number; total: number }) => void) => {
      return window.electronAPI.onProgressUpdate(callback);
    },

    onStatusUpdate: (callback: (status: string) => void) => {
      return window.electronAPI.onStatusUpdate(callback);
    },

    onBadgeUpdate: (callback: (badges: any) => void) => {
      return window.electronAPI.onBadgeUpdate(callback);
    },

    onLogMessage: (callback: (message: string) => void) => {
      return window.electronAPI.onLogMessage(callback);
    },

    onProcessingComplete: (callback: () => void) => {
      return window.electronAPI.onProcessingComplete(callback);
    },

    // WebView controls
    webViewGoBack: () => {
      window.electronAPI.webViewGoBack();
    },

    webViewGoForward: () => {
      window.electronAPI.webViewGoForward();
    },

    webViewReload: () => {
      window.electronAPI.webViewReload();
    },

    webViewGoHome: () => {
      window.electronAPI.webViewGoHome();
    },

    // WebView event listeners
    onWebViewUrlChange: (callback: (url: string) => void) => {
      return window.electronAPI.onWebViewUrlChange(callback);
    },

    onWebViewLoading: (callback: (loading: boolean) => void) => {
      return window.electronAPI.onWebViewLoading(callback);
    },

    onWebViewNavigationState: (callback: (state: { canGoBack: boolean; canGoForward: boolean }) => void) => {
      return window.electronAPI.onWebViewNavigationState(callback);
    },

    // Generic send method
    send: (channel: string, ...args: any[]) => {
      window.electronAPI.send(channel, ...args);
    },

    // Window resize event listener
    onWindowResized: (callback: () => void) => {
      return window.electronAPI.onWindowResized(callback);
    }
  };
};

/**
 * Hook per auto-subscribe a eventi IPC con cleanup automatico
 */
export const useIpcEvent = <T>(
  event: 'file-selected' | 'excel-loaded' | 'progress-update' | 'status-update' | 'badge-update' | 'log-message' | 'processing-complete',
  callback: (data: T) => void
) => {
  useEffect(() => {
    let unsubscribe: (() => void) | undefined;

    switch (event) {
      case 'file-selected':
        unsubscribe = window.electronAPI.onFileSelected(callback as any);
        break;
      case 'excel-loaded':
        unsubscribe = window.electronAPI.onExcelLoaded(callback as any);
        break;
      case 'progress-update':
        unsubscribe = window.electronAPI.onProgressUpdate(callback as any);
        break;
      case 'status-update':
        unsubscribe = window.electronAPI.onStatusUpdate(callback as any);
        break;
      case 'badge-update':
        unsubscribe = window.electronAPI.onBadgeUpdate(callback as any);
        break;
      case 'log-message':
        unsubscribe = window.electronAPI.onLogMessage(callback as any);
        break;
      case 'processing-complete':
        unsubscribe = window.electronAPI.onProcessingComplete(callback as any);
        break;
    }

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, [event, callback]);
};
