import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { processingOrchestrator } from './workers/processor';

let mainWindow: BrowserWindow | null = null;
let splashWindow: BrowserWindow | null = null;

function createSplashScreen() {
  splashWindow = new BrowserWindow({
    width: 450,
    height: 550,
    transparent: false,
    frame: false,
    alwaysOnTop: true,
    resizable: false,
    backgroundColor: '#2d3139',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // In development, load from webpack-dev-server
  if (process.env.NODE_ENV === 'development') {
    splashWindow.loadURL('http://localhost:3000?splash=true');
  } else {
    splashWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'), {
      hash: 'splash'
    });
  }

  splashWindow.center();
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    show: false,
    backgroundColor: '#36393f',
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webviewTag: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // NOTE: We no longer use BrowserView - automation runs on the visible <webview> tag
  // The webview registers its webContents ID via IPC when it loads

  // In development, load from webpack-dev-server
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
    // Enable DevTools in production for debugging
    mainWindow.webContents.openDevTools();
  }

  // Log when page starts loading
  mainWindow.webContents.on('did-start-loading', () => {
    console.log('[MAIN] Main window started loading');
  });

  // Log when page finishes loading
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('[MAIN] Main window finished loading');
  });

  // Log any errors
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('[MAIN] Main window failed to load:', errorCode, errorDescription);
  });

  // Show main window when ready
  let windowShown = false;
  mainWindow.once('ready-to-show', () => {
    console.log('[MAIN] Main window ready-to-show event fired');
    windowShown = true;
    // Close splash screen after minimum time
    setTimeout(() => {
      if (splashWindow) {
        splashWindow.close();
        splashWindow = null;
      }
      if (mainWindow) {
        mainWindow.show();
        mainWindow.focus();

        // Set main window for processing orchestrator
        processingOrchestrator.setMainWindow(mainWindow);
      }
    }, 5000); // 5 seconds minimum splash time
  });

  // FALLBACK: Force show main window after 10 seconds if ready-to-show didn't fire
  setTimeout(() => {
    if (!windowShown && mainWindow) {
      console.warn('[MAIN] WARNING: ready-to-show did not fire - forcing window visibility');
      if (splashWindow) {
        splashWindow.close();
        splashWindow = null;
      }
      mainWindow.show();
      mainWindow.focus();
      processingOrchestrator.setMainWindow(mainWindow);
      // Keep DevTools open to see errors
      console.error('[MAIN] Check DevTools console for errors preventing ready-to-show');
    }
  }, 10000);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App lifecycle
app.on('ready', () => {
  createSplashScreen();
  // Start creating main window immediately
  createMainWindow();
  // Import other IPC handlers
  import('./ipc-handlers');
});

app.on('window-all-closed', () => {
  // On macOS, keep app active until user quits explicitly
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On macOS, re-create window when dock icon is clicked
  if (BrowserWindow.getAllWindows().length === 0) {
    createSplashScreen();
    createMainWindow(); // BrowserView will be initialized inside createMainWindow()
  }
});
