/**
 * Playwright-based web automation for NSIS state checking
 */

import { chromium, Browser, Page, BrowserContext } from 'playwright';
import {
  URL_NSIS, STATO_SELECTOR, ALL_CELLS_JS, MAX_RETRIES,
  DELAY_AFTER_INPUT_JS, DELAY_AFTER_CLICK_JS, DELAY_BETWEEN_RETRIES
} from '../../shared/constants/config';
import { ProcessingResult } from '../../shared/types/excel-types';

export interface FetchResult {
  success: boolean;
  code: string;
  state?: string;
  cells?: string[];
  error?: string;
}

export class PlaywrightAutomation {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private page: Page | null = null;
  private isInitialized: boolean = false;

  /**
   * Initialize Playwright browser
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      console.log('[Playwright] Already initialized');
      return;
    }

    try {
      console.log('[Playwright] Initializing browser...');

      // Launch browser in headless mode for production
      this.browser = await chromium.launch({
        headless: false, // Set to true for production
        args: [
          '--disable-blink-features=AutomationControlled',
          '--no-sandbox',
          '--disable-setuid-sandbox'
        ]
      });

      // Create context with viewport
      this.context = await this.browser.newContext({
        viewport: { width: 1280, height: 720 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      });

      // Create page
      this.page = await this.context.newPage();

      // Navigate to NSIS URL
      console.log(`[Playwright] Navigating to ${URL_NSIS}`);
      await this.page.goto(URL_NSIS, { waitUntil: 'networkidle', timeout: 30000 });

      this.isInitialized = true;
      console.log('[Playwright] Initialization complete');

    } catch (error) {
      console.error('[Playwright] Initialization error:', error);
      await this.cleanup();
      throw error;
    }
  }

  /**
   * Fetch state for a specific code
   */
  async fetchStateForCode(code: string): Promise<FetchResult> {
    if (!this.isInitialized || !this.page) {
      return {
        success: false,
        code: code,
        error: 'Browser not initialized'
      };
    }

    console.log(`[Playwright] Fetching state for code: ${code}`);

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        if (attempt > 0) {
          console.log(`[Playwright] Retry attempt ${attempt} for code: ${code}`);
          await this.page.waitForTimeout(DELAY_BETWEEN_RETRIES);
        }

        // Step 1: Input code
        const inputSuccess = await this.inputCode(code);
        if (!inputSuccess) {
          continue; // Retry
        }

        // Step 2: Click search button
        await this.page.waitForTimeout(DELAY_AFTER_INPUT_JS);
        const clickSuccess = await this.clickSearchButton();
        if (!clickSuccess) {
          continue; // Retry
        }

        // Step 3: Wait for results
        await this.page.waitForTimeout(DELAY_AFTER_CLICK_JS);
        const result = await this.extractResults(code);

        if (result.success) {
          return result;
        }

      } catch (error) {
        console.error(`[Playwright] Error on attempt ${attempt + 1}:`, error);
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
    if (!this.page) return false;

    try {
      // Try different selectors for input field
      const selectors = [
        'input[type="text"]',
        'input[name*="codice"]',
        'input[id*="codice"]',
        'input[placeholder*="codice"]'
      ];

      for (const selector of selectors) {
        try {
          const input = await this.page.$(selector);
          if (input) {
            // Clear existing value
            await input.fill('');
            // Type the code
            await input.fill(code);
            // Trigger input events
            await input.dispatchEvent('input');
            await input.dispatchEvent('change');

            console.log(`[Playwright] Code input successful: ${code}`);
            return true;
          }
        } catch (e) {
          // Try next selector
          continue;
        }
      }

      console.error('[Playwright] Failed to find input field');
      return false;

    } catch (error) {
      console.error('[Playwright] Error in inputCode:', error);
      return false;
    }
  }

  /**
   * Click search button
   */
  private async clickSearchButton(): Promise<boolean> {
    if (!this.page) return false;

    try {
      // Find and click search button
      // @ts-ignore - Code runs in browser context with DOM
      const clicked = await this.page.evaluate(() => {
        // @ts-ignore
        const buttons = document.querySelectorAll('button, input[type="submit"], .btn');
        for (let i = 0; i < buttons.length; i++) {
          const btn = buttons[i] as any;
          const text = btn.textContent || btn.value || '';
          if (text.toLowerCase().includes('cerca') ||
              text.toLowerCase().includes('search') ||
              text.toLowerCase().includes('invia') ||
              text.toLowerCase().includes('submit')) {
            btn.click();
            return true;
          }
        }
        return false;
      });

      if (clicked) {
        console.log('[Playwright] Search button clicked');
        return true;
      } else {
        console.error('[Playwright] Search button not found');
        return false;
      }

    } catch (error) {
      console.error('[Playwright] Error in clickSearchButton:', error);
      return false;
    }
  }

  /**
   * Extract results from page
   */
  private async extractResults(code: string): Promise<FetchResult> {
    if (!this.page) {
      return {
        success: false,
        code: code,
        error: 'Page not available'
      };
    }

    try {
      // Wait for results table (with timeout)
      await this.page.waitForSelector(STATO_SELECTOR, { timeout: 5000 });

      // Extract all cells using the JavaScript from config
      // @ts-ignore - Code runs in browser context with DOM
      const cells = await this.page.evaluate(() => {
        // @ts-ignore
        const row = document.querySelector('#risultatiConsultazionePratica tbody tr');
        if (!row) return null;
        const tds = row.querySelectorAll('td');
        const texts: string[] = [];
        tds.forEach((td: any) => texts.push(td.innerText.trim()));
        return texts;
      });

      if (!cells || cells.length === 0) {
        return {
          success: false,
          code: code,
          error: 'No results found'
        };
      }

      // Extract state (index 2 as per original Python code)
      const state = cells[2] || 'SCONOSCIUTO';

      console.log(`[Playwright] Results extracted for ${code}: ${state}`);

      return {
        success: true,
        code: code,
        state: state,
        cells: cells
      };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('[Playwright] Error extracting results:', errorMessage);
      return {
        success: false,
        code: code,
        error: errorMessage
      };
    }
  }

  /**
   * Parse cells into ProcessingResult
   */
  parseCellsToResult(code: string, cells: string[]): ProcessingResult {
    // Map cells to result structure
    // Based on original Python logic and DEFAULT_IDX_* constants
    return {
      'Input Code': code,
      'Stato': cells[2] || '',                         // DEFAULT_IDX_STATO = 3 (0-indexed = 2)
      'Protocollo uscita': cells[3] || '',            // DEFAULT_IDX_PROTOCOLLO = 4 (0-indexed = 3)
      'Provvedimento': cells[4] || '',                 // DEFAULT_IDX_PROVVEDIMENTO = 5 (0-indexed = 4)
      'Data Provvedimento': cells[5] || '',            // DEFAULT_IDX_DATA_PROVV = 6 (0-indexed = 5)
      'Codice richiesta (risultato)': cells[6] || '', // DEFAULT_IDX_CODICE_RIS = 7 (0-indexed = 6)
      'Note Usmaf': cells[7] || ''                     // DEFAULT_IDX_NOTE = 8 (0-indexed = 7)
    };
  }

  /**
   * Reload page to clear state
   */
  async reloadPage(): Promise<void> {
    if (!this.page) return;

    try {
      console.log('[Playwright] Reloading page...');
      await this.page.reload({ waitUntil: 'networkidle' });
    } catch (error) {
      console.error('[Playwright] Error reloading page:', error);
    }
  }

  /**
   * Cleanup and close browser
   */
  async cleanup(): Promise<void> {
    try {
      console.log('[Playwright] Cleaning up...');

      if (this.page) {
        await this.page.close();
        this.page = null;
      }

      if (this.context) {
        await this.context.close();
        this.context = null;
      }

      if (this.browser) {
        await this.browser.close();
        this.browser = null;
      }

      this.isInitialized = false;
      console.log('[Playwright] Cleanup complete');

    } catch (error) {
      console.error('[Playwright] Error during cleanup:', error);
    }
  }

  /**
   * Check if initialized
   */
  isReady(): boolean {
    return this.isInitialized && this.page !== null;
  }
}

// Export singleton instance
export const playwrightAutomation = new PlaywrightAutomation();
