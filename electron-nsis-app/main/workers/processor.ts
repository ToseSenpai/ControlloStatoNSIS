/**
 * Processing orchestrator for batch code checking
 */

import { BrowserWindow } from 'electron';
import { webViewAutomation } from '../automation/webview-automation';
import { ProcessingResult } from '../../shared/types/excel-types';

export interface BadgeStats {
  annullate: number;
  aperte: number;
  chiuse: number;
  inLavorazione: number;
  inviate: number;
  eccezioni: number;
}

export class ProcessingOrchestrator {
  private isProcessing: boolean = false;
  private shouldStop: boolean = false;
  private mainWindow: BrowserWindow | null = null;
  private webViewContentsId: number | null = null;
  private results: ProcessingResult[] = [];
  private badges: BadgeStats = {
    annullate: 0,
    aperte: 0,
    chiuse: 0,
    inLavorazione: 0,
    inviate: 0,
    eccezioni: 0
  };

  /**
   * Set main window for IPC events
   */
  setMainWindow(window: BrowserWindow): void {
    this.mainWindow = window;
  }

  /**
   * Set webview webContents ID for automation
   */
  setWebViewContentsId(webContentsId: number): void {
    console.log('[Processor] Set webview webContents ID:', webContentsId);
    this.webViewContentsId = webContentsId;
  }

  /**
   * Start processing codes
   */
  async startProcessing(codes: string[]): Promise<ProcessingResult[]> {
    if (this.isProcessing) {
      console.warn('[Processor] Already processing');
      return [];
    }

    console.log(`[Processor] Starting processing for ${codes.length} codes`);
    this.isProcessing = true;
    this.shouldStop = false;
    this.results = [];
    this.resetBadges();

    try {
      // Check if webview webContents ID is set
      if (!this.webViewContentsId) {
        throw new Error('WebView not registered. Please navigate to a page first.');
      }

      // Initialize WebView automation with the visible webview's webContents ID
      await webViewAutomation.initialize(this.webViewContentsId);

      // Send initial progress
      this.sendProgress(0, codes.length);
      this.sendStatus('Inizializzazione completata');
      this.sendLog('WebView inizializzata, avvio elaborazione...');

      // Process each code
      for (let i = 0; i < codes.length; i++) {
        // Check if stop was requested
        if (this.shouldStop) {
          this.sendLog('Elaborazione interrotta dall\'utente');
          break;
        }

        const code = codes[i];
        this.sendLog(`Elaborazione codice ${i + 1}/${codes.length}: ${code}`);
        this.sendStatus(`Elaborazione codice: ${code}`);

        try {
          // Fetch state for code
          const fetchResult = await webViewAutomation.fetchStateForCode(code);

          if (fetchResult.success && fetchResult.cells) {
            // Parse result
            const result = webViewAutomation.parseCellsToResult(code, fetchResult.cells);
            this.results.push(result);

            // Update badges
            this.updateBadges(result.Stato);

            // Log success
            this.sendLog(`✓ ${code}: ${result.Stato}`);
          } else {
            // Log failure
            this.sendLog(`✗ ${code}: ${fetchResult.error || 'Errore sconosciuto'}`);

            // Create error result with all 11 columns
            const errorResult: ProcessingResult = {
              'Input Code': code,
              'Taric': '',
              'Stato': 'ERRORE',
              'Protocollo ingresso': '',
              'Inserita il': '',
              'Protocollo uscita': '',
              'Provvedimento': '',
              'Data Provvedimento': '',
              'Codice richiesta (risultato)': '',
              'Tipo pratica': '',
              'Note Usmaf': fetchResult.error || 'Errore durante elaborazione',
              'Invio SUD': ''
            };
            this.results.push(errorResult);
            this.badges.eccezioni++;
          }

        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Errore sconosciuto';
          this.sendLog(`✗ ${code}: ${errorMessage}`);

          // Create error result with all 11 columns
          const errorResult: ProcessingResult = {
            'Input Code': code,
            'Taric': '',
            'Stato': 'ERRORE',
            'Protocollo ingresso': '',
            'Inserita il': '',
            'Protocollo uscita': '',
            'Provvedimento': '',
            'Data Provvedimento': '',
            'Codice richiesta (risultato)': '',
            'Tipo pratica': '',
            'Note Usmaf': errorMessage,
            'Invio SUD': ''
          };
          this.results.push(errorResult);
          this.badges.eccezioni++;
        }

        // Update progress
        this.sendProgress(i + 1, codes.length);
        this.sendBadgeUpdate();

        // Small delay between requests
        if (i < codes.length - 1 && !this.shouldStop) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }

      // Complete processing
      if (!this.shouldStop) {
        this.sendLog(`Elaborazione completata: ${this.results.length}/${codes.length} codici processati`);
        this.sendStatus('Elaborazione completata');
        this.sendProcessingComplete();

        // Show custom completion dialog
        const message = `Processati ${this.results.length} codici su ${codes.length} totali.\n\nI risultati sono stati salvati nel file Excel.`;
        this.sendCompletionDialog(message);
      }

      return this.results;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Errore sconosciuto';
      console.error('[Processor] Processing error:', error);
      this.sendLog(`Errore durante l'elaborazione: ${errorMessage}`);
      this.sendStatus('Errore');
      throw error;

    } finally {
      // Cleanup
      await webViewAutomation.cleanup();
      this.isProcessing = false;
      console.log('[Processor] Processing finished');
    }
  }

  /**
   * Stop processing
   */
  stopProcessing(): void {
    if (this.isProcessing) {
      console.log('[Processor] Stop requested');
      this.shouldStop = true;
      this.sendLog('Richiesta interruzione elaborazione...');
    }
  }

  /**
   * Update badge statistics based on state
   */
  private updateBadges(stato: string): void {
    const statoLower = stato.toLowerCase();

    if (statoLower.includes('annullat')) {
      this.badges.annullate++;
    } else if (statoLower.includes('apert')) {
      this.badges.aperte++;
    } else if (statoLower.includes('chius')) {
      this.badges.chiuse++;
    } else if (statoLower.includes('lavorazione') || statoLower.includes('istruttoria')) {
      this.badges.inLavorazione++;
    } else if (statoLower.includes('inviat')) {
      this.badges.inviate++;
    } else {
      // Unknown state counts as exception
      this.badges.eccezioni++;
    }
  }

  /**
   * Reset badge statistics
   */
  private resetBadges(): void {
    this.badges = {
      annullate: 0,
      aperte: 0,
      chiuse: 0,
      inLavorazione: 0,
      inviate: 0,
      eccezioni: 0
    };
    this.sendBadgeUpdate();
  }

  /**
   * Send progress update to renderer
   */
  private sendProgress(current: number, total: number): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('progress-update', {
        current,
        total
      });
    }
  }

  /**
   * Send status update to renderer
   */
  private sendStatus(status: string): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('status-update', status);
    }
  }

  /**
   * Send badge update to renderer
   */
  private sendBadgeUpdate(): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('badge-update', this.badges);
    }
  }

  /**
   * Send log message to renderer
   */
  private sendLog(message: string): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('log-message', message);
    }
  }

  /**
   * Send processing complete event to renderer
   */
  private sendProcessingComplete(): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('processing-complete');
    }
  }

  /**
   * Send completion dialog event to renderer
   */
  private sendCompletionDialog(message: string): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.webContents.send('show-completion-dialog', message);
    }
  }

  /**
   * Get current results
   */
  getResults(): ProcessingResult[] {
    return [...this.results];
  }

  /**
   * Check if currently processing
   */
  isCurrentlyProcessing(): boolean {
    return this.isProcessing;
  }
}

// Export singleton instance
export const processingOrchestrator = new ProcessingOrchestrator();
