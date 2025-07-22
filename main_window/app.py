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
        """Setup the user interface with Glassmorphism design."""
        # Set window properties for Glassmorphism
        self.setWindowTitle("Controllo Stato Richiesta NSIS v2.0 - Glassmorphism")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Enable window transparency for Glassmorphism effect
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        
        # Set window background with increased opacity for better visibility
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(248, 250, 252, 0.6),
                    stop:1 rgba(241, 245, 249, 0.6));
                border-radius: 12px;
            }
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(248, 250, 252, 0.6),
                    stop:1 rgba(241, 245, 249, 0.6));
                border-radius: 12px;
            }
        """)
        # Background applied for balanced glassmorphism
        
        # Set font
        if ui_font_family and ui_font_family != 'Arial':
            font = QtWidgets.QApplication.font()
            font.setFamily(ui_font_family)
            QtWidgets.QApplication.setFont(font)
        
        # Set window icon if available
        icon_path = "icon.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Background is now set directly on the window
        
        # Add window controls for frameless window
        self._setup_window_controls()
        
        # Setup resize functionality
        self._setup_resize_functionality()
        
        # Connect resize event for responsive layout
        self.resizeEvent = self._handle_resize_event
        
        # Connect child added event to enable mouse tracking
        self.childEvent = self._handle_child_event
    

    
    def _setup_window_controls(self):
        """Setup window control buttons for frameless window."""
        # Create window controls container
        self._window_controls = QtWidgets.QWidget(self)
        self._window_controls.setObjectName("windowControls")
        self._window_controls.setFixedSize(120, 40)
        self._window_controls.move(self.width() - 130, 10)
        
        # Ensure controls are on top
        self._window_controls.raise_()
        
        # Store window state
        self._is_maximized = False
        self._normal_geometry = None
        
        # Create layout for controls
        controls_layout = QtWidgets.QHBoxLayout(self._window_controls)
        controls_layout.setSpacing(4)
        controls_layout.setContentsMargins(4, 2, 4, 2)
        
        # Minimize button
        self._minimize_btn = QtWidgets.QPushButton()
        self._minimize_btn.setObjectName("minimizeButton")
        self._minimize_btn.setFixedSize(32, 32)
        self._minimize_btn.clicked.connect(self.showMinimized)
        self._load_window_control_icon(self._minimize_btn, "minimize.png")
        
        # Maximize/Restore button
        self._maximize_btn = QtWidgets.QPushButton()
        self._maximize_btn.setObjectName("maximizeButton")
        self._maximize_btn.setFixedSize(32, 32)
        self._maximize_btn.clicked.connect(self._toggle_maximize)
        self._load_window_control_icon(self._maximize_btn, "large.png")
        
        # Close button
        self._close_btn = QtWidgets.QPushButton()
        self._close_btn.setObjectName("closeButton")
        self._close_btn.setFixedSize(32, 32)
        self._close_btn.clicked.connect(self.close)
        self._load_window_control_icon(self._close_btn, "close.png")
        
        controls_layout.addWidget(self._minimize_btn)
        controls_layout.addWidget(self._maximize_btn)
        controls_layout.addWidget(self._close_btn)
        
        # Style the controls with modern black design
        self._window_controls.setStyleSheet("""
            QWidget#windowControls {
                background: transparent;
                border: none;
            }
            QPushButton#minimizeButton, QPushButton#maximizeButton, QPushButton#closeButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;
                margin: 0px;
                min-width: 32px;
                min-height: 32px;
                max-width: 32px;
                max-height: 32px;
            }
            QPushButton#minimizeButton:hover, QPushButton#maximizeButton:hover {
                background: transparent;
                color: rgba(255, 255, 255, 1.0);
                border: none;
                border-radius: 8px;
            }
            QPushButton#closeButton:hover {
                background: transparent;
                color: rgba(255, 255, 255, 1.0);
                border: none;
                border-radius: 8px;
            }
            QPushButton#minimizeButton:pressed, QPushButton#maximizeButton:pressed {
                background: transparent;
                color: rgba(255, 255, 255, 1.0);
                border: none;
                border-radius: 8px;
            }
            QPushButton#closeButton:pressed {
                background: transparent;
                color: rgba(255, 255, 255, 1.0);
                border: none;
                border-radius: 8px;
            }
        """)
    
    def _load_window_control_icon(self, button, icon_filename):
        """Load PNG icon for window control button."""
        try:
            import os
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", icon_filename)
            if os.path.exists(icon_path):
                from PyQt6.QtGui import QIcon, QPixmap
                icon = QIcon(icon_path)
                # Scale icon to fit button (24x24 to leave some padding)
                pixmap = icon.pixmap(24, 24)
                button.setIcon(QIcon(pixmap))
                button.setIconSize(QtCore.QSize(24, 24))
        except Exception as e:
            # Fallback to text if icon loading fails
            if "minimize" in icon_filename:
                button.setText("−")
            elif "large" in icon_filename:
                button.setText("□")
            elif "close" in icon_filename:
                button.setText("×")
    
    def _setup_resize_functionality(self):
        """Setup resize functionality for frameless window."""
        # Variables for resize functionality
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
        
        # Set up resize areas
        self._resize_border = 8  # Border width for resize detection
        
        # Enable mouse tracking for resize detection
        self.setMouseTracking(True)
        
        # Also enable mouse tracking for child widgets
        self._enable_mouse_tracking_recursive(self)
    
    def _enable_mouse_tracking_recursive(self, widget):
        """Enable mouse tracking for widget and all its children."""
        widget.setMouseTracking(True)
        for child in widget.findChildren(QtWidgets.QWidget):
            child.setMouseTracking(True)
    
    def _handle_child_event(self, event):
        """Handle child added/removed events to maintain mouse tracking."""
        if event.type() == QtCore.QEvent.Type.ChildAdded:
            child = event.child()
            if isinstance(child, QtWidgets.QWidget):
                child.setMouseTracking(True)
                self._enable_mouse_tracking_recursive(child)
        event.accept()
    
    def _toggle_maximize(self):
        """Toggle between maximized and normal window state."""
        if self._is_maximized:
            # Restore to normal size
            if self._normal_geometry:
                self.setGeometry(self._normal_geometry)
            else:
                self.resize(1200, 800)
                self.move(100, 100)
            self._is_maximized = False
            # Icon stays the same for large button
        else:
            # Maximize
            self._normal_geometry = self.geometry()
            screen = QtWidgets.QApplication.primaryScreen().geometry()
            self.setGeometry(screen)
            self._is_maximized = True
            # Icon stays the same for large button
        
        # Update window controls position
        self._update_window_controls_position()
    
    def _update_window_controls_position(self):
        """Update window controls position based on window state."""
        if hasattr(self, '_window_controls'):
            if self._is_maximized:
                # Position controls in top-right corner when maximized
                self._window_controls.move(self.width() - 130, 10)
            else:
                # Position controls normally
                self._window_controls.move(self.width() - 130, 10)
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging and resizing."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Check if we're in a resize area
            edge = self._get_resize_edge(event.pos())
            if edge:
                self._resize_edge = edge
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geometry = self.geometry()
                # Clear any existing drag position to prevent conflicts
                if hasattr(self, '_drag_position'):
                    delattr(self, '_drag_position')
                event.accept()
            else:
                # Normal dragging - only if not in resize mode
                if not hasattr(self, '_resize_edge') or not self._resize_edge:
                    self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging and resizing."""
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            if hasattr(self, '_resize_edge') and self._resize_edge:
                # Handle resizing
                self._handle_resize(event.globalPosition().toPoint())
                event.accept()
                return  # Don't process dragging when resizing
            elif hasattr(self, '_drag_position'):
                # Handle dragging
                self.move(event.globalPosition().toPoint() - self._drag_position)
                event.accept()
                return
        else:
            # Update cursor based on position
            edge = self._get_resize_edge(event.pos())
            self._update_cursor(edge)
    
    def _get_resize_edge(self, pos):
        """Get the resize edge based on mouse position."""
        if self._is_maximized:
            return None
        
        # Don't allow resizing if mouse is over window controls
        if hasattr(self, '_window_controls') and self._window_controls:
            controls_rect = self._window_controls.geometry()
            if controls_rect.contains(pos):
                return None
        
        x, y = pos.x(), pos.y()
        width, height = self.width(), self.height()
        border = self._resize_border
        
        # Check corners first (larger detection area)
        if x < border + 2 and y < border + 2:
            return 'top-left'
        elif x > width - border - 2 and y < border + 2:
            return 'top-right'
        elif x < border + 2 and y > height - border - 2:
            return 'bottom-left'
        elif x > width - border - 2 and y > height - border - 2:
            return 'bottom-right'
        # Check edges
        elif x < border:
            return 'left'
        elif x > width - border:
            return 'right'
        elif y < border:
            return 'top'
        elif y > height - border:
            return 'bottom'
        
        return None
    
    def _update_cursor(self, edge):
        """Update cursor based on resize edge."""
        if not edge:
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            return
        
        cursor_map = {
            'top': QtCore.Qt.CursorShape.SizeVerCursor,
            'bottom': QtCore.Qt.CursorShape.SizeVerCursor,
            'left': QtCore.Qt.CursorShape.SizeHorCursor,
            'right': QtCore.Qt.CursorShape.SizeHorCursor,
            'top-left': QtCore.Qt.CursorShape.SizeFDiagCursor,
            'top-right': QtCore.Qt.CursorShape.SizeBDiagCursor,
            'bottom-left': QtCore.Qt.CursorShape.SizeBDiagCursor,
            'bottom-right': QtCore.Qt.CursorShape.SizeFDiagCursor,
        }
        
        self.setCursor(cursor_map.get(edge, QtCore.Qt.CursorShape.ArrowCursor))
    
    def _handle_resize(self, global_pos):
        """Handle window resizing."""
        if not self._resize_start_pos or not self._resize_start_geometry:
            return
        
        delta = global_pos - self._resize_start_pos
        new_geometry = QtCore.QRect(self._resize_start_geometry)
        
        # Apply resize based on edge
        if 'left' in self._resize_edge:
            new_left = new_geometry.left() + delta.x()
            if new_left < new_geometry.right() - self.minimumWidth():
                new_geometry.setLeft(new_left)
        if 'right' in self._resize_edge:
            new_right = new_geometry.right() + delta.x()
            if new_right > new_geometry.left() + self.minimumWidth():
                new_geometry.setRight(new_right)
        if 'top' in self._resize_edge:
            new_top = new_geometry.top() + delta.y()
            if new_top < new_geometry.bottom() - self.minimumHeight():
                new_geometry.setTop(new_top)
        if 'bottom' in self._resize_edge:
            new_bottom = new_geometry.bottom() + delta.y()
            if new_bottom > new_geometry.top() + self.minimumHeight():
                new_geometry.setBottom(new_bottom)
        
        # Ensure the geometry is valid
        if new_geometry.isValid() and new_geometry.width() >= self.minimumWidth() and new_geometry.height() >= self.minimumHeight():
            self.setGeometry(new_geometry)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging/resizing."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Clear resize state
            self._resize_edge = None
            self._resize_start_pos = None
            self._resize_start_geometry = None
            
            # Clear drag state
            if hasattr(self, '_drag_position'):
                delattr(self, '_drag_position')
            
            # Reset cursor
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            event.accept()
    
    def _handle_resize_event(self, event):
        """Handle window resize event to optimize layout."""
        # Update window controls position
        self._update_window_controls_position()
        
        # Update UI manager layout
        self._ui_manager.update_layout_on_resize()
    
    def _setup_web_engine(self):
        """Setup web engine components like in the original working version."""
        try:
            # Create web view like in original
            self._web_view = QtWebEngineWidgets.QWebEngineView()
            
            # Create page like in original
            from PyQt6.QtWebEngineCore import QWebEnginePage
            # Use our custom WebEnginePage from web_automation module
            from .web_automation import WebEnginePage
            page = WebEnginePage(self._web_view)
            self._web_view.setPage(page)
            
            # Set up web automation with the web view
            self._web_automation.setup_web_engine(self._web_view)
            
            # Set web view in UI
            self._ui_manager.set_web_view(self._web_view)
            
            # Connect page load signal like in original
            page.loadFinished.connect(self._handle_page_load_finished)
            
            # Load initial URL immediately like in original
            self._web_view.load(QtCore.QUrl("https://www.impresa.gov.it/intro/info/news.html"))
            
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
        
        # Web navigation signals
        self._ui_manager.webBackClicked.connect(self._web_back)
        self._ui_manager.webForwardClicked.connect(self._web_forward)
        self._ui_manager.webReloadClicked.connect(self._web_reload)
        
        # State Manager signals
        self._state_manager.stateChanged.connect(self._on_state_changed)
        
        # Web Automation signals
        self._web_automation.fetchCompleted.connect(self._on_fetch_completed)
        self._web_automation.fetchFailed.connect(self._on_fetch_failed)
        self._web_automation.stateChanged.connect(self._on_web_state_changed)
    
    def start_processing(self):
        """Start the processing of NSIS codes."""
        try:
            if not self._state_manager.can_start_processing():
                self._ui_manager.add_log_message("⚠️ Non è possibile avviare l'elaborazione in questo stato")
                return
            
            # Check if file is loaded
            if not self._excel_handler.codes:
                self._ui_manager.add_log_message("❌ Nessun file Excel caricato o nessun codice trovato")
                return
            
            # Transition to loading state
            self._state_manager.transition_to(AppState.LOADING)
            
            # Create and setup worker
            self._worker = Worker(self._excel_handler.codes)
            self._worker_thread = QThread()
            self._worker.moveToThread(self._worker_thread)
            
            # Connect worker signals
            self._worker.progress.connect(self._ui_manager.update_progress)
            self._worker.statusUpdate.connect(self._ui_manager.update_progress_status)
            self._worker.logUpdate.connect(self._ui_manager.add_log_message)
            self._worker.badgeUpdate.connect(self._ui_manager.update_badge)
            self._worker.finished.connect(self._on_worker_finished)
            self._worker.resultsReady.connect(self._on_results_ready)
            self._worker.requestFetch.connect(self._web_automation.fetch_state_for_code)
            
            # Connect thread signals
            self._worker_thread.started.connect(self._worker.run)
            self._worker_thread.finished.connect(self._worker_thread.deleteLater)
            
            # Start processing
            self._ui_manager.set_processing_state(True)
            self._ui_manager.reset_badges()
            self._ui_manager.add_log_message("🚀 Avvio elaborazione codici...")
            
            self._worker_thread.start()
            self._state_manager.transition_to(AppState.PROCESSING)
            
        except Exception as e:
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
            # Update file path display with nice effects
            self._ui_manager.set_file_path(file_path)
            self._ui_manager.add_log_message(f"✅ Caricati {len(codes)} codici dal file")

        else:
            # Reset file path on error
            self._ui_manager.reset_file_path()
            self._ui_manager.add_log_message(f"❌ Errore caricamento file: {error_msg}")

    
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
        self._ui_manager.add_log_message(f"📊 Elaborazione completata: {len(results_list)} risultati")
        
        # Save results to Excel
        if self._excel_handler.current_file_path:
            success, output_path, error_msg = self._excel_handler.save_results_to_excel(
                results_list, self._excel_handler.current_file_path
            )
            
            if success:
                self._ui_manager.add_log_message(f"💾 Risultati salvati in: {os.path.basename(output_path)}")
    
            else:
                self._ui_manager.add_log_message(f"❌ Errore salvataggio: {error_msg}")
    
    
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
            pass
    
    def _on_web_state_changed(self, new_state: AppState):
        """Handle web automation state change."""
        pass
    
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
    
    def _web_back(self):
        """Navigate back in web view."""
        if self._web_view and self._web_view.history().canGoBack():
            self._web_view.back()
            self._ui_manager.add_log_message("⬅️ Navigazione indietro")
            self._logger.info("Web navigation: back")
        else:
            self._ui_manager.add_log_message("⚠️ Non è possibile tornare indietro")
    
    def _web_forward(self):
        """Navigate forward in web view."""
        if self._web_view and self._web_view.history().canGoForward():
            self._web_view.forward()
            self._ui_manager.add_log_message("➡️ Navigazione avanti")
            self._logger.info("Web navigation: forward")
        else:
            self._ui_manager.add_log_message("⚠️ Non è possibile andare avanti")
    
    def _web_reload(self):
        """Reload current page in web view."""
        if self._web_view:
            self._web_view.reload()
            self._ui_manager.add_log_message("🔄 Ricaricamento pagina")
            self._logger.info("Web navigation: reload")
        else:
            self._ui_manager.add_log_message("❌ Browser non disponibile")
    
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