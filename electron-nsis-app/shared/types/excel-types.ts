/**
 * TypeScript types for Excel data handling
 */

export interface ExcelData {
  codes: string[];
  columns: string[];
  filePath: string;
}

export interface ProcessingResult {
  'Input Code': string;
  'Stato': string;
  'Protocollo uscita': string;
  'Provvedimento': string;
  'Data Provvedimento': string;
  'Codice richiesta (risultato)': string;
  'Note Usmaf': string;
}

export interface LoadExcelResult {
  success: boolean;
  codes: string[];
  error?: string;
}

export interface SaveExcelResult {
  success: boolean;
  outputPath?: string;
  error?: string;
}
