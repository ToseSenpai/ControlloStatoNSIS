import { ipcMain, dialog } from 'electron';
import { excelHandler } from './excel/excel-handler';
import { ExcelData } from '../shared/types/excel-types';

// File selection handler
ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [
      { name: 'Excel Files', extensions: ['xlsx', 'xls'] }
    ]
  });

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// Excel loading handler
ipcMain.handle('load-excel', async (_event, filePath: string): Promise<ExcelData> => {
  console.log('[IPC] Loading Excel file:', filePath);

  try {
    const result = await excelHandler.loadExcelFile(filePath);

    if (!result.success) {
      throw new Error(result.error || 'Errore caricamento file');
    }

    // Extract column names (for now, just return basic info)
    const columns: string[] = [];

    return {
      codes: result.codes,
      columns: columns,
      filePath: filePath
    };
  } catch (error) {
    console.error('[IPC] Errore caricamento Excel:', error);
    throw error;
  }
});

// Excel saving handler
ipcMain.handle('save-excel', async (_event, filePath: string, data: any) => {
  console.log('[IPC] Saving Excel file:', filePath);

  try {
    const result = await excelHandler.saveResultsToExcel(data.results, filePath);

    if (!result.success) {
      throw new Error(result.error || 'Errore salvataggio file');
    }

    return {
      success: true,
      outputPath: result.outputPath
    };
  } catch (error) {
    console.error('[IPC] Errore salvataggio Excel:', error);
    throw error;
  }
});

// Import processing orchestrator
import { processingOrchestrator } from './workers/processor';
import { excelHandler as excelHandlerInstance } from './excel/excel-handler';

// Processing handlers
ipcMain.on('start-processing', async (_event, codes: string[]) => {
  console.log('[IPC] Start processing codes:', codes.length);

  try {
    // Start processing
    const results = await processingOrchestrator.startProcessing(codes);

    // Save results to Excel
    const currentFilePath = excelHandlerInstance.getCurrentFilePath();
    if (currentFilePath && results.length > 0) {
      console.log('[IPC] Saving results to Excel...');
      const saveResult = await excelHandlerInstance.saveResultsToExcel(results, currentFilePath);

      if (saveResult.success) {
        console.log('[IPC] Results saved successfully:', saveResult.outputPath);
      } else {
        console.error('[IPC] Failed to save results:', saveResult.error);
      }
    }
  } catch (error) {
    console.error('[IPC] Processing error:', error);
  }
});

ipcMain.on('stop-processing', () => {
  console.log('[IPC] Stop processing');
  processingOrchestrator.stopProcessing();
});

// WebView navigation handlers
import { browserViewManager } from './browser-view-manager';

ipcMain.on('webview-go-back', () => {
  console.log('[IPC] WebView go back');
  browserViewManager.goBack();
});

ipcMain.on('webview-go-forward', () => {
  console.log('[IPC] WebView go forward');
  browserViewManager.goForward();
});

ipcMain.on('webview-reload', () => {
  console.log('[IPC] WebView reload');
  browserViewManager.reload();
});

ipcMain.on('webview-go-home', () => {
  console.log('[IPC] WebView go home');
  browserViewManager.goHome();
});

// BrowserView bounds update handler
ipcMain.on('update-webview-bounds', (_event, bounds: { x: number; y: number; width: number; height: number }) => {
  console.log('[IPC] Update WebView bounds:', bounds);
  browserViewManager.updateBoundsFromRenderer(bounds);
});

export {};
