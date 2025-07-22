# main_window/app.py
# Main application class for NSIS state checker

from PyQt6 import QtCore, QtWidgets, QtWebEngineWidgets
from PyQt6.QtCore import QThread
import logging
import os
from typing import Optional

# Import our modules
from .state_manager import StateManager, AppState
from .worker import Worker
from .excel_handler import ExcelHandler
from .web_automation import WebAutomation
from .ui_manager import UIManager

class App(QtWidgets.QWidget):
    """Main application window class."""
    
    def __init__(self, ui_font_family: str = 'Arial'):
        super().__init__()
        
        try:
            # Setup logging
            self._setup_logging()
            self._logger = logging.getLogger(__name__)
            
            # Initialize components
            self._state_manager = StateManager()
            self._excel_handler = ExcelHandler()
            self._web_automation = WebAutomation()
            self._ui_manager = UIManager(self)
            
            # Thread management
            self._worker_thread: Optional[QThread] = None
            self._worker: Optional[Worker] = None
            
            # Setup UI
            self._setup_ui(ui_font_family)
            self._setup_web_engine()
            self._connect_signals()
            
            # Set initial state
            self._state_manager.transition_to(AppState.IDLE)
            
            # Show the window
            self.show()
            
            self._logger.info("Application initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error in App.__init__: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('nsis_app.log', encoding='utf-8')
            ]
        )
    
    def _setup_ui(self, ui_font_family: str):
        """Setup the user interface."""
        # Set window properties
        self.setWindowTitle("Controllo Stato Richiesta NSIS v2.0")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Set font
        if ui_font_family and ui_font_family != 'Arial':
            font = QtWidgets.QApplication.font()
            font.setFamily(ui_font_family)
            QtWidgets.QApplication.setFont(font)
        
        # Set window icon if available
        icon_path = "icon.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Connect resize event for responsive layout
        self.resizeEvent = self._handle_resize_event
    
    def _handle_resize_event(self, event):
        """Handle window resize event to optimize layout."""
        self._ui_manager.update_layout_on_resize()
    
    def _setup_web_engine(self):
        """Setup web engine components like in the original working version."""
        try:
            print("DEBUG: Setup web engine come nel file originale...")
            
            # Create web view like in original
            web_view = QtWebEngineWidgets.QWebEngineView()
            print("DEBUG: QWebEngineView creato")
            
            # Create page like in original
            from PyQt6.QtWebEngineCore import QWebEnginePage
            # Use our custom WebEnginePage from web_automation module
            from .web_automation import WebEnginePage
            page = WebEnginePage(web_view)
            web_view.setPage(page)
            print("DEBUG: WebEnginePage personalizzata creata e impostata")
            
            # Set up web automation with the web view
            self._web_automation.setup_web_engine(web_view)
            print("DEBUG: Web automation setup completato")
            
            # Set web view in UI
            self._ui_manager.set_web_view(web_view)
            print("DEBUG: Web view impostato in UI")
            
            # Connect page load signal like in original
            page.loadFinished.connect(self._handle_page_load_finished)
            print("DEBUG: Segnale loadFinished connesso")
            
            # Load initial URL immediately like in original
            web_view.load(QtCore.QUrl("https://www.impresa.gov.it/intro/info/news.html"))
            
            self._logger.info("Web engine setup completed successfully")
            self._ui_manager.add_log_message("✅ Web Engine inizializzato correttamente")
            
        except Exception as e:
            self._logger.error(f"Failed to setup web engine: {e}")
            self._ui_manager.add_log_message(f"❌ Errore setup web engine: {e}")
            # Create fallback placeholder
            self._create_web_placeholder()
    
    def _handle_page_load_finished(self, ok):
        """Handle page load finished like in the original version."""
        if ok:
            self._logger.info("Page loaded successfully")
            self._ui_manager.add_log_message("✅ Pagina web caricata correttamente")
        else:
            self._logger.error("Page load failed")
            self._ui_manager.add_log_message("❌ Errore caricamento pagina web")
    
    def _create_web_placeholder(self):
        """Create a placeholder when web engine fails."""
        placeholder = QtWidgets.QWidget()
        placeholder.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(placeholder)
        label = QtWidgets.QLabel("🌐 Area Web\n(Web Engine non disponibile)")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(label)
        
        self._ui_manager.set_web_view(placeholder)
    
    def _connect_signals(self):
        """Connect all signals between components."""
        # UI Manager signals
        self._ui_manager.startButtonClicked.connect(self.start_processing)
        self._ui_manager.stopButtonClicked.connect(self.stop_processing)
        self._ui_manager.clearLogClicked.connect(self._clear_log)
        self._ui_manager.openNsisClicked.connect(self._open_nsis_url)
        self._ui_manager.resetLayoutClicked.connect(self._reset_layout)
        self._ui_manager.fileSelected.connect(self._on_file_selected)
        
        # State Manager signals
        self._state_manager.stateChanged.connect(self._on_state_changed)
        
        # Web Automation signals
        self._web_automation.fetchCompleted.connect(self._on_fetch_completed)
        self._web_automation.fetchFailed.connect(self._on_fetch_failed)
        self._web_automation.stateChanged.connect(self._on_web_state_changed)
    
    def start_processing(self):
        """Start the processing of NSIS codes."""
        try:
            print("DEBUG: start_processing chiamato")
            
            if not self._state_manager.can_start_processing():
                print("DEBUG: Non può avviare elaborazione in questo stato")
                self._ui_manager.add_log_message("⚠️ Non è possibile avviare l'elaborazione in questo stato")
                return
            
            print("DEBUG: Controllo file Excel...")
            # Check if file is loaded
            if not self._excel_handler.codes:
                print("DEBUG: Nessun file Excel caricato")
                self._ui_manager.add_log_message("❌ Nessun file Excel caricato o nessun codice trovato")
                return
            
            print(f"DEBUG: {len(self._excel_handler.codes)} codici trovati")
            print("DEBUG: Transizione a LOADING...")
            # Transition to loading state
            self._state_manager.transition_to(AppState.LOADING)
            
            print("DEBUG: Creazione Worker...")
            # Create and setup worker
            self._worker = Worker(self._excel_handler.codes)
            print("DEBUG: Worker creato")
            
            print("DEBUG: Creazione QThread...")
            self._worker_thread = QThread()
            print("DEBUG: QThread creato")
            
            print("DEBUG: Spostamento Worker nel thread...")
            self._worker.moveToThread(self._worker_thread)
            print("DEBUG: Worker spostato nel thread")
            
            print("DEBUG: Connessione segnali Worker...")
            # Connect worker signals
            self._worker.progress.connect(self._ui_manager.update_progress)
            self._worker.statusUpdate.connect(self._ui_manager.update_status)
            self._worker.logUpdate.connect(self._ui_manager.add_log_message)
            self._worker.badgeUpdate.connect(self._ui_manager.update_badge)
            self._worker.finished.connect(self._on_worker_finished)
            self._worker.resultsReady.connect(self._on_results_ready)
            self._worker.requestFetch.connect(self._web_automation.fetch_state_for_code)
            print("DEBUG: Segnali Worker connessi")
            
            print("DEBUG: Connessione segnali Thread...")
            # Connect thread signals
            self._worker_thread.started.connect(self._worker.run)
            self._worker_thread.finished.connect(self._worker_thread.deleteLater)
            print("DEBUG: Segnali Thread connessi")
            
            print("DEBUG: Setup UI per elaborazione...")
            # Start processing
            self._ui_manager.set_processing_state(True)
            self._ui_manager.reset_badges()
            self._ui_manager.add_log_message("🚀 Avvio elaborazione codici...")
            print("DEBUG: UI setup completato")
            
            print("DEBUG: Avvio worker thread...")
            self._worker_thread.start()
            print("DEBUG: Worker thread avviato")
            
            print("DEBUG: Transizione a PROCESSING...")
            self._state_manager.transition_to(AppState.PROCESSING)
            print("DEBUG: start_processing completato con successo")
            
        except Exception as e:
            print(f"ERRORE in start_processing: {e}")
            import traceback
            traceback.print_exc()
            self._ui_manager.add_log_message(f"❌ Errore avvio elaborazione: {e}")
    
    def stop_processing(self):
        """Stop the processing of NSIS codes."""
        if not self._state_manager.can_stop_processing():
            return
        
        self._state_manager.transition_to(AppState.STOPPING)
        
        if self._worker:
            self._worker.request_stop()
        
        self._web_automation.stop()
        self._ui_manager.add_log_message("⏹️ Interruzione elaborazione...")
    
    def _on_file_selected(self, file_path: str):
        """Handle file selection."""
        self._ui_manager.add_log_message(f"📁 Caricamento file: {os.path.basename(file_path)}")
        
        success, codes, error_msg = self._excel_handler.load_excel_file(file_path)
        
        if success:
            self._ui_manager.add_log_message(f"✅ Caricati {len(codes)} codici dal file")
            self._ui_manager.update_status(f"Pronto: {len(codes)} codici da elaborare")
        else:
            self._ui_manager.add_log_message(f"❌ Errore caricamento file: {error_msg}")
            self._ui_manager.update_status("Errore caricamento file")
    
    def _on_fetch_completed(self, code: str, state: str, cells: list):
        """Handle completed fetch from web automation."""
        if self._worker:
            self._worker.processFetchedResult(code, state, cells)
    
    def _on_fetch_failed(self, code: str, error_msg: str):
        """Handle failed fetch from web automation."""
        if code == "UNKNOWN":
            self._ui_manager.add_log_message(f"❌ Errore fetch: {error_msg}")
        else:
            self._ui_manager.add_log_message(f"❌ Errore fetch per {code}: {error_msg}")
        
        # Process as exception
        if self._worker:
            self._worker.processFetchedResult(code, "ERRORE FETCH", [])
    
    def _on_results_ready(self, results_list: list):
        """Handle results ready from worker."""
        self._logger.debug(f"Risultati ricevuti dal worker: {len(results_list)} elementi")
        for i, result in enumerate(results_list[:3]):  # Log primi 3 risultati
            self._logger.debug(f"Risultato {i+1}: {result}")
        
        self._ui_manager.add_log_message(f"📊 Elaborazione completata: {len(results_list)} risultati")
        
        # Save results to Excel
        if self._excel_handler.current_file_path:
            success, output_path, error_msg = self._excel_handler.save_results_to_excel(
                results_list, self._excel_handler.current_file_path
            )
            
            if success:
                self._ui_manager.add_log_message(f"💾 Risultati salvati in: {os.path.basename(output_path)}")
                self._ui_manager.update_status("✅ Elaborazione completata e salvata")
            else:
                self._ui_manager.add_log_message(f"❌ Errore salvataggio: {error_msg}")
                self._ui_manager.update_status("❌ Errore salvataggio risultati")
    
    def _on_worker_finished(self):
        """Handle worker thread finished."""
        if self._worker_thread:
            self._worker_thread.quit()
            self._worker_thread.wait()
        
        self._ui_manager.set_processing_state(False)
        self._state_manager.transition_to(AppState.COMPLETED)
        
        self._ui_manager.add_log_message("🏁 Elaborazione terminata")
    
    def _on_state_changed(self, old_state: AppState, new_state: AppState):
        """Handle application state change."""
        self._logger.info(f"Application state changed: {old_state.value} -> {new_state.value}")
        
        # Update UI based on state
        if new_state == AppState.PROCESSING:
            self._ui_manager.set_processing_state(True)
        elif new_state in [AppState.IDLE, AppState.COMPLETED]:
            self._ui_manager.set_processing_state(False)
        elif new_state == AppState.ERROR:
            self._ui_manager.update_status("❌ Errore applicazione")
    
    def _on_web_state_changed(self, new_state: AppState):
        """Handle web automation state change."""
        self._logger.debug(f"Web automation state: {new_state.value}")
    
    def _clear_log(self):
        """Clear the log display."""
        self._ui_manager.clear_log()
        self._ui_manager.add_log_message("🗑️ Log pulito")
    
    def _open_nsis_url(self):
        """Open NSIS URL in internal browser."""
        try:
            from config import URL_NSIS
            
            if self._web_automation.web_view:
                # Load NSIS URL in internal browser
                self._web_automation.web_view.load(QtCore.QUrl(URL_NSIS))
                self._ui_manager.add_log_message("🌐 Caricamento NSIS nel browser interno")
                self._logger.info(f"Loading NSIS URL in internal browser: {URL_NSIS}")
            else:
                self._ui_manager.add_log_message("❌ Browser interno non disponibile")
                self._logger.error("Internal browser not available")
        except Exception as e:
            self._ui_manager.add_log_message(f"❌ Errore caricamento NSIS: {e}")
            self._logger.error(f"Error loading NSIS URL: {e}")
    
    def _reset_layout(self):
        """Reset the layout to default sizes."""
        try:
            self._ui_manager.reset_splitter_to_default()
            self._ui_manager.add_log_message("📐 Layout ripristinato alle dimensioni predefinite")
            self._logger.info("Layout reset to default sizes")
        except Exception as e:
            self._ui_manager.add_log_message(f"❌ Errore reset layout: {e}")
            self._logger.error(f"Error resetting layout: {e}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self._state_manager.is_processing():
            reply = QtWidgets.QMessageBox.question(
                self, 
                "Conferma Chiusura",
                "L'elaborazione è ancora in corso. Vuoi davvero chiudere l'applicazione?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        # Stop processing if running
        if self._worker:
            self._worker.request_stop()
        
        # Safely stop worker thread
        if self._worker_thread:
            try:
                if self._worker_thread.isRunning():
                    self._worker_thread.quit()
                    self._worker_thread.wait(5000)  # Wait up to 5 seconds
            except RuntimeError:
                # Thread already deleted, ignore
                pass
        
        self._logger.info("Application closing")
        event.accept() 