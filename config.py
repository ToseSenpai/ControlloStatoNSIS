# config.py
# Contains all constants used in the application

# Operazioni Web
URL_NSIS = 'https://www.impresa.gov.it/intro/info/news.html' # <<< COSTANTE AGGIUNTA
MAX_RETRIES = 2
FETCH_TIMEOUT_MS = 10000
FETCH_CHECK_INTERVAL_MS = 100
STATO_SELECTOR = "#risultatiConsultazionePratica tbody tr td:nth-child(3)" # Selettore CSS per lo stato
ALL_CELLS_JS = '''(function() {
    var row = document.querySelector('#risultatiConsultazionePratica tbody tr');
    if(!row) return null;
    var tds = row.querySelectorAll('td');
    var texts = [];
    tds.forEach(function(td){ texts.push(td.innerText.trim()); });
    return texts;
})();''' # Script JS per ottenere tutte le celle

# Ritardi e Controlli Fetch (in millisecondi)
DELAY_AFTER_INPUT_JS = 100
DELAY_AFTER_CLICK_JS = 1000
DELAY_BETWEEN_RETRIES = 1000
MAX_NULL_CHECKS = 5


# Colori Interfaccia
COLOR_STATUS_WAITING = "#e67e22" # Arancio
COLOR_STATUS_ERROR = "#e74c3c" # Rosso
COLOR_STATUS_SUCCESS = "#2ecc71" # Verde
COLOR_STATUS_INFO = "#3498db" # Blu
COLOR_STATUS_DEFAULT = "#333333" # Grigio scuro (per testo log)

# Colori Badge
COLOR_ANNULATA = "#f39c12" # Orange/Yellow
COLOR_APERTA = "#3498db" # Blue
COLOR_CHIUSA = "#27ae60" # Green (vibrant)
COLOR_LAVORAZIONE = "#e67e22" # Carrot Orange
COLOR_INVIATA = "#9b59b6" # Purple
COLOR_ECCEZIONI = "#e74c3c" # Red

# Nomi Colonne Excel (usati case-insensitive per ricerca)
COL_RICERCA = "ricerca"
COL_STATO = "stato"
COL_PROTOCOLLO = "protocollo uscita"
COL_PROVVEDIMENTO = "provvedimento"
COL_DATA_PROVV = "data provvedimento"
COL_CODICE_RIS = "codice richiesta (risultato)"
COL_NOTE = "note usmaf"

# Indici Colonne Default (usati se nome non trovato)
DEFAULT_IDX_STATO = 3
DEFAULT_IDX_PROTOCOLLO = 4
DEFAULT_IDX_PROVVEDIMENTO = 5
DEFAULT_IDX_DATA_PROVV = 6
DEFAULT_IDX_CODICE_RIS = 7
DEFAULT_IDX_NOTE = 8