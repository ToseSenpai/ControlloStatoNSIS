/**
 * Application configuration constants
 */
export declare const URL_NSIS = "https://www.impresa.gov.it/intro/info/news.html";
export declare const MAX_RETRIES = 2;
export declare const FETCH_TIMEOUT_MS = 5000;
export declare const FETCH_CHECK_INTERVAL_MS = 50;
export declare const STATO_SELECTOR = "#risultatiConsultazionePratica tbody tr td:nth-child(3)";
export declare const ALL_CELLS_JS = "(function() {\n    var row = document.querySelector('#risultatiConsultazionePratica tbody tr');\n    if(!row) return null;\n    var tds = row.querySelectorAll('td');\n    var texts = [];\n    tds.forEach(function(td){ texts.push(td.innerText.trim()); });\n    return texts;\n})();";
export declare const DELAY_AFTER_INPUT_JS = 50;
export declare const DELAY_AFTER_CLICK_JS = 500;
export declare const DELAY_BETWEEN_RETRIES = 500;
export declare const MAX_NULL_CHECKS = 3;
export declare const COL_RICERCA = "ricerca";
export declare const COL_STATO = "stato";
export declare const COL_PROTOCOLLO = "protocollo uscita";
export declare const COL_PROVVEDIMENTO = "provvedimento";
export declare const COL_DATA_PROVV = "data provvedimento";
export declare const COL_CODICE_RIS = "codice richiesta (risultato)";
export declare const COL_NOTE = "note usmaf";
export declare const DEFAULT_IDX_STATO = 3;
export declare const DEFAULT_IDX_PROTOCOLLO = 4;
export declare const DEFAULT_IDX_PROVVEDIMENTO = 5;
export declare const DEFAULT_IDX_DATA_PROVV = 6;
export declare const DEFAULT_IDX_CODICE_RIS = 7;
export declare const DEFAULT_IDX_NOTE = 8;
export declare const COLOR_ANNULATA = "#F59E0B";
export declare const COLOR_APERTA = "#3B82F6";
export declare const COLOR_CHIUSA = "#10B981";
export declare const COLOR_LAVORAZIONE = "#F97316";
export declare const COLOR_INVIATA = "#8B5CF6";
export declare const COLOR_ECCEZIONI = "#EF4444";
//# sourceMappingURL=config.d.ts.map