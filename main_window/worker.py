# main_window/worker.py
# Worker class for background processing of NSIS codes

from PyQt6 import QtCore
from typing import List, Dict, Any, Optional
import logging
from .state_manager import AppState

class Worker(QtCore.QObject):
    """Worker class for processing NSIS codes in background thread."""
    
    # Signals for communication with main thread
    progress = QtCore.pyqtSignal(int, int)  # current, total
    statusUpdate = QtCore.pyqtSignal(str)   # status message
    logUpdate = QtCore.pyqtSignal(str)      # log message
    badgeUpdate = QtCore.pyqtSignal(str, int)  # badge_prefix, count
    finished = QtCore.pyqtSignal()          # processing finished
    resultsReady = QtCore.pyqtSignal(list)  # results list
    requestFetch = QtCore.pyqtSignal(str)   # request to fetch code
    stateChanged = QtCore.pyqtSignal(AppState)  # worker state change
    
    def __init__(self, codes_to_process: List[str]):
        super().__init__()
        self.codes = codes_to_process
        self._stop_requested = False
        self._results: List[Dict[str, Any]] = []
        self._current_code_index = 0
        self._total_codes = len(codes_to_process)
        self._logger = logging.getLogger(__name__)
        
        # Initialize counters for different states
        self._counts = {
            "annullata": 0, 
            "aperta": 0, 
            "chiusa": 0, 
            "lavorazione": 0, 
            "inviata": 0, 
            "eccezioni": 0
        }
        
        # Badge mapping for UI display
        self._badge_map = {
            "ANNULLATA": "🟡 Annullate", 
            "APERTA": "🟢 Aperte", 
            "CHIUSA": "✅ Chiuse",
            "IN LAVORAZIONE": "🟠 In lavorazione", 
            "INVIATA": "📤 Inviate",
            "ECCEZIONE": "❗ Eccezioni"
        }
        
        # Mapping from state to counter key
        self._count_keys = {
            "ANNULLATA": "annullata", 
            "APERTA": "aperta", 
            "CHIUSA": "chiusa",
            "IN LAVORAZIONE": "lavorazione", 
            "INVIATA": "inviata"
        }
        
        # Exception states that should be counted as errors
        self._exception_states = {
            "NON TROVATO", "ERRORE TIMEOUT", "ERRORE PAGINA", 
            "ERRORE INTERNO FETCH", "SCONOSCIUTO", "INTERROTTO",
            "ERRORE CARICAMENTO PAGINA", "ELEMENTO NON TROVATO (JS)", 
            "ERRORE RISULTATO JS"
        }
        
        self._finished_emitted_after_stop = False
        self._current_state = AppState.IDLE
    
    def run(self):
        """Main execution logic for the worker thread."""
        try:
            self._logger.info("Worker thread started")
            self._set_state(AppState.PROCESSING)
            
            # Reset state
            self._results = []
            self._counts = {k: 0 for k in self._counts}
            self._stop_requested = False
            self._finished_emitted_after_stop = False
            
            if not self.codes:
                self.logUpdate.emit("Nessun codice da processare nel worker.")
                self._set_state(AppState.COMPLETED)
                self.finished.emit()
                return
            
            self.progress.emit(0, self._total_codes)
            self._current_code_index = 0
            
            if not self._stop_requested:
                self.statusUpdate.emit("⚙️ Inizializzazione elaborazione...")
                if self._current_code_index < len(self.codes):
                    code = self.codes[self._current_code_index]
                    self.statusUpdate.emit(f"🚀 Avvio elaborazione codice {code}")
                    self.requestFetch.emit(code)
                else:
                    self.logUpdate.emit("Lista codici vuota.")
                    self._set_state(AppState.COMPLETED)
                    self.finished.emit()
            else:
                self.logUpdate.emit("❌ Interrotto prima dell'inizio.")
                self._set_state(AppState.IDLE)
                self.finished.emit()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.logUpdate.emit(f"❌ Errore nel worker: {e}")
            self._set_state(AppState.ERROR)
            self.finished.emit()
    
    @QtCore.pyqtSlot(str, str, list)
    def processFetchedResult(self, code: str, state: str, last_cells: List[str]):
        """Process the result received from the main thread for a code."""
        self._logger.debug(f"processFetchedResult ricevuto: codice='{code}', stato='{state}', celle={len(last_cells)}")
        
        if self._stop_requested:
            if not self._finished_emitted_after_stop:
                thread = self.thread()
                if thread and thread.isRunning():
                    self.logUpdate.emit(f"❌ Elaborazione interrotta nel worker (risultato per {code} ricevuto: {state}). Fine.")
                    self.resultsReady.emit(self._results)
                    self._set_state(AppState.IDLE)
                    self.finished.emit()
                    self._finished_emitted_after_stop = True
            return
        
        current_idx = self._current_code_index
        self.logUpdate.emit(f"{current_idx + 1}/{self._total_codes} ➜ Codice: {code} | Stato Web: {state}")
        
        # Process state and update counters
        normalized_state_upper = state.strip().upper()
        status_key_for_count, badge_prefix = self._process_state(normalized_state_upper)
        
        # Update counters
        self._counts[status_key_for_count] += 1
        count_to_display = self._counts[status_key_for_count]
        self.badgeUpdate.emit(badge_prefix, count_to_display)
        
        # Extract data from cells
        result_data = self._extract_result_data(code, state, last_cells, normalized_state_upper)
        self._results.append(result_data)
        
        # Update progress
        self.progress.emit(current_idx + 1, self._total_codes)
        self._current_code_index += 1
        
        # Continue with next code or finish
        if self._current_code_index < self._total_codes:
            next_code = self.codes[self._current_code_index]
            self.statusUpdate.emit(f"🌐 Recupero dati per codice {next_code}")
            self.requestFetch.emit(next_code)
        else:
            self.logUpdate.emit("✅ Elaborazione codici completata.")
            self.statusUpdate.emit("🎉 Elaborazione completata con successo!")
            self.resultsReady.emit(self._results)
            self._set_state(AppState.COMPLETED)
            self.finished.emit()
    
    def _process_state(self, normalized_state: str) -> tuple[str, str]:
        """Process state and return counter key and badge prefix."""
        if normalized_state in self._exception_states:
            status_key_for_count = "eccezioni"
            badge_prefix = self._badge_map["ECCEZIONE"]
        else:
            status_key_for_count = self._count_keys.get(normalized_state, "eccezioni")
            badge_prefix = self._badge_map.get(normalized_state, self._badge_map["ECCEZIONE"])
            if status_key_for_count == "eccezioni" and normalized_state not in self._exception_states:
                self.logUpdate.emit(f"⚠️ Stato non mappato: '{normalized_state}'. Conteggiato come Eccezione.")
        
        if status_key_for_count not in self._counts:
            self.logUpdate.emit(f"⚠️ Chiave conteggio interna non prevista: {status_key_for_count} per stato {normalized_state}")
            status_key_for_count = "eccezioni"
        
        return status_key_for_count, badge_prefix
    
    def _extract_result_data(self, code: str, state: str, last_cells: List[str], normalized_state: str) -> Dict[str, Any]:
        """Extract result data from cells and create result dictionary."""
        self._logger.debug(f"_extract_result_data: codice='{code}', stato='{state}'")
        
        stato_res = state
        protocollo_uscita_res = last_cells[5] if len(last_cells) > 5 else ''
        provvedimento_res = last_cells[6] if len(last_cells) > 6 else ''
        data_provvedimento_res = last_cells[7] if len(last_cells) > 7 else ''
        codice_richiesta_risultato_res = last_cells[8] if len(last_cells) > 8 and last_cells[8] else code
        note_usmaf_res = last_cells[10] if len(last_cells) > 10 else ''
        
        if normalized_state in self._exception_states:
            note_usmaf_res = f"Stato recuperato: {state}. {note_usmaf_res}".strip()
        
        result_dict = {
            'Input Code': code,
            'Stato': stato_res,
            'Protocollo uscita': protocollo_uscita_res,
            'Provvedimento': provvedimento_res,
            'Data Provvedimento': data_provvedimento_res,
            'Codice richiesta (risultato)': codice_richiesta_risultato_res,
            'Note Usmaf': note_usmaf_res
        }
        
        self._logger.debug(f"Risultato estratto: {result_dict}")
        return result_dict
    
    def request_stop(self):
        """Request the worker to stop processing."""
        self._stop_requested = True
        self._logger.info("Stop requested for worker")
    
    def _set_state(self, state: AppState):
        """Set worker state and emit signal."""
        self._current_state = state
        self.stateChanged.emit(state)
    
    @property
    def current_state(self) -> AppState:
        """Get current worker state."""
        return self._current_state
    
    @property
    def results(self) -> List[Dict[str, Any]]:
        """Get current results."""
        return self._results.copy()
    
    @property
    def counts(self) -> Dict[str, int]:
        """Get current counts."""
        return self._counts.copy()
    
    @property
    def progress_percentage(self) -> float:
        """Get current progress as percentage."""
        if self._total_codes == 0:
            return 0.0
        return (self._current_code_index / self._total_codes) * 100
    

    
    def _simulate_fetch_result(self, code: str):
        """Simulate fetch result for testing without web automation."""
        try:
            import random
            
            # Simulate different states
            states = ["APERTA", "CHIUSA", "IN LAVORAZIONE", "ANNULLATA", "INVIATA"]
            simulated_state = random.choice(states)
            
            # Simulate cells data
            simulated_cells = [
                "", "", simulated_state, "", "",  # Stato in posizione 2
                f"PROT-{code}", f"PROV-{code}", "2024-01-01", code, "", f"Note per {code}"
            ]
            
            # Process the simulated result
            self.processFetchedResult(code, simulated_state, simulated_cells)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def reset(self):
        """Reset worker state for reuse."""
        self._stop_requested = False
        self._results = []
        self._counts = {k: 0 for k in self._counts}
        self._current_code_index = 0
        self._finished_emitted_after_stop = False
        self._set_state(AppState.IDLE) 