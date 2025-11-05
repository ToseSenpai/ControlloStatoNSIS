"use strict";
/**
 * Application configuration constants
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.COLOR_ECCEZIONI = exports.COLOR_INVIATA = exports.COLOR_LAVORAZIONE = exports.COLOR_CHIUSA = exports.COLOR_APERTA = exports.COLOR_ANNULATA = exports.DEFAULT_IDX_NOTE = exports.DEFAULT_IDX_CODICE_RIS = exports.DEFAULT_IDX_DATA_PROVV = exports.DEFAULT_IDX_PROVVEDIMENTO = exports.DEFAULT_IDX_PROTOCOLLO = exports.DEFAULT_IDX_STATO = exports.COL_NOTE = exports.COL_CODICE_RIS = exports.COL_DATA_PROVV = exports.COL_PROVVEDIMENTO = exports.COL_PROTOCOLLO = exports.COL_STATO = exports.COL_RICERCA = exports.MAX_NULL_CHECKS = exports.DELAY_BETWEEN_RETRIES = exports.DELAY_AFTER_CLICK_JS = exports.DELAY_AFTER_INPUT_JS = exports.ALL_CELLS_JS = exports.STATO_SELECTOR = exports.FETCH_CHECK_INTERVAL_MS = exports.FETCH_TIMEOUT_MS = exports.MAX_RETRIES = exports.URL_NSIS = void 0;
// Web Operations
exports.URL_NSIS = 'https://www.impresa.gov.it/intro/info/news.html';
exports.MAX_RETRIES = 2;
exports.FETCH_TIMEOUT_MS = 5000;
exports.FETCH_CHECK_INTERVAL_MS = 50;
exports.STATO_SELECTOR = "#risultatiConsultazionePratica tbody tr td:nth-child(3)";
exports.ALL_CELLS_JS = `(function() {
    var row = document.querySelector('#risultatiConsultazionePratica tbody tr');
    if(!row) return null;
    var tds = row.querySelectorAll('td');
    var texts = [];
    tds.forEach(function(td){ texts.push(td.innerText.trim()); });
    return texts;
})();`;
// Delays and Fetch Controls (in milliseconds)
exports.DELAY_AFTER_INPUT_JS = 50;
exports.DELAY_AFTER_CLICK_JS = 500;
exports.DELAY_BETWEEN_RETRIES = 500;
exports.MAX_NULL_CHECKS = 3;
// Excel Column Names (case-insensitive)
exports.COL_RICERCA = "ricerca";
exports.COL_STATO = "stato";
exports.COL_PROTOCOLLO = "protocollo uscita";
exports.COL_PROVVEDIMENTO = "provvedimento";
exports.COL_DATA_PROVV = "data provvedimento";
exports.COL_CODICE_RIS = "codice richiesta (risultato)";
exports.COL_NOTE = "note usmaf";
// Default Column Indices (fallback)
exports.DEFAULT_IDX_STATO = 3;
exports.DEFAULT_IDX_PROTOCOLLO = 4;
exports.DEFAULT_IDX_PROVVEDIMENTO = 5;
exports.DEFAULT_IDX_DATA_PROVV = 6;
exports.DEFAULT_IDX_CODICE_RIS = 7;
exports.DEFAULT_IDX_NOTE = 8;
// Status Colors (for badges)
exports.COLOR_ANNULATA = "#F59E0B";
exports.COLOR_APERTA = "#3B82F6";
exports.COLOR_CHIUSA = "#10B981";
exports.COLOR_LAVORAZIONE = "#F97316";
exports.COLOR_INVIATA = "#8B5CF6";
exports.COLOR_ECCEZIONI = "#EF4444";
//# sourceMappingURL=config.js.map