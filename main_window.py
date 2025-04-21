# -*- coding: utf-8 -*-
# main_window.py
# Contains the main application window class and the Worker class
# Versione con QThread + Lettura Openpyxl - FIX ASINCRONO V8 + Miglioramenti UI + Icone QTAwesome + Funzione Salvataggio

import os
import sys
import time
import datetime # <= AGGIUNTO per timestamp nel salvataggio
import logging
import logging.handlers
from PyQt6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets, QtWebChannel, QtWebEngineCore

# Import openpyxl e stili necessari
import openpyxl # <= SPOSTATO E ASSICURATO qui
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.styles import Font, Color, PatternFill, numbers, Alignment # <= AGGIUNTI stili per salvataggio
from openpyxl.utils import get_column_letter # <= AGGIUNTO se necessario per manipolazione colonne
import traceback

# Importa qtawesome e imposta flag di disponibilità
try:
    import qtawesome as qta
    QTAWESOME_AVAILABLE = True
    print("INFO: Libreria 'qtawesome' caricata correttamente.")
except ImportError:
    QTAWESOME_AVAILABLE = False
    print("WARNING: Libreria 'qtawesome' non trovata. "
          "Installa con 'pip install qtawesome' per icone moderne. "
          "Verranno usate le icone standard/nessuna icona.")

# Import from our modules
from config import (
    MAX_RETRIES, FETCH_TIMEOUT_MS, FETCH_CHECK_INTERVAL_MS, STATO_SELECTOR,
    ALL_CELLS_JS, COLOR_STATUS_WAITING, COLOR_STATUS_ERROR, COLOR_STATUS_SUCCESS,
    COLOR_STATUS_INFO, COLOR_STATUS_DEFAULT, COLOR_ANNULATA, COLOR_APERTA,
    COLOR_CHIUSA, COLOR_LAVORAZIONE, COLOR_INVIATA, COLOR_ECCEZIONI,
    COL_RICERCA, COL_STATO, COL_PROTOCOLLO, COL_PROVVEDIMENTO,
    COL_DATA_PROVV, COL_CODICE_RIS, COL_NOTE, DEFAULT_IDX_STATO,
    DEFAULT_IDX_PROTOCOLLO, DEFAULT_IDX_PROVVEDIMENTO, DEFAULT_IDX_DATA_PROVV,
    DEFAULT_IDX_CODICE_RIS, DEFAULT_IDX_NOTE, DELAY_AFTER_INPUT_JS, DELAY_AFTER_CLICK_JS, DELAY_BETWEEN_RETRIES,
    MAX_NULL_CHECKS, URL_NSIS
)
# Assicurati che questi import esistano o crea i file corrispondenti
try:
    from ui_components import CustomProgressBar, SpinnerWidget
    from web_engine import WebEnginePage, JSBridge
except ImportError as e:
    logging.basicConfig(level=logging.ERROR) # Setup logger base se fallisce qui
    logging.error(f"Impossibile importare ui_components o web_engine: {e}", exc_info=True)
    class CustomProgressBar(QtWidgets.QProgressBar): pass
    class SpinnerWidget(QtWidgets.QWidget):
        def startAnimation(self): self.show()
        def stopAnimation(self): self.hide()
    class WebEnginePage(QtWebEngineWidgets.QWebEnginePage): pass
    class JSBridge(QtCore.QObject): pass

# ------------------- Worker Class (per QThread) -------------------
# (Worker class rimane invariata rispetto alla versione precedente fornita)
class Worker(QtCore.QObject):
    progress = QtCore.pyqtSignal(int, int)
    statusUpdate = QtCore.pyqtSignal(str)
    logUpdate = QtCore.pyqtSignal(str) # Signal to send log messages to main thread
    badgeUpdate = QtCore.pyqtSignal(str, int)
    finished = QtCore.pyqtSignal()
    resultsReady = QtCore.pyqtSignal(list)
    requestFetch = QtCore.pyqtSignal(str) # Signal to request fetching a code

    def __init__(self, codes_to_process):
        super().__init__()
        self.codes = codes_to_process
        self._stop_requested = False
        self._results = []
        self._current_code_index = 0
        self._total_codes = len(codes_to_process)
        # Initialize status counts
        self._counts = { "annullata": 0, "aperta": 0, "chiusa": 0, "lavorazione": 0, "inviata": 0, "eccezioni": 0 }
        # Map normalized status to badge text
        self._badge_map = {
            "ANNULLATA": "🟡 Annullate", "APERTA": "🟢 Aperte", "CHIUSA": "✅ Chiuse",
            "IN LAVORAZIONE": "🟠 In lavorazione", "INVIATA": "📤 Inviate",
            "ECCEZIONE": "❗ Eccezioni" # Specific key for exceptions
        }
        # Map normalized status to the key used in self._counts
        self._count_keys = {
            "ANNULLATA": "annullata", "APERTA": "aperta", "CHIUSA": "chiusa",
            "IN LAVORAZIONE": "lavorazione", "INVIATA": "inviata"
            # Exceptions are handled separately
        }
        # Set of states considered exceptions
        self._exception_states = {
            "NON TROVATO", "ERRORE TIMEOUT", "ERRORE PAGINA", "ERRORE INTERNO FETCH",
            "SCONOSCIUTO", "INTERROTTO",
            "ERRORE CARICAMENTO PAGINA", "ELEMENTO NON TROVATO (JS)", "ERRORE RISULTATO JS"
        }
        self._finished_emitted_after_stop = False # Flag to prevent multiple finished signals on stop

    def run(self):
        """Main execution logic for the worker thread."""
        print("--- Worker Thread Started ---")
        # Reset state at the beginning of each run
        self._results = []; self._counts = {k: 0 for k in self._counts}; self._stop_requested = False
        self._finished_emitted_after_stop = False
        if not self.codes:
            self.logUpdate.emit("Nessun codice da processare nel worker.")
            self.finished.emit(); return

        self.progress.emit(0, self._total_codes) # Initial progress
        self._current_code_index = 0

        if not self._stop_requested:
            if self._current_code_index < len(self.codes):
                code = self.codes[self._current_code_index]
                self.statusUpdate.emit(f"Inizio elaborazione per: {code} (1/{self._total_codes})")
                # Request the main thread to fetch the first code
                self.requestFetch.emit(code)
            else:
                self.logUpdate.emit("Lista codici vuota."); self.finished.emit()
        else:
            self.logUpdate.emit("❌ Interrotto prima dell'inizio."); self.finished.emit()

    @QtCore.pyqtSlot(str, str, list)
    def processFetchedResult(self, code, state, last_cells):
        """Processes the result received from the main thread for a code."""
        # If stop was requested while fetching, handle termination
        if self._stop_requested:
            if not self._finished_emitted_after_stop:
                thread = self.thread() # Get the QThread instance this worker lives in
                if thread and thread.isRunning():
                    # Log interruption and emit final signals
                    self.logUpdate.emit(f"❌ Elaborazione interrotta nel worker (risultato per {code} ricevuto: {state}). Fine.")
                    self.resultsReady.emit(self._results) # Emit collected results so far
                    self.finished.emit()
                    self._finished_emitted_after_stop = True
            return # Stop processing further

        current_idx = self._current_code_index
        # Log the received state
        self.logUpdate.emit(f"{current_idx + 1}/{self._total_codes} ➜ Codice: {code} | Stato Web: {state}")

        # Normalize state and update counts/badges
        normalized_state_upper = state.strip().upper()
        if normalized_state_upper in self._exception_states:
            status_key_for_count = "eccezioni"
            badge_prefix = self._badge_map["ECCEZIONE"]
        else:
            # Use normalized state to find the count key, default to 'eccezioni' if unknown
            status_key_for_count = self._count_keys.get(normalized_state_upper, "eccezioni")
            # Use normalized state to find the badge prefix, default to exception badge if unknown
            badge_prefix = self._badge_map.get(normalized_state_upper, self._badge_map["ECCEZIONE"])
            # If an unknown state defaulted to 'eccezioni', log a warning
            if status_key_for_count == "eccezioni" and normalized_state_upper not in self._exception_states:
                 self.logUpdate.emit(f"⚠️ Stato non mappato: '{state}'. Conteggiato come Eccezione.")


        # Ensure the key exists before incrementing (should always exist now)
        if status_key_for_count not in self._counts:
             self.logUpdate.emit(f"⚠️ Chiave conteggio interna non prevista: {status_key_for_count} per stato {state}")
             status_key_for_count = "eccezioni" # Fallback safely

        self._counts[status_key_for_count] += 1
        count_to_display = self._counts[status_key_for_count]
        # Emit signal to update the corresponding badge in the UI
        self.badgeUpdate.emit(badge_prefix, count_to_display)

        # Prepare result dictionary based on received cells
        stato_res = state # Use the state as received
        # Safely get cell values, providing defaults if index is out of bounds
        protocollo_uscita_res = last_cells[5] if len(last_cells) > 5 else ''
        provvedimento_res = last_cells[6] if len(last_cells) > 6 else ''
        data_provvedimento_res = last_cells[7] if len(last_cells) > 7 else ''
        # Use the code found in the table if available, otherwise fallback to input code
        codice_richiesta_risultato_res = last_cells[8] if len(last_cells) > 8 and last_cells[8] else code
        note_usmaf_res = last_cells[10] if len(last_cells) > 10 else ''
        # Prepend the exception state to notes if it was an exception
        if normalized_state_upper in self._exception_states:
            note_usmaf_res = f"Stato recuperato: {state}. {note_usmaf_res}".strip()

        # Append the result to the list
        self._results.append({
            'Input Code': code, # Chiave usata per matchare la riga in Excel
            'Stato': stato_res,
            'Protocollo uscita': protocollo_uscita_res,
            'Provvedimento': provvedimento_res,
            'Data Provvedimento': data_provvedimento_res,
            'Codice richiesta (risultato)': codice_richiesta_risultato_res,
            'Note Usmaf': note_usmaf_res
        })

        # Update overall progress
        self.progress.emit(current_idx + 1, self._total_codes)
        self._current_code_index += 1 # Move to the next code index

        # Check if there are more codes to process
        if self._current_code_index < self._total_codes:
            next_code = self.codes[self._current_code_index]
            self.statusUpdate.emit(f"Richiesta fetch per: {next_code} ({self._current_code_index + 1}/{self._total_codes})")
            # Request the main thread to fetch the next code
            self.requestFetch.emit(next_code)
        else:
            # All codes processed
            self.logUpdate.emit("✅ Elaborazione codici completata.")
            self.statusUpdate.emit("✅ Elaborazione completata.")
            # Emit final results and finished signal
            self.resultsReady.emit(self._results)
            self.finished.emit()

    def request_stop(self):
        """Sets the stop flag for the worker."""
        print("--- Worker Stop Requested ---")
        self._stop_requested = True
# ------------------- Fine Worker Class -------------------


# ------------------- Classe App Modificata -------------------
# Get a logger for this module
logger = logging.getLogger(__name__) # Logger definito qui per essere usato nella classe

class App(QtWidgets.QWidget):
    """Classe principale dell'applicazione GUI."""
    fetchCompleted = QtCore.pyqtSignal(str, str, list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controllo Stato Richiesta - NSIS")
        self.setGeometry(QtCore.QRect(100, 100, 1200, 800))

        self._badge_widgets = set()
        self._badge_widgets_map = {} # Inizializza mappa badge
        self.max_retries = MAX_RETRIES
        self.last_cells = []
        self.current_file_path = None
        self.thread = None
        self.worker = None
        self._current_fetch_context = None
        self._active_badge_animations = {}

        # Colori e opzioni icone qtawesome (centralizzati)
        self.icon_color_nav = '#555555' # Grigio scuro per nav
        self.icon_color_open = '#1A1A1A' # Colore scuro standard
        self.icon_color_start = 'white'  # Bianco per contrasto su blu
        self.icon_color_stop = '#D32F2F'  # Rosso per stop

        # Setup Logging PRIMA dell'UI per catturare eventuali errori UI
        self._setup_logging()
        # Setup UI
        self._setup_ui()
        # Setup WebEngine dopo che la UI (self.view) è stata creata
        self._setup_webengine()

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
            }
            QPushButton#NavButton {
                padding: 2px 5px;
                min-width: 28px; max-width: 28px;
                min-height: 28px; max-height: 28px;
                background-color: #FFFFFF; border: 1px solid #D0D0D0;
                border-radius: 4px; outline: none;
            }
            QPushButton#NavButton:hover { background-color: #F0F0F0; }
            QPushButton#NavButton:pressed { background-color: #E0E0E0; border: 1px solid #C0C0C0; }
            QPushButton#NavButton:disabled { background-color: #F5F5F5; border: 1px solid #E8E8E8; }
        """)

        logger.info("Applicazione inizializzata con icone qtawesome (se disponibile).")


    def _setup_logging(self):
        """Configura il modulo logging per Console e File."""
        log_level = logging.DEBUG
        log_format_standard = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        log_file = "app_log.log"

        root_logger = logging.getLogger()
        if not root_logger.hasHandlers():
             root_logger.setLevel(log_level)
             for handler in root_logger.handlers[:]:
                 root_logger.removeHandler(handler)
                 handler.close()

             console_handler = logging.StreamHandler(sys.stdout)
             console_handler.setFormatter(log_format_standard)
             console_handler.setLevel(logging.INFO)
             root_logger.addHandler(console_handler)

             try:
                 file_handler = logging.handlers.RotatingFileHandler(
                     log_file, maxBytes=1 * 1024 * 1024, backupCount=3, encoding='utf-8'
                 )
                 file_handler.setFormatter(log_format_standard)
                 file_handler.setLevel(logging.DEBUG)
                 root_logger.addHandler(file_handler)
             except Exception as e:
                  print(f"ERRORE CRITICO: Impossibile configurare FileHandler: {e}")

             logging.getLogger("openpyxl").setLevel(logging.WARNING)
             logger.info("Sistema di logging configurato (Console, File).")
        else:
             logger.info("Sistema di logging già configurato.")


    def _setup_ui(self):
        """Crea e organizza i widget dell'interfaccia utente con icone qtawesome."""
        main_layout = QtWidgets.QHBoxLayout(self)

        # --- Web View Frame ---
        web_view_frame = QtWidgets.QFrame()
        self.web_view_frame = web_view_frame
        web_view_frame.setObjectName("WebViewContainer")
        web_view_frame.setStyleSheet("""
            QFrame#WebViewContainer {
                border: 1px solid #D0D0D0; border-radius: 8px; background-color: white;
            }
        """)
        web_view_frame.setContentsMargins(0, 0, 0, 0)

        web_view_layout = QtWidgets.QVBoxLayout(web_view_frame)
        padding_size = 4
        web_view_layout.setContentsMargins(padding_size, padding_size, padding_size, padding_size)
        web_view_layout.setSpacing(5)

        # Creazione della Web View (anticipata)
        self.view = QtWebEngineWidgets.QWebEngineView()

        # --- Barra di Navigazione Web con Icone QTAwesome ---
        nav_toolbar_layout = QtWidgets.QHBoxLayout()
        nav_toolbar_layout.setContentsMargins(0, 0, 0, 0)
        nav_toolbar_layout.setSpacing(3)

        self.btn_back = QtWidgets.QPushButton()
        self.btn_back.setObjectName("NavButton")
        if QTAWESOME_AVAILABLE: icon_back = qta.icon('fa5s.arrow-left', color=self.icon_color_nav)
        else: icon_back = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowBack)
        self.btn_back.setIcon(icon_back); self.btn_back.setToolTip("Indietro")
        self.btn_back.setEnabled(False); self.btn_back.clicked.connect(self.view.back)
        nav_toolbar_layout.addWidget(self.btn_back)

        self.btn_forward = QtWidgets.QPushButton()
        self.btn_forward.setObjectName("NavButton")
        if QTAWESOME_AVAILABLE: icon_forward = qta.icon('fa5s.arrow-right', color=self.icon_color_nav)
        else: icon_forward = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowForward)
        self.btn_forward.setIcon(icon_forward); self.btn_forward.setToolTip("Avanti")
        self.btn_forward.setEnabled(False); self.btn_forward.clicked.connect(self.view.forward)
        nav_toolbar_layout.addWidget(self.btn_forward)

        self.btn_reload = QtWidgets.QPushButton()
        self.btn_reload.setObjectName("NavButton")
        if QTAWESOME_AVAILABLE: icon_reload = qta.icon('fa5s.sync-alt', color=self.icon_color_nav)
        else: icon_reload = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload)
        self.btn_reload.setIcon(icon_reload); self.btn_reload.setToolTip("Ricarica Pagina")
        self.btn_reload.setEnabled(False); self.btn_reload.clicked.connect(self.view.reload)
        nav_toolbar_layout.addWidget(self.btn_reload)

        nav_toolbar_layout.addStretch()
        web_view_layout.addLayout(nav_toolbar_layout)

        web_view_layout.addWidget(self.view)
        main_layout.addWidget(web_view_frame, stretch=3)

        # --- Pannello Controlli Destro ---
        right_column_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(right_column_layout, stretch=1)

        ctrl_container = QtWidgets.QFrame()
        ctrl_container.setObjectName("ControlContainer")
        ctrl_container.setStyleSheet("""
            #ControlContainer { background-color: #f8f8f8; border: 1px solid #dddddd;
                               border-radius: 8px; padding: 10px; }
        """)
        ctrl_layout = QtWidgets.QVBoxLayout(ctrl_container)
        ctrl_layout.setContentsMargins(5, 5, 5, 5); ctrl_layout.setSpacing(8)
        right_column_layout.addWidget(ctrl_container)

        professional_button_style = """
            QPushButton { background-color: #F9F9F9; color: #1A1A1A; border: 1px solid #E0E0E0;
                          padding: 7px 12px; border-radius: 4px; font-weight: 600; outline: none;
                          text-align: center; }
            QPushButton:hover { background-color: #F0F0F0; border: 1px solid #D0D0D0; }
            QPushButton:pressed { background-color: #E0E0E0; color: #000000; border: 1px solid #C0C0C0; }
            QPushButton:disabled { background-color: #FDFDFD; color: #B0B0B0; border: 1px solid #F0F0F0; }
        """
        primary_button_style = """
            QPushButton { background-color: #0078D4; color: white; border: none;
                          padding: 8px 12px; border-radius: 4px; font-weight: 600; outline: none;
                          text-align: center; }
            QPushButton:hover { background-color: #106EBF; }
            QPushButton:pressed { background-color: #005A9E; }
            QPushButton:disabled { background-color: #F0F0F0; color: #B0B0B0; border: none; }
        """
        stop_button_style = """
             QPushButton { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5;
                           padding: 7px 12px; border-radius: 4px; font-weight: 600; outline: none;
                           text-align: center; }
            QPushButton:hover { background-color: #FECACA; border-color: #F87171; }
            QPushButton:pressed { background-color: #FCA5A5; color: #991B1B; border-color: #EF4444;}
            QPushButton:disabled { background-color: #FEF2F2; color: #FCA5A5; border-color: #FEE2E2; }
        """

        self.btn_open = QtWidgets.QPushButton(" Apri NSIS")
        self.btn_open.setObjectName("ActionButton")
        if QTAWESOME_AVAILABLE: self.btn_open.setIcon(qta.icon('fa5s.external-link-alt', color=self.icon_color_open))
        self.btn_open.clicked.connect(self.open_nsis_url_test); self.btn_open.setStyleSheet(professional_button_style)
        ctrl_layout.addWidget(self.btn_open)

        self.btn_start = QtWidgets.QPushButton(" Seleziona e Avvia")
        self.btn_start.setObjectName("ActionButton")
        if QTAWESOME_AVAILABLE: self.btn_start.setIcon(qta.icon('fa5s.play', color=self.icon_color_start))
        self.btn_start.clicked.connect(self.start_processing); self.btn_start.setStyleSheet(primary_button_style)
        ctrl_layout.addWidget(self.btn_start)

        self.btn_stop = QtWidgets.QPushButton(" Interrompi")
        self.btn_stop.setObjectName("ActionButton")
        if QTAWESOME_AVAILABLE: self.btn_stop.setIcon(qta.icon('fa5s.stop', color=self.icon_color_stop))
        self.btn_stop.clicked.connect(self.stop_processing); self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet(stop_button_style)
        ctrl_layout.addWidget(self.btn_stop)

        ctrl_layout.addSpacing(10)
        line1 = QtWidgets.QFrame(); line1.setFrameShape(QtWidgets.QFrame.Shape.HLine); line1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        ctrl_layout.addWidget(line1); ctrl_layout.addSpacing(10)

        progress_layout = QtWidgets.QHBoxLayout(); progress_layout.setContentsMargins(0,0,0,0); progress_layout.setSpacing(5)
        self.spinner = SpinnerWidget(self); progress_layout.addWidget(self.spinner)
        self.progress = CustomProgressBar(); self.progress.setRange(0, 100); self.progress.setValue(0)
        progress_layout.addWidget(self.progress, stretch=1)
        self.progress_label = QtWidgets.QLabel("0%"); self.progress_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.progress_label.setMinimumWidth(35); self.progress_label.setStyleSheet("color: #1A1A1A;")
        progress_layout.addWidget(self.progress_label)
        ctrl_layout.addLayout(progress_layout)

        self.status = QtWidgets.QLabel("Pronto.", alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("color: #1A1A1A;")
        ctrl_layout.addWidget(self.status)

        self.log = QtWidgets.QTextEdit()  # Crea il widget
        self.log.setReadOnly(True)  # Lo rende non modificabile dall'utente

        # La riga del placeholder è stata rimossa, NON c'è più setPlaceholderText qui.

        # Applica uno stile per il log (colore testo più scuro per leggibilità)
        self.log.setStyleSheet(f""" QTextEdit {{
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
                font-size: 10px;
                color: #333333; /* Nero/Grigio scuro invece di grigio chiaro */
                background-color: #FFFFFF;
            }} """)
        ctrl_layout.addWidget(self.log)  # Aggiunge il widget al layout


        ctrl_layout.addSpacing(10)
        line2 = QtWidgets.QFrame(); line2.setFrameShape(QtWidgets.QFrame.Shape.HLine); line2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        ctrl_layout.addWidget(line2); ctrl_layout.addSpacing(10)

        self.badge_layout = QtWidgets.QVBoxLayout(); self.badge_layout.setSpacing(4)
        ctrl_layout.addLayout(self.badge_layout)

        badge_data = [
            ("🟡", "Annullate", COLOR_ANNULATA), ("🟢", "Aperte", COLOR_APERTA),
            ("✅", "Chiuse", COLOR_CHIUSA), ("🟠", "In lavorazione", COLOR_LAVORAZIONE),
            ("📤", "Inviate", COLOR_INVIATA), ("❗", "Eccezioni", COLOR_ECCEZIONI)
        ]
        self._badge_info_list = [] # Riempi dopo
        self._badge_widgets_map = {} # Resetta mappa
        for icon, text, color in badge_data:
            badge_tuple = self.create_badge(icon, text, color)
            self._badge_info_list.append(badge_tuple)
            # Mappa il prefisso (es. "🟡 Annullate") alla tupla completa del badge
            prefix = badge_tuple[0].property("badgePrefix")
            if prefix:
                 self._badge_widgets_map[prefix] = badge_tuple
            badge_tuple[0].setVisible(False) # Nascondi inizialmente

        right_column_layout.addStretch()

        firma_h_layout = QtWidgets.QHBoxLayout(); firma_h_layout.setContentsMargins(0, 0, 0, 0)
        firma_h_layout.addStretch()
        self.firma_label = QtWidgets.QLabel("<i>©2025 ST, version 1.3-savefix</i>") # Versione Aggiornata
        self.firma_label.setStyleSheet("QLabel { color: #777777; font-size: 9px; margin-right: 15px; }")
        firma_h_layout.addWidget(self.firma_label)
        right_column_layout.addLayout(firma_h_layout)

        self.view.urlChanged.connect(self._update_navigation_buttons_state)
        self.view.loadFinished.connect(self._update_navigation_buttons_state)
        self._update_navigation_buttons_state() # Stato iniziale


    # --- Metodi Gestione WebEngine, Processo, UI ---

    def _setup_webengine(self):
        """Inizializza la pagina WebEngine, il bridge e connette segnali."""
        page = WebEnginePage(self.view) if 'WebEnginePage' in globals() else QtWebEngineWidgets.QWebEnginePage(self.view)
        self.view.setPage(page)

        self.bridge = JSBridge() if 'JSBridge' in globals() else QtCore.QObject()
        self.channel = QtWebChannel.QWebChannel()
        if hasattr(self.bridge, 'evaluate') or hasattr(self.bridge, 'receive'):
             logger.debug("Registering JSBridge object 'bridge'")
             self.channel.registerObject('bridge', self.bridge)
        else:
             logger.warning("JSBridge object does not have expected methods, not registered.")

        page = self.view.page()
        if page:
            page.setWebChannel(self.channel)
            page.setBackgroundColor(QtCore.Qt.GlobalColor.transparent)
        else:
            logger.critical("Impossibile ottenere la pagina web dopo averla impostata.")
            QtWidgets.QMessageBox.critical(self, "Errore Critico", "Impossibile inizializzare componente Web.")


    @QtCore.pyqtSlot(bool)
    def _handle_page_load_finished(self, ok):
        """Gestisce il segnale loadFinished (SOLO per logica fetch)."""
        logger.debug(f"Page load finished (for fetch context), success: {ok}")
        if self._current_fetch_context:
            self._current_fetch_context['page_load_error'] = not ok
            if not ok:
                logger.error(f"Errore durante il caricamento della pagina (fetch context): {self.view.url().toString()}")
                QtCore.QTimer.singleShot(0, lambda ctx=self._current_fetch_context: \
                    self._process_fetch_result(ctx['code'], 'Errore Caricamento Pagina', []) if ctx else None)

    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(QtCore.QUrl)
    @QtCore.pyqtSlot(bool)
    def _update_navigation_buttons_state(self, *args):
        """Aggiorna stato e colore icone dei pulsanti di navigazione web."""
        page = self.view.page()
        if page:
            history = page.history()
            can_go_back = history.canGoBack()
            self.btn_back.setEnabled(can_go_back)
            if QTAWESOME_AVAILABLE: self.btn_back.setIcon(qta.icon('fa5s.arrow-left', color=self.icon_color_nav if can_go_back else '#CCCCCC'))

            can_go_forward = history.canGoForward()
            self.btn_forward.setEnabled(can_go_forward)
            if QTAWESOME_AVAILABLE: self.btn_forward.setIcon(qta.icon('fa5s.arrow-right', color=self.icon_color_nav if can_go_forward else '#CCCCCC'))

            is_valid_url = not page.url().isEmpty() and page.url().isValid()
            self.btn_reload.setEnabled(is_valid_url)
            if QTAWESOME_AVAILABLE: self.btn_reload.setIcon(qta.icon('fa5s.sync-alt', color=self.icon_color_nav if is_valid_url else '#CCCCCC'))
        else:
            self.btn_back.setEnabled(False); self.btn_forward.setEnabled(False); self.btn_reload.setEnabled(False)
            if QTAWESOME_AVAILABLE: # Imposta icone grigie disabilitate
                 self.btn_back.setIcon(qta.icon('fa5s.arrow-left', color='#CCCCCC'))
                 self.btn_forward.setIcon(qta.icon('fa5s.arrow-right', color='#CCCCCC'))
                 self.btn_reload.setIcon(qta.icon('fa5s.sync-alt', color='#CCCCCC'))


    def start_processing(self):
        """Avvia il processo: seleziona file, leggi codici, avvia worker thread."""
        logger.info("Avvio start_processing...")
        if self.thread is not None and self.thread.isRunning():
            logger.warning("Elaborazione già in corso."); return

        logger.debug("Prima di QFileDialog.getOpenFileName")
        options = QtWidgets.QFileDialog.Option.DontUseNativeDialog if sys.platform == 'linux' else QtWidgets.QFileDialog.Option(0)
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Seleziona file Excel", "", "Excel Files (*.xlsx *.xls)", options=options )
        if not file_path: logger.info("Nessun file selezionato, uscita."); return
        self.current_file_path = file_path; logger.info(f"File selezionato: {self.current_file_path}")

        codes = []; workbook = None; logger.debug("Inizio blocco lettura Excel")
        try:
            logger.info(f"Lettura file (openpyxl): {os.path.basename(file_path)}")
            # Usiamo read_only=True, data_only=True per la lettura iniziale veloce
            workbook = load_workbook(filename=file_path, read_only=True, data_only=True, keep_vba=False)
            if not workbook.sheetnames: raise ValueError("Il file Excel non contiene fogli.")
            sheet = workbook.active; logger.debug(f"Foglio attivo: {sheet.title}")
            if sheet.max_row <= 1: raise ValueError("Foglio vuoto o solo intestazione.")

            header_row = sheet[1]; ricerca_col_idx = -1
            for idx, cell in enumerate(header_row):
                if cell.value is not None and str(cell.value).strip().lower() == COL_RICERCA.lower():
                    ricerca_col_idx = idx + 1; break # +1 perché openpyxl è 1-based per le colonne
            if ricerca_col_idx == -1: raise ValueError(f"Colonna '{COL_RICERCA}' non trovata.")
            logger.debug(f"Colonna ricerca '{COL_RICERCA}' trovata all'indice {ricerca_col_idx}")

            code_count = 0
            # Leggi solo la colonna COL_RICERCA
            for row_cells in sheet.iter_rows(min_row=2, min_col=ricerca_col_idx, max_col=ricerca_col_idx):
                cell = row_cells[0] # C'è solo una cella per riga in questo iteratore
                if cell.value is not None:
                    code = str(cell.value).strip()
                    # Aggiungi controllo per ignorare valori vuoti o 'nan' comuni da pandas/excel
                    if code and code.lower() != 'nan':
                        codes.append(code); code_count += 1
            logger.debug(f"Estrazione completata ({code_count} codici)")

            if not codes:
                logger.warning("Nessun codice valido trovato nel file Excel."); self._set_status_message("⚠️ Nessun codice valido.", False)
                QtWidgets.QMessageBox.information(self, "Nessun Codice", f"Nessun codice valido trovato nella colonna '{COL_RICERCA}' del file selezionato.")
                # Chiudi il workbook qui se non ci sono codici
                if workbook: workbook.close(); logger.debug("Workbook chiuso dopo lettura (nessun codice).")
                return # Esce dalla funzione se non ci sono codici

            logger.info(f"Trovati {len(codes)} codici da elaborare.")

        except (InvalidFileException, FileNotFoundError, ValueError, Exception) as e:
            error_prefix = "Errore File Excel"
            if isinstance(e, InvalidFileException): error_msg = "File Excel non valido o corrotto."
            elif isinstance(e, FileNotFoundError): error_msg = f"File non trovato: {file_path}"; error_prefix="File Non Trovato"
            elif isinstance(e, ValueError): error_msg = f"Errore contenuto file Excel: {e}"; error_prefix="Errore Contenuto"
            else: error_msg = "Errore imprevisto durante la lettura del file Excel."; error_prefix="Errore Lettura"; logger.exception(error_msg)

            logger.error(f"{error_prefix}: {error_msg}")
            self._set_status_message(f"❌ {error_prefix}", False)
            QtWidgets.QMessageBox.critical(self, error_prefix, f"{error_msg}\nDettagli nel log.")
            # Assicura chiusura anche in caso di errore durante la lettura
            if workbook:
                 try: workbook.close(); logger.debug("Workbook chiuso dopo errore lettura.")
                 except Exception as close_err: logger.warning(f"Errore chiusura workbook dopo errore: {close_err}")
            self._reset_ui_after_processing(); return # Resetta UI e esce
        finally:
             # La chiusura avviene dentro il blocco try o nel blocco except
             # Qui non è più necessario chiudere di nuovo se è già stato fatto.
             # Si potrebbe aggiungere un controllo 'if workbook and workbook_is_open_flag:' ma diventa complesso.
             # Essendo read_only, la chiusura è meno critica ma buona pratica.
             # Assicuriamoci che venga chiuso in ogni caso sopra.
             logger.debug("Blocco finally lettura Excel completato.")


        # --- Avvio Thread Worker (solo se ci sono codici) ---
        self.btn_start.setEnabled(False); self.btn_stop.setEnabled(True); self.btn_open.setEnabled(False)
        self._set_status_message("⏳ Avvio elaborazione...", True)
        self.log.clear()
        self._reset_badges()
        self.progress.setValue(0)
        self.progress_label.setText("0%")

        logger.debug("Inizio blocco creazione Thread/Worker")
        try:
            self.thread = QtCore.QThread(self); self.worker = Worker(codes)
            self.worker.moveToThread(self.thread)
            # Connessioni segnali/slot
            self.worker.progress.connect(self.update_progress); self.worker.statusUpdate.connect(self.update_status)
            self.worker.logUpdate.connect(self.update_log); self.worker.badgeUpdate.connect(self.update_badge_ui)
            self.worker.resultsReady.connect(self.handle_results)
            self.worker.requestFetch.connect(self.do_fetch_state_async, QtCore.Qt.ConnectionType.QueuedConnection)
            self.thread.started.connect(self.worker.run); self.worker.finished.connect(self.handle_thread_finished)
            self.worker.finished.connect(self.thread.quit); self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.fetchCompleted.connect(self.worker.processFetchedResult)
            logger.debug("Connessioni segnali/slot completate.")
            self.thread.start(); logger.info("Thread worker avviato.")
        except Exception as e_thread:
            error_msg = "Errore durante creazione/avvio thread."; logger.exception(error_msg)
            self._set_status_message(f"❌ Errore Thread", False);
            QtWidgets.QMessageBox.critical(self, "Errore Thread", f"{error_msg}\n{e_thread}\n\nConsultare il log.")
            self._reset_ui_after_processing()
        logger.debug("Fine start_processing")


    def stop_processing(self):
        """Requests the worker thread to stop processing."""
        if self.worker and self.thread and self.thread.isRunning():
            logger.info("Richiesta interruzione elaborazione...")
            self.worker.request_stop(); self._set_status_message("⏳ Interruzione in corso...", False)
            self.btn_stop.setEnabled(False)
        else: logger.info("Nessuna elaborazione da interrompere.")


    @QtCore.pyqtSlot(int, int)
    def update_progress(self, current_value, max_value):
        """Updates the progress bar and label."""
        if max_value > 0:
            self.progress.setMaximum(max_value); self.progress.setValue(current_value)
            percentage = int((current_value / max_value) * 100); self.progress_label.setText(f"{percentage}%")
        else: self.progress.setMaximum(1); self.progress.setValue(0); self.progress_label.setText("0%")


    @QtCore.pyqtSlot(str)
    def update_status(self, message): self.status.setText(message)


    @QtCore.pyqtSlot(str)
    def update_log(self, message):
        """
        Aggiorna sia il logger principale (console/file) che il widget
        QTextEdit nell'interfaccia utente con il messaggio ricevuto.
        Esegue lo scroll automatico del widget di log.
        """
        # Mantieni il logging standard su console e file
        logger.info(message)

        # Aggiunge il messaggio al widget QTextEdit nell'interfaccia
        # Questo avviene nel thread principale della GUI, quindi è sicuro.
        self.log.append(message)

        # Assicura che l'ultima riga aggiunta sia visibile (scroll automatico)
        # Utile per vedere sempre gli ultimi messaggi senza scrollare manualmente.
        scrollbar = self.log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


    @QtCore.pyqtSlot(str, int)
    def update_badge_ui(self, badge_prefix, count):
        """Updates the count on the corresponding status badge with animations."""
        if badge_prefix not in self._badge_widgets_map:
            logger.warning(f"Prefisso badge UI non trovato per '{badge_prefix}'")
            return

        # Recupera card, label, e ora l'effetto opacità
        card, label, opacity_effect = self._badge_widgets_map[badge_prefix]
        if not card or not label or not opacity_effect:  # Controllo robustezza
            logger.error(f"Widget badge o effetto mancante per {badge_prefix}")
            return

        new_text = f"{badge_prefix}: {count}"
        old_text = label.text()
        was_visible = card.isVisible() and opacity_effect.opacity() == 1.0

        # --- Gestione Animazioni Precedenti ---
        # Stoppa e rimuovi eventuali animazioni precedenti per questo badge
        if badge_prefix in self._active_badge_animations:
            try:
                self._active_badge_animations[badge_prefix].stop()
                # Non è necessario rimuovere esplicitamente se creiamo nuove animazioni
                # del self._active_badge_animations[badge_prefix].clear() # Se era un gruppo
            except Exception as e_stop:
                logger.warning(f"Errore stop animazione precedente per {badge_prefix}: {e_stop}")
            del self._active_badge_animations[badge_prefix]

        # Aggiorna il testo solo se necessario
        if old_text != new_text:
            label.setText(new_text)
            logger.debug(f"Aggiornato badge: {badge_prefix}, Nuovo Conto: {count}")

        # --- Logica Animazioni ---
        animation_group = None

        # CASO 1: Prima comparsa (da 0 a >0) -> Fade-in
        if count > 0 and not was_visible:
            logger.debug(f"Animazione Comparsa (Fade-in) per {badge_prefix}")
            if card not in self._badge_widgets:
                self.badge_layout.addWidget(card)
                self._badge_widgets.add(card)

            card.setVisible(True)  # Rendi visibile PRIMA di animare l'opacità da 0
            opacity_effect.setOpacity(0.0)  # Assicura che parta da 0

            fade_in_anim = QtCore.QPropertyAnimation(opacity_effect, b"opacity", card)
            fade_in_anim.setDuration(350)  # Durata in ms
            fade_in_anim.setStartValue(0.0)
            fade_in_anim.setEndValue(1.0)
            fade_in_anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)
            animation_group = fade_in_anim  # In questo caso è una singola animazione

        # CASO 2: Aggiornamento (da >0 a >0) -> Flash + Pulse
        elif count > 0 and was_visible and old_text != new_text:
            logger.debug(f"Animazione Aggiornamento (Flash+Pulse) per {badge_prefix}")
            # Assicurati sia visibile e opaco
            card.setVisible(True)
            opacity_effect.setOpacity(1.0)

            # Gruppo parallelo per eseguire flash e pulse insieme
            parallel_anim_group = QtCore.QParallelAnimationGroup(card)

            # --- Animazione Flash (cambio colore sfondo) ---
            # Useremo QVariantAnimation per interpolare i colori
            color_anim = QtCore.QVariantAnimation(card)
            color_anim.setDuration(400)  # Durata totale flash (andata e ritorno)
            original_color = card.property("originalBgColor")
            flash_color = card.property("flashColor")

            # Interpolatore di colore personalizzato
            def interpolate_color(start, end, progress):
                r = int(start.red() + (end.red() - start.red()) * progress)
                g = int(start.green() + (end.green() - start.green()) * progress)
                b = int(start.blue() + (end.blue() - start.blue()) * progress)
                return QtGui.QColor(r, g, b)

            # Funzione chiamata ad ogni step dell'animazione colore
            def update_flash_color(value):  # value va da 0 a 1 e ritorno
                # Esempio: 0 -> 0.5 (flash in), 0.5 -> 1 (flash out)
                progress = value * 2 if value <= 0.5 else (1 - value) * 2
                current_color = interpolate_color(original_color, flash_color, progress)
                # Applica lo stile dinamico - ATTENZIONE: può essere pesante
                # Prendiamo lo stile originale e sostituiamo solo il background-color
                original_style = card.property("originalStyleSheet")
                new_style = original_style.replace(
                    f"background-color: {original_color.name()}",
                    f"background-color: {current_color.name()}"
                )
                card.setStyleSheet(new_style)

            color_anim.setStartValue(0.0)
            color_anim.setEndValue(1.0)  # Simula un ciclo 0->1->0 all'interno di valueChanged
            color_anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)  # Easing per andata/ritorno
            color_anim.valueChanged.connect(update_flash_color)
            # Alla fine, ripristina lo stile originale
            color_anim.finished.connect(lambda: card.setStyleSheet(card.property("originalStyleSheet")))

            parallel_anim_group.addAnimation(color_anim)

            # --- Animazione Pulse (cambio geometria) ---
            geom_anim_seq = QtCore.QSequentialAnimationGroup()  # Sequenza: cresci -> torna normale
            original_geom = card.geometry()
            pulse_factor = 1.1  # Fattore di ingrandimento (leggero)
            pulse_duration_step = 150  # Durata crescita / durata ritorno

            # Calcola nuova geometria ingrandita (mantenendo il centro)
            new_width = int(original_geom.width() * pulse_factor)
            new_height = int(original_geom.height() * pulse_factor)
            delta_w = new_width - original_geom.width()
            delta_h = new_height - original_geom.height()
            pulsed_geom = QtCore.QRect(
                original_geom.x() - delta_w // 2,
                original_geom.y() - delta_h // 2,
                new_width,
                new_height
            )

            # Animazione 1: Cresci
            grow_anim = QtCore.QPropertyAnimation(card, b"geometry", geom_anim_seq)
            grow_anim.setDuration(pulse_duration_step)
            grow_anim.setStartValue(original_geom)
            grow_anim.setEndValue(pulsed_geom)
            grow_anim.setEasingCurve(QtCore.QEasingCurve.Type.OutQuad)

            # Animazione 2: Torna normale
            shrink_anim = QtCore.QPropertyAnimation(card, b"geometry", geom_anim_seq)
            shrink_anim.setDuration(pulse_duration_step)
            shrink_anim.setStartValue(pulsed_geom)
            shrink_anim.setEndValue(original_geom)
            shrink_anim.setEasingCurve(QtCore.QEasingCurve.Type.InQuad)

            geom_anim_seq.addAnimation(grow_anim)
            geom_anim_seq.addAnimation(shrink_anim)

            parallel_anim_group.addAnimation(geom_anim_seq)  # Aggiungi sequenza pulse al gruppo parallelo
            animation_group = parallel_anim_group  # Il gruppo parallelo è l'animazione principale

        # CASO 3: Scomparsa (da >0 a 0) -> Fade-out (Opzionale)
        elif count == 0 and was_visible:
            logger.debug(f"Animazione Scomparsa (Fade-out) per {badge_prefix}")
            fade_out_anim = QtCore.QPropertyAnimation(opacity_effect, b"opacity", card)
            fade_out_anim.setDuration(350)
            fade_out_anim.setStartValue(1.0)
            fade_out_anim.setEndValue(0.0)
            fade_out_anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)
            # Nascondi il widget QUANDO l'animazione finisce
            fade_out_anim.finished.connect(lambda w=card: w.setVisible(False))
            # Potresti voler rimuovere dal set _badge_widgets qui o in _reset_badges
            # fade_out_anim.finished.connect(lambda b=badge_prefix: self._badge_widgets.discard(self._badge_widgets_map[b][0]))
            animation_group = fade_out_anim

        # --- Avvio Animazione e Memorizzazione ---
        if animation_group:
            # Memorizza l'animazione corrente
            self._active_badge_animations[badge_prefix] = animation_group
            # Pulisci riferimento quando finisce
            animation_group.finished.connect(lambda bp=badge_prefix: self._active_badge_animations.pop(bp, None))
            animation_group.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        else:
            # Nessuna animazione necessaria (es. testo non cambiato o count ancora 0)
            # Assicura stato corretto se count è 0 e non era visibile
            if count == 0 and not was_visible:
                card.setVisible(False)
                opacity_effect.setOpacity(0.0)


    @QtCore.pyqtSlot(list)
    def handle_results(self, results_list):
        """Receives the final list of results from the worker and initiates saving."""
        logger.info(f"Ricevuti {len(results_list)} risultati finali dal worker.")
        if results_list and self.current_file_path:
            # Chiama la funzione per salvare
            self._save_results_to_excel(results_list, self.current_file_path)
        elif not results_list and self.worker and not self.worker._stop_requested:
             logger.info("Nessun risultato valido raccolto."); self._set_status_message("ℹ️ Nessun risultato da salvare.", False)
        elif not self.current_file_path:
             logger.warning("Impossibile salvare: percorso file non memorizzato."); self._set_status_message("⚠️ Percorso file non disponibile.", False)


    # <<<=== NUOVA FUNZIONE PER SALVARE I RISULTATI ===>>>
    def _save_results_to_excel(self, results_list, original_file_path):
        """Scrive i risultati raccolti nel file Excel originale o in una copia."""
        logger.info(f"Tentativo di salvataggio di {len(results_list)} risultati su {original_file_path}")
        self._set_status_message(f"⏳ Salvataggio risultati su Excel...", True)
        workbook = None # Inizializza a None

        try:
            # Tenta di caricare il workbook esistente per modificarlo
            try:
                workbook = openpyxl.load_workbook(filename=original_file_path)
                is_read_only_or_corrupted = False
                output_file_path = original_file_path # Salva sull'originale per default
                logger.debug(f"Workbook '{os.path.basename(original_file_path)}' caricato per la scrittura.")
            except (PermissionError, IOError) as pe:
                 logger.warning(f"Impossibile aprire '{os.path.basename(original_file_path)}' in scrittura ({pe}). Tento di salvarlo come copia.")
                 is_read_only_or_corrupted = True
                 # Riprova a caricare in modalità read_only per poter leggere i dati prima di salvare su un nuovo file
                 try:
                     workbook = openpyxl.load_workbook(filename=original_file_path, read_only=True)
                     logger.debug(f"Workbook '{os.path.basename(original_file_path)}' ricaricato in read-only per creare copia.")
                 except Exception as e_reload:
                     logger.error(f"Errore anche nel ricaricare '{os.path.basename(original_file_path)}' in read-only: {e_reload}", exc_info=True)
                     # Se anche la rilettura fallisce, non possiamo fare molto, errore critico
                     self._set_status_message("❌ Errore critico lettura file Excel.", False)
                     QtWidgets.QMessageBox.critical(self, "Errore Lettura File", f"Errore critico durante la lettura del file Excel originale:\n'{os.path.basename(original_file_path)}'.\nImpossibile procedere con il salvataggio.")
                     return # Esce dalla funzione
            except Exception as e_load: # Cattura altri errori di caricamento (es. file corrotto)
                 logger.error(f"Errore imprevisto durante il caricamento del workbook '{os.path.basename(original_file_path)}': {e_load}", exc_info=True)
                 is_read_only_or_corrupted = True
                 # Non possiamo salvare su un file corrotto, usciamo
                 self._set_status_message("❌ Errore caricamento file Excel corrotto.", False)
                 QtWidgets.QMessageBox.critical(self, "Errore File Corrotto", f"Impossibile caricare il file Excel:\n'{os.path.basename(original_file_path)}'.\nIl file potrebbe essere corrotto.")
                 return # Esce

            # Se dobbiamo salvare su copia
            if is_read_only_or_corrupted and workbook:
                # Crea un nuovo nome file
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                base, ext = os.path.splitext(original_file_path)
                output_file_path = f"{base}_output_{timestamp}{ext}"
                logger.info(f"Salvataggio risultati su nuovo file: {output_file_path}")
                self._set_status_message(f"⚠️ Salvataggio su nuovo file: {os.path.basename(output_file_path)}", False)
                QtWidgets.QMessageBox.information(self, "Salvataggio su Copia",
                                                  f"Impossibile scrivere sul file originale (forse è aperto, protetto o corrotto).\n"
                                                  f"I risultati saranno salvati nel nuovo file:\n'{os.path.basename(output_file_path)}'")
                # IMPORTANTE: Se abbiamo caricato in read_only, dobbiamo creare un NUOVO workbook in memoria
                # e copiarci i dati (o almeno quelli che ci servono). Openpyxl non permette di salvare
                # un workbook aperto in read_only. Per semplicità, ora creiamo un nuovo workbook
                # e ci scriviamo SOLO i dati aggiornati. L'ideale sarebbe copiare tutti i fogli/dati.
                # Questo è un compromesso.
                # TODO: Implementare una copia completa del workbook se necessario.
                new_workbook = openpyxl.Workbook() # Crea un workbook vuoto
                new_sheet = new_workbook.active
                new_sheet.title = workbook.active.title # Usa lo stesso nome foglio se possibile

                # Copia l'intestazione dal workbook originale (letto in read-only) al nuovo
                original_sheet = workbook.active
                header_values = [cell.value for cell in original_sheet[1]]
                new_sheet.append(header_values)
                logger.debug(f"Intestazione copiata nel nuovo workbook per il salvataggio su copia.")

                # Copia tutte le righe dati dal workbook originale al nuovo
                # Questo è necessario per non perdere i dati delle righe non aggiornate
                logger.debug("Copia dati dal workbook originale al nuovo workbook in memoria...")
                for row_idx in range(2, original_sheet.max_row + 1):
                    row_values = [cell.value for cell in original_sheet[row_idx]]
                    new_sheet.append(row_values)
                logger.debug(f"Copiati {original_sheet.max_row - 1} righe di dati nel nuovo workbook.")

                # Ora lavoreremo sul new_workbook e new_sheet
                workbook_to_save = new_workbook
                sheet = new_sheet
                workbook.close() # Chiudiamo il workbook originale letto in read-only
                logger.debug("Workbook originale (read-only) chiuso.")
            elif workbook: # Se abbiamo caricato normalmente per scrittura
                workbook_to_save = workbook
                sheet = workbook.active
            else: # Caso imprevisto, non dovremmo arrivare qui se la logica sopra è corretta
                 logger.error("Errore logico: workbook non definito per il salvataggio.")
                 raise RuntimeError("Stato inconsistente del workbook per il salvataggio.")


            # --- Trova gli indici delle colonne di output (sul foglio corretto 'sheet') ---
            header_row = sheet[1]
            col_indices = {
                'Input Code': -1, 'Stato': -1, 'Protocollo uscita': -1, 'Provvedimento': -1,
                'Data Provvedimento': -1, 'Codice richiesta (risultato)': -1, 'Note Usmaf': -1
            }
            col_name_map = {
                'Input Code': COL_RICERCA, 'Stato': COL_STATO, 'Protocollo uscita': COL_PROTOCOLLO,
                'Provvedimento': COL_PROVVEDIMENTO, 'Data Provvedimento': COL_DATA_PROVV,
                'Codice richiesta (risultato)': COL_CODICE_RIS, 'Note Usmaf': COL_NOTE
            }

            for idx, cell in enumerate(header_row):
                if cell.value is not None:
                    header_text = str(cell.value).strip()
                    for key, excel_col_name in col_name_map.items():
                        if header_text.lower() == excel_col_name.lower():
                            col_indices[key] = idx + 1
                            logger.debug(f"Colonna '{excel_col_name}' trovata all'indice {col_indices[key]} nel foglio '{sheet.title}'")
                            break

            missing_cols = [col_name_map[k] for k, v in col_indices.items() if v == -1]
            if missing_cols:
                logger.error(f"Colonne obbligatorie mancanti nel foglio Excel '{sheet.title}': {', '.join(missing_cols)}")
                raise ValueError(f"Colonne mancanti: {', '.join(missing_cols)}")

            # --- Mappa per indicizzare rapidamente i risultati ---
            results_map = {str(res['Input Code']).strip(): res for res in results_list}
            logger.debug(f"Creata mappa risultati con {len(results_map)} voci.")

            # --- Scrittura dei dati ---
            ricerca_col_idx = col_indices['Input Code']
            updated_rows = 0
            processed_keys = set()

            logger.info(f"Inizio scansione righe e scrittura risultati sul foglio '{sheet.title}'...")
            for row_idx in range(2, sheet.max_row + 1):
                cell_ricerca = sheet.cell(row=row_idx, column=ricerca_col_idx)
                excel_code = str(cell_ricerca.value).strip() if cell_ricerca.value is not None else ''

                if excel_code and excel_code in results_map:
                    result_data = results_map[excel_code]
                    processed_keys.add(excel_code)

                    # --- INCOLLA QUESTO BLOCCO AGGIORNATO al posto del ciclo for key, col_idx ... originale ---

                    # Itera sulle colonne da scrivere per la riga corrente
                    for key, col_idx in col_indices.items():
                        # Salta la colonna 'Input Code' (COL_RICERCA) perché quella serve solo per trovare la riga
                        # e assicurati che l'indice della colonna sia stato trovato (non sia -1)
                        if key != 'Input Code' and col_idx != -1:

                            # --- Inizio Logica Aggiornata per Recupero e Scrittura Valore ---

                            # Recupera il valore originale dai risultati raccolti per la chiave corrente (es. 'Stato', 'Note Usmaf')
                            original_value = result_data.get(key,
                                                             '')  # Usa '' come default se la chiave non esiste nei risultati

                            # Inizializza il valore da scrivere nella cella con quello originale
                            value_to_write = original_value

                            # --- Logica Specifica per 'Note Usmaf' ---
                            # Controlla se stiamo processando la colonna specifica 'Note Usmaf'
                            # E se il valore originale recuperato è vuoto (o contiene solo spazi)
                            if key == 'Note Usmaf' and not original_value.strip():
                                # Se entrambe le condizioni sono vere, imposta il testo predefinito
                                value_to_write = "NOTA USMAF"
                            # --- Fine Logica Specifica ---

                            # Ottieni l'oggetto cella dalla libreria openpyxl
                            cell_to_write = sheet.cell(row=row_idx, column=col_idx)

                            # Scrivi il valore finale (originale o il testo predefinito) nella cella
                            cell_to_write.value = value_to_write

                            # Applica formattazione alla cella per assicurare che sia testo
                            # e per migliorare la leggibilità (allineamento e a capo automatico)
                            cell_to_write.number_format = numbers.FORMAT_TEXT
                            cell_to_write.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

                            # --- Fine Logica Aggiornata per Recupero e Scrittura Valore ---

                    # Incrementa il contatore delle righe aggiornate dopo aver processato tutte le colonne per questa riga
                    updated_rows += 1
                    # logger.debug(f"Riga {row_idx}: Aggiornata per codice '{excel_code}'.") # Mantenuto commentato

                # --- FINE BLOCCO AGGIORNATO ---

            logger.info(f"Scansione foglio '{sheet.title}' completata. Aggiornate {updated_rows} righe.")

            unmatched_codes = set(results_map.keys()) - processed_keys
            if unmatched_codes:
                logger.warning(f"I seguenti {len(unmatched_codes)} codici elaborati non sono stati trovati nel file Excel durante il salvataggio: {', '.join(list(unmatched_codes)[:10])}{'...' if len(unmatched_codes)>10 else ''}")

            # --- Salvataggio del workbook modificato ---
            logger.info(f"Salvataggio modifiche su: {output_file_path}...")
            try:
                workbook_to_save.save(output_file_path)
                logger.info(f"Salvataggio Excel '{os.path.basename(output_file_path)}' completato.")
                self._set_status_message(f"✅ Risultati salvati su {os.path.basename(output_file_path)}", False)
                QtWidgets.QMessageBox.information(self, "Salvataggio Completato",
                                                 f"{updated_rows} righe aggiornate con successo nel file:\n"
                                                 f"'{os.path.basename(output_file_path)}'")
            except Exception as e_save:
                logger.error(f"Errore durante il salvataggio del file Excel '{output_file_path}': {e_save}", exc_info=True)
                self._set_status_message(f"❌ Errore salvataggio Excel", False)
                QtWidgets.QMessageBox.critical(self, "Errore Salvataggio", f"Impossibile salvare il file Excel:\n'{os.path.basename(output_file_path)}'.\nErrore: {e_save}\nControllare se il file è aperto o protetto.")

        except (InvalidFileException, FileNotFoundError, ValueError, Exception) as e:
            error_prefix = "Errore Salvataggio Excel"
            if isinstance(e, (InvalidFileException, FileNotFoundError, ValueError)):
                error_msg = str(e)
                logger.error(f"{error_prefix} (Errore dati/file/colonne): {error_msg}")
            else:
                error_msg = "Errore imprevisto durante il processo di salvataggio Excel."
                logger.exception(error_msg)

            self._set_status_message(f"❌ {error_prefix}", False)
            QtWidgets.QMessageBox.critical(self, error_prefix, f"{error_msg}\nControllare il file Excel e i log per dettagli.")

        finally:
            # Assicura la chiusura del workbook che stavamo per salvare (se esiste)
            if 'workbook_to_save' in locals() and workbook_to_save:
                try:
                    workbook_to_save.close()
                    logger.debug("Workbook (per salvataggio) chiuso.")
                except Exception as close_err:
                    logger.warning(f"Errore durante la chiusura del workbook (per salvataggio): {close_err}")
            # Anche il workbook originale se era stato aperto e non ancora chiuso
            elif 'workbook' in locals() and workbook:
                 try:
                     workbook.close()
                     logger.debug("Workbook originale (residuo) chiuso nel finally.")
                 except Exception as close_err:
                      logger.warning(f"Errore durante la chiusura del workbook originale (residuo): {close_err}")

            self.spinner.stopAnimation() # Assicura che lo spinner sia fermo


    @QtCore.pyqtSlot()
    def handle_thread_finished(self):
        """Cleans up after the worker thread has finished."""
        logger.info("Thread di elaborazione terminato.")
        final_status = self.status.text()
        stopped_manually = self.worker and self.worker._stop_requested
        # Non sovrascrivere messaggi di successo/errore dal salvataggio
        if "salvat" not in final_status.lower() and "errore" not in final_status.lower():
            if stopped_manually: final_status = "❌ Elaborazione Interrotta."
            elif "completata" not in final_status.lower() : final_status = "ℹ️ Elaborazione terminata."

        self._set_status_message(final_status, False); self._reset_ui_after_processing()
        self.thread = None; self.worker = None; self._current_fetch_context = None
        logger.debug("Thread, Worker, and Fetch Context cleaned")


    def _set_status_message(self, base_message, is_waiting):
        """Helper function to set the status label and control the spinner visibility."""
        self.status.setText(base_message)
        if is_waiting: self.spinner.startAnimation()
        else: self.spinner.stopAnimation()


    @QtCore.pyqtSlot(str)
    def do_fetch_state_async(self, code):
        """Slot called by worker signal to initiate fetching state for a code in the main thread."""
        page = self.view.page();
        if not page: logger.critical(f"Errore critico: Pagina Web non disponibile (Codice: {code})."); self._process_fetch_result(code, 'Errore Pagina', []); return
        if not self.worker or self.worker._stop_requested: logger.debug(f"Skipping fetch {code} - worker fermato/nullo."); return

        logger.info(f"Ricevuta richiesta fetch ASYNC per {code}")
        self.last_cells = [''] * 11; self.last_cells[8] = str(code).strip()
        self._current_fetch_context = { 'code': code, 'attempt': 0, 'start_time': None, 'check_count': 0, 'null_check_count': 0, 'page_load_error': False }
        self._attempt_fetch(page, code)


    def _attempt_fetch(self, page, code):
        """Initiates a fetch attempt (handles retries)."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: logger.debug(f"Context changed, skip fetch {code}"); return
        attempt = self._current_fetch_context['attempt']
        if self.worker and self.worker._stop_requested: logger.info(f"Interruzione {attempt + 1} {code}."); self._process_fetch_result(code, 'Interrotto', self.last_cells); return
        if self._current_fetch_context['page_load_error']: logger.error(f"Errore pagina {attempt + 1} {code}."); self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells); return
        if attempt > self.max_retries: logger.warning(f"Timeout {code} dopo {attempt} tentativi."); self._process_fetch_result(code, 'Errore Timeout', self.last_cells); return

        if attempt > 0:
            logger.info(f"Riprovo '{code}' ({attempt + 1}/{self.max_retries + 1})")
            self._set_status_message(f"⏳ Riprovo '{code}' ({attempt + 1})...", False) # Non mostrare spinner per riprovo
            QtCore.QTimer.singleShot(DELAY_BETWEEN_RETRIES, lambda: self._execute_js_input(page, code))
        else: logger.debug(f"Inizio tentativo 1 {code}"); self._execute_js_input(page, code)


    def _execute_js_input(self, page, code):
        """Executes JavaScript to insert the code into the input field."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
        attempt = self._current_fetch_context['attempt']
        if self.worker and self.worker._stop_requested: logger.info(f"Interruzione JS input {code} ({attempt+1})."); self._process_fetch_result(code, 'Interrotto', self.last_cells); return
        if self._current_fetch_context['page_load_error']: logger.error(f"Errore pagina JS input {code} ({attempt+1})."); self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells); return

        try:
            logger.info(f"Inserimento codice {code}..."); self._set_status_message(f"Inserimento codice {code}...", True)
            escaped_code = str(code).strip().replace("'", "\\'").replace('"', '\\"')
            js_input = f"document.getElementById('codiceRichiesta').value='{escaped_code}';"
            logger.debug(f"JS Input ({attempt+1}): {js_input[:50]}...")
            # Usiamo una lambda per passare page e code al callback
            page.runJavaScript(js_input, lambda result, p=page, c=code: self._schedule_js_click(p, c))
        except Exception as js_error:
            logger.error(f"Errore JS input {code} ({attempt+1}): {js_error}", exc_info=True); self._set_status_message(f"Errore JS input {code}", False)
            self._schedule_next_attempt(page, code)

    def _schedule_js_click(self, page, code):
        """Schedules the JS click execution after a short delay."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
        # Verifica aggiuntiva pagina valida
        if not page or not hasattr(page, 'url'):
             logger.error(f"Errore pagina non valida prima di schedulare JS click per {code}.")
             self._process_fetch_result(code, 'Errore Pagina', self.last_cells)
             return
        QtCore.QTimer.singleShot(DELAY_AFTER_INPUT_JS, lambda: self._execute_js_click(page, code))

    def _execute_js_click(self, page, code):
        """Executes JavaScript to click the search button."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
        attempt = self._current_fetch_context['attempt']
        # Verifica aggiuntiva pagina valida
        if not page or not hasattr(page, 'url'):
             logger.error(f"Errore pagina non valida prima di eseguire JS click per {code}.")
             self._process_fetch_result(code, 'Errore Pagina', self.last_cells)
             return

        if self.worker and self.worker._stop_requested: logger.info(f"Interruzione JS click {code} ({attempt+1})."); self._process_fetch_result(code, 'Interrotto', self.last_cells); return
        if self._current_fetch_context['page_load_error']: logger.error(f"Errore pagina JS click {code} ({attempt+1})."); self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells); return

        try:
            logger.info(f"Click ricerca per {code}..."); self._set_status_message(f"Click ricerca per {code}...", True)
            js_click = "document.getElementById('cercaRichiestaNullaOstaBtn').click();"
            logger.debug(f"JS Click ({attempt+1})")
            # Usiamo una lambda per passare page e code al callback
            page.runJavaScript(js_click, lambda result, p=page, c=code: self._schedule_first_check(p, c))
        except Exception as js_error:
            logger.error(f"Errore JS click {code} ({attempt+1}): {js_error}", exc_info=True); self._set_status_message(f"Errore JS click {code}", False)
            self._schedule_next_attempt(page, code)

    def _schedule_first_check(self, page, code):
        """Schedules the first check for results after the click delay."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
        # Verifica aggiuntiva pagina valida
        if not page or not hasattr(page, 'url'):
             logger.error(f"Errore pagina non valida prima di schedulare check per {code}.")
             self._process_fetch_result(code, 'Errore Pagina', self.last_cells)
             return
        logger.info(f"Attesa risultato per {code}..."); self._set_status_message(f"Attesa risultato per {code}...", True)
        self._current_fetch_context['start_time'] = time.monotonic(); self._current_fetch_context['check_count'] = 0; self._current_fetch_context['null_check_count'] = 0
        QtCore.QTimer.singleShot(DELAY_AFTER_CLICK_JS, lambda: self._check_fetch_result(page, code))

    def _check_fetch_result(self, page, code):
        """Executes JS to check if the result table/data is available."""
        if not self._current_fetch_context or self._current_fetch_context['code'] != code: return
         # Verifica aggiuntiva pagina valida
        if not page or not hasattr(page, 'url'):
             logger.error(f"Errore pagina non valida prima di eseguire check JS per {code}.")
             self._process_fetch_result(code, 'Errore Pagina', self.last_cells)
             return
        attempt = self._current_fetch_context['attempt']
        if self.worker and self.worker._stop_requested: logger.info(f"Interruzione attesa JS {code} ({attempt+1})."); self._process_fetch_result(code, 'Interrotto', self.last_cells); return
        if self._current_fetch_context['page_load_error']: logger.error(f"Errore pagina attesa JS {code} ({attempt+1})."); self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells); return

        start_time = self._current_fetch_context['start_time']
        if start_time is None: logger.warning(f"start_time mancante {code}. Reimposto."); start_time = time.monotonic(); self._current_fetch_context['start_time'] = start_time
        elapsed_time_ms = (time.monotonic() - start_time) * 1000
        if elapsed_time_ms > FETCH_TIMEOUT_MS: logger.warning(f"Timeout {attempt + 1} {code} ({elapsed_time_ms:.0f} ms)"); self._schedule_next_attempt(page, code); return

        status_msg = f"Controllo risultato {code} (check {self._current_fetch_context['check_count']+1})..."; logger.debug(status_msg)
        self._set_status_message(status_msg, True); logger.debug(f"Eseguo JS celle ({attempt+1}) {code}")
        try:
            # Passiamo il risultato alla funzione _handle_js_evaluation_result
            page.runJavaScript(ALL_CELLS_JS, self._handle_js_evaluation_result)
        except Exception as eval_error:
            logger.error(f"Errore runJavaScript {code} ({attempt+1}): {eval_error}", exc_info=True); self._set_status_message(f"Errore JS check {code}", False); self._schedule_next_attempt(page, code)


    def _handle_js_evaluation_result(self, result):
        """Handles the asynchronous result from the page.runJavaScript call."""
        # È fondamentale recuperare il contesto CORRENTE quando il risultato arriva
        # perché potrebbe essere cambiato nel frattempo (se l'elaborazione è molto veloce)
        current_context = self._current_fetch_context
        if not current_context: logger.warning(f"Risultato JS ({str(result)[:50]}...) ricevuto senza contesto attivo."); return

        code = current_context['code']; attempt = current_context['attempt']; start_time = current_context['start_time']
        page = self.view.page() # Recupera la pagina corrente

         # Verifica aggiuntiva pagina valida
        if not page or not hasattr(page, 'url'):
             logger.error(f"Errore pagina non valida in _handle_js_evaluation_result per {code}.")
             self._process_fetch_result(code, 'Errore Pagina', self.last_cells) # Usa last_cells come fallback
             return

        if self.worker and self.worker._stop_requested: logger.info(f"Interruzione DOPO JS {code} ({attempt+1})."); self._process_fetch_result(code, 'Interrotto', self.last_cells); return
        if current_context['page_load_error']: logger.error(f"Errore pagina DOPO JS {code} ({attempt+1})."); self._process_fetch_result(code, 'Errore Caricamento Pagina', self.last_cells); return

        logger.debug(f"Ricevuto JS result per {code} ({attempt+1}): {str(result)[:100]}...")
        current_context['check_count'] += 1

        cells = result; result_found = False; fetched_state = 'Errore Interno Fetch'; current_cells = []

        if cells is None:
            current_context['null_check_count'] += 1
            logger.debug(f"JS result is None per {code} (check: {current_context['check_count']}, nulls: {current_context['null_check_count']})")
            if current_context['null_check_count'] >= MAX_NULL_CHECKS:
                logger.warning(f"Elemento non trovato (JS) per {code} dopo {MAX_NULL_CHECKS} controlli null consecutivi.");
                self._process_fetch_result(code, 'Elemento Non Trovato (JS)', self.last_cells); return # Usa last_cells come fallback
        elif isinstance(cells, list):
            current_context['null_check_count'] = 0 # Resetta il contatore se riceviamo una lista valida
            current_cells = [str(c).strip() if c is not None else '' for c in cells]
            # Assicura che la lista abbia almeno 11 elementi per evitare IndexError dopo
            while len(current_cells) < 11: current_cells.append('')

            # Caso 1: Messaggio "Nessun dato presente"
            if len(cells) >= 1 and 'Nessun dato presente' in cells[0]:
                fetched_state = 'Non Trovato'; current_cells[2] = fetched_state # Mette "Non Trovato" anche nella colonna stato per coerenza
                result_found = True
                logger.info(f"'Nessun dato presente' rilevato per {code}.")
            # Caso 2: Lista con dati, controlla se il codice corrisponde
            elif len(current_cells) > 8: # Assicura che l'indice 8 esista
                code_in_table = current_cells[8]
                if code_in_table == str(code).strip():
                    fetched_state = current_cells[2] if current_cells[2] else 'Sconosciuto' # Usa lo stato dalla colonna 2
                    result_found = True
                    logger.info(f"Corrispondenza trovata per {code} ({attempt+1}). Stato: {fetched_state}")
                else:
                    # Codice trovato nella tabella ma non corrisponde a quello cercato
                    # Questo potrebbe indicare un problema di sincronizzazione o un bug
                    logger.warning(f"Codice trovato nella tabella ('{code_in_table}') non corrisponde a quello cercato ('{code}') per tentativo {attempt+1}. Riprovo check.")
                    # Non considerarlo un risultato valido, continua a controllare
                    result_found = False # Assicura che non venga processato come trovato
            else:
                 # La lista non ha abbastanza elementi per contenere il codice (indice 8)
                 logger.debug(f"Lista risultato JS per {code} troppo corta ({len(current_cells)} elementi). Riprovo check.")
                 result_found = False

        else: # Tipo di risultato inatteso (non None, non list)
            logger.error(f"Risultato JS inatteso per {code} ({attempt+1}): Tipo {type(cells)} - Valore: {str(cells)[:100]}");
            self._process_fetch_result(code, 'Errore Risultato JS', self.last_cells); return # Usa last_cells come fallback

        # Se abbiamo trovato un risultato valido (corrispondenza codice o "Non trovato")
        if result_found:
            logger.info(f"Risultato finale per {code} ({attempt+1}): {fetched_state}")
            self._process_fetch_result(code, fetched_state, current_cells); return # Passa le celle trovate

        # --- Se non abbiamo ancora trovato il risultato ---
        # Controlla il timeout
        if start_time is None: start_time = time.monotonic(); current_context['start_time'] = start_time # Fallback
        elapsed_time_ms = (time.monotonic() - start_time) * 1000
        if elapsed_time_ms > FETCH_TIMEOUT_MS:
            logger.warning(f"Timeout {attempt + 1} per {code} ({elapsed_time_ms:.0f} ms) dopo check JS.");
            self._schedule_next_attempt(page, code); return # Schedula nuovo tentativo

        # Se non è timeout e non trovato, schedula un altro check
        logger.debug(f"Risultato per {code} non ancora pronto o non corrispondente, schedulo nuovo check.");
        QtCore.QTimer.singleShot(FETCH_CHECK_INTERVAL_MS, lambda p=page, c=code: self._check_fetch_result(p, c))


    def _schedule_next_attempt(self, page, code):
         """Schedules the next fetch attempt after a failure or timeout."""
         # Recupera contesto CORRENTE
         current_context = self._current_fetch_context
         if not current_context or current_context['code'] != code:
             logger.debug(f"Context changed or null, skip scheduling next attempt for {code}")
             return
          # Verifica aggiuntiva pagina valida
         if not page or not hasattr(page, 'url'):
             logger.error(f"Errore pagina non valida prima di schedulare next attempt per {code}.")
             self._process_fetch_result(code, 'Errore Pagina', self.last_cells)
             return

         next_attempt = current_context['attempt'] + 1; logger.debug(f"Schedulo tentativo {next_attempt} per {code}")
         current_context['attempt'] = next_attempt
         # Resetta stato per il nuovo tentativo
         current_context['start_time'] = None; current_context['check_count'] = 0; current_context['null_check_count'] = 0; current_context['page_load_error'] = False
         # Usa singleShot con 0ms per mettere l'esecuzione in coda nel loop eventi
         QtCore.QTimer.singleShot(0, lambda p=page, c=code: self._attempt_fetch(p, c))


    def _process_fetch_result(self, code, state, cells):
        """Final step to process the fetch outcome and signal the worker."""
        # NON usare self._current_fetch_context qui perché potrebbe essere già cambiato.
        # Questa funzione è il punto finale per un DATO 'code'.
        logger.info(f"Processando risultato finale per codice '{code}': Stato='{state}'");

        # Pulisci il contesto SOLO SE corrisponde al codice che stiamo processando
        if self._current_fetch_context and self._current_fetch_context['code'] == code:
            self._current_fetch_context = None # Clear context
            logger.debug(f"Contesto fetch per '{code}' pulito.")
        else:
             logger.warning(f"Tentativo di processare risultato per '{code}', ma contesto attuale è per '{self._current_fetch_context['code'] if self._current_fetch_context else 'None'}'.")
             # Decidi se ignorare o meno. Potrebbe essere un risultato tardivo.
             # Per ora, lo inviamo comunque al worker, sarà lui a gestirlo se necessario.

        self.last_cells = cells # Aggiorna comunque le celle trovate/usate
        self._set_status_message(f"Risultato per {code}: {state}", False) # Aggiorna status UI

        # Invia il risultato al worker se il worker esiste ancora
        if self.worker:
             logger.debug(f"Invio segnale fetchCompleted per {code} (Stato: {state}) al worker.");
             # Usa QueuedConnection per assicurare che arrivi nel thread del worker
             QtCore.QMetaObject.invokeMethod(self.worker, "processFetchedResult", QtCore.Qt.ConnectionType.QueuedConnection,
                                             QtCore.Q_ARG(str, code), QtCore.Q_ARG(str, state), QtCore.Q_ARG(list, self.last_cells))
             # self.fetchCompleted.emit(code, state, self.last_cells) # Alternativa con segnale (verificare connessione)
        else:
             logger.warning(f"Worker nullo, impossibile inviare risultato per {code}.")


    def open_nsis_url_test(self):
        """Loads about:blank first, then the actual URL after a delay."""
        logger.info("Apertura URL NSIS (via about:blank)...")
        try:
            # Disconnetti il gestore specifico del fetch PRIMA di caricare about:blank
            if self.view and self.view.page():
                 try: self.view.loadFinished.disconnect(self._handle_page_load_finished)
                 except TypeError: pass # Ignora se non era connesso
            blank_url = QtCore.QUrl("about:blank"); self.view.load(blank_url)
            # Riconnetti il gestore DOPO aver richiesto il caricamento di about:blank
            # Ma schedula il caricamento reale con un timer
            QtCore.QTimer.singleShot(500, self.load_real_url)
        except Exception as e: logger.exception("Eccezione in open_nsis_url_test"); QtWidgets.QMessageBox.critical(self, "Errore Test", f"Errore caricando about:blank.\n{e}")


    def load_real_url(self):
        """Loads the actual target URL."""
        # Resetta lo stato di errore pagina per il nuovo caricamento
        if self._current_fetch_context: self._current_fetch_context['page_load_error'] = False
        try:
            url_str = URL_NSIS; real_url = QtCore.QUrl(url_str); logger.info(f"Carico URL reale: {real_url.toString()}")
            if real_url.isValid():
                 page = self.view.page()
                 if page:
                     # Assicurati che sia connesso SOLO una volta
                     try: page.loadFinished.disconnect(self._handle_page_load_finished)
                     except TypeError: pass
                     page.loadFinished.connect(self._handle_page_load_finished) # Connetti per logica fetch
                     page.load(real_url) # Usa page.load
                 else:
                     logger.error("Pagina non disponibile per caricare URL reale.")
                     QtWidgets.QMessageBox.warning(self, "Errore Interno", "Componente Web non pronto.")
            else: logger.error(f"URL non valido: {url_str}"); QtWidgets.QMessageBox.warning(self, "URL Non Valido", f"URL configurato non valido:\n{url_str}")
        except Exception as e: logger.exception("Eccezione in load_real_url"); QtWidgets.QMessageBox.critical(self, "Errore Caricamento", f"Errore caricando URL reale.\n{e}")

    def create_badge(self, icon, label_text, color_hex):
        """Creates a styled badge widget with effects for animation."""
        frame = QtWidgets.QFrame()
        text_color = "black"
        try:
            bg_color = QtGui.QColor(color_hex)
            luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()) / 255
            text_color = "black" if luminance > 0.6 else "white"
        except Exception as e:
            logger.warning(f"Errore calcolo colore testo badge per {color_hex}: {e}")

        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_hex};
                border-radius: 6px;
                padding: 4px 6px;
                border: none;
            }}
            QLabel {{
                color: {text_color};
                font-weight: 600;
                font-size: 11px;
                background-color: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }}
        """)
        frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Fixed)

        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(5)

        badge_prefix_text = f"{icon} {label_text}"
        label = QtWidgets.QLabel(f"{badge_prefix_text}: 0")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)

        layout.addWidget(label)
        layout.addStretch(1)

        # --- AGGIUNGI EFFETTI GRAFICI ---
        # Effetto Opacità per fade-in/out
        opacity_effect = QtWidgets.QGraphicsOpacityEffect(frame)
        opacity_effect.setOpacity(0.0)  # Inizia trasparente
        frame.setGraphicsEffect(opacity_effect)
        frame.setProperty("opacityEffect", opacity_effect)  # Salva riferimento

        # Effetto Colorize per il flash
        colorize_effect = QtWidgets.QGraphicsColorizeEffect(frame)
        colorize_effect.setColor(QtGui.QColor("white"))  # Colore per il flash
        colorize_effect.setStrength(0.0)  # Inizia senza effetto
        # NOTA: Un widget può avere un solo effetto grafico diretto.
        # Per averne due, uno deve essere applicato all'altro o usare tecniche diverse.
        # Applichiamo l'effetto colorize *all'effetto opacità*? No, non funziona così.
        # Alternativa: Applichiamo il Colorize al *contenuto* del frame (il layout)? No.
        # Soluzione: Applichiamo il Colorize al Frame, e gestiamo l'opacità separatamente
        # impostando opacity_effect come effetto del frame solo quando serve il fade.
        # Riprogettazione: Usiamo SOLO l'effetto opacità per fade-in/out.
        # Per il flash, animeremo direttamente lo STILE del frame (background-color).
        # Per il pulse, animeremo la GEOMETRIA.

        # --- FINE AGGIUNTA EFFETTI ---

        frame.setProperty("badgePrefix", badge_prefix_text)
        frame.setProperty("originalStyleSheet", frame.styleSheet())  # Salva lo stile originale
        frame.setProperty("originalBgColor", QtGui.QColor(color_hex))  # Salva colore originale
        frame.setProperty("flashColor", QtGui.QColor("white"))  # Colore per il flash

        # Rimuoviamo il colorize_effect per ora, useremo lo stylesheet
        # frame.setProperty("colorizeEffect", colorize_effect)

        # Restituisce frame, label, e l'effetto opacità
        return frame, label, opacity_effect  # Modificato valore restituito


    def animate_badge(self, badge_frame):
        """Rende semplicemente visibile il badge_frame."""
        if not badge_frame: return
        if not badge_frame.isVisible():
            logger.debug(f"animate_badge: Rendo visibile {badge_frame.property('badgePrefix')}")
            badge_frame.setVisible(True)


    def _reset_badges(self):
        """Hides all badges, resets their counts to 0, and stops animations."""
        logger.debug("Resetting badges...")
        # Stoppa tutte le animazioni attive dei badge
        for prefix, animation in list(self._active_badge_animations.items()):
            try:
                animation.stop()
                logger.debug(f"Animazione stoppata per badge {prefix} durante reset.")
            except Exception as e_stop:
                 logger.warning(f"Errore stop animazione per {prefix} durante reset: {e_stop}")
        self._active_badge_animations.clear() # Svuota il dizionario

        # Rimuovi widget dal layout e resetta stato/effetti
        for widget in list(self._badge_widgets):
             try:
                 if widget:
                     widget.setVisible(False)
                     # Reset effetti grafici
                     opacity_effect = widget.property("opacityEffect")
                     if isinstance(opacity_effect, QtWidgets.QGraphicsOpacityEffect):
                         opacity_effect.setOpacity(0.0)
                     # Ripristina lo stylesheet originale se modificato dal flash
                     original_style = widget.property("originalStyleSheet")
                     if original_style:
                          widget.setStyleSheet(original_style)

                     self.badge_layout.removeWidget(widget)
                     self._badge_widgets.remove(widget)
             except Exception as e:
                 logger.warning(f"Errore durante rimozione/reset badge dal layout: {e}")

        # Resetta il testo nelle label interne alla mappa (anche se nascoste)
        for prefix, (card, label, opacity_effect) in self._badge_widgets_map.items():
            if label: label.setText(f"{prefix}: 0")
            if card:
                card.setVisible(False) # Assicura sia nascosto
                if isinstance(opacity_effect, QtWidgets.QGraphicsOpacityEffect):
                    opacity_effect.setOpacity(0.0) # Assicura opacità a 0
                original_style = card.property("originalStyleSheet")
                if original_style:
                     card.setStyleSheet(original_style) # Ripristina stile

        logger.debug("Reset badges completato.")


    def _reset_ui_after_processing(self):
        """Resets button states and stops spinner after processing."""
        logger.debug("Resetting UI after processing...")
        self.btn_start.setEnabled(True); self.btn_stop.setEnabled(False); self.btn_open.setEnabled(True)
        self.spinner.stopAnimation() # Assicura che lo spinner sia fermo


    def closeEvent(self, event: QtGui.QCloseEvent):
        """Handles the application window closing event."""
        logger.info("Evento Chiusura Finestra ricevuto.")
        if self.thread is not None and self.thread.isRunning():
            reply = QtWidgets.QMessageBox.question(self, "Conferma Uscita",
                                                   "L'elaborazione è ancora in corso.\nVuoi interromperla e uscire?",
                                                   QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                                                   QtWidgets.QMessageBox.StandardButton.No)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                logger.info("Richiesta stop al worker prima di chiudere...")
                self.stop_processing()
                self._set_status_message("⏳ Chiusura in corso...", False)
                # Dai un po' di tempo al thread per terminare
                if not self.thread.wait(1500): # Aumentato leggermente il timeout
                    logger.warning("Timeout attesa worker durante la chiusura. Uscita forzata.")
                else:
                    logger.info("Worker thread terminato correttamente.")
                event.accept() # Accetta la chiusura
            else:
                logger.info("Chiusura annullata dall'utente.")
                event.ignore() # Ignora l'evento di chiusura
        else:
            event.accept() # Nessun thread in corso, chiudi normalmente

# Nota: Il blocco if __name__ == '__main__': si trova in main.py (o nel file principale che avvia l'app)

# --- Assicurati che il file principale (es. main.py) abbia questo blocco ---
# if __name__ == '__main__':
#     # Imposta attributi per rendering alta DPI (opzionale ma consigliato)
#     if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
#         QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
#     if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
#         QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
#
#     app = QtWidgets.QApplication(sys.argv)
#     # Imposta stile (opzionale)
#     # app.setStyle('Fusion')
#
#     # Carica font personalizzato se qtawesome è disponibile (opzionale)
#     if QTAWESOME_AVAILABLE:
#         try:
#              qta.load_font('fa5s', 'fontawesome5-solid-900.ttf', 'fa5s-charmap.json')
#              qta.load_font('fa5r', 'fontawesome5-regular-400.ttf', 'fa5r-charmap.json')
#              qta.load_font('fa5b', 'fontawesome5-brands-400.ttf', 'fa5b-charmap.json')
#              logger.info("Font Awesome caricati tramite qtawesome.")
#         except Exception as e_font:
#              logger.warning(f"Impossibile caricare font Awesome: {e_font}")
#
#     window = App() # Crea l'istanza della finestra principale
#     window.show()
#     sys.exit(app.exec())