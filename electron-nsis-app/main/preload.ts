import { contextBridge, ipcRenderer, IpcRendererEvent } from 'electron';

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Window controls
  windowMinimize: () => ipcRenderer.send('window-minimize'),
  windowMaximize: () => ipcRenderer.send('window-maximize'),
  windowClose: () => ipcRenderer.send('window-close'),

  // File operations
  selectFile: () => ipcRenderer.invoke('select-file'),
  loadExcel: (filePath: string) => ipcRenderer.invoke('load-excel', filePath),
  saveExcel: (filePath: string, data: any) => ipcRenderer.invoke('save-excel', filePath, data),

  // Processing
  startProcessing: (codes: string[]) => ipcRenderer.send('start-processing', codes),
  stopProcessing: () => ipcRenderer.send('stop-processing'),

  // Event listeners
  onFileSelected: (callback: (filePath: string) => void) => {
    const subscription = (_event: IpcRendererEvent, filePath: string) => callback(filePath);
    ipcRenderer.on('file-selected', subscription);
    return () => ipcRenderer.removeListener('file-selected', subscription);
  },

  onExcelLoaded: (callback: (data: any) => void) => {
    const subscription = (_event: IpcRendererEvent, data: any) => callback(data);
    ipcRenderer.on('excel-loaded', subscription);
    return () => ipcRenderer.removeListener('excel-loaded', subscription);
  },

  onProgressUpdate: (callback: (data: { current: number; total: number }) => void) => {
    const subscription = (_event: IpcRendererEvent, data: { current: number; total: number }) => callback(data);
    ipcRenderer.on('progress-update', subscription);
    return () => ipcRenderer.removeListener('progress-update', subscription);
  },

  onStatusUpdate: (callback: (status: string) => void) => {
    const subscription = (_event: IpcRendererEvent, status: string) => callback(status);
    ipcRenderer.on('status-update', subscription);
    return () => ipcRenderer.removeListener('status-update', subscription);
  },

  onBadgeUpdate: (callback: (badges: any) => void) => {
    const subscription = (_event: IpcRendererEvent, badges: any) => callback(badges);
    ipcRenderer.on('badge-update', subscription);
    return () => ipcRenderer.removeListener('badge-update', subscription);
  },

  onLogMessage: (callback: (message: string) => void) => {
    const subscription = (_event: IpcRendererEvent, message: string) => callback(message);
    ipcRenderer.on('log-message', subscription);
    return () => ipcRenderer.removeListener('log-message', subscription);
  },

  onProcessingComplete: (callback: () => void) => {
    const subscription = () => callback();
    ipcRenderer.on('processing-complete', subscription);
    return () => ipcRenderer.removeListener('processing-complete', subscription);
  },

  onShowCompletionDialog: (callback: (message: string) => void) => {
    const subscription = (_event: IpcRendererEvent, message: string) => callback(message);
    ipcRenderer.on('show-completion-dialog', subscription);
    return () => ipcRenderer.removeListener('show-completion-dialog', subscription);
  },

  // WebView controls
  webViewGoBack: () => ipcRenderer.send('webview-go-back'),
  webViewGoForward: () => ipcRenderer.send('webview-go-forward'),
  webViewReload: () => ipcRenderer.send('webview-reload'),
  webViewGoHome: () => ipcRenderer.send('webview-go-home'),

  // Register webview webContents ID for automation
  registerWebView: (webContentsId: number) => ipcRenderer.send('register-webview', webContentsId),

  // WebView event listeners
  onWebViewUrlChange: (callback: (url: string) => void) => {
    const subscription = (_event: IpcRendererEvent, url: string) => callback(url);
    ipcRenderer.on('webview-url-change', subscription);
    return () => ipcRenderer.removeListener('webview-url-change', subscription);
  },

  onWebViewLoading: (callback: (loading: boolean) => void) => {
    const subscription = (_event: IpcRendererEvent, loading: boolean) => callback(loading);
    ipcRenderer.on('webview-loading', subscription);
    return () => ipcRenderer.removeListener('webview-loading', subscription);
  },

  onWebViewNavigationState: (callback: (state: { canGoBack: boolean; canGoForward: boolean }) => void) => {
    const subscription = (_event: IpcRendererEvent, state: { canGoBack: boolean; canGoForward: boolean }) => callback(state);
    ipcRenderer.on('webview-navigation-state', subscription);
    return () => ipcRenderer.removeListener('webview-navigation-state', subscription);
  },

  // Generic send method for IPC
  send: (channel: string, ...args: any[]) => {
    ipcRenderer.send(channel, ...args);
  },

  // Window resize event listener
  onWindowResized: (callback: () => void) => {
    const subscription = () => callback();
    ipcRenderer.on('window-resized', subscription);
    return () => ipcRenderer.removeListener('window-resized', subscription);
  }
});

// Type definitions for TypeScript
export interface ElectronAPI {
  windowMinimize: () => void;
  windowMaximize: () => void;
  windowClose: () => void;
  selectFile: () => Promise<string | null>;
  loadExcel: (filePath: string) => Promise<any>;
  saveExcel: (filePath: string, data: any) => Promise<void>;
  startProcessing: (codes: string[]) => void;
  stopProcessing: () => void;
  onFileSelected: (callback: (filePath: string) => void) => () => void;
  onExcelLoaded: (callback: (data: any) => void) => () => void;
  onProgressUpdate: (callback: (data: { current: number; total: number }) => void) => () => void;
  onStatusUpdate: (callback: (status: string) => void) => () => void;
  onBadgeUpdate: (callback: (badges: any) => void) => () => void;
  onLogMessage: (callback: (message: string) => void) => () => void;
  onProcessingComplete: (callback: () => void) => () => void;
  registerWebView: (webContentsId: number) => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
