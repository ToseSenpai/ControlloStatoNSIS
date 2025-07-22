# config.py
# Contains all constants used in the application

# Operazioni Web
URL_NSIS = 'https://www.impresa.gov.it/intro/info/news.html'
MAX_RETRIES = 2
FETCH_TIMEOUT_MS = 5000  # Ridotto da 10000 a 5000ms
FETCH_CHECK_INTERVAL_MS = 50  # Ridotto da 100 a 50ms
STATO_SELECTOR = "#risultatiConsultazionePratica tbody tr td:nth-child(3)" # Selettore CSS per lo stato
ALL_CELLS_JS = '''(function() {
    var row = document.querySelector('#risultatiConsultazionePratica tbody tr');
    if(!row) return null;
    var tds = row.querySelectorAll('td');
    var texts = [];
    tds.forEach(function(td){ texts.push(td.innerText.trim()); });
    return texts;
})();''' # Script JS per ottenere tutte le celle

# Ritardi e Controlli Fetch (in millisecondi) - Ottimizzati per velocità
DELAY_AFTER_INPUT_JS = 50  # Ridotto da 100 a 50ms
DELAY_AFTER_CLICK_JS = 500  # Ridotto da 1000 a 500ms
DELAY_BETWEEN_RETRIES = 500  # Ridotto da 1000 a 500ms
MAX_NULL_CHECKS = 3  # Ridotto da 5 a 3

# --- Palette Colori stile Luma (Light Theme) ---
COLOR_LUMA_WHITE = "#FFFFFF"
COLOR_LUMA_GRAY_10 = "#F9FAFB"
COLOR_LUMA_GRAY_30 = "#E5E7EB"
COLOR_LUMA_GRAY_50 = "#6B7280"  # Per bordi / testo secondario
COLOR_LUMA_GRAY_70 = "#374151"  # Testo su sfondi chiari (alternativa)
COLOR_LUMA_GRAY_90 = "#1F2937"  # Testo primario scuro

COLOR_LUMA_PURPLE_400 = "#9C57FF"
COLOR_LUMA_PURPLE_500 = "#6759FF"

# Manteniamo colori vecchi per status specifici (Badge, Log) o ridefiniamo
# Ridefinizione colori stato usando logica simile a Luma o colori vibranti
COLOR_ANNULATA = "#F59E0B" # Amber 500/600 (Giallo/Arancio)
COLOR_APERTA = "#3B82F6" # Blue 500 (Blu acceso)
COLOR_CHIUSA = "#10B981" # Emerald 500 (Verde brillante)
COLOR_LAVORAZIONE = "#F97316" # Orange 500 (Arancio)
COLOR_INVIATA = "#8B5CF6" # Violet 500 (Viola Luma-like)
COLOR_ECCEZIONI = "#EF4444" # Red 500 (Rosso acceso)

# Nomi Colonne Excel (usati case-insensitive per ricerca)
COL_RICERCA = "ricerca"
COL_STATO = "stato"
COL_PROTOCOLLO = "protocollo uscita"
COL_PROVVEDIMENTO = "provvedimento"
COL_DATA_PROVV = "data provvedimento"
COL_CODICE_RIS = "codice richiesta (risultato)"
COL_NOTE = "note usmaf"

# --- Valori Stile Luma ---
LUMA_BORDER_RADIUS_BUTTON = "8px" # 0.5rem approx
LUMA_BORDER_RADIUS_CONTAINER = "12px" # rounded-xl approx
LUMA_BORDER_COLOR_INPUT = COLOR_LUMA_GRAY_30 # Esempio


# Indici Colonne Default (MENO RILEVANTI ora che usiamo i nomi, ma tenuti come fallback)
DEFAULT_IDX_STATO = 3
DEFAULT_IDX_PROTOCOLLO = 4
DEFAULT_IDX_PROVVEDIMENTO = 5
DEFAULT_IDX_DATA_PROVV = 6
DEFAULT_IDX_CODICE_RIS = 7
DEFAULT_IDX_NOTE = 8

# Vecchi colori stato (COMMENTATI - usare quelli Luma-style sopra)
# COLOR_STATUS_WAITING = "#e67e22"
# COLOR_STATUS_ERROR = "#e74c3c"
# COLOR_STATUS_SUCCESS = "#2ecc71"
# COLOR_STATUS_INFO = "#3498db"
# COLOR_STATUS_DEFAULT = "#333333" # Grigio scuro (per testo log)