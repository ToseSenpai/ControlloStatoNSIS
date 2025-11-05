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
  'Taric': string;
  'Stato': string;
  'Protocollo ingresso': string;
  'Inserita il': string;
  'Protocollo uscita': string;
  'Provvedimento': string;
  'Data Provvedimento': string;
  'Codice richiesta (risultato)': string;
  'Tipo pratica': string;
  'Note Usmaf': string;
  'Invio SUD': string;
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
