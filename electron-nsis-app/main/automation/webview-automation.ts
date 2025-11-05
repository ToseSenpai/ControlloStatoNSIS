/**
 * WebView-based web automation for NSIS state checking
 * Uses the VISIBLE <webview> tag instead of hidden BrowserView
 */

import { webContents as allWebContents, WebContents } from 'electron';
import {
  URL_NSIS, STATO_SELECTOR, MAX_RETRIES,
  DELAY_AFTER_INPUT_JS, DELAY_AFTER_CLICK_JS, DELAY_BETWEEN_RETRIES,
  FETCH_CHECK_INTERVAL_MS
} from '../../shared/constants/config';
import { ProcessingResult } from '../../shared/types/excel-types';

export interface FetchResult {
  success: boolean;
  code: string;
  state?: string;
  cells?: string[];
  error?: string;
}

export class WebViewAutomation {
  private isInitialized: boolean = false;
  private webContentsId: number | null = null;
  private webContents: WebContents | null = null;

  /**
   * Get WebContents from stored ID
   */
  private getWebContents(): WebContents {
    if (!this.webContents) {
      throw new Error('WebContents not available - automation not initialized');
    }
    if (this.webContents.isDestroyed()) {
      throw new Error('WebContents has been destroyed');
    }
    return this.webContents;
  }

  /**
   * Initialize WebView automation using the VISIBLE webview's webContents
   * This uses the same webview the user sees and has navigated to
   */
  async initialize(webContentsId: number): Promise<void> {
    if (this.isInitialized) {
      console.log('[WebView Automation] Already initialized');
      return;
    }

    try {
      console.log('[WebView Automation] Initializing with webContents ID:', webContentsId);

      // Get the webContents from the ID (this is the VISIBLE webview)
      this.webContentsId = webContentsId;
      this.webContents = allWebContents.fromId(webContentsId) || null;

      if (!this.webContents) {
        throw new Error(`WebContents with ID ${webContentsId} not found`);
      }

      if (this.webContents.isDestroyed()) {
        throw new Error('WebContents has been destroyed');
      }

      const currentUrl = this.webContents.getURL();
      console.log(`[WebView Automation] Using visible webview at URL: ${currentUrl}`);
      console.log('[WebView Automation] This is the SAME webview the user sees');

      // NO NEED to load URL - we use the page the user is already on!
      // The user has already navigated and logged in

      // Give a moment for the page to settle
      await this.sleep(500);

      // Inject link click interceptor (in case it's needed)
      await this.injectLinkInterceptor();

      this.isInitialized = true;
      console.log('[WebView Automation] Initialization complete - using visible webview');

    } catch (error) {
      console.error('[WebView Automation] Initialization error:', error);
      throw error;
    }
  }

  /**
   * Fetch state for a specific code
   */
  async fetchStateForCode(code: string): Promise<FetchResult> {
    if (!this.isInitialized) {
      return {
        success: false,
        code: code,
        error: 'WebView not initialized'
      };
    }

    console.log(`[WebView Automation] Fetching state for code: ${code}`);

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        if (attempt > 0) {
          console.log(`[WebView Automation] Retry attempt ${attempt} for code: ${code}`);
          await this.sleep(DELAY_BETWEEN_RETRIES);
        }

        // Step 1: Input code
        const inputSuccess = await this.inputCode(code);
        if (!inputSuccess) {
          console.error('[WebView Automation] Failed to input code');
          continue; // Retry
        }

        // Step 2: Wait before clicking
        await this.sleep(DELAY_AFTER_INPUT_JS);

        // Step 3: Click search button
        const clickSuccess = await this.clickSearchButton();
        if (!clickSuccess) {
          console.error('[WebView Automation] Failed to click search button');
          continue; // Retry
        }

        // Step 4: Wait for results
        await this.sleep(DELAY_AFTER_CLICK_JS);
        const result = await this.extractResults(code);

        if (result.success) {
          console.log(`[WebView Automation] Successfully fetched state for ${code}: ${result.state}`);
          return result;
        }

      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        console.error(`[WebView Automation] Error on attempt ${attempt + 1}:`, errorMessage);
      }
    }

    // All retries failed
    return {
      success: false,
      code: code,
      error: `Failed after ${MAX_RETRIES + 1} attempts`
    };
  }

  /**
   * Input code into search field
   */
  private async inputCode(code: string): Promise<boolean> {
    try {
      const webContents = this.getWebContents();

      // Try different selectors for input field
      const result = await webContents.executeJavaScript(`
        (function() {
          var selectors = [
            'input[type="text"]',
            'input[name*="codice"]',
            'input[id*="codice"]',
            'input[placeholder*="codice"]'
          ];

          for (var i = 0; i < selectors.length; i++) {
            var input = document.querySelector(selectors[i]);
            if (input) {
              // Clear existing value
              input.value = '';
              // Type the code
              input.value = '${code.replace(/'/g, "\\'")}';
              // Trigger input events
              input.dispatchEvent(new Event('input', { bubbles: true }));
              input.dispatchEvent(new Event('change', { bubbles: true }));

              console.log('[WebView Automation] Code input successful:', '${code}');
              return true;
            }
          }

          console.error('[WebView Automation] Failed to find input field');
          return false;
        })();
      `);

      return result;

    } catch (error) {
      console.error('[WebView Automation] Error in inputCode:', error);
      return false;
    }
  }

  /**
   * Click search button
   */
  private async clickSearchButton(): Promise<boolean> {
    try {
      const webContents = this.getWebContents();

      // Find search button/link and extract href or prepare for click
      const result = await webContents.executeJavaScript(`
        (function() {
          var elements = document.querySelectorAll('button, input[type="submit"], .btn, a');

          for (var i = 0; i < elements.length; i++) {
            var el = elements[i];
            var text = el.textContent || el.value || '';

            if (text.toLowerCase().includes('cerca') ||
                text.toLowerCase().includes('search') ||
                text.toLowerCase().includes('invia') ||
                text.toLowerCase().includes('submit')) {

              // If it's a link, return the href for programmatic navigation
              if (el.tagName.toLowerCase() === 'a' && el.href) {
                console.log('[WebView Automation] Found search link:', el.href);
                return { type: 'link', href: el.href };
              }

              // If it's a button/submit, click it directly (form submission)
              console.log('[WebView Automation] Clicking search button');
              el.click();
              return { type: 'button', clicked: true };
            }
          }

          console.error('[WebView Automation] Search button/link not found');
          return null;
        })();
      `);

      if (!result) {
        console.error('[WebView Automation] Search button/link not found');
        return false;
      }

      // Handle link navigation programmatically to avoid new windows
      if (result.type === 'link' && result.href) {
        console.log('[WebView Automation] Navigating to search link:', result.href);
        const navigationPromise = this.waitForEvent('did-navigate');
        await webContents.loadURL(result.href);
        await navigationPromise;
        await this.waitForEvent('did-stop-loading');

        // Reinstall interceptor after navigation
        await this.injectLinkInterceptor();
        return true;
      }

      // Button was clicked in evaluate()
      if (result.type === 'button' && result.clicked) {
        console.log('[WebView Automation] Search button clicked');
        return true;
      }

      return false;

    } catch (error) {
      console.error('[WebView Automation] Error in clickSearchButton:', error);
      return false;
    }
  }

  /**
   * Extract results from page
   */
  private async extractResults(code: string): Promise<FetchResult> {
    try {
      const webContents = this.getWebContents();

      // Wait for results table (with timeout)
      const selectorExists = await this.waitForSelector('#risultatiConsultazionePratica tbody tr', 5000);

      if (!selectorExists) {
        return {
          success: false,
          code: code,
          error: 'Results table not found'
        };
      }

      // Extract all cells using JavaScript
      const cells = await webContents.executeJavaScript(`
        (function() {
          var row = document.querySelector('#risultatiConsultazionePratica tbody tr');
          if (!row) return null;

          var tds = row.querySelectorAll('td');
          var texts = [];
          tds.forEach(function(td) {
            texts.push(td.innerText.trim());
          });

          return texts;
        })();
      `);

      if (!cells || cells.length === 0) {
        return {
          success: false,
          code: code,
          error: 'No results found'
        };
      }

      // Extract state (index 2 as per original Python code)
      const state = cells[2] || 'SCONOSCIUTO';

      console.log(`[WebView Automation] Results extracted for ${code}: ${state}`);

      return {
        success: true,
        code: code,
        state: state,
        cells: cells
      };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('[WebView Automation] Error extracting results:', errorMessage);
      return {
        success: false,
        code: code,
        error: errorMessage
      };
    }
  }

  /**
   * Wait for a selector to appear on the page (polling-based)
   */
  private async waitForSelector(selector: string, timeout: number): Promise<boolean> {
    const webContents = this.getWebContents();
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      try {
        const exists = await webContents.executeJavaScript(`
          !!document.querySelector('${selector.replace(/'/g, "\\'")}');
        `);

        if (exists) {
          return true;
        }

        // Wait before next check
        await this.sleep(FETCH_CHECK_INTERVAL_MS); // 50ms

      } catch (error) {
        // Page might be navigating, continue polling
        await this.sleep(FETCH_CHECK_INTERVAL_MS);
      }
    }

    console.error(`[WebView Automation] Selector ${selector} not found after ${timeout}ms`);
    return false;
  }

  /**
   * Wait for a WebContents event
   */
  private waitForEvent(eventName: string, timeout: number = 30000): Promise<void> {
    const webContents = this.getWebContents();

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Event ${eventName} timeout after ${timeout}ms`));
      }, timeout);

      // Use any to allow dynamic event names
      (webContents as any).once(eventName, () => {
        clearTimeout(timer);
        resolve();
      });
    });
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Inject link click interceptor to prevent new windows
   */
  private async injectLinkInterceptor(): Promise<void> {
    try {
      const webContents = this.getWebContents();

      await webContents.executeJavaScript(`
        (function() {
          console.log('[WebView Automation Interceptor] Installing...');

          // CRITICAL: Override window.open() globally
          window.open = function(url, name, features) {
            console.log('[WebView Automation Interceptor] Blocked window.open():', url);
            if (url) {
              window.location.href = url;
            }
            return null;
          };

          // Remove existing interceptors if present
          if (window.__webview_automation_interceptor) {
            document.removeEventListener('click', window.__webview_automation_interceptor, true);
            document.removeEventListener('mousedown', window.__webview_automation_interceptor, true);
            document.removeEventListener('auxclick', window.__webview_automation_interceptor, true);
          }

          // Create new interceptor that handles ALL clicks on links
          var interceptor = function(e) {
            var link = e.target.closest('a');

            if (link && link.href) {
              var hasModifier = e.ctrlKey || e.shiftKey || e.metaKey || e.altKey;
              var isMiddleClick = e.button === 1;
              var opensNewWindow = link.target === '_blank' ||
                                  link.target === '_new' ||
                                  link.rel.includes('noopener') ||
                                  link.rel.includes('noreferrer');

              // Intercept if any condition that would open new window is true
              if (opensNewWindow || hasModifier || isMiddleClick) {
                console.log('[WebView Automation Interceptor] Blocked link click:', link.href);
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
          window.__webview_automation_interceptor = interceptor;

          // Add listeners for all types of clicks in capture phase
          document.addEventListener('click', interceptor, true);
          document.addEventListener('mousedown', interceptor, true);
          document.addEventListener('auxclick', interceptor, true); // Middle click

          console.log('[WebView Automation Interceptor] window.open() override + click interceptor installed');
        })();
      `);

      console.log('[WebView Automation] Link interceptor injected successfully');

    } catch (error) {
      console.error('[WebView Automation] Error injecting link interceptor:', error);
    }
  }

  /**
   * Parse cells into ProcessingResult
   */
  parseCellsToResult(code: string, cells: string[]): ProcessingResult {
    // Map cells to result structure
    // Based on Python worker.py logic - CORRECT indices!
    return {
      'Input Code': code,
      'Taric': cells[0] || '',                         // Index 0 - Codice TARIC
      'Stato': cells[2] || '',                         // Index 2 - Stato
      'Protocollo ingresso': cells[3] || '',          // Index 3 - Protocollo ingresso
      'Inserita il': cells[4] || '',                   // Index 4 - Inserita il
      'Protocollo uscita': cells[5] || '',            // Index 5 - Protocollo uscita (FIXED!)
      'Provvedimento': cells[6] || '',                 // Index 6 - Provvedimento (FIXED!)
      'Data Provvedimento': cells[7] || '',            // Index 7 - Data provvedimento (FIXED!)
      'Codice richiesta (risultato)': cells[8] || code, // Index 8 - Codice richiesta (FIXED! Fallback to input code)
      'Tipo pratica': cells[9] || '',                  // Index 9 - Tipo pratica
      'Note Usmaf': cells[10] || '',                   // Index 10 - Note Usmaf (FIXED!)
      'Invio SUD': cells[11] || ''                     // Index 11 - Invio SUD
    };
  }

  /**
   * Reload page to clear state
   */
  async reloadPage(): Promise<void> {
    try {
      const webContents = this.getWebContents();

      console.log('[WebView Automation] Reloading page...');
      await webContents.loadURL(URL_NSIS);
      await this.waitForEvent('did-stop-loading');

      // Reinstall interceptor after reload
      await this.injectLinkInterceptor();

    } catch (error) {
      console.error('[WebView Automation] Error reloading page:', error);
    }
  }

  /**
   * Cleanup
   * NOTE: Does NOT reload page - keeps user on current page (results page)
   */
  async cleanup(): Promise<void> {
    try {
      console.log('[WebView Automation] Cleaning up...');

      // Don't reload - let user stay on current page with results
      // No need to go back to homepage after processing

      this.isInitialized = false;
      console.log('[WebView Automation] Cleanup complete - staying on current page');

    } catch (error) {
      console.error('[WebView Automation] Error during cleanup:', error);
    }
  }

  /**
   * Check if initialized
   */
  isReady(): boolean {
    return this.isInitialized && this.webContents !== null;
  }
}

// Export singleton instance
export const webViewAutomation = new WebViewAutomation();
