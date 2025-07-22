# main_window/ui_manager.py
# UI Manager module for NSIS application

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWebEngineWidgets import QWebEngineView
import os
from typing import Dict, Any, Optional, Callable
import logging

# Import UI components
from .excel_handler import ExcelHandler
from .state_manager import StateManager
from .web_automation import WebAutomation
from .worker import Worker

# Import configuration
from config import (
    COLOR_LUMA_WHITE, COLOR_LUMA_GRAY_10, COLOR_LUMA_GRAY_30, COLOR_LUMA_GRAY_50,
    COLOR_LUMA_GRAY_70, COLOR_LUMA_GRAY_90, COLOR_LUMA_PURPLE_400, COLOR_LUMA_PURPLE_500,
    LUMA_BORDER_RADIUS_BUTTON, LUMA_BORDER_RADIUS_CONTAINER, LUMA_BORDER_COLOR_INPUT,
    COLOR_ANNULATA, COLOR_APERTA, COLOR_CHIUSA, COLOR_LAVORAZIONE, COLOR_INVIATA, COLOR_ECCEZIONI
)

# Custom UI Components
class CustomProgressBar(QtWidgets.QProgressBar):
    """Custom progress bar with enhanced styling."""
    pass

class SpinnerWidget(QtWidgets.QWidget):
    """Custom spinner widget for loading states."""
    def __init__(self, parent=None): 
        super().__init__(parent)
        self.hide()
    def startAnimation(self): self.show()
    def stopAnimation(self): self.hide()
    def setColor(self, color): pass

class UIManager(QtCore.QObject):
    """Manages UI components and their interactions."""
    
    # Signals
    startButtonClicked = QtCore.pyqtSignal()
    stopButtonClicked = QtCore.pyqtSignal()
    clearLogClicked = QtCore.pyqtSignal()
    openNsisClicked = QtCore.pyqtSignal()
    resetLayoutClicked = QtCore.pyqtSignal()
    fileSelected = QtCore.pyqtSignal(str)  # file_path
    
    def __init__(self, parent_widget: QtWidgets.QWidget):
        super().__init__()
        self._parent = parent_widget
        self._logger = logging.getLogger(__name__)
        
        # UI Components
        self._main_layout: Optional[QtWidgets.QVBoxLayout] = None
        self._file_selection_frame: Optional[QtWidgets.QFrame] = None
        self._control_frame: Optional[QtWidgets.QFrame] = None
        self._progress_frame: Optional[QtWidgets.QFrame] = None
        self._badges_frame: Optional[QtWidgets.QFrame] = None
        self._log_frame: Optional[QtWidgets.QFrame] = None
        self._web_frame: Optional[QtWidgets.QFrame] = None
        
        # Widgets
        self._file_path_label: Optional[QtWidgets.QLabel] = None
        self._select_file_button: Optional[QtWidgets.QPushButton] = None
        self._start_button: Optional[QtWidgets.QPushButton] = None
        self._stop_button: Optional[QtWidgets.QPushButton] = None
        self._clear_log_button: Optional[QtWidgets.QPushButton] = None
        self._open_nsis_button: Optional[QtWidgets.QPushButton] = None
        self._progress_bar: Optional[CustomProgressBar] = None
        self._status_label: Optional[QtWidgets.QLabel] = None
        self._log_text: Optional[QtWidgets.QTextEdit] = None
        self._web_view: Optional[QtWidgets.QWidget] = None  # Placeholder for QWebEngineView
        
        # Badge widgets
        self._badge_widgets: Dict[str, QtWidgets.QFrame] = {}
        
        # Setup UI
        self._setup_ui()
        self._setup_styles()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the complete UI with integrated layout."""
        # Main layout with better space utilization
        main_layout = QtWidgets.QVBoxLayout(self._parent)
        main_layout.setSpacing(6)  # Reduced spacing
        main_layout.setContentsMargins(12, 12, 12, 12)  # Reduced margins
        
        # Main content area with integrated controls
        self._create_main_content_area(main_layout)
        
        # Bottom status/log area
        self._create_bottom_status_area(main_layout)
        
        # Initialize responsive behavior
        self._parent.resizeEvent = self._handle_resize_event

    def _create_header_section(self, parent_layout):
        """Create the header section with title and subtitle."""
        header_container = QtWidgets.QFrame()
        header_container.setObjectName("headerContainer")
        header_container.setStyleSheet("""
            QFrame#headerContainer {
                background: transparent;
                border: none;
            }
        """)
        
        header_layout = QtWidgets.QVBoxLayout(header_container)
        header_layout.setSpacing(4)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main title
        title_label = QtWidgets.QLabel("NSIS Controller")
        title_label.setObjectName("mainTitle")
        title_label.setStyleSheet("""
            QLabel#mainTitle {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        
        # Subtitle
        subtitle_label = QtWidgets.QLabel("Controllo Stato Richieste")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setStyleSheet("""
            QLabel#subtitle {
                color: #a0aec0;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        parent_layout.addWidget(header_container)

    def _create_main_content_area(self, parent_layout):
        """Create the main content area with integrated controls and web view."""
        # Main content container
        content_container = QtWidgets.QFrame()
        content_container.setObjectName("contentContainer")
        content_container.setStyleSheet("""
            QFrame#contentContainer {
                background: transparent;
                border: none;
            }
        """)
        
        content_layout = QtWidgets.QHBoxLayout(content_container)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel with controls and stats
        self._create_left_panel(content_layout)
        
        # Web view area
        self._create_web_area(content_layout)
        
        parent_layout.addWidget(content_container, 1)  # Give it stretch priority

    def _create_left_panel(self, parent_layout):
        """Create the left panel with controls and statistics."""
        left_panel = QtWidgets.QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setStyleSheet("""
            QFrame#leftPanel {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 12px;
            }
        """)
        left_panel.setMinimumWidth(280)
        left_panel.setMaximumWidth(350)
        
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls section
        self._create_controls_section(left_layout)
        
        # Statistics section
        self._create_statistics_section(left_layout)
        
        parent_layout.addWidget(left_panel)

    def _create_controls_section(self, parent_layout):
        """Create the controls section with integrated file selection."""
        controls_container = QtWidgets.QFrame()
        controls_container.setObjectName("controlsContainer")
        controls_container.setStyleSheet("""
            QFrame#controlsContainer {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        controls_layout = QtWidgets.QVBoxLayout(controls_container)
        controls_layout.setSpacing(8)  # Reduced spacing
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls title - Compact
        controls_title = QtWidgets.QLabel("🎮 Controlli")
        controls_title.setObjectName("controlsTitle")
        controls_title.setFixedHeight(20)  # Fixed compact height
        controls_title.setStyleSheet("""
            QLabel#controlsTitle {
                color: #ffffff;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 0.5px;
                margin: 0;
                padding: 0;
            }
        """)
        
        # File selection section (integrated) - Increased height
        file_container = QtWidgets.QFrame()
        file_container.setObjectName("fileContainer")
        file_container.setFixedHeight(40)  # Increased height to prevent text cutting
        file_container.setStyleSheet("""
            QFrame#fileContainer {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        file_layout = QtWidgets.QHBoxLayout(file_container)
        file_layout.setSpacing(8)
        file_layout.setContentsMargins(0, 0, 0, 0)
        
        # Compact file selection button with Excel icon
        self._file_button = QtWidgets.QPushButton("📊 Seleziona File Excel")
        self._file_button.setObjectName("fileButton")
        self._file_button.setFixedHeight(28)  # Increased height
        self._file_button.setStyleSheet("""
            QPushButton#fileButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton#fileButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
        """)
        
        # Compact file status label
        self._file_status = QtWidgets.QLabel("Nessun file selezionato")
        self._file_status.setObjectName("fileStatus")
        self._file_status.setFixedHeight(28)  # Increased height
        self._file_status.setStyleSheet("""
            QLabel#fileStatus {
                color: #a0aec0;
                font-size: 10px;
                padding: 6px 10px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        file_layout.addWidget(self._file_button)
        file_layout.addWidget(self._file_status, 1)  # Give it stretch
        
        # Action buttons container - Increased height
        buttons_container = QtWidgets.QFrame()
        buttons_container.setObjectName("buttonsContainer")
        buttons_container.setFixedHeight(40)  # Increased height
        buttons_container.setStyleSheet("""
            QFrame#buttonsContainer {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        buttons_layout = QtWidgets.QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(8)  # Consistent spacing
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self._start_button = QtWidgets.QPushButton("▶️ Avvia")
        self._start_button.setObjectName("startButton")
        self._start_button.setFixedHeight(28)  # Increased height
        self._start_button.setStyleSheet("""
            QPushButton#startButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #48bb78, stop:0.5 #38a169, stop:1 #2f855a);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton#startButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #38a169, stop:0.5 #2f855a, stop:1 #276749);
            }
            QPushButton#startButton:disabled {
                background: #4a5568;
                color: #a0aec0;
            }
        """)
        
        self._stop_button = QtWidgets.QPushButton("⏹️ Stop")
        self._stop_button.setObjectName("stopButton")
        self._stop_button.setFixedHeight(28)  # Increased height
        self._stop_button.setStyleSheet("""
            QPushButton#stopButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f56565, stop:0.5 #e53e3e, stop:1 #c53030);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton#stopButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e53e3e, stop:0.5 #c53030, stop:1 #9b2c2c);
            }
            QPushButton#stopButton:disabled {
                background: #4a5568;
                color: #a0aec0;
            }
        """)
        
        # Single utility button (clear log) - Increased height
        self._clear_button = QtWidgets.QPushButton("🗑️ Pulisci Log")
        self._clear_button.setObjectName("clearButton")
        self._clear_button.setFixedHeight(28)  # Increased height
        self._clear_button.setStyleSheet("""
            QPushButton#clearButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                color: #a0aec0;
                font-size: 10px;
                padding: 6px 12px;
            }
            QPushButton#clearButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        buttons_layout.addWidget(self._start_button)
        buttons_layout.addWidget(self._stop_button)
        buttons_layout.addWidget(self._clear_button)
        buttons_layout.addStretch()
        
        controls_layout.addWidget(controls_title)
        controls_layout.addWidget(file_container)
        controls_layout.addWidget(buttons_container)
        controls_layout.addStretch()  # Push everything to the top
        parent_layout.addWidget(controls_container)

    def _create_statistics_section(self, parent_layout):
        """Create the statistics section with badges."""
        stats_container = QtWidgets.QFrame()
        stats_container.setObjectName("statsContainer")
        stats_container.setStyleSheet("""
            QFrame#statsContainer {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        stats_layout = QtWidgets.QVBoxLayout(stats_container)
        stats_layout.setSpacing(8)  # Consistent spacing
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        # Statistics title
        stats_title = QtWidgets.QLabel("📈 Statistiche")
        stats_title.setObjectName("statsTitle")
        stats_title.setStyleSheet("""
            QLabel#statsTitle {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }
        """)
        
        stats_layout.addWidget(stats_title)
        
        # Create badges with improved layout
        self._create_modern_badges(stats_layout)
        parent_layout.addWidget(stats_container)

    def _create_web_area(self, parent_layout):
        """Create the web view area."""
        web_container = QtWidgets.QFrame()
        web_container.setObjectName("webContainer")
        web_container.setStyleSheet("""
            QFrame#webContainer {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 8px;
            }
        """)
        
        web_layout = QtWidgets.QVBoxLayout(web_container)
        web_layout.setSpacing(8)
        web_layout.setContentsMargins(0, 0, 0, 0)
        
        # Navigation toolbar
        nav_container = QtWidgets.QFrame()
        nav_container.setObjectName("navContainer")
        nav_container.setStyleSheet("""
            QFrame#navContainer {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
            }
        """)
        nav_container.setMaximumHeight(48)
        
        nav_layout = QtWidgets.QHBoxLayout(nav_container)
        nav_layout.setSpacing(8)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        # Navigation buttons
        self._back_button = QtWidgets.QPushButton("←")
        self._back_button.setObjectName("backButton")
        self._back_button.setFixedSize(32, 28)
        self._back_button.setStyleSheet("""
            QPushButton#backButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                color: #a0aec0;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#backButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        self._forward_button = QtWidgets.QPushButton("→")
        self._forward_button.setObjectName("forwardButton")
        self._forward_button.setFixedSize(32, 28)
        self._forward_button.setStyleSheet("""
            QPushButton#forwardButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                color: #a0aec0;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#forwardButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        self._reload_button = QtWidgets.QPushButton("🔄")
        self._reload_button.setObjectName("reloadButton")
        self._reload_button.setFixedSize(32, 28)
        self._reload_button.setStyleSheet("""
            QPushButton#reloadButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                color: #a0aec0;
                font-size: 12px;
            }
            QPushButton#reloadButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        # URL display
        self._url_label = QtWidgets.QLabel("Caricamento...")
        self._url_label.setObjectName("urlLabel")
        self._url_label.setStyleSheet("""
            QLabel#urlLabel {
                color: #a0aec0;
                font-size: 11px;
                padding: 6px 10px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        # Toggle sidebar button
        self._toggle_sidebar_button = QtWidgets.QPushButton("◀")
        self._toggle_sidebar_button.setObjectName("toggleSidebarButton")
        self._toggle_sidebar_button.setFixedSize(32, 28)
        self._toggle_sidebar_button.setStyleSheet("""
            QPushButton#toggleSidebarButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                color: #a0aec0;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#toggleSidebarButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        nav_layout.addWidget(self._back_button)
        nav_layout.addWidget(self._forward_button)
        nav_layout.addWidget(self._reload_button)
        nav_layout.addWidget(self._url_label, 1)
        nav_layout.addWidget(self._toggle_sidebar_button)
        
        # Web view
        self._web_view = QWebEngineView()
        self._web_view.setObjectName("webView")
        self._web_view.setStyleSheet("""
            QWebEngineView {
                background: white;
                border-radius: 6px;
            }
        """)
        
        web_layout.addWidget(nav_container)
        web_layout.addWidget(self._web_view, 1)
        parent_layout.addWidget(web_container, 1)

    def _create_bottom_status_area(self, parent_layout):
        """Create the bottom status area with progress bar and log."""
        bottom_container = QtWidgets.QFrame()
        bottom_container.setObjectName("bottomContainer")
        bottom_container.setStyleSheet("""
            QFrame#bottomContainer {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        bottom_layout = QtWidgets.QVBoxLayout(bottom_container)
        bottom_layout.setSpacing(8)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress section (initially hidden)
        self._progress_container = QtWidgets.QFrame()
        self._progress_container.setObjectName("progressContainer")
        self._progress_container.setStyleSheet("""
            QFrame#progressContainer {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self._progress_container.hide()  # Initially hidden
        
        progress_layout = QtWidgets.QVBoxLayout(self._progress_container)
        progress_layout.setSpacing(6)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress title
        progress_title = QtWidgets.QLabel("📊 Progresso")
        progress_title.setObjectName("progressTitle")
        progress_title.setStyleSheet("""
            QLabel#progressTitle {
                color: #ffffff;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
        """)
        
        # Status label
        self._status_label = QtWidgets.QLabel("Pronto per l'elaborazione")
        self._status_label.setObjectName("statusLabel")
        self._status_label.setStyleSheet("""
            QLabel#statusLabel {
                color: #cbd5e0;
                font-size: 9px;
                padding: 4px 6px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 3px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                font-weight: 500;
            }
        """)
        
        # Progress bar
        self._progress_bar = CustomProgressBar()
        self._progress_bar.setObjectName("progressBar")
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                background: rgba(0, 0, 0, 0.3);
                text-align: center;
                color: white;
                font-size: 9px;
                font-weight: bold;
                height: 14px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #48bb78, stop:0.5 #38a169, stop:1 #2f855a);
                border-radius: 2px;
                margin: 1px;
            }
        """)
        
        progress_layout.addWidget(progress_title)
        progress_layout.addWidget(self._status_label)
        progress_layout.addWidget(self._progress_bar)
        
        # Log area
        self._log_text = QtWidgets.QTextEdit()
        self._log_text.setObjectName("logText")
        self._log_text.setMaximumHeight(80)
        self._log_text.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                color: #a0aec0;
                font-size: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                padding: 8px;
            }
        """)
        self._log_text.setReadOnly(True)
        
        bottom_layout.addWidget(self._progress_container)
        bottom_layout.addWidget(self._log_text)
        parent_layout.addWidget(bottom_container)
    
    def _create_modern_badges(self, parent_layout):
        """Create modern badge widgets with improved responsive layout."""
        # Create a container frame for better organization
        badges_container = QtWidgets.QFrame()
        badges_container.setObjectName("badgesContainer")
        badges_container.setStyleSheet("""
            QFrame#badgesContainer {
                background: transparent;
                border: none;
            }
        """)
        
        # Use QGridLayout for uniform distribution
        badges_layout = QtWidgets.QGridLayout(badges_container)
        badges_layout.setSpacing(4)  # Uniform spacing
        badges_layout.setContentsMargins(0, 0, 0, 0)
        
        badge_configs = [
            ("🟡", "Annullate", COLOR_ANNULATA, "Richieste annullate"),
            ("🟢", "Aperte", COLOR_APERTA, "Richieste aperte"),
            ("✅", "Chiuse", COLOR_CHIUSA, "Richieste chiuse"),
            ("🟠", "Lavorazione", COLOR_LAVORAZIONE, "Richieste in lavorazione"),
            ("📤", "Inviate", COLOR_INVIATA, "Richieste inviate"),
            ("❗", "Eccezioni", COLOR_ECCEZIONI, "Errori ed eccezioni")
        ]
        
        # Create badges in a 2x3 grid layout
        for i, (icon, label, color, tooltip) in enumerate(badge_configs):
            badge = self._create_modern_badge(icon, label, color, tooltip)
            self._badge_widgets[f"{icon} {label}"] = badge
            
            # Arrange in 2 columns, 3 rows
            row = i // 2
            col = i % 2
            badges_layout.addWidget(badge, row, col)
        
        parent_layout.addWidget(badges_container)

    def _create_modern_badge(self, icon: str, label: str, color: str, tooltip: str) -> QtWidgets.QFrame:
        """Create a simplified badge widget with just number and text."""
        badge_frame = QtWidgets.QFrame()
        badge_frame.setObjectName(f"badge_{label.lower()}")
        badge_frame.setToolTip(tooltip)
        badge_frame.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        
        # Set fixed size for uniform appearance
        badge_frame.setFixedHeight(32)
        badge_frame.setMinimumWidth(120)
        
        # Simple glassmorphism style without borders
        badge_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.08),
                    stop:1 rgba(255, 255, 255, 0.03));
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                margin: 1px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.12),
                    stop:1 rgba(255, 255, 255, 0.06));
            }}
        """)
        
        badge_layout = QtWidgets.QHBoxLayout(badge_frame)
        badge_layout.setSpacing(8)
        badge_layout.setContentsMargins(6, 4, 6, 4)
        
        # Count label (colored)
        count_label = QtWidgets.QLabel("0")
        count_label.setObjectName("countLabel")
        count_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        count_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 14px;
            color: {color};
            margin: 0;
            padding: 0;
            min-width: 20px;
        """)
        
        # Label text
        label_widget = QtWidgets.QLabel(label)
        label_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        label_widget.setStyleSheet("""
            color: #a0aec0;
            font-size: 10px;
            font-weight: 500;
            margin: 0;
            padding: 0;
        """)
        
        badge_layout.addWidget(count_label)
        badge_layout.addWidget(label_widget)
        badge_layout.addStretch()
        
        return badge_frame

    def _setup_styles(self):
        """Setup global styles for the application."""
        # Global styles can be added here if needed
        pass

    def _connect_signals(self):
        """Connect all UI signals."""
        # File selection
        self._file_button.clicked.connect(self._on_select_file_clicked)
        
        # Control buttons
        self._start_button.clicked.connect(self.startButtonClicked.emit)
        self._stop_button.clicked.connect(self.stopButtonClicked.emit)
        
        # Utility button (only clear log)
        self._clear_button.clicked.connect(self.clearLogClicked.emit)
        
        # Navigation buttons
        self._back_button.clicked.connect(lambda: self._web_view.back())
        self._forward_button.clicked.connect(lambda: self._web_view.forward())
        self._reload_button.clicked.connect(lambda: self._web_view.reload())
        self._toggle_sidebar_button.clicked.connect(self.toggle_sidebar)

    def _on_select_file_clicked(self):
        """Handle file selection button click."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self._parent,
            "Seleziona File Excel",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            self.set_file_path(file_path)
            self.fileSelected.emit(file_path)

    def set_file_path(self, file_path: str):
        """Update the file path display."""
        if file_path:
            filename = os.path.basename(file_path)
            self._file_status.setText(f"📄 {filename}")
            self._file_status.setStyleSheet("""
                QLabel#fileStatus {
                    color: #48bb78;
                    font-size: 10px;
                    padding: 6px 10px;
                    background: rgba(72, 187, 120, 0.1);
                    border-radius: 4px;
                    border: 1px solid rgba(72, 187, 120, 0.3);
                }
            """)
        else:
            self._file_status.setText("Nessun file selezionato")
            self._file_status.setStyleSheet("""
                QLabel#fileStatus {
                    color: #a0aec0;
                    font-size: 10px;
                    padding: 6px 10px;
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 4px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
            """)

    def update_progress(self, current: int, maximum: int):
        """Update the progress bar."""
        self._progress_bar.setMaximum(maximum)
        self._progress_bar.setValue(current)
        
        # Show progress container when processing starts
        if current > 0 and self._progress_container.isHidden():
            self._progress_container.show()
        elif current == 0 and maximum == 0 and not self._progress_container.isHidden():
            self._progress_container.hide()

    def update_status(self, message: str):
        """Update the status message."""
        self._status_label.setText(message)

    def add_log_message(self, message: str):
        """Add a message to the log area."""
        timestamp = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss")
        formatted_message = f"[{timestamp}] ✅ {message}"
        
        # Add to log text area
        self._log_text.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self._log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """Clear the log area."""
        self._log_text.clear()

    def update_badge(self, badge_prefix: str, count: int):
        """Update a specific badge with new count."""
        badge_key = None
        for key in self._badge_widgets.keys():
            if badge_prefix.lower() in key.lower():
                badge_key = key
                break
        
        if badge_key and badge_key in self._badge_widgets:
            badge = self._badge_widgets[badge_key]
            count_label = badge.findChild(QtWidgets.QLabel, "countLabel")
            if count_label:
                count_label.setText(str(count))
                self._animate_badge(badge)

    def _animate_badge(self, badge: QtWidgets.QFrame):
        """Animate badge update with smooth and modern effects."""
        count_label = badge.findChild(QtWidgets.QLabel, "countLabel")
        if not count_label:
            return

        original_style = badge.styleSheet()
        animation_styles = [
            original_style.replace("border: 1px solid", "border: 2px solid"),
            original_style
        ]

        for i, style in enumerate(animation_styles):
            delay = i * 200
            QtCore.QTimer.singleShot(delay, lambda s=style: badge.setStyleSheet(s))

        if count_label:
            original_text = count_label.text()
            original_color = count_label.styleSheet()
            try:
                count_value = int(original_text)
                flash_color = original_color.replace("color:", "color: #ffffff;")
                count_label.setStyleSheet(flash_color)
                QtCore.QTimer.singleShot(300, lambda: count_label.setStyleSheet(original_color))
            except ValueError:
                pass

    def reset_badges(self):
        """Reset all badges to zero."""
        for badge in self._badge_widgets.values():
            count_label = badge.findChild(QtWidgets.QLabel, "countLabel")
            if count_label:
                count_label.setText("0")

    def _update_ui_state(self, is_processing: bool):
        """Update UI state based on processing status."""
        self._start_button.setEnabled(not is_processing)
        self._stop_button.setEnabled(is_processing)
        self._file_button.setEnabled(not is_processing)

    def set_processing_state(self, is_processing: bool):
        """Set the processing state and update UI accordingly."""
        self._update_ui_state(is_processing)
        
        if is_processing:
            self._start_button.setStyleSheet("""
                QPushButton#startButton {
                    background: #4a5568;
                    color: #a0aec0;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                    font-size: 11px;
                    min-height: 32px;
                }
            """)
        else:
            self._start_button.setStyleSheet("""
                QPushButton#startButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #48bb78, stop:0.5 #38a169, stop:1 #2f855a);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                    font-size: 11px;
                    min-height: 32px;
                }
                QPushButton#startButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #38a169, stop:0.5 #2f855a, stop:1 #276749);
                }
            """)

    def set_web_view(self, web_view: QtWidgets.QWidget):
        """Set the web view widget."""
        if hasattr(self, '_web_view') and self._web_view:
            # Remove existing web view
            self._web_view.setParent(None)
        
        # Replace with new web view
        self._web_view = web_view
        if self._web_view:
            # Find the web container and add the new web view
            web_container = self._parent.findChild(QtWidgets.QFrame, "webContainer")
            if web_container:
                web_layout = web_container.layout()
                if web_layout:
                    # Remove the placeholder and add the real web view
                    for i in range(web_layout.count()):
                        item = web_layout.itemAt(i)
                        if item.widget() and item.widget().objectName() == "webView":
                            web_layout.removeWidget(item.widget())
                            item.widget().setParent(None)
                            break
                    
                    # Add the new web view
                    web_layout.addWidget(self._web_view, 1)  # Give it stretch priority

    @property
    def web_view_placeholder(self) -> QtWidgets.QWidget:
        """Get the web view placeholder widget."""
        return self._web_view

    def handle_window_resize(self, width: int, height: int):
        """Handle window resize events for responsive design."""
        # Adjust left panel width based on window size
        left_panel = self._parent.findChild(QtWidgets.QFrame, "leftPanel")
        if left_panel:
            if width < 1000:
                left_panel.setMaximumWidth(280)
                left_panel.setMinimumWidth(250)
            elif width < 1400:
                left_panel.setMaximumWidth(320)
                left_panel.setMinimumWidth(280)
            else:
                left_panel.setMaximumWidth(350)
                left_panel.setMinimumWidth(300)
        
        # Optimize badge layout
        self._optimize_badge_layout(width)

    def _optimize_badge_layout(self, window_width: int):
        """Optimize badge layout based on window width."""
        badges_container = self._parent.findChild(QtWidgets.QFrame, "badgesContainer")
        if not badges_container:
            return
            
        layout = badges_container.layout()
        if not layout:
            return
            
        # Adjust spacing and margins based on window width
        if window_width < 800:
            spacing = 2
            margin = 2
        elif window_width < 1200:
            spacing = 3
            margin = 3
        else:
            spacing = 4
            margin = 4
            
        layout.setSpacing(spacing)
        layout.setContentsMargins(margin, margin, margin, margin)

    def update_layout_on_resize(self):
        """Update layout when parent widget is resized."""
        if hasattr(self._parent, 'width') and hasattr(self._parent, 'height'):
            self.handle_window_resize(self._parent.width(), self._parent.height())

    def reset_splitter_to_default(self):
        """Reset the layout to default proportions."""
        # This method is kept for compatibility but may not be needed with the new layout
        pass

    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        left_panel = self._parent.findChild(QtWidgets.QFrame, "leftPanel")
        if left_panel:
            if left_panel.isVisible():
                left_panel.hide()
                self._toggle_sidebar_button.setText("▶")
                self._toggle_sidebar_button.setToolTip("Mostra pannello di controllo")
            else:
                left_panel.show()
                self._toggle_sidebar_button.setText("◀")
                self._toggle_sidebar_button.setToolTip("Nascondi pannello di controllo")

    def _handle_resize_event(self, event):
        """Handle resize events for responsive design."""
        self.update_layout_on_resize()
        if hasattr(event, 'accept'):
            event.accept() 