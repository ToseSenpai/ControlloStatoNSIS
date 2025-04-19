# main_window.py
# Contains the main application window class and the Worker class
# Versione con QThread + Lettura Openpyxl - FIX ASINCRONO V8 (Standard Logging - Fixed)

import os
import sys
import time
# --- Modifica: Import logging ---
import logging
import logging.handlers
# --- Fine Modifica ---
from PyQt6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets, QtWebChannel, QtWebEngineCore
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.styles import numbers
import traceback

# Import from our modules
from config import (
    MAX_RETRIES, FETCH_TIMEOUT_MS, FETCH_CHECK_INTERVAL_MS, STATO_SELECTOR,
    ALL_CELLS_JS, COLOR_STATUS_WAITING, COLOR_STATUS_ERROR, COLOR_STATUS_SUCCESS,
    COLOR_STATUS_INFO, COLOR_STATUS_DEFAULT, COLOR_ANNULATA, COLOR_APERTA,
    COLOR_CHIUSA, COLOR_LAVORAZIONE, COLOR_INVIATA, COLOR_ECCEZIONI,
    COL_RICERCA, COL_STATO, COL_PROTOCOLLO, COL_PROVVEDIMENTO,
    COL_DATA_PROVV, COL_CODICE_RIS, COL_NOTE, DEFAULT_IDX_STATO,
    DEFAULT_IDX_PROTOCOLLO, DEFAULT_IDX_PROVVEDIMENTO, DEFAULT_IDX_DATA_PROVV,
    DEFAULT_IDX_CODICE_RIS, DEFAULT_IDX_NOTE,
    URL_NSIS
)
# Assicurati che questi import esistano o crea i file corrispondenti
try:
    from ui_components import CustomProgressBar, SpinnerWidget
    from web_engine import WebEnginePage, JSBridge
except ImportError as e:
    # Usa il logger base se fallisce prima della configurazione completa
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"Impossibile importare ui_components o web_engine: {e}", exc_info=True)
    class CustomProgressBar(QtWidgets.QProgressBar): pass
    class SpinnerWidget(QtWidgets.QWidget):
        def startAnimation(self): self.show()
        def stopAnimation(self): self.hide()
    class WebEnginePage(QtWebEngineWidgets.QWebEnginePage): pass
    class JSBridge(QtCore.QObject):
         pass
    # sys.exit(1)

# Costanti per i ritardi (milliseconds)
DELAY_AFTER_INPUT_JS = 150
DELAY_AFTER_CLICK_JS = 1500
DELAY_BETWEEN_RETRIES = 1500
MAX_NULL_CHECKS = 5

# --- NUOVA CLASSE: Handler per QTextEdit ---
class QTextEditLogHandler(logging.Handler, QtCore.QObject):
    """
    Un handler per il modulo logging che emette segnali PyQt
    per aggiornare un widget QTextEdit.
    """
    log_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        logging.Handler.__init__(self)
        QtCore.QObject.__init__(self, parent)
        # Imposta un formatter di default qui per sicurezza
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))


    def emit(self, record):
        """
        Emette il record di log formattato tramite un segnale PyQt.
        """
        # Non fare il log di messaggi provenienti dal logger stesso per evitare ricorsioni
        if record.name == __name__: # O il nome specifico del logger se ne usi uno dedicato
             return
        try:
            msg = self.format(record)
            # Emette il segnale SOLO se il messaggio non è vuoto
            if msg:
                self.log_signal.emit(msg)
        except Exception:
            self.handleError(record)
# --- FINE NUOVA CLASSE ---


# ------------------- Worker Class (per QThread) -------------------
# (Invariato)
class Worker(QtCore.QObject):
    progress = QtCore.pyqtSignal(int, int)
    statusUpdate = QtCore.pyqtSignal(str)
    logUpdate = QtCore.pyqtSignal(str)
    badgeUpdate = QtCore.pyqtSignal(str, int)
    finished = QtCore.pyqtSignal()
    resultsReady = QtCore.pyqtSignal(list)
    requestFetch = QtCore.pyqtSignal(str)

    def __init__(self, codes_to_process):
        super().__init__()
        self.codes = codes_to_process
        self._stop_requested = False
        self._results = []
        self._current_code_index = 0
        self._total_codes = len(codes_to_process)
        self._counts = { "annullata": 0, "aperta": 0, "chiusa": 0, "lavorazione": 0, "inviata": 0, "eccezioni": 0 }
        self._badge_map = {
            "ANNULLATA": "🟡 Annullate", "APERTA": "🟢 Aperte", "CHIUSA": "✅ Chiuse",
            "IN LAVORAZIONE": "🟠 In lavorazione", "INVIATA": "📤 Inviate",
            "ECCEZIONE": "❗ Eccezioni"
        }
        self._count_keys = {
            "ANNULLATA": "annullata", "APERTA": "aperta", "CHIUSA": "chiusa",
            "IN LAVORAZIONE": "lavorazione", "INVIATA": "inviata"
        }
        self._exception_states = {
            "NON TROVATO", "ERRORE TIMEOUT", "ERRORE PAGINA", "ERRORE INTERNO FETCH",
            "SCONOSCIUTO", "INTERROTTO",
            "ERRORE CARICAMENTO PAGINA", "ELEMENTO NON TROVATO (JS)", "ERRORE RISULTATO JS"
        }
        self._finished_emitted_after_stop = False

    def run(self):
        print("--- Worker Thread Started ---")
        self._results = []; self._counts = {k: 0 for k in self._counts}; self._stop_requested = False
        self._finished_emitted_after_stop = False
        if not self.codes:
            self.logUpdate.emit("Nessun codice da processare nel worker.")
            self.finished.emit(); return
        self.progress.emit(0, self._total_codes)
        self._current_code_index = 0
        if not self._stop_requested:
            if self._current_code_index < len(self.codes):
                code = self.codes[self._current_code_index]
                self.statusUpdate.emit(f"Inizio elaborazione per: {code} (1/{self._total_codes})")
                self.requestFetch.emit(code)
            else:
                self.logUpdate.emit("Lista codici vuota."); self.finished.emit()
        else:
            self.logUpdate.emit("❌ Interrotto prima dell'inizio."); self.finished.emit()

    @QtCore.pyqtSlot(str, str, list)
    def processFetchedResult(self, code, state, last_cells):
        if self._stop_requested:
            if not self._finished_emitted_after_stop:
                thread = self.thread()
                if thread and thread.isRunning():
                    self.logUpdate.emit(f"❌ Elaborazione interrotta nel worker (risultato per {code} ricevuto: {state}). Fine.")
                    self.resultsReady.emit(self._results)
                    self.finished.emit()
                    self._finished_emitted_after_stop = True
            return

        current_idx = self._current_code_index
        self.logUpdate.emit(f"{current_idx + 1}/{self._total_codes} ➜ Codice: {code} | Stato Web: {state}")

        normalized_state_upper = state.strip().upper()
        if normalized_state_upper in self._exception_states:
            status_key_for_count = "eccezioni"
            badge_prefix = self._badge_map["ECCEZIONE"]
        else:
            status_key_for_count = self._count_keys.get(normalized_state_upper, "eccezioni")
            badge_prefix = self._badge_map.get(normalized_state_upper, self._badge_map["ECCEZIONE"])

        if status_key_for_count not in self._counts:
             self.logUpdate.emit(f"⚠️ Chiave conteggio non prevista: {status_key_for_count} per stato {state}")
             status_key_for_count = "eccezioni"
        self._counts[status_key_for_count] += 1
        count_to_display = self._counts[status_key_for_count]
        self.badgeUpdate.emit(badge_prefix, count_to_display)

        stato_res = state
        protocollo_uscita_res = last_cells[5] if len(last_cells) > 5 else ''
        provvedimento_res = last_cells[6] if len(last_cells) > 6 else ''
        data_provvedimento_res = last_cells[7] if len(last_cells) > 7 else ''
        codice_richiesta_risultato_res = last_cells[8] if len(last_cells) > 8 and last_cells[8] else code
        note_usmaf_res = last_cells[10] if len(last_cells) > 10 else ''
        if normalized_state_upper in self._exception_states:
            note_usmaf_res = f"Stato recuperato: {state}. {note_usmaf_res}".strip()
        self._results.append({
            'Input Code': code, 'Stato': stato_res, 'Protocollo uscita': protocollo_uscita_res,
            'Provvedimento': provvedimento_res, 'Data Provvedimento': data_provvedimento_res,
            'Codice richiesta (risultato)': codice_richiesta_risultato_res, 'Note Usmaf': note_usmaf_res
        })

        self.progress.emit(current_idx + 1, self._total_codes)
        self._current_code_index += 1

        if self._current_code_index < self._total_codes:
            next_code = self.codes[self._current_code_index]
            self.statusUpdate.emit(f"Richiesta fetch per: {next_code} ({self._current_code_index + 1}/{self._total_codes})")
            self.requestFetch.emit(next_code)
        else:
            self.logUpdate.emit("✅ Elaborazione codici completata.")
            self.statusUpdate.emit("✅ Elaborazione completata.")
            self.resultsReady.emit(self._results)
            self.finished.emit()

    def request_stop(self):
        print("--- Worker Stop Requested ---")
        self._stop_requested = True
# ------------------- Fine Worker Class -------------------


# ------------------- Classe App Modificata -------------------
# Ottieni un logger per questo modulo (o usa il root logger)
# Usare __name__ è buona pratica per identificare l'origine dei log
logger = logging.getLogger(__name__)
# Imposta il livello anche per questo logger specifico se necessario
# logger.setLevel(logging.DEBUG)

class App(QtWidgets.QWidget):
    """Classe principale dell'applicazione GUI."""
    fetchCompleted = QtCore.pyqtSignal(str, str, list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controllo Stato Richiesta - NSIS"); self.setGeometry(QtCore.QRect(100, 100, 1200, 800))
        self._badge_widgets = set(); self.max_retries = MAX_RETRIES; self.last_cells = []; self.current_file_path = None
        self.thread = None; self.worker = None
        self._current_fetch_context = None

        # --- Configurazione Logging Iniziale (Console/File) ---
        self._setup_logging()

        # --- Setup UI e WebEngine ---
        self._setup_ui() # Crea self.log qui dentro
        self._setup_webengine()
        self.setStyleSheet("QWidget { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; }")

        # --- Modifica: Aggiungi Handler UI posticipato ---
        # Usa QTimer.singleShot per aggiungere l'handler UI dopo che l'init è completato
        # e il ciclo eventi è partito.
        QtCore.QTimer.singleShot(0, self._add_ui_log_handler)

        logger.info("Applicazione inizializzata.")

    def _setup_logging(self):
        """Configura il modulo logging per Console e File."""
        log_level = logging.DEBUG
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        log_file = "app_log.log"

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Rimuovi handler esistenti per evitare duplicati
        for handler in root_logger.handlers[:]:
            # Non rimuovere l'handler UI se già aggiunto (improbabile qui ma per sicurezza)
            if not isinstance(handler, QTextEditLogHandler):
                root_logger.removeHandler(handler)
                handler.close()

        # Aggiungi handler solo se non già presenti
        has_console_handler = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
        has_file_handler = any(isinstance(h, logging.handlers.RotatingFileHandler) for h in root_logger.handlers)

        if not has_console_handler:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(log_format)
            console_handler.setLevel(logging.INFO)
            root_logger.addHandler(console_handler)

        if not has_file_handler:
            try:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file, maxBytes=1*1024*1024, backupCount=3, encoding='utf-8'
                )
                file_handler.setFormatter(log_format)
                file_handler.setLevel(logging.DEBUG)
                root_logger.addHandler(file_handler)
            except Exception as e:
                 # Logga su console se fallisce la configurazione del file handler
                 print(f"ERRORE CRITICO: Impossibile configurare FileHandler per il logging: {e}")

        logging.getLogger("openpyxl").setLevel(logging.WARNING)
        logger.info("Sistema di logging configurato (Console, File).")

    # --- NUOVO METODO ---
    def _add_ui_log_handler(self):
        """Crea e aggiunge l'handler per il QTextEdit al logger."""
        try:
            # Verifica se l'handler UI è già stato aggiunto
            if any(isinstance(h, QTextEditLogHandler) for h in logging.getLogger().handlers):
                logger.debug("Handler UI già presente.")
                return

            if hasattr(self, 'log') and self.log is not None:
                log_handler_ui = QTextEditLogHandler(self)
                # Imposta lo stesso formatter o uno dedicato per la UI
                log_handler_ui.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
                log_handler_ui.setLevel(logging.INFO) # Livello per la UI
                # Connetti il segnale allo slot
                log_handler_ui.log_signal.connect(self._append_log_to_widget)
                # Aggiungi l'handler al root logger
                logging.getLogger().addHandler(log_handler_ui)
                logger.info("Handler di logging per l'interfaccia utente aggiunto.")
            else:
                logger.error("Impossibile aggiungere handler UI: widget self.log non trovato.")
        except Exception as e:
            logger.exception("Errore durante l'aggiunta dell'handler UI.")


    def _setup_ui(self):
        """Crea e organizza i widget dell'interfaccia utente."""
        # ... (Codice UI invariato fino alla creazione di self.log) ...
        main_layout = QtWidgets.QHBoxLayout(self)
        self.view = QtWebEngineWidgets.QWebEngineView(); main_layout.addWidget(self.view, stretch=3)
        right_column_layout = QtWidgets.QVBoxLayout(); main_layout.addLayout(right_column_layout, stretch=1)
        ctrl_container = QtWidgets.QFrame(); ctrl_container.setStyleSheet("""QFrame { background-color: #f8f8f8; border: 1px solid #dddddd; border-radius: 8px; padding: 10px; }""")
        ctrl_layout = QtWidgets.QVBoxLayout(ctrl_container); ctrl_layout.setContentsMargins(5, 5, 5, 5); ctrl_layout.setSpacing(8); right_column_layout.addWidget(ctrl_container)
        professional_button_style = """QPushButton { background-color: #F9F9F9; color: #1A1A1A; border: 1px solid #E0E0E0; padding: 7px 15px; border-radius: 4px; font-weight: 600; outline: none; } QPushButton:hover { background-color: #F0F0F0; border: 1px solid #D0D0D0; } QPushButton:pressed { background-color: #E0E0E0; color: #000000; border: 1px solid #C0C0C0; } QPushButton:disabled { background-color: #FDFDFD; color: #B0B0B0; border: 1px solid #F0F0F0; }"""
        primary_button_style =    """QPushButton { background-color: #0078D4; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: 600; outline: none; } QPushButton:hover { background-color: #106EBF; } QPushButton:pressed { background-color: #005A9E; } QPushButton:disabled { background-color: #F0F0F0; color: #B0B0B0; border: none; }"""
        self.btn_open = QtWidgets.QPushButton("Apri NSIS"); self.btn_open.clicked.connect(self.open_nsis_url_test); self.btn_open.setStyleSheet(professional_button_style)
        self.btn_start = QtWidgets.QPushButton("Seleziona file e Avvia"); self.btn_start.clicked.connect(self.start_processing); self.btn_start.setStyleSheet(primary_button_style)
        self.btn_stop = QtWidgets.QPushButton("Interrompi"); self.btn_stop.clicked.connect(self.stop_processing); self.btn_stop.setEnabled(False); self.btn_stop.setStyleSheet(professional_button_style)
        ctrl_layout.addWidget(self.btn_open); ctrl_layout.addWidget(self.btn_start); ctrl_layout.addWidget(self.btn_stop)
        ctrl_layout.addSpacing(10); line1 = QtWidgets.QFrame(); line1.setFrameShape(QtWidgets.QFrame.Shape.HLine); line1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken); ctrl_layout.addWidget(line1); ctrl_layout.addSpacing(10)
        progress_layout = QtWidgets.QHBoxLayout(); progress_layout.setContentsMargins(0,0,0,0); progress_layout.setSpacing(5)
        self.spinner = SpinnerWidget(self)
        progress_layout.addWidget(self.spinner)
        self.progress = CustomProgressBar(); self.progress.setRange(0, 100); self.progress.setValue(0); progress_layout.addWidget(self.progress, stretch=1)
        self.progress_label = QtWidgets.QLabel("0%"); self.progress_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter); self.progress_label.setMinimumWidth(35); self.progress_label.setStyleSheet("color: #1A1A1A;")
        progress_layout.addWidget(self.progress_label);
        ctrl_layout.addLayout(progress_layout)
        self.status = QtWidgets.QLabel("Pronto.", alignment=QtCore.Qt.AlignmentFlag.AlignCenter); self.status.setStyleSheet("color: #1A1A1A;")
        ctrl_layout.addWidget(self.status)

        # Crea il widget QTextEdit per il log
        self.log = QtWidgets.QTextEdit(); self.log.setReadOnly(True); self.log.setStyleSheet(f""" QTextEdit {{ border: 1px solid #E0E0E0; border-radius: 4px; padding: 5px; font-size: 10px; color: #1A1A1A; background-color: #FFFFFF; }}""")
        ctrl_layout.addWidget(self.log); ctrl_layout.addSpacing(10); line2 = QtWidgets.QFrame(); line2.setFrameShape(QtWidgets.QFrame.Shape.HLine); line2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken); ctrl_layout.addWidget(line2); ctrl_layout.addSpacing(10)

        # --- Handler UI NON viene più aggiunto qui ---

        self.badge_layout = QtWidgets.QVBoxLayout(); self.badge_layout.setSpacing(4); ctrl_layout.addLayout(self.badge_layout)
        self._badge_info_list = [ self.create_badge("🟡", "Annullate", COLOR_ANNULATA), self.create_badge("🟢", "Aperte", COLOR_APERTA), self.create_badge("✅", "Chiuse", COLOR_CHIUSA), self.create_badge("🟠", "In lavorazione", COLOR_LAVORAZIONE), self.create_badge("📤", "Inviate", COLOR_INVIATA), self.create_badge("❗", "Eccezioni", COLOR_ECCEZIONI)]
        self._badge_widgets_map = {
             "🟡 Annullate": self._badge_info_list[0], "🟢 Aperte": self._badge_info_list[1],
             "✅ Chiuse": self._badge_info_list[2], "🟠 In lavorazione": self._badge_info_list[3],
             "📤 Inviate": self._badge_info_list[4], "❗ Eccezioni": self._badge_info_list[5]
        }
        for card_frame, _, _ in self._badge_info_list: card_frame.setVisible(False)
        right_column_layout.addStretch()
        firma_h_layout = QtWidgets.QHBoxLayout(); firma_h_layout.setContentsMargins(0, 0, 0, 0); firma_h_layout.addStretch()
        self.firma_label = QtWidgets.QLabel("<i>©2025 ST, version 1.0</i>"); self.firma_label.setStyleSheet("QLabel { color: #777777; font-size: 9px; margin-right: 15px; }")
        firma_h_layout.addWidget(self.firma_label); right_column_layout.addLayout(firma_h_layout)

    # --- Slot RIPRISTINATO per Handler UI ---
    @QtCore.pyqtSlot(str)
    def _append_log_to_widget(self, message):
        """Aggiunge un messaggio al QTextEdit del log."""
        # Assicura che l'aggiornamento avvenga nel thread principale
        if QtCore.QThread.currentThread() != self.thread():
             # Usa invokeMethod per sicurezza se chiamato da altro thread
             QtCore.QMetaObject.invokeMethod(self, "_append_log_to_widget", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.QGenericArgument("QString", message))
             return
        try:
            self.log.append(message) # Aggiunge il messaggio già formattato
            cursor = self.log.textCursor()
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
            self.log.setTextCursor(cursor)
        except Exception as e:
             # Logga l'errore sulla console se fallisce l'append
             print(f"ERRORE in _append_log_to_widget: {e}")

    # ... (Il resto del codice rimane invariato rispetto alla versione precedente V8-debug) ...
    # ... (_setup_webengine, _handle_page_load_finished, start_processing, ...)
    # ... (stop_processing, update_progress, update_status, update_log, ...)
    # ... (update_badge_ui, handle_results, handle_thread_finished, ...)
    # ... (_set_status_message, fetch async methods, UI ausiliari, save_excel, ...)
    # ... (reset methods, closeEvent) ...

    # --- Metodi Invariati (copiati per completezza ma senza modifiche interne rispetto a V8-debug) ---
    def _setup_webengine(self):
        """Inizializza la pagina WebEngine, il bridge e connette segnali."""
        page = WebEnginePage(self.view) if 'WebEnginePage' in globals() else QtWebEngineWidgets.QWebEnginePage(self.view)
        self.view.setPage(page)
        self.bridge = JSBridge() if 'JSBridge' in globals() else QtCore.QObject()
        self.channel = QtWebChannel.QWebChannel()
        if hasattr(self.bridge, 'evaluate') or hasattr(self.bridge, 'receive'):
             logger.debug("Registering JSBridge object")
             self.channel.registerObject('bridge', self.bridge)
        else:
             logger.debug("JSBridge object not registered")
        page = self.view.page()
        if page:
            page.setWebChannel(self.channel)
            page.setBackgroundColor(QtGui.QColor("#FFFFFF"))
            page.loadFinished.connect(self._handle_page_load_finished)
        else:
            logger.critical("Impossibile ottenere pagina web.")
            QtWidgets.QMessageBox.critical(self, "Errore Critico", "Impossibile inizializzare componente Web.")

    @QtCore.pyqtSlot(bool)
    def _handle_page_load_finished(self, ok):
        """Gestisce il segnale loadFinished della pagina web."""
        logger.debug(f"Page load finished, success: {ok}")
        if self._current_fetch_context:
            self._current_fetch_context['page_load_error'] = not ok
            if not ok:
                logger.error(f"Errore durante il caricamento della pagina: {self.view.url().toString()}")
                if self._current_fetch_context:
                     QtCore.QTimer.singleShot(0, lambda: self._process_fetch_result(self._current_fetch_context['code'], 'Errore Caricamento Pagina', []))

    def start_processing(self):
        """Avvia il processo di selezione file e preparazione elaborazione."""
        logger.info("Avvio start_processing...")
        if self.thread is not None and self.thread.isRunning():
            logger.warning("Elaborazione già in corso."); return

        logger.debug("Prima di QFileDialog.getOpenFileName")
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Seleziona file Excel", "", "Excel Files (*.xlsx *.xls)")
        logger.debug(f"Dopo QFileDialog.getOpenFileName, file_path: {file_path}")
        if not file_path:
            logger.info("Nessun file selezionato, uscita.")
            return
        self.current_file_path = file_path
        logger.info(f"File selezionato: {self.current_file_path}")

        codes = []
        workbook = None
        logger.debug("Inizio blocco lettura Excel")
        try:
            logger.debug("Prima di load_workbook")
            logger.info(f"Lettura file (openpyxl): {os.path.basename(file_path)}")
            workbook = load_workbook(filename=file_path, read_only=True, data_only=True, keep_vba=False)
            logger.debug("Dopo load_workbook")
            if not workbook.sheetnames:
                 logger.error("Il file Excel non contiene fogli di lavoro.")
                 raise ValueError("Il file Excel non contiene fogli di lavoro.")
            sheet = workbook.active
            logger.debug(f"Foglio attivo ottenuto: {sheet.title}")
            if sheet.max_row < 1:
                 logger.error("Il foglio di lavoro attivo è vuoto.")
                 raise ValueError("Il foglio di lavoro attivo è vuoto.")
            logger.debug(f"Foglio valido (max_row={sheet.max_row})")
            logger.debug("Prima di leggere intestazione")
            header_iter = sheet.iter_rows(min_row=1, max_row=1)
            try:
                header_row_cells = next(header_iter)
                logger.debug("Intestazione letta")
            except StopIteration:
                 logger.error("StopIteration leggendo intestazione")
                 raise ValueError("Impossibile leggere la riga di intestazione (foglio vuoto?).")
            ricerca_col_idx = -1
            logger.debug(f"Ricerca colonna '{COL_RICERCA}'")
            for idx, cell in enumerate(header_row_cells):
                if cell.value is not None and str(cell.value).strip().lower() == COL_RICERCA.lower():
                    ricerca_col_idx = idx + 1
                    break
            if ricerca_col_idx == -1:
                logger.error(f"Colonna '{COL_RICERCA}' non trovata")
                raise ValueError(f"Colonna '{COL_RICERCA}' non trovata nell'intestazione del foglio '{sheet.title}'.")
            logger.debug(f"Colonna '{COL_RICERCA}' trovata: indice {ricerca_col_idx}")
            logger.debug("Prima di estrarre codici")
            code_count = 0
            for row_idx, row_cells in enumerate(sheet.iter_rows(min_row=2, min_col=ricerca_col_idx, max_col=ricerca_col_idx), start=2):
                cell = row_cells[0]
                if cell.value is not None:
                    code = str(cell.value).strip()
                    if code and code.lower() != 'nan':
                        codes.append(code)
                        code_count += 1
            logger.debug(f"Estrazione codici completata ({code_count} codici aggiunti)")
            if not codes:
                logger.warning("Nessun codice valido trovato dopo l'estrazione")
                self.status.setText("⚠️ Nessun codice valido trovato.")
                QtWidgets.QMessageBox.information(self, "Nessun Codice", f"Nessun codice valido trovato nella colonna '{COL_RICERCA}' del foglio '{sheet.title}'.")
                if workbook: workbook.close()
                return
            logger.info(f"Trovati {len(codes)} codici. Preparazione elaborazione background...")
            logger.debug("Lettura Excel completata con successo")
        except InvalidFileException as ife:
            error_msg = f"File Excel non valido o corrotto: {os.path.basename(file_path)}."
            logger.exception(f"{error_msg} Dettagli: {ife}")
            self.status.setText(f"❌ Errore File Excel")
            QtWidgets.QMessageBox.critical(self, "Errore Lettura File", f"{error_msg}\nDettagli nel log.")
            self._reset_ui_after_processing()
            return
        except FileNotFoundError:
            error_msg = f"File non trovato: {file_path}"
            logger.error(error_msg)
            self.status.setText(f"❌ File non trovato")
            QtWidgets.QMessageBox.critical(self, "Errore Lettura File", error_msg)
            self._reset_ui_after_processing()
            return
        except ValueError as ve:
            error_msg = f"Errore nel contenuto del file Excel: {ve}"
            logger.error(error_msg)
            self.status.setText(f"❌ Errore Contenuto File")
            QtWidgets.QMessageBox.warning(self, "Errore Contenuto File", error_msg)
            self._reset_ui_after_processing()
            return
        except Exception as e:
            error_msg = f"Errore imprevisto durante la lettura del file Excel."
            logger.exception(error_msg)
            self.status.setText(f"❌ Errore Lettura Imprevisto")
            QtWidgets.QMessageBox.critical(self, "Errore Lettura Imprevisto", f"{error_msg}\n\nConsultare il log per i dettagli tecnici.")
            self._reset_ui_after_processing()
            return
        finally:
             logger.debug("Entro nel blocco finally della lettura Excel")
             if workbook:
                 try:
                     logger.debug("Tento di chiudere il workbook")
                     workbook.close()
                     logger.debug("Workbook chiuso correttamente.")
                 except Exception as close_err:
                     logger.warning(f"Errore durante la chiusura del workbook: {close_err}", exc_info=False)
             logger.debug("Esco dal blocco finally della lettura Excel")

        logger.debug("Preparazione UI prima del thread")
        self.btn_start.setEnabled(False); self.btn_stop.setEnabled(True); self.btn_open.setEnabled(False)
        self.status.setText("⏳ Avvio elaborazione..."); self.log.clear(); self._reset_badges(); self.progress.setValue(0)
        self.spinner.stopAnimation()
        logger.debug("Inizio blocco creazione Thread/Worker")
        try:
            logger.debug("Prima di creare QThread"); self.thread = QtCore.QThread(self); logger.debug("Dopo aver creato QThread")
            logger.debug("Prima di creare Worker"); self.worker = Worker(codes); logger.debug("Dopo aver creato Worker")
            logger.debug("Prima di moveToThread"); self.worker.moveToThread(self.thread); logger.debug("Dopo moveToThread")
            logger.debug("Prima delle connessioni segnali/slot")
            self.worker.progress.connect(self.update_progress)
            self.worker.statusUpdate.connect(self.update_status)
            self.worker.logUpdate.connect(self.update_log)
            self.worker.badgeUpdate.connect(self.update_badge_ui)
            self.worker.resultsReady.connect(self.handle_results)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.handle_thread_finished)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.requestFetch.connect(self.do_fetch_state_async, QtCore.Qt.ConnectionType.QueuedConnection)
            self.fetchCompleted.connect(self.worker.processFetchedResult)
            logger.debug("Dopo le connessioni segnali/slot")
            logger.debug("Prima di thread.start()"); self.thread.start(); logger.debug("Dopo thread.start()")
            logger.info("Thread worker avviato.")
        except Exception as e_thread:
            error_msg = f"Errore durante creazione/avvio thread."
            logger.exception(error_msg)
            self.status.setText(f"❌ Errore Thread");
            QtWidgets.QMessageBox.critical(self, "Errore Thread", f"{error_msg}\n{e_thread}\n\nConsultare il log.")
            self._reset_ui_after_processing()
        logger.debug("Fine start_processing")

    def stop_processing(self):
        """Richiede l'interruzione del worker e annulla fetch in corso."""
        if self.worker and self.thread and self.thread.isRunning():
            logger.info("Richiesta interruzione elaborazione...")
            self.worker.request_stop()
            self._set_status_message("⏳ Interruzione in corso...", is_waiting=False)
            self.btn_stop.setEnabled(False)
        else:
            logger.info("Nessuna elaborazione da interrompere.")

    @QtCore.pyqtSlot(int, int)
    def update_progress(self, current_value, max_value):
        if max_value > 0: self.progress.setMaximum(max_value); self.progress.setValue(current_value); percentage = int((current_value / max_value) * 100); self.progress_label.setText(f"{percentage}%")
        else: self.progress.setMaximum(1); self.progress.setValue(0); self.progress_label.setText("0%")

    @QtCore.pyqtSlot(str)
    def update_status(self, message):
        """Aggiorna il messaggio di stato base ricevuto dal worker."""
        self._set_status_message(message, is_waiting=False)

    @QtCore.pyqtSlot(str)
    def update_log(self, message):
        """Riceve un messaggio dal worker e lo logga (verrà mostrato nella UI tramite l'handler)."""
        logger.info(message)

    @QtCore.pyqtSlot(str, int)
    def update_badge_ui(self, badge_prefix, count):
        target_prefix = badge_prefix
        if badge_prefix == "❗ Eccezioni":
             target_prefix = "❗ Eccezioni"

        if target_prefix in self._badge_widgets_map:
            card, label, sparkle = self._badge_widgets_map[target_prefix]
            new_text = f"{target_prefix}: {count}"
            if label.text() != new_text:
                label.setText(new_text)
                is_exception = (target_prefix == "❗ Eccezioni")
                self.flash_emoji(sparkle, "⚠️" if is_exception else "✨")
                if count > 0 and not card.isVisible():
                    if card not in self._badge_widgets: self.badge_layout.addWidget(card); self._badge_widgets.add(card)
                    card.setVisible(True); self.animate_badge(card)
        else: logger.warning(f"Prefisso badge UI non trovato per '{target_prefix}' (originale: '{badge_prefix}')")

    @QtCore.pyqtSlot(list)
    def handle_results(self, results_list):
        """Gestisce i risultati finali ricevuti dal worker."""
        logger.info(f"Ricevuti {len(results_list)} risultati finali dal worker.")
        if results_list and self.current_file_path:
            self._save_results_to_excel(results_list, self.current_file_path)
        elif not results_list and self.worker and not self.worker._stop_requested:
             logger.info("Nessun risultato valido raccolto.")
             self.status.setText("ℹ️ Nessun risultato da salvare.")
        elif not self.current_file_path:
             logger.warning("Impossibile salvare: percorso file non memorizzato.")
             self.status.setText("⚠️ Percorso file non disponibile per salvataggio.")

    @QtCore.pyqtSlot()
    def handle_thread_finished(self):
        """Chiamato quando il worker emette il segnale finished."""
        logger.info("Thread di elaborazione terminato.")
        self._set_status_message(self.status.text(), is_waiting=False)
        self._reset_ui_after_processing()
        self.thread = None
        self.worker = None
        self._current_fetch_context = None
        logger.debug("Thread, Worker, and Fetch Context cleaned")

    def _set_status_message(self, base_message, is_waiting):
        """Imposta il messaggio di stato e gestisce lo spinner grafico."""
        self.status.setText(base_message)
        if is_waiting:
            self.spinner.startAnimation()
        else:
            self.spinner.stopAnimation()

    @QtCore.pyqtSlot(str)
    def do_fetch_state_async(self, code):
        """Slot chiamato dal worker per iniziare il fetch di un codice."""
        page = self.view.page()
        if not page:
            logger.critical(f"Errore critico (fetch): Pagina Web non disponibile (Codice: {code}).")
            self._process_fetch_result(code, 'Errore Pagina', [])
            return
        if not self.worker or self.worker._stop_requested:
            logger.debug(f"Skipping fetch for {code} - worker fermato/nullo prima di iniziare.")
            return
        logger.info(f"Ricevuta richiesta fetch ASYNC per {code}")
        self.last_cells = [''] * 11
        self.last_cells[8] = str(code).strip()
        self._current_fetch_context = {
            'code': code, 'attempt': 0, 'start_time': None,
            'check_count': 0, 'null_check_count': 0, 'page_load_error': False
        }
        self._attempt_fetch(page, code)

    def _attempt_fetch(self, page, code):
        """Tenta di eseguire il fetch per un codice (gestisce i retries)."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
        attempt = self._current_fetch_context['attempt']
        if self.worker and self.worker._stop_requested:
            logger.info(f"Interruzione rilevata prima del tentativo {attempt + 1} per {code}.")
            self._process_fetch_result(code, 'Interrotto', self.last_cells)
            return
        if self._current_fetch_context['page_load_error']:
            logger.error(f"Errore caricamento pagina rilevato prima del tentativo {attempt + 1} per {code}.")
            self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells)
            return
        if attempt > self.max_retries:
            logger.warning(f"Timeout/Errore Fetch per {code} dopo {attempt} tentativi.")
            self._process_fetch_result(code, 'Errore Timeout', self.last_cells)
            return
        if attempt > 0:
            logger.info(f"Riprovo '{code}' (tentativo {attempt + 1}/{self.max_retries + 1})")
            self._set_status_message(f"⏳ Riprovo '{code}' (tentativo {attempt + 1}/{self.max_retries + 1})...", is_waiting=False)
            QtCore.QTimer.singleShot(DELAY_BETWEEN_RETRIES, lambda: self._execute_js_input(page, code))
        else:
            logger.debug(f"Inizio primo tentativo per {code}")
            self._execute_js_input(page, code)

    def _execute_js_input(self, page, code):
        """Esegue il Javascript per inserire il codice nel campo."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
        attempt = self._current_fetch_context['attempt']
        if self.worker and self.worker._stop_requested:
            logger.info(f"Interruzione rilevata prima di JS input per {code} (tentativo {attempt+1}).")
            self._process_fetch_result(code, 'Interrotto', self.last_cells)
            return
        if self._current_fetch_context['page_load_error']:
            logger.error(f"Errore caricamento pagina rilevato prima di JS input per {code} (tentativo {attempt+1}).")
            self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells)
            return
        try:
            logger.info(f"Inserimento codice {code}...")
            self._set_status_message(f"Inserimento codice {code}...", is_waiting=True)
            code_str = str(code).strip()
            escaped_code = code_str.replace("'", "\\'").replace('"', '\\"')
            js_input = f"document.getElementById('codiceRichiesta').value='{escaped_code}';"
            logger.debug(f"JS Input (Attempt {attempt+1}): {js_input[:50]}...")
            page.runJavaScript(js_input, lambda result, p=page, c=code: self._schedule_js_click(p, c))
        except Exception as js_error:
            logger.error(f"Errore durante esecuzione JS (input) per {code} (tentativo {attempt+1}): {js_error}", exc_info=True)
            self._set_status_message(f"Errore JS input per {code}", is_waiting=False)
            self._schedule_next_attempt(page, code)

    def _schedule_js_click(self, page, code):
         if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
         QtCore.QTimer.singleShot(DELAY_AFTER_INPUT_JS, lambda: self._execute_js_click(page, code))

    def _execute_js_click(self, page, code):
        """Esegue il Javascript per cliccare il pulsante di ricerca."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
        attempt = self._current_fetch_context['attempt']
        if self.worker and self.worker._stop_requested:
             logger.info(f"Interruzione rilevata prima di JS click per {code} (tentativo {attempt+1}).")
             self._process_fetch_result(code, 'Interrotto', self.last_cells)
             return
        if self._current_fetch_context['page_load_error']:
             logger.error(f"Errore caricamento pagina rilevato prima di JS click per {code} (tentativo {attempt+1}).")
             self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells)
             return
        try:
            logger.info(f"Click ricerca per {code}...")
            self._set_status_message(f"Click ricerca per {code}...", is_waiting=True)
            js_click = "document.getElementById('cercaRichiestaNullaOstaBtn').click();"
            logger.debug(f"JS Click (Attempt {attempt+1})")
            page.runJavaScript(js_click, lambda result, p=page, c=code: self._schedule_first_check(p, c))
        except Exception as js_error:
            logger.error(f"Errore durante esecuzione JS (click) per {code} (tentativo {attempt+1}): {js_error}", exc_info=True)
            self._set_status_message(f"Errore JS click per {code}", is_waiting=False)
            self._schedule_next_attempt(page, code)

    def _schedule_first_check(self, page, code):
         if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
         logger.info(f"Attesa risultato per {code}...")
         self._set_status_message(f"Attesa risultato per {code}...", is_waiting=True)
         self._current_fetch_context['start_time'] = time.monotonic()
         self._current_fetch_context['check_count'] = 0
         self._current_fetch_context['null_check_count'] = 0
         QtCore.QTimer.singleShot(DELAY_AFTER_CLICK_JS, lambda: self._check_fetch_result(page, code))

    def _check_fetch_result(self, page, code):
        """Avvia l'esecuzione JS per controllare il risultato."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
        attempt = self._current_fetch_context['attempt']
        if self.worker and self.worker._stop_requested:
             logger.info(f"Interruzione rilevata durante attesa JS per {code} (tentativo {attempt+1}).")
             self._process_fetch_result(code, 'Interrotto', self.last_cells)
             return
        if self._current_fetch_context['page_load_error']:
             logger.error(f"Errore caricamento pagina rilevato durante attesa JS per {code} (tentativo {attempt+1}).")
             self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells)
             return
        status_msg = f"Controllo risultato per {code} (check {self._current_fetch_context['check_count']+1})..."
        logger.debug(status_msg)
        self._set_status_message(status_msg, is_waiting=True)
        logger.debug(f"Eseguo script JS celle (Attempt {attempt+1}) per {code}")
        try:
            page.runJavaScript(ALL_CELLS_JS, self._handle_js_evaluation_result)
        except Exception as eval_error:
             logger.error(f"Errore immediato durante chiamata runJavaScript per {code} (tentativo {attempt+1}): {eval_error}", exc_info=True)
             self._set_status_message(f"Errore JS check per {code}", is_waiting=False)
             self._schedule_next_attempt(page, code)

    def _handle_js_evaluation_result(self, result):
        """Gestisce il risultato asincrono della valutazione JS."""
        if not self._current_fetch_context:
             logger.warning(f"Ricevuto risultato JS ({result}) ma nessun contesto fetch attivo.")
             return
        code = self._current_fetch_context['code']
        attempt = self._current_fetch_context['attempt']
        start_time = self._current_fetch_context['start_time']
        page = self.view.page()
        if self.worker and self.worker._stop_requested:
            logger.info(f"Interruzione rilevata DOPO valutazione JS per {code} (tentativo {attempt+1}).")
            self._process_fetch_result(code, 'Interrotto', self.last_cells)
            return
        if self._current_fetch_context['page_load_error']:
             logger.error(f"Errore caricamento pagina rilevato DOPO valutazione JS per {code} (tentativo {attempt+1}).")
             self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells)
             return
        logger.debug(f"Ricevuto risultato JS per {code} (Attempt {attempt+1}): {result}")
        self._current_fetch_context['check_count'] += 1
        cells = result
        result_found = False
        fetched_state = 'Errore Interno Fetch'
        current_cells = []
        if cells is None:
            self._current_fetch_context['null_check_count'] += 1
            logger.debug(f"Script JS ha restituito null per {code} (check: {self._current_fetch_context['check_count']}, null checks: {self._current_fetch_context['null_check_count']})")
            if self._current_fetch_context['null_check_count'] >= MAX_NULL_CHECKS:
                 logger.warning(f"Elemento tabella non trovato per {code} dopo {MAX_NULL_CHECKS} controlli null.")
                 self._process_fetch_result(code, 'Elemento Non Trovato (JS)', self.last_cells)
                 return
        elif isinstance(cells, list):
            self._current_fetch_context['null_check_count'] = 0
            current_cells = [str(c).strip() if c is not None else '' for c in cells]
            while len(current_cells) < 11: current_cells.append('')
            if len(cells) == 1 and 'Nessun dato presente' in cells[0]:
                fetched_state = 'Non Trovato'
                current_cells[2] = fetched_state
                result_found = True
            elif len(cells) > 8:
                code_in_table = current_cells[8]
                if code_in_table == str(code).strip():
                    fetched_state = current_cells[2] if current_cells[2] else 'Sconosciuto'
                    result_found = True
        else:
            logger.error(f"Risultato JS inatteso per {code} (tentativo {attempt+1}): {type(cells)} - {str(cells)[:100]}")
            self._process_fetch_result(code, 'Errore Risultato JS', self.last_cells)
            return
        if result_found:
            logger.info(f"Risultato trovato per {code} (tentativo {attempt+1}): {fetched_state}")
            self._process_fetch_result(code, fetched_state, current_cells)
            return
        if start_time is None:
             logger.warning(f"start_time mancante per {code} in _handle_js_evaluation_result.")
             start_time = time.monotonic()
             self._current_fetch_context['start_time'] = start_time
        elapsed_time_ms = (time.monotonic() - start_time) * 1000
        if elapsed_time_ms > FETCH_TIMEOUT_MS:
            logger.warning(f"Timeout tentativo {attempt + 1} (fetch) per codice '{code}' dopo {elapsed_time_ms:.0f} ms")
            self._schedule_next_attempt(page, code)
            return
        logger.debug(f"Risultato non ancora trovato per {code}, schedulo prossimo check.")
        QtCore.QTimer.singleShot(FETCH_CHECK_INTERVAL_MS, lambda: self._check_fetch_result(page, code))

    def _schedule_next_attempt(self, page, code):
         """Schedula il prossimo tentativo di fetch."""
         if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
         next_attempt = self._current_fetch_context['attempt'] + 1
         logger.debug(f"Schedulo tentativo {next_attempt} per {code}")
         self._current_fetch_context['attempt'] = next_attempt
         self._current_fetch_context['start_time'] = None
         self._current_fetch_context['check_count'] = 0
         self._current_fetch_context['null_check_count'] = 0
         QtCore.QTimer.singleShot(0, lambda: self._attempt_fetch(page, code))

    def _process_fetch_result(self, code, state, cells):
        """Metodo finale per processare il risultato del fetch e inviarlo al worker."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code:
             logger.info(f"Risultato per {code} ({state}) ignorato, contesto fetch cambiato.")
             return
        logger.info(f"Processando risultato finale per {code}: {state}")
        self.last_cells = cells
        context_to_clear = self._current_fetch_context
        self._current_fetch_context = None
        self._set_status_message(f"Risultato per {code}: {state}", is_waiting=False)
        if self.worker:
            logger.debug(f"Invio fetchCompleted per {code} con stato {state} al worker.")
            self.fetchCompleted.emit(code, state, self.last_cells)
        else:
             logger.warning(f"Worker non trovato prima di inviare risultato per {code}. Segnale non inviato.")

    def open_nsis_url_test(self):
        """Carica about:blank e poi l'URL reale con ritardo."""
        logger.info("Apertura URL NSIS (via about:blank)...")
        try:
            blank_url = QtCore.QUrl("about:blank")
            self.view.load(blank_url)
            QtCore.QTimer.singleShot(500, self.load_real_url)
        except Exception as e:
            logger.exception("Eccezione in open_nsis_url_test")
            QtWidgets.QMessageBox.critical(self, "Errore Test", f"Errore caricando about:blank.\n{e}")

    def load_real_url(self):
        """Carica l'URL effettivo del sito NSIS."""
        if self._current_fetch_context: self._current_fetch_context['page_load_error'] = False
        try:
            url_str = URL_NSIS
            real_url = QtCore.QUrl(url_str)
            logger.info(f"Carico URL: {real_url.toString()}")
            if real_url.isValid():
                self.view.load(real_url)
                logger.debug("Chiamata load URL reale completata.")
            else:
                logger.error(f"URL non valido: {url_str}")
                QtWidgets.QMessageBox.warning(self, "URL Non Valido", f"URL non valido:\n{url_str}")
        except Exception as e:
            logger.exception("Eccezione in load_real_url")
            QtWidgets.QMessageBox.critical(self, "Errore Caricamento", f"Errore caricando URL reale.\n{e}")

    def create_badge(self, icon, label_text, color):
        """Crea un widget badge (QFrame + QLabel) con colori e testo specificati."""
        frame = QtWidgets.QFrame();
        try: bg_color = QtGui.QColor(color); lum = (0.299*bg_color.red()+0.587*bg_color.green()+0.114*bg_color.blue())/255; tc = "black" if lum > 0.6 else "white"
        except Exception as e: logger.warning(f"Errore colore badge {color}: {e}"); tc = "black"
        frame.setStyleSheet(f"""QFrame{{background-color:{color};border-radius:6px;padding:4px 6px;border:none;}} QLabel{{color:{tc};font-weight:600;font-size:11px;}}""")
        frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Fixed); layout = QtWidgets.QVBoxLayout(frame); layout.setContentsMargins(2,2,2,2); layout.setSpacing(1); layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label = QtWidgets.QLabel(f"{icon} {label_text}: 0"); label.setWordWrap(True); label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter); label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sparkle = QtWidgets.QLabel(""); sparkle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter); sparkle.setFixedHeight(12); layout.addWidget(label); layout.addWidget(sparkle)
        return frame, label, sparkle

    def flash_emoji(self, sparkle_label, emoji="✨"):
        """Mostra brevemente un emoji sulla label 'sparkle' del badge."""
        sparkle_label.setText(emoji);
        QtCore.QTimer.singleShot(700, lambda: sparkle_label.setText("") if sparkle_label else None)

    def animate_badge(self, badge_frame):
        """Applica un'animazione di fade-in al badge quando appare."""
        if not badge_frame.isVisible(): badge_frame.setVisible(True)
        current_effect = badge_frame.graphicsEffect()
        if isinstance(current_effect, QtWidgets.QGraphicsOpacityEffect) and current_effect.opacity() != 1.0:
             badge_frame.setGraphicsEffect(None)
        effect = QtWidgets.QGraphicsOpacityEffect(badge_frame); badge_frame.setGraphicsEffect(effect)
        animation = QtCore.QPropertyAnimation(effect, b"opacity", badge_frame)
        animation.setDuration(600); animation.setStartValue(0.3); animation.setEndValue(1.0)
        animation.finished.connect(lambda bf=badge_frame: bf.setGraphicsEffect(None) if bf.graphicsEffect() else None)
        animation.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def _save_results_to_excel(self, results_to_save, file_path):
        """Salva i risultati raccolti nel file Excel specificato."""
        logger.info(f"Inizio salvataggio risultati su: {file_path}")
        self.status.setText("⏳ Salvataggio su file Excel..."); QtWidgets.QApplication.processEvents()
        try:
            wb = load_workbook(file_path); ws = wb.active; header = [c.value for c in ws[1]]; hc = [str(h).strip().lower() if h is not None else '' for h in header]
            try: cri = hc.index(COL_RICERCA.lower()) + 1
            except ValueError: raise ValueError(f"Colonna '{COL_RICERCA}' non trovata.")
            tcm = { COL_STATO: DEFAULT_IDX_STATO, COL_PROTOCOLLO: DEFAULT_IDX_PROTOCOLLO, COL_PROVVEDIMENTO: DEFAULT_IDX_PROVVEDIMENTO, COL_DATA_PROVV: DEFAULT_IDX_DATA_PROVV, COL_CODICE_RIS: DEFAULT_IDX_CODICE_RIS, COL_NOTE: DEFAULT_IDX_NOTE }
            ci = {};
            header_lower_map = {str(h).strip().lower(): idx + 1 for idx, h in enumerate(header) if h is not None}
            for cn_config, di in tcm.items():
                 cn_lower = cn_config.lower()
                 if cn_lower in header_lower_map:
                     ci[cn_config] = header_lower_map[cn_lower]
                 else:
                     ci[cn_config] = di
                     logger.warning(f"Colonna '{cn_config}' non trovata nel file, usando indice default {di}.")
            rm = {};
            for r_idx, row in enumerate(ws.iter_rows(min_row=2, min_col=cri, max_col=cri), start=2):
                cell_value = str(row[0].value).strip() if row[0].value is not None else ""
                if cell_value:
                    rm[cell_value.lower()] = r_idx
            ru = 0
            for res in results_to_save:
                ic = res.get('Input Code', '').strip(); ri = rm.get(ic.lower()) if ic else None
                if ri is not None:
                    ws.cell(row=ri, column=ci[COL_STATO], value=res.get('Stato', ''))
                    ws.cell(row=ri, column=ci[COL_PROTOCOLLO], value=res.get('Protocollo uscita', ''))
                    ws.cell(row=ri, column=ci[COL_PROVVEDIMENTO], value=res.get('Provvedimento', ''))
                    ws.cell(row=ri, column=ci[COL_DATA_PROVV], value=res.get('Data Provvedimento', ''))
                    ws.cell(row=ri, column=ci[COL_CODICE_RIS], value=res.get('Codice richiesta (risultato)', ''))
                    ws.cell(row=ri, column=ci[COL_NOTE], value=res.get('Note Usmaf', ''))
                    ru += 1
                elif ic:
                    logger.warning(f"Impossibile trovare riga per codice input durante salvataggio: {ic}.")
            target_col_idx_ris = ci.get(COL_CODICE_RIS)
            if target_col_idx_ris:
                 logger.debug(f"Applico formato testo a colonna risultato {target_col_idx_ris}")
                 for r_idx in range(2, ws.max_row + 1):
                      cell = ws.cell(row=r_idx, column=target_col_idx_ris);
                      if cell.value is not None: cell.number_format = numbers.FORMAT_TEXT
            logger.debug(f"Applico formato testo a colonna input {cri}")
            for r_idx in range(2, ws.max_row + 1):
                 cell = ws.cell(row=r_idx, column=cri);
                 if cell.value is not None: cell.number_format = numbers.FORMAT_TEXT
            wb.save(file_path)
            logger.info(f"Salvataggio completato. {ru}/{len(results_to_save)} risultati aggiornati/trovati.")
            self.status.setText('✅ Salvataggio Completato!')
        except ValueError as ve:
            err = str(ve)
            logger.error(f"Errore (ValueError) durante salvataggio Excel: {err}")
            self.status.setText(f"❌ Errore Salvataggio: Colonna mancante?");
            QtWidgets.QMessageBox.critical(self, "Errore Salvataggio", f"{err}\nSalvataggio annullato.")
        except PermissionError:
            err = f"Permesso negato salvataggio '{os.path.basename(file_path)}'. Il file è aperto?"
            logger.error(err)
            self.status.setText(f"❌ Errore Permesso");
            QtWidgets.QMessageBox.critical(self, "Errore Salvataggio", err)
        except Exception as e:
            err = f"Errore imprevisto durante il salvataggio."
            logger.exception(err)
            self.status.setText(f"❌ Errore Salvataggio");
            QtWidgets.QMessageBox.critical(self, "Errore Salvataggio", f"{err}\n{e}\n\nVedi app_log.log per dettagli.")

    def _reset_badges(self):
        for widget in list(self._badge_widgets):
             try:
                 self.badge_layout.removeWidget(widget)
                 widget.setVisible(False)
                 self._badge_widgets.remove(widget)
             except Exception as e:
                  logger.warning(f"Errore durante rimozione badge: {e}")
        for prefix, (card, label, sparkle) in self._badge_widgets_map.items():
            label.setText(f"{prefix}: 0")
            sparkle.setText("")
            card.setVisible(False)

    def _reset_ui_after_processing(self):
        """Riabilita/Disabilita i pulsanti alla fine o in caso di errore/interruzione."""
        logger.debug("Resetting UI after processing...")
        self.btn_start.setEnabled(True); self.btn_stop.setEnabled(False); self.btn_open.setEnabled(True)
        self._set_status_message(self.status.text(), is_waiting=False)

    # Rimosso log_message

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Gestisce l'evento di chiusura della finestra."""
        logger.info("Evento Chiusura Finestra ricevuto.")
        if self.thread is not None and self.thread.isRunning():
            logger.info("Richiesta stop al worker prima di chiudere...")
            self.stop_processing()
            logger.info("Attesa (max 1s) termine worker...")
            if not self.thread.wait(1000):
                 logger.warning("Timeout attesa worker. Il thread potrebbe non terminare correttamente.")
        event.accept()

# --- Punto di ingresso principale ---
if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())