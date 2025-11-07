import { app, BrowserWindow, ipcMain } from 'electron';
import { autoUpdater } from 'electron-updater';
import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';
import { processingOrchestrator } from './workers/processor';

// ===== CRITICAL: Error handling BEFORE any other code =====
process.on('uncaughtException', (error) => {
  const logPath = path.join(os.tmpdir(), 'electron-crash.log');
  const logMessage = `${new Date().toISOString()}\nUNCIAUGHT EXCEPTION:\n${error.stack}\n\n`;
  try {
    fs.writeFileSync(logPath, logMessage, { flag: 'a' });
  } catch (e) {
    console.error('Cannot write crash log:', e);
  }
  console.error('[FATAL] Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason: any) => {
  const logPath = path.join(os.tmpdir(), 'electron-rejection.log');
  const logMessage = `${new Date().toISOString()}\nUNHANDLED REJECTION:\n${JSON.stringify(reason, null, 2)}\n\n`;
  try {
    fs.writeFileSync(logPath, logMessage, { flag: 'a' });
  } catch (e) {
    console.error('Cannot write rejection log:', e);
  }
  console.error('[FATAL] Unhandled Rejection:', reason);
});

// ===== CRITICAL: Set userData path BEFORE app.on('ready') =====
// This ensures Electron uses the correct AppData location with proper permissions
const userDataPath = path.join(app.getPath('appData'), 'ControlloStatoNSIS');
app.setPath('userData', userDataPath);

// Create userData directory if it doesn't exist
try {
  if (!fs.existsSync(userDataPath)) {
    fs.mkdirSync(userDataPath, { recursive: true, mode: 0o755 });
    console.log('[APP] Created userData directory:', userDataPath);
  } else {
    console.log('[APP] userData directory exists:', userDataPath);
  }

  // Test write permissions
  const testFile = path.join(userDataPath, '.permission-test');
  fs.writeFileSync(testFile, 'test');
  fs.unlinkSync(testFile);
  console.log('[APP] userData is writable');
} catch (error) {
  console.error('[APP] CRITICAL: Cannot access userData:', error);
  // Continue anyway - app might still work with memory partition
}

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
    icon: path.join(__dirname, '..', 'assets', 'icon.ico'),
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
    icon: path.join(__dirname, '..', 'assets', 'icon.ico'),
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

// ===== AUTO-UPDATE CONFIGURATION =====
function setupAutoUpdater() {
  const isDev = !app.isPackaged;

  if (!isDev) {
    // Configure autoUpdater
    autoUpdater.autoDownload = true;
    autoUpdater.autoInstallOnAppQuit = false;

    // Event Listeners
    autoUpdater.on('checking-for-update', () => {
      console.log('🔍 Checking for updates...');
    });

    autoUpdater.on('update-available', (info) => {
      console.log('✅ Update available:', info.version);
      console.log('Release notes:', info.releaseNotes);
      console.log('Release date:', info.releaseDate);
      if (mainWindow) {
        mainWindow.webContents.send('update-available', info);
      }
    });

    autoUpdater.on('update-not-available', (info) => {
      console.log('ℹ️ No updates available');
      console.log('Current version:', app.getVersion());
    });

    autoUpdater.on('error', (err) => {
      console.error('❌ Auto-updater error:', err);
      // Don't show 404 errors (normal when no releases exist)
      if (!err.message || !err.message.includes('404')) {
        if (mainWindow) {
          mainWindow.webContents.send('update-error', err.message);
        }
      }
    });

    autoUpdater.on('download-progress', (progressObj) => {
      const percent = Math.round(progressObj.percent);
      const transferred = Math.round(progressObj.transferred / 1024 / 1024);
      const total = Math.round(progressObj.total / 1024 / 1024);

      console.log(`📊 Download progress: ${percent}% (${transferred}MB / ${total}MB)`);
      console.log(`Speed: ${Math.round(progressObj.bytesPerSecond / 1024)}KB/s`);

      // Send progress to renderer
      if (mainWindow) {
        mainWindow.webContents.send('update-download-progress', progressObj);
      }
    });

    autoUpdater.on('update-downloaded', (info) => {
      console.log('✅ Update downloaded successfully:', info.version);
      console.log('Files:', info.files);

      // Notify renderer that update is ready to install
      if (mainWindow) {
        mainWindow.webContents.send('update-downloaded', info);
      }
    });

    // Check for updates after main window is shown
    setTimeout(() => {
      console.log('🚀 Production mode - checking for updates...');
      console.log('Current version:', app.getVersion());

      autoUpdater.checkForUpdates()
        .then(result => {
          console.log('Update check result:', result);
        })
        .catch(err => {
          console.log('Update check failed:', err.message);
        });
    }, 3000); // Wait 3 seconds after app start
  } else {
    console.log('🔧 Development mode - skipping update check');
  }
}

// App lifecycle
app.on('ready', () => {
  createSplashScreen();
  // Start creating main window immediately
  createMainWindow();
  // Import other IPC handlers
  import('./ipc-handlers');
  // Setup auto-updater
  setupAutoUpdater();
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
