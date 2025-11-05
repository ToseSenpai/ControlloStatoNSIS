/**
 * BrowserView manager for integrated web navigation
 */

import { BrowserWindow, BrowserView } from 'electron';
import { URL_NSIS } from '../shared/constants/config';

export class BrowserViewManager {
  private browserView: BrowserView | null = null;
  private mainWindow: BrowserWindow | null = null;
  private isInitialized: boolean = false;

  /**
   * Initialize BrowserView and attach to main window
   */
  initialize(mainWindow: BrowserWindow): void {
    if (this.isInitialized) {
      console.log('[BrowserView] Already initialized');
      return;
    }

    this.mainWindow = mainWindow;

    try {
      console.log('[BrowserView] Creating BrowserView...');

      // Create BrowserView
      this.browserView = new BrowserView({
        webPreferences: {
          nodeIntegration: false,
          contextIsolation: true,
          sandbox: true
        }
      });

      // Add to main window
      mainWindow.addBrowserView(this.browserView);

      // Set initial bounds (will be updated by renderer)
      this.updateBounds();

      // Setup navigation event handlers
      this.setupEventHandlers();

      // Load initial URL
      this.browserView.webContents.loadURL(URL_NSIS);

      this.isInitialized = true;
      console.log('[BrowserView] Initialization complete');

    } catch (error) {
      console.error('[BrowserView] Initialization error:', error);
      this.cleanup();
    }
  }

  /**
   * Setup event handlers for navigation events
   */
  private setupEventHandlers(): void {
    if (!this.browserView || !this.mainWindow) return;

    const webContents = this.browserView.webContents;

    // URL change event
    webContents.on('did-navigate', (_event, url) => {
      this.sendUrlChange(url);
      this.sendNavigationState();
    });

    webContents.on('did-navigate-in-page', (_event, url) => {
      this.sendUrlChange(url);
      this.sendNavigationState();
    });

    // Loading events
    webContents.on('did-start-loading', () => {
      this.sendLoadingState(true);
    });

    webContents.on('did-stop-loading', () => {
      this.sendLoadingState(false);
      this.sendNavigationState();
    });

    // Error handling
    webContents.on('did-fail-load', (_event, errorCode, errorDescription) => {
      console.error('[BrowserView] Load failed:', errorCode, errorDescription);
      this.sendLoadingState(false);
    });
  }

  /**
   * Update BrowserView bounds based on renderer-provided coordinates
   */
  updateBoundsFromRenderer(bounds: { x: number; y: number; width: number; height: number }): void {
    if (!this.browserView || !this.mainWindow) return;

    console.log('[BrowserView] Setting bounds from renderer:', bounds);

    this.browserView.setBounds({
      x: Math.round(bounds.x),
      y: Math.round(bounds.y),
      width: Math.round(bounds.width),
      height: Math.round(bounds.height)
    });
  }

  /**
   * Update BrowserView bounds based on window size (fallback)
   */
  updateBounds(): void {
    if (!this.browserView || !this.mainWindow) return;

    console.log('[BrowserView] Using fallback bounds calculation');
    // Fallback positioning - will be overridden by renderer
    const windowBounds = this.mainWindow.getBounds();
    const x = 20;
    const y = 420;
    const width = Math.max(windowBounds.width - 40, 400);
    const height = 500;

    this.browserView.setBounds({ x, y, width, height });
  }

  /**
   * Send URL change to renderer
   */
  private sendUrlChange(url: string): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('webview-url-change', url);
    }
  }

  /**
   * Send loading state to renderer
   */
  private sendLoadingState(loading: boolean): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('webview-loading', loading);
    }
  }

  /**
   * Send navigation state to renderer
   */
  private sendNavigationState(): void {
    if (!this.browserView || !this.mainWindow || this.mainWindow.isDestroyed()) {
      return;
    }

    const webContents = this.browserView.webContents;
    this.mainWindow.webContents.send('webview-navigation-state', {
      canGoBack: webContents.canGoBack(),
      canGoForward: webContents.canGoForward()
    });
  }

  /**
   * Navigation: Go back
   */
  goBack(): void {
    if (this.browserView && this.browserView.webContents.canGoBack()) {
      this.browserView.webContents.goBack();
    }
  }

  /**
   * Navigation: Go forward
   */
  goForward(): void {
    if (this.browserView && this.browserView.webContents.canGoForward()) {
      this.browserView.webContents.goForward();
    }
  }

  /**
   * Navigation: Reload
   */
  reload(): void {
    if (this.browserView) {
      this.browserView.webContents.reload();
    }
  }

  /**
   * Navigation: Go to home (NSIS URL)
   */
  goHome(): void {
    if (this.browserView) {
      this.browserView.webContents.loadURL(URL_NSIS);
    }
  }

  /**
   * Get current URL
   */
  getCurrentUrl(): string {
    if (this.browserView) {
      return this.browserView.webContents.getURL();
    }
    return '';
  }

  /**
   * Cleanup and remove BrowserView
   */
  cleanup(): void {
    try {
      console.log('[BrowserView] Cleaning up...');

      if (this.browserView && this.mainWindow) {
        this.mainWindow.removeBrowserView(this.browserView);
        // Note: BrowserView doesn't have a destroy() method in newer Electron versions
        // It will be garbage collected after being removed
        this.browserView = null;
      }

      this.mainWindow = null;
      this.isInitialized = false;
      console.log('[BrowserView] Cleanup complete');

    } catch (error) {
      console.error('[BrowserView] Error during cleanup:', error);
    }
  }

  /**
   * Check if initialized
   */
  isReady(): boolean {
    return this.isInitialized && this.browserView !== null;
  }
}

// Export singleton instance
export const browserViewManager = new BrowserViewManager();
