import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { processingOrchestrator } from './workers/processor';

let mainWindow: BrowserWindow | null = null;
let splashWindow: BrowserWindow | null = null;

function createSplashScreen() {
  splashWindow = new BrowserWindow({
    width: 400,
    height: 250,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: false,
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

  // In development, load from webpack-dev-server
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
  }

  // Show main window when ready
  mainWindow.once('ready-to-show', () => {
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
    createMainWindow();
  }
});
