// Global type definitions for the renderer process

interface ElectronAPI {
  // Window controls
  windowMinimize: () => void;
  windowMaximize: () => void;
  windowClose: () => void;

  // File operations
  selectFile: () => Promise<string | null>;
  loadExcel: (filePath: string) => Promise<any>;
  saveExcel: (filePath: string, data: any) => Promise<void>;

  // Processing
  startProcessing: (codes: string[]) => void;
  stopProcessing: () => void;

  // Event listeners
  onFileSelected: (callback: (filePath: string) => void) => () => void;
  onExcelLoaded: (callback: (data: any) => void) => () => void;
  onProgressUpdate: (callback: (data: { current: number; total: number }) => void) => () => void;
  onStatusUpdate: (callback: (status: string) => void) => () => void;
  onBadgeUpdate: (callback: (badges: any) => void) => () => void;
  onLogMessage: (callback: (message: string) => void) => () => void;
  onProcessingComplete: (callback: () => void) => () => void;
  onShowCompletionDialog: (callback: (message: string) => void) => () => void;

  // WebView controls
  webViewGoBack: () => void;
  webViewGoForward: () => void;
  webViewReload: () => void;
  webViewGoHome: () => void;

  // Register webview for automation
  registerWebView: (webContentsId: number) => void;

  // WebView event listeners
  onWebViewUrlChange: (callback: (url: string) => void) => () => void;
  onWebViewLoading: (callback: (loading: boolean) => void) => () => void;
  onWebViewNavigationState: (callback: (state: { canGoBack: boolean; canGoForward: boolean }) => void) => () => void;

  // Generic IPC methods
  send: (channel: string, ...args: any[]) => void;
  onWindowResized: (callback: () => void) => () => void;

  // Auto-update APIs
  getAppVersion: () => Promise<string>;
  downloadUpdate: () => void;
  installUpdate: () => void;
  onUpdateAvailable: (callback: (info: any) => void) => () => void;
  onUpdateDownloaded: (callback: (info: any) => void) => () => void;
  onUpdateError: (callback: (error: string) => void) => () => void;
  onUpdateDownloadProgress: (callback: (progress: any) => void) => () => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

export {};
