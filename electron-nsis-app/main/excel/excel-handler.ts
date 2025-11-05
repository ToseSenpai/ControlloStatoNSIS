/**
 * Excel file handling module using ExcelJS
 */

import ExcelJS from 'exceljs';
import * as path from 'path';
import * as fs from 'fs';
import {
  COL_RICERCA, COL_TARIC, COL_STATO, COL_PROTOCOLLO_INGRESSO, COL_INSERITA_IL,
  COL_PROTOCOLLO, COL_PROVVEDIMENTO, COL_DATA_PROVV, COL_CODICE_RIS,
  COL_TIPO_PRATICA, COL_NOTE, COL_INVIO_SUD
} from '../../shared/constants/config';
import { LoadExcelResult, SaveExcelResult, ProcessingResult } from '../../shared/types/excel-types';

export class ExcelHandler {
  private currentFilePath: string | null = null;
  private codes: string[] = [];

  /**
   * Load Excel file and extract codes from the search column
   */
  async loadExcelFile(filePath: string): Promise<LoadExcelResult> {
    console.log(`[ExcelHandler] Caricamento file: ${filePath}`);
    this.currentFilePath = filePath;

    try {
      // Check if file exists
      if (!fs.existsSync(filePath)) {
        return {
          success: false,
          codes: [],
          error: 'File non trovato'
        };
      }

      // Load workbook
      const workbook = new ExcelJS.Workbook();
      await workbook.xlsx.readFile(filePath);

      if (workbook.worksheets.length === 0) {
        return {
          success: false,
          codes: [],
          error: 'File Excel non contiene fogli di lavoro'
        };
      }

      const worksheet = workbook.worksheets[0];
      console.log(`[ExcelHandler] Caricato foglio: ${worksheet.name}`);

      // Find search column
      const searchColIdx = this.findSearchColumn(worksheet);
      if (searchColIdx === null) {
        return {
          success: false,
          codes: [],
          error: `Colonna di ricerca '${COL_RICERCA}' non trovata nel file`
        };
      }

      // Extract codes
      const codes = this.extractCodesFromColumn(worksheet, searchColIdx);
      this.codes = codes;

      console.log(`[ExcelHandler] Estratti ${codes.length} codici dal file Excel`);

      return {
        success: true,
        codes: codes,
        error: undefined
      };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Errore sconosciuto';
      console.error('[ExcelHandler] Errore caricamento file:', error);
      return {
        success: false,
        codes: [],
        error: `Errore durante il caricamento: ${errorMessage}`
      };
    }
  }

  /**
   * Find the search column index in the Excel sheet
   */
  private findSearchColumn(worksheet: ExcelJS.Worksheet): number | null {
    const headerRow = worksheet.getRow(1);
    let searchColIdx: number | null = null;

    headerRow.eachCell((cell, colNumber) => {
      if (cell.value && typeof cell.value === 'string') {
        if (cell.value.trim().toLowerCase() === COL_RICERCA.toLowerCase()) {
          searchColIdx = colNumber;
        }
      }
    });

    return searchColIdx;
  }

  /**
   * Extract codes from the specified column
   */
  private extractCodesFromColumn(worksheet: ExcelJS.Worksheet, columnIdx: number): string[] {
    const codes: string[] = [];

    // Start from row 2 (skip header)
    for (let rowNumber = 2; rowNumber <= worksheet.rowCount; rowNumber++) {
      const row = worksheet.getRow(rowNumber);
      const cell = row.getCell(columnIdx);

      if (cell.value) {
        const code = String(cell.value).trim();
        if (code) {
          codes.push(code);
        }
      }
    }

    return codes;
  }

  /**
   * Save results to Excel file
   */
  async saveResultsToExcel(
    results: ProcessingResult[],
    originalFilePath: string
  ): Promise<SaveExcelResult> {
    console.log(`[ExcelHandler] Tentativo salvataggio ${results.length} risultati su ${path.basename(originalFilePath)}`);

    try {
      let workbook: ExcelJS.Workbook;
      let outputFilePath = originalFilePath;
      let isReadOnly = false;

      // Try to load workbook for writing
      try {
        workbook = new ExcelJS.Workbook();
        await workbook.xlsx.readFile(originalFilePath);
        console.log('[ExcelHandler] Workbook caricato per scrittura');
      } catch (error) {
        console.warn('[ExcelHandler] Errore caricamento per scrittura, tento con backup:', error);
        isReadOnly = true;

        const backupPath = await this.createBackupFile(originalFilePath);
        if (!backupPath) {
          return {
            success: false,
            error: 'Impossibile creare copia del file'
          };
        }

        outputFilePath = backupPath;
        workbook = new ExcelJS.Workbook();
        await workbook.xlsx.readFile(backupPath);
      }

      if (workbook.worksheets.length === 0) {
        return {
          success: false,
          error: 'Workbook non valido o senza fogli'
        };
      }

      const worksheet = workbook.worksheets[0];

      // Write results to sheet
      const success = await this.writeResultsToSheet(worksheet, results);

      if (success) {
        await workbook.xlsx.writeFile(outputFilePath);
        console.log(`[ExcelHandler] Risultati salvati con successo in: ${outputFilePath}`);
        return {
          success: true,
          outputPath: outputFilePath
        };
      } else {
        return {
          success: false,
          error: 'Errore durante la scrittura dei risultati'
        };
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Errore sconosciuto';
      console.error('[ExcelHandler] Errore durante il salvataggio:', error);
      return {
        success: false,
        error: `Errore durante il salvataggio: ${errorMessage}`
      };
    }
  }

  /**
   * Create a backup file when original is read-only
   */
  private async createBackupFile(originalFilePath: string): Promise<string | null> {
    try {
      const workbook = new ExcelJS.Workbook();
      await workbook.xlsx.readFile(originalFilePath);

      // Create backup filename
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const parsed = path.parse(originalFilePath);
      const backupPath = path.join(parsed.dir, `${parsed.name}_output_${timestamp}${parsed.ext}`);

      // Save backup
      await workbook.xlsx.writeFile(backupPath);
      console.log(`[ExcelHandler] Backup creato: ${backupPath}`);

      return backupPath;
    } catch (error) {
      console.error('[ExcelHandler] Errore creazione backup:', error);
      return null;
    }
  }

  /**
   * Write results to the Excel sheet
   */
  private async writeResultsToSheet(
    worksheet: ExcelJS.Worksheet,
    results: ProcessingResult[]
  ): Promise<boolean> {
    try {
      // Column mapping - ALL 11 columns!
      const colNameMap: Record<string, string> = {
        'Taric': COL_TARIC,
        'Stato': COL_STATO,
        'Protocollo ingresso': COL_PROTOCOLLO_INGRESSO,
        'Inserita il': COL_INSERITA_IL,
        'Protocollo uscita': COL_PROTOCOLLO,
        'Provvedimento': COL_PROVVEDIMENTO,
        'Data Provvedimento': COL_DATA_PROVV,
        'Codice richiesta (risultato)': COL_CODICE_RIS,
        'Tipo pratica': COL_TIPO_PRATICA,
        'Note Usmaf': COL_NOTE,
        'Invio SUD': COL_INVIO_SUD
      };

      const outputConfigKeys = [
        'Taric', 'Stato', 'Protocollo ingresso', 'Inserita il',
        'Protocollo uscita', 'Provvedimento', 'Data Provvedimento',
        'Codice richiesta (risultato)', 'Tipo pratica', 'Note Usmaf', 'Invio SUD'
      ];

      // Get existing headers
      const headerRow = worksheet.getRow(1);
      const existingHeaders: Record<string, number> = {};

      headerRow.eachCell((cell, colNumber) => {
        if (cell.value && typeof cell.value === 'string') {
          existingHeaders[cell.value.trim().toLowerCase()] = colNumber;
        }
      });

      // Find search column
      const ricercaColIdx = existingHeaders[COL_RICERCA.toLowerCase()];
      if (!ricercaColIdx) {
        console.error(`[ExcelHandler] Colonna di ricerca '${COL_RICERCA}' non trovata`);
        return false;
      }

      // Determine next available column
      let nextAvailableColIdx = worksheet.columnCount + 1;

      // Map column indices
      const finalColIndices: Record<string, number> = {};

      // Find or create output columns
      for (const configKey of outputConfigKeys) {
        const excelHeaderName = colNameMap[configKey];
        const excelHeaderNameLower = excelHeaderName.toLowerCase();

        if (existingHeaders[excelHeaderNameLower]) {
          // Column exists
          finalColIndices[configKey] = existingHeaders[excelHeaderNameLower];
        } else {
          // Column missing, add it
          finalColIndices[configKey] = nextAvailableColIdx;

          // Add header
          const headerCell = worksheet.getRow(1).getCell(nextAvailableColIdx);
          headerCell.value = excelHeaderName;
          headerCell.font = { bold: true };

          nextAvailableColIdx++;
        }
      }

      // Write results
      for (const result of results) {
        const code = result['Input Code'];
        console.log(`[ExcelHandler] Processando risultato per codice: ${code}`);

        const rowIdx = this.findRowForCode(worksheet, ricercaColIdx, code);
        if (rowIdx === null) {
          console.warn(`[ExcelHandler] Riga non trovata per codice: ${code}`);
          continue;
        }

        const row = worksheet.getRow(rowIdx);

        // Write result data
        for (const configKey of outputConfigKeys) {
          if (finalColIndices[configKey]) {
            const colIdx = finalColIndices[configKey];
            const cell = row.getCell(colIdx);

            // Special handling for Note Usmaf column
            if (configKey === 'Note Usmaf') {
              const noteValue = result[configKey] || '';
              cell.value = noteValue.trim() ? noteValue : 'NOTA USMAF';
            } else {
              cell.value = result[configKey as keyof ProcessingResult] || '';
            }
          }
        }
      }

      return true;

    } catch (error) {
      console.error('[ExcelHandler] Errore scrittura risultati:', error);
      return false;
    }
  }

  /**
   * Find the row index for a specific code
   */
  private findRowForCode(
    worksheet: ExcelJS.Worksheet,
    searchColIdx: number,
    code: string
  ): number | null {
    console.log(`[ExcelHandler] Ricerca codice '${code}' nella colonna ${searchColIdx}`);

    for (let rowNumber = 2; rowNumber <= worksheet.rowCount; rowNumber++) {
      const row = worksheet.getRow(rowNumber);
      const cell = row.getCell(searchColIdx);

      if (cell.value) {
        const cellValueStr = String(cell.value).trim();
        if (cellValueStr === code.trim()) {
          console.log(`[ExcelHandler] Codice trovato nella riga ${rowNumber}`);
          return rowNumber;
        }
      }
    }

    console.warn(`[ExcelHandler] Codice '${code}' non trovato in nessuna riga`);
    return null;
  }

  /**
   * Get current file path
   */
  getCurrentFilePath(): string | null {
    return this.currentFilePath;
  }

  /**
   * Get loaded codes
   */
  getCodes(): string[] {
    return [...this.codes];
  }

  /**
   * Reset handler state
   */
  reset(): void {
    this.currentFilePath = null;
    this.codes = [];
  }
}

// Export singleton instance
export const excelHandler = new ExcelHandler();
