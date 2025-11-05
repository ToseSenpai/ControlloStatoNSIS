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

      // Create BrowserView with SAME partition as renderer's <webview>
      // This allows sharing cookies/session/authentication
      this.browserView = new BrowserView({
        webPreferences: {
          partition: 'persist:nsis', // CRITICAL: Share session with <webview> tag
          nodeIntegration: false,
          contextIsolation: true,
          sandbox: true
        }
      });

      // Add to main window
      mainWindow.addBrowserView(this.browserView);

      // Set BrowserView to be hidden off-screen but with realistic dimensions
      // Use 1280x720 viewport (same as Playwright) for proper rendering
      // Position far off-screen where it won't be visible
      this.browserView.setBounds({
        x: -10000,
        y: -10000,
        width: 1280,
        height: 720
      });
      console.log('[BrowserView] Positioned off-screen (1280x720) for automation use only');

      // Setup navigation event handlers
      this.setupEventHandlers();

      // DO NOT load URL here - let webview-automation handle loading
      // This avoids race conditions with event listeners

      this.isInitialized = true;
      console.log('[BrowserView] Initialization complete (ready for automation)');

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

    // Prevent new windows/tabs from opening - force navigation in same view
    webContents.setWindowOpenHandler(({ url }) => {
      console.log('[BrowserView] Intercepted new-window attempt:', url);
      // Instead of opening a new window, navigate in the same BrowserView
      webContents.loadURL(url);
      return { action: 'deny' }; // Block the new window
    });

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

      // Inject link click interceptor after page loads
      this.injectLinkClickInterceptor();
    });

    // Error handling
    webContents.on('did-fail-load', (_event, errorCode, errorDescription) => {
      console.error('[BrowserView] Load failed:', errorCode, errorDescription);
      this.sendLoadingState(false);
    });
  }

  /**
   * Inject JavaScript to intercept all link clicks and prevent new windows
   */
  private injectLinkClickInterceptor(): void {
    if (!this.browserView) return;

    const webContents = this.browserView.webContents;

    // Inject JavaScript to intercept link clicks AND override window.open()
    webContents.executeJavaScript(`
      (function() {
        // CRITICAL: Override window.open() globally (like old PyQt6 system)
        // This catches ALL JavaScript-initiated window opens
        window.open = function(url, name, features) {
          console.log('[BrowserView Interceptor] Blocked window.open():', url);
          if (url) {
            window.location.href = url;
          }
          return null;
        };

        // Remove existing interceptors if present
        if (window.__browserview_link_interceptor) {
          document.removeEventListener('click', window.__browserview_link_interceptor, true);
          document.removeEventListener('mousedown', window.__browserview_link_interceptor, true);
          document.removeEventListener('auxclick', window.__browserview_link_interceptor, true);
        }

        // Create new interceptor that handles ALL clicks on links
        const interceptor = function(e) {
          const link = e.target.closest('a');

          if (link && link.href) {
            // Check if any modifier key is pressed or if it's a non-left click
            const hasModifier = e.ctrlKey || e.shiftKey || e.metaKey || e.altKey;
            const isMiddleClick = e.button === 1;
            const opensNewWindow = link.target === '_blank' ||
                                  link.target === '_new' ||
                                  link.rel.includes('noopener') ||
                                  link.rel.includes('noreferrer');

            // Intercept if any condition that would open new window is true
            if (opensNewWindow || hasModifier || isMiddleClick) {
              console.log('[BrowserView Interceptor] Blocked link click (Ctrl/Shift/Middle/target="_blank"):', link.href);
              e.preventDefault();
              e.stopPropagation();
              e.stopImmediatePropagation();

              // Navigate in same page instead of opening new window
              window.location.href = link.href;
              return false;
            }
          }
        };

        // Store reference
        window.__browserview_link_interceptor = interceptor;

        // Add listeners for all types of clicks in capture phase
        document.addEventListener('click', interceptor, true);
        document.addEventListener('mousedown', interceptor, true);
        document.addEventListener('auxclick', interceptor, true); // Middle click

        console.log('[BrowserView Interceptor] window.open() override + click interceptor installed');
      })();
    `).catch(error => {
      console.error('[BrowserView] Error injecting link interceptor:', error);
    });
  }

  /**
   * Update BrowserView bounds based on renderer-provided coordinates
   * DISABLED: BrowserView is kept off-screen for automation only
   */
  updateBoundsFromRenderer(bounds: { x: number; y: number; width: number; height: number }): void {
    // BrowserView is intentionally kept off-screen for automation
    // Do not reposition it based on renderer coordinates
    console.log('[BrowserView] Ignoring bounds update - BrowserView is for automation only');
    return;
  }

  /**
   * Update BrowserView bounds based on window size (fallback)
   * DISABLED: BrowserView is kept off-screen for automation only
   */
  updateBounds(): void {
    // BrowserView is intentionally kept off-screen for automation
    // Do not reposition it
    console.log('[BrowserView] Ignoring bounds update - BrowserView is for automation only');
    return;
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
   * Get BrowserView instance (for automation)
   */
  getBrowserView(): BrowserView | null {
    return this.browserView;
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
