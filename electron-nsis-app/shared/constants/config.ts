/**
 * Application configuration constants
 */

// Web Operations
export const URL_NSIS = 'https://www.impresa.gov.it/intro/info/news.html';
export const MAX_RETRIES = 2;
export const FETCH_TIMEOUT_MS = 5000;
export const FETCH_CHECK_INTERVAL_MS = 50;
export const STATO_SELECTOR = "#risultatiConsultazionePratica tbody tr td:nth-child(3)";

export const ALL_CELLS_JS = `(function() {
    var row = document.querySelector('#risultatiConsultazionePratica tbody tr');
    if(!row) return null;
    var tds = row.querySelectorAll('td');
    var texts = [];
    tds.forEach(function(td){ texts.push(td.innerText.trim()); });
    return texts;
})();`;

// Delays and Fetch Controls (in milliseconds)
export const DELAY_AFTER_INPUT_JS = 50;
export const DELAY_AFTER_CLICK_JS = 500;
export const DELAY_BETWEEN_RETRIES = 500;
export const MAX_NULL_CHECKS = 3;

// Excel Column Names (case-insensitive)
export const COL_RICERCA = "ricerca";
export const COL_TARIC = "taric";
export const COL_STATO = "stato";
export const COL_PROTOCOLLO_INGRESSO = "protocollo ingresso";
export const COL_INSERITA_IL = "inserita il";
export const COL_PROTOCOLLO = "protocollo uscita";
export const COL_PROVVEDIMENTO = "provvedimento";
export const COL_DATA_PROVV = "data provvedimento";
export const COL_CODICE_RIS = "codice richiesta (risultato)";
export const COL_TIPO_PRATICA = "tipo pratica";
export const COL_NOTE = "note usmaf";
export const COL_INVIO_SUD = "invio sud";

// Default Column Indices (fallback)
export const DEFAULT_IDX_STATO = 3;
export const DEFAULT_IDX_PROTOCOLLO = 4;
export const DEFAULT_IDX_PROVVEDIMENTO = 5;
export const DEFAULT_IDX_DATA_PROVV = 6;
export const DEFAULT_IDX_CODICE_RIS = 7;
export const DEFAULT_IDX_NOTE = 8;

// Status Colors (for badges)
export const COLOR_ANNULATA = "#F59E0B";
export const COLOR_APERTA = "#3B82F6";
export const COLOR_CHIUSA = "#10B981";
export const COLOR_LAVORAZIONE = "#F97316";
export const COLOR_INVIATA = "#8B5CF6";
export const COLOR_ECCEZIONI = "#EF4444";
