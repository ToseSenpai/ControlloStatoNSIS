# main_window/ui_manager.py
# UI Manager module for NSIS application - FINAL POLISHED DESIGN

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWebEngineWidgets import QWebEngineView
import qtawesome as qta
import os
from typing import Dict, Any, Optional, Callable
import logging

# Import UI components
from .excel_handler import ExcelHandler
from .state_manager import StateManager
from .web_automation import WebAutomation
from .worker import Worker

# Glassmorphism Design Color Palette (Light Theme)
COLORS = {
    'bg_primary': '#ffffff',      # Pure white background
    'bg_secondary': '#f8f9fa',    # Light gray background
    'bg_tertiary': '#e9ecef',     # Lighter gray background
    'text_primary': '#212529',    # Dark text for high contrast
    'text_secondary': '#6c757d',  # Medium gray text
    'text_muted': '#adb5bd',      # Light gray text
    'accent_primary': '#007BFF',  # Vibrant blue
    'accent_primary_alt': '#0056b3', # Darker blue
    'accent_secondary': '#28a745', # Vibrant green
    'accent_secondary_alt': '#1e7e34', # Darker green
    'accent_error': '#dc3545',    # Vibrant red
    'accent_error_alt': '#c82333', # Darker red
    'accent_warning': '#ffc107',  # Vibrant yellow
    'accent_warning_alt': '#e0a800', # Darker yellow
    'accent_info': '#17a2b8',     # Vibrant cyan
    'accent_info_alt': '#138496', # Darker cyan
    'border': 'rgba(255, 255, 255, 0.25)', # Glass border
    'border_light': 'rgba(255, 255, 255, 0.15)', # Light glass border
    'shadow': 'rgba(0, 0, 0, 0.1)', # Subtle shadow
    'signature': '#6c757d',       # Signature text color
    'glass_white': 'rgba(255, 255, 255, 0.15)', # Glass white overlay
    'glass_highlight': 'rgba(255, 255, 255, 0.25)', # Glass highlight
    'title_accent': '#0078d4',    # Windows 11 blue accent for titles
    'title_accent_light': '#106ebe',  # Lighter Windows 11 blue for gradients
}

# Icon mapping with QtAwesome professional icons - Enhanced
ICONS = {
    'play': 'fa5s.rocket',           # Rocket for start
    'stop': 'fa5s.power-off',        # Power off for stop
    'trash': 'fa5s.trash-alt',
    'home': 'fa5s.home',
    'folder': 'fa5s.folder-open',    # Open folder for file selection
    'check': 'fa5s.check-square',
    'settings': 'fa5s.cog',
    'send': 'fa5s.paper-plane',
    'alert': 'fa5s.exclamation-triangle',
    'arrow_left': 'fa5s.arrow-left',
    'arrow_right': 'fa5s.arrow-right',
    'rotate': 'fa5s.redo',
    'file': 'fa5s.file-excel',       # Excel file icon
}

# Custom UI Components
class GlassPanel(QtWidgets.QFrame):
    """Glassmorphism panel with transparency and rounded corners."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassPanel")
        self.setStyleSheet(f"""
            QFrame#glassPanel {{
                background-color: {COLORS['glass_white']};
                border-radius: 15px;
                border: 1px solid {COLORS['border']};
            }}
        """)

class ModernProgressBar(QtWidgets.QProgressBar):
    """Modern liquid glass progress bar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QProgressBar {{
                background: {COLORS['glass_white']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                text-align: center;
                color: {COLORS['text_primary']};
                font-size: 12px;
                font-weight: 600;
                height: 24px;
                margin: 4px 0;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['accent_secondary']},
                    stop:1 {COLORS['accent_secondary_alt']});
                border-radius: 11px;
                margin: 1px;
            }}
        """)

class CompactStatisticItem(QtWidgets.QWidget):
    """Compact horizontal statistic item with QtAwesome icons."""
    def __init__(self, icon_name: str, label: str, color: str, tooltip: str = "", parent=None):
        super().__init__(parent)
        self._count = 0
        self._icon_name = icon_name
        self._label = label
        self._color = color
        self._tooltip = tooltip
        
        self.setObjectName("compactStatisticItem")
        self.setToolTip(tooltip)
        self.setFixedHeight(32)
        
        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon label with QtAwesome
        self._icon_label = QtWidgets.QLabel()
        self._icon_label.setFixedSize(16, 16)
        self._icon_label.setStyleSheet(f"""
            background: transparent;
            border: none;
        """)
        self._load_qtawesome_icon(icon_name, color)
        
        self._name_label = QtWidgets.QLabel(label)
        self._name_label.setStyleSheet(f"""
            background: transparent;
            color: {COLORS['text_primary']};
            font-size: 12px;
            font-weight: 500;
            border: none;
        """)
        
        # Spacer
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        spacer.setStyleSheet("background: transparent; border: none;")
        
        # Count label
        self._count_label = QtWidgets.QLabel("0")
        self._count_label.setObjectName("countLabel")
        self._count_label.setStyleSheet(f"""
            QLabel#countLabel {{
                background: transparent;
                color: {color};
                font-size: 12px;
                font-weight: 700;
                min-width: 20px;
                text-align: right;
                border: none;
            }}
        """)
        
        layout.addWidget(self._icon_label)
        layout.addWidget(self._name_label)
        layout.addWidget(spacer)
        layout.addWidget(self._count_label)
        
        # Hover effect
        self.setStyleSheet(f"""
            QWidget#compactStatisticItem {{
                background: transparent;
                border-radius: 6px;
                margin: 1px 0;
                padding: 2px;
            }}
            QWidget#compactStatisticItem:hover {{
                background: transparent;
                border: none;
            }}
        """)
    
    def _load_qtawesome_icon(self, icon_name: str, color: str):
        """Load QtAwesome icon with custom color."""
        try:
            icon = qta.icon(icon_name, color=color)
            self._icon_label.setPixmap(icon.pixmap(16, 16))
        except Exception as e:
            # Fallback to text icon
            self._icon_label.setText("•")
            self._icon_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
    
    def set_count(self, count: int):
        """Update the count with animation."""
        if self._count != count:
            self._count = count
            self._count_label.setText(str(count))
            self._animate_update()
    
    def _animate_update(self):
        """Simple animation for count updates."""
        # Flash effect
        original_style = self._count_label.styleSheet()
        flash_style = original_style.replace("font-weight: 700", "font-weight: 900")
        self._count_label.setStyleSheet(flash_style)
        
        # Reset after 200ms
        QtCore.QTimer.singleShot(200, lambda: self._count_label.setStyleSheet(original_style))

class SectionTitle(QtWidgets.QLabel):
    """Unified section title with consistent styling and proper spacing."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("sectionTitle")
        self.setStyleSheet(f"""
            QLabel#sectionTitle {{
                background: transparent;
                color: {COLORS['title_accent']};
                font-size: 14px;
                font-weight: 700;
                margin: 24px 0 12px 0;
                padding: 0 0 4px 0;
                letter-spacing: 0.3px;
                border: none;
            }}
        """)
    


class ModernButton(QtWidgets.QPushButton):
    """Modern liquid glass button with QtAwesome icons and glassmorphism effect."""
    def __init__(self, text: str, button_type: str = "primary", icon_name: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName(f"modernButton_{button_type}")
        
        # Set icon if provided
        if icon_name:
            self._load_qtawesome_icon(icon_name, button_type)
        
        # Define liquid glass button styles based on type
        styles = {
            "primary": f"""
                QPushButton#modernButton_primary {{
                    background: {COLORS['accent_primary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 8px 16px;
                    min-height: 32px;
                }}
                QPushButton#modernButton_primary:hover {{
                    background: {COLORS['accent_primary_alt']};
                    border-radius: 8px;
                }}
                QPushButton#modernButton_primary:pressed {{
                    background: {COLORS['accent_primary']};
                    border-radius: 8px;
                }}
                QPushButton#modernButton_primary:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                }}
            """,
            "success": f"""
                QPushButton#modernButton_success {{
                    background: {COLORS['accent_secondary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 8px 16px;
                    min-height: 32px;
                }}
                QPushButton#modernButton_success:hover {{
                    background: {COLORS['accent_secondary_alt']};
                    border-radius: 8px;
                }}
                QPushButton#modernButton_success:pressed {{
                    background: {COLORS['accent_secondary']};
                    border-radius: 8px;
                }}
                QPushButton#modernButton_success:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                }}
            """,
            "danger": f"""
                QPushButton#modernButton_danger {{
                    background: {COLORS['accent_error']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 8px 16px;
                    min-height: 32px;
                }}
                QPushButton#modernButton_danger:hover {{
                    background: {COLORS['accent_error_alt']};
                    border-radius: 8px;
                }}
                QPushButton#modernButton_danger:pressed {{
                    background: {COLORS['accent_error']};
                    border-radius: 8px;
                }}
                QPushButton#modernButton_danger:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                }}
            """,
            "secondary": f"""
                QPushButton#modernButton_secondary {{
                    background: {COLORS['glass_white']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 6px 12px;
                    min-height: 28px;
                }}
                QPushButton#modernButton_secondary:hover {{
                    background: {COLORS['glass_highlight']};
                    border: 1px solid {COLORS['border_light']};
                    border-radius: 8px;
                }}
                QPushButton#modernButton_secondary:pressed {{
                    background: {COLORS['glass_white']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                }}
                QPushButton#modernButton_secondary:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                }}
            """
        }
        
        self.setStyleSheet(styles.get(button_type, styles["secondary"]))
        
        # Force hover effects by overriding styles after a short delay
        QtCore.QTimer.singleShot(100, self._force_hover_styles)
    
    def _force_hover_styles(self):
        """Force hover styles to ensure they work."""
        current_style = self.styleSheet()
        if "secondary" in self.objectName():
            hover_style = current_style.replace(
                "QPushButton#modernButton_secondary:hover {",
                "QPushButton#modernButton_secondary:hover {\n    background: rgba(255, 255, 255, 0.4) !important;\n    border: 1px solid rgba(255, 255, 255, 0.6) !important;\n    color: #212529 !important;"
            )
            self.setStyleSheet(hover_style)
    
    def _load_qtawesome_icon(self, icon_name: str, button_type: str):
        """Load QtAwesome icon for button."""
        try:
            # Choose color based on button type
            if button_type in ["primary", "success", "danger"]:
                icon_color = COLORS['bg_primary']  # White for filled buttons
            else:
                icon_color = COLORS['text_secondary']  # Gray for outline buttons
            
            icon = qta.icon(icon_name, color=icon_color)
            self.setIcon(icon)
        except Exception as e:
            pass  # Fallback to text only

class WebNavButton(QtWidgets.QPushButton):
    """Specialized navigation button for web controls with QtAwesome icons."""
    def __init__(self, icon_name: str, parent=None):
        super().__init__(parent)
        self.setObjectName("webNavButton")
        self.setFixedSize(40, 36)
        
        # Load QtAwesome icon
        self._load_qtawesome_icon(icon_name)
        
        self.setStyleSheet(f"""
            QPushButton#webNavButton {{
                background: transparent;
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 6px;
            }}
            QPushButton#webNavButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 6px;
            }}
            QPushButton#webNavButton:pressed {{
                background: rgba(255, 255, 255, 0.2);
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
            }}
        """)
    
    def _load_qtawesome_icon(self, icon_name: str):
        """Load QtAwesome icon for navigation button."""
        try:
            icon = qta.icon(icon_name, color=COLORS['text_primary'])
            self.setIcon(icon)
        except Exception as e:
            pass  # Fallback to text only

class SignatureLabel(QtWidgets.QLabel):
    """Discrete signature label for the application."""
    def __init__(self, parent=None):
        super().__init__("Made with ❤️ by ST", parent)
        self.setObjectName("signatureLabel")
        self.setStyleSheet(f"""
            QLabel#signatureLabel {{
                color: {COLORS['signature']};
                font-size: 8px;
                font-weight: 400;
                padding: 4px 8px;
                background: transparent;
                border: none;
            }}
        """)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop)

class SpinnerWidget(QtWidgets.QWidget):
    """Custom spinner widget for loading states."""
    def __init__(self, parent=None): 
        super().__init__(parent)
        self.hide()
    def startAnimation(self): self.show()
    def stopAnimation(self): self.hide()
    def setColor(self, color): pass

class RoundedWebContainer(QtWidgets.QWidget):
    """Container widget that forces rounded corners on QWebEngineView using aggressive masking."""
    
    def __init__(self, web_view: QtWidgets.QWidget, radius: int = 12, parent=None):
        super().__init__(parent)
        self._web_view = web_view
        self._radius = radius
        
        # Setup layout with padding for shadow
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)  # Padding for shadow effect
        layout.addWidget(web_view)
        
        # Apply aggressive styling with pronounced border (removed clip-path)
        self.setStyleSheet(f"""
            QWidget {{
                background: rgba(255, 255, 255, 0.4);
                border: 3px solid rgba(255, 255, 255, 0.8);
                border-radius: {radius}px;
            }}
        """)
        
        # Apply rounded corner mask immediately
        self._apply_rounded_mask()
        
        # Force mask update after widget is shown
        QtCore.QTimer.singleShot(100, self._apply_rounded_mask)
    
    def _apply_rounded_mask(self):
        """Apply rounded corner mask to the container with aggressive approach."""
        try:
            # Create a rounded rectangle path with larger radius to hide sharp corners
            path = QtGui.QPainterPath()
            rect = self.rect()
            rect_f = QtCore.QRectF(rect)
            
            # Use a slightly larger radius to ensure sharp corners are completely hidden
            effective_radius = self._radius + 2
            path.addRoundedRect(rect_f, effective_radius, effective_radius)
            
            # Create and apply the mask
            mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
            self.setMask(mask)
            
            # Also apply mask to the web view itself with even more aggressive masking
            if hasattr(self._web_view, 'setMask'):
                # Create a slightly smaller mask for the web view to ensure it's fully contained
                web_rect = self._web_view.rect()
                web_rect_f = QtCore.QRectF(web_rect)
                web_path = QtGui.QPainterPath()
                web_path.addRoundedRect(web_rect_f, effective_radius - 1, effective_radius - 1)
                web_mask = QtGui.QRegion(web_path.toFillPolygon().toPolygon())
                self._web_view.setMask(web_mask)
                
        except Exception as e:
            print(f"Mask application error: {e}")
    
    def resizeEvent(self, event):
        """Override resize event to update mask."""
        super().resizeEvent(event)
        QtCore.QTimer.singleShot(10, self._apply_rounded_mask)
    
    def showEvent(self, event):
        """Override show event to ensure mask is applied."""
        super().showEvent(event)
        QtCore.QTimer.singleShot(50, self._apply_rounded_mask)
    
    def paintEvent(self, event):
        """Custom paint event to add elegant shadow effect."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # Create shadow effect
        shadow_color = QtGui.QColor(0, 0, 0, 50)
        shadow_offset = 4
        
        # Draw shadow
        shadow_rect = self.rect().adjusted(shadow_offset, shadow_offset, shadow_offset, shadow_offset)
        shadow_path = QtGui.QPainterPath()
        shadow_path.addRoundedRect(QtCore.QRectF(shadow_rect), self._radius, self._radius)
        painter.fillPath(shadow_path, shadow_color)
        
        # Draw main container
        main_rect = self.rect()
        main_path = QtGui.QPainterPath()
        main_path.addRoundedRect(QtCore.QRectF(main_rect), self._radius, self._radius)
        
        # Create gradient background
        gradient = QtGui.QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QtGui.QColor(255, 255, 255, 50))
        gradient.setColorAt(1, QtGui.QColor(255, 255, 255, 30))
        
        painter.fillPath(main_path, gradient)
        
        # Draw border with more pronounced effect
        border_pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 100), 2.5)
        painter.setPen(border_pen)
        painter.drawPath(main_path)
        
        # Draw additional inner border for extra definition
        inner_rect = self.rect().adjusted(2, 2, -2, -2)
        inner_path = QtGui.QPainterPath()
        inner_path.addRoundedRect(QtCore.QRectF(inner_rect), self._radius - 2, self._radius - 2)
        inner_border_pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 60), 1)
        painter.setPen(inner_border_pen)
        painter.drawPath(inner_path)

class UIManager(QtCore.QObject):
    """Manages UI components with final polished design."""
    
    # Signals
    startButtonClicked = QtCore.pyqtSignal()
    stopButtonClicked = QtCore.pyqtSignal()
    clearLogClicked = QtCore.pyqtSignal()
    openNsisClicked = QtCore.pyqtSignal()
    resetLayoutClicked = QtCore.pyqtSignal()
    fileSelected = QtCore.pyqtSignal(str)  # file_path
    webBackClicked = QtCore.pyqtSignal()
    webForwardClicked = QtCore.pyqtSignal()
    webReloadClicked = QtCore.pyqtSignal()
    
    def __init__(self, parent_widget: QtWidgets.QWidget):
        super().__init__()
        self._parent = parent_widget
        self._logger = logging.getLogger(__name__)
        
        # UI Components
        self._main_layout: Optional[QtWidgets.QVBoxLayout] = None
        self._splitter: Optional[QtWidgets.QSplitter] = None
        self._left_panel: Optional[QtWidgets.QWidget] = None
        self._right_panel: Optional[QtWidgets.QWidget] = None
        self._signature_label: Optional[SignatureLabel] = None
        
        # Widgets

        self._select_file_button: Optional[ModernButton] = None
        self._start_button: Optional[ModernButton] = None
        self._stop_button: Optional[ModernButton] = None
        self._clear_log_button: Optional[ModernButton] = None
        self._open_nsis_button: Optional[ModernButton] = None
        self._progress_bar: Optional[ModernProgressBar] = None
        self._status_label: Optional[QtWidgets.QLabel] = None
        self._log_text: Optional[QtWidgets.QTextEdit] = None
        self._web_view: Optional[QtWidgets.QWidget] = None
        
        # Statistic widgets - using new CompactStatisticItem
        self._statistic_widgets: Dict[str, CompactStatisticItem] = {}
        
        # Setup UI
        self._setup_ui()
        self._setup_global_styles()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the complete UI with final polished design."""
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self._parent)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add signature label to bottom-right corner
        self._signature_label = SignatureLabel(self._parent)
        self._signature_label.setGeometry(self._parent.width() - 120, self._parent.height() - 30, 110, 20)
        
        # Create splitter for better space distribution
        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self._splitter.setChildrenCollapsible(False)
        self._splitter.setHandleWidth(1)
        self._splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {COLORS['border']};
                border: none;
            }}
            QSplitter::handle:hover {{
                background: {COLORS['border_light']};
            }}
        """)
        
        # Create left and right panels
        self._create_left_panel()
        self._create_right_panel()
        
        # Add panels to splitter
        self._splitter.addWidget(self._left_panel)
        self._splitter.addWidget(self._right_panel)
        
        # Set initial splitter sizes (20% left, 80% right)
        self._splitter.setSizes([240, 760])
        
        # Add splitter to main layout
        main_layout.addWidget(self._splitter)
        
        # Initialize responsive behavior
        self._parent.resizeEvent = self._handle_resize_event

    def _create_left_panel(self):
        """Create the optimized left panel with glassmorphism design."""
        self._left_panel = GlassPanel()
        self._left_panel.setObjectName("leftPanel")
        self._left_panel.setMinimumWidth(220)
        self._left_panel.setMaximumWidth(280)
        
        left_layout = QtWidgets.QVBoxLayout(self._left_panel)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(16, 12, 16, 12)
        
        # File selection section
        self._create_file_section(left_layout)
        
        # Controls section (no separator line)
        self._create_controls_section(left_layout)
        
        # Statistics section (no separator line)
        self._create_statistics_section(left_layout)
        
        # Add stretch to push everything to the top
        left_layout.addStretch()

    def _create_file_section(self, parent_layout):
        """Create file selection section with elegant design."""
        # File selection title
        file_title = SectionTitle("📁 Selezione File")
        parent_layout.addWidget(file_title)
        
        # Create a container for the file selection area
        self._file_selection_container = QtWidgets.QFrame()
        self._file_selection_container.setObjectName("fileSelectionContainer")
        self._file_selection_container.setStyleSheet(f"""
            QFrame#fileSelectionContainer {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 16px;
                margin: 8px 0;
            }}
        """)
        
        # Container layout
        container_layout = QtWidgets.QVBoxLayout(self._file_selection_container)
        container_layout.setSpacing(12)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # File selection button
        self._select_file_button = ModernButton("Seleziona File Excel", "primary", ICONS['file'])
        
        # File display area (initially hidden)
        self._file_display_area = QtWidgets.QFrame()
        self._file_display_area.setObjectName("fileDisplayArea")
        self._file_display_area.setStyleSheet(f"""
            QFrame#fileDisplayArea {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        self._file_display_area.hide()  # Initially hidden
        
        # File display layout
        file_display_layout = QtWidgets.QHBoxLayout(self._file_display_area)
        file_display_layout.setContentsMargins(8, 8, 8, 8)
        file_display_layout.setSpacing(8)
        
        # File icon
        self._file_icon_label = QtWidgets.QLabel("📄")
        self._file_icon_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent_secondary']};
                font-size: 16px;
                background: transparent;
                border: none;
            }}
        """)
        
        # File name label
        self._file_name_label = QtWidgets.QLabel("Nessun file selezionato")
        self._file_name_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        """)
        
        # Success indicator (initially hidden)
        self._success_indicator = QtWidgets.QLabel("✅ File caricato con successo!")
        self._success_indicator.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent_secondary']};
                font-size: 10px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        self._success_indicator.hide()
        
        # Add widgets to file display layout
        file_display_layout.addWidget(self._file_icon_label)
        file_display_layout.addWidget(self._file_name_label)
        file_display_layout.addStretch()
        file_display_layout.addWidget(self._success_indicator)
        
        # Add widgets to container
        container_layout.addWidget(self._select_file_button)
        container_layout.addWidget(self._file_display_area)
        
        parent_layout.addWidget(self._file_selection_container)

    def _create_controls_section(self, parent_layout):
        """Create controls section with QtAwesome icons and improved spacing."""
        # Controls title
        controls_title = SectionTitle("🎮 Controlli")
        parent_layout.addWidget(controls_title)
        
        # Main action buttons (primary) with increased spacing
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(12)  # Increased spacing between buttons
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Start button with QtAwesome icon
        self._start_button = ModernButton("Avvia", "success", ICONS['play'])
        
        # Stop button with QtAwesome icon
        self._stop_button = ModernButton("Stop", "danger", ICONS['stop'])
        
        button_layout.addWidget(self._start_button)
        button_layout.addWidget(self._stop_button)
        
        # Secondary buttons (outline style) with increased spacing
        secondary_layout = QtWidgets.QHBoxLayout()
        secondary_layout.setSpacing(8)  # Increased spacing between buttons
        secondary_layout.setContentsMargins(0, 0, 0, 0)
        
        # Clear log button with QtAwesome icon
        self._clear_log_button = ModernButton("Pulisci", "secondary", ICONS['trash'])
        
        # Open NSIS button with QtAwesome icon
        self._open_nsis_button = ModernButton("NSIS", "secondary", ICONS['home'])
        
        secondary_layout.addWidget(self._clear_log_button)
        secondary_layout.addWidget(self._open_nsis_button)
        secondary_layout.addStretch()
        
        # Add spacing between primary and secondary button rows
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(8)
        spacer.setStyleSheet("background: transparent; border: none;")
        
        parent_layout.addLayout(button_layout)
        parent_layout.addWidget(spacer)
        parent_layout.addLayout(secondary_layout)

    def _create_statistics_section(self, parent_layout):
        """Create statistics section with QtAwesome icons."""
        # Statistics title
        stats_title = SectionTitle("📊 Statistiche")
        parent_layout.addWidget(stats_title)
        
        # Create compact statistics in a vertical list
        stats_layout = QtWidgets.QVBoxLayout()
        stats_layout.setSpacing(4)  # Increased spacing between items
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create statistics with QtAwesome icons
        statistic_configs = [
            (ICONS['alert'], "Annullate", COLORS['accent_warning'], "Richieste annullate"),
            (ICONS['folder'], "Aperte", COLORS['accent_secondary'], "Richieste aperte"),
            (ICONS['check'], "Chiuse", COLORS['accent_secondary'], "Richieste chiuse"),
            (ICONS['settings'], "Lavorazione", COLORS['accent_warning'], "Richieste in lavorazione"),
            (ICONS['send'], "Inviate", COLORS['accent_info'], "Richieste inviate"),
            (ICONS['alert'], "Eccezioni", COLORS['accent_error'], "Errori ed eccezioni")
        ]
        
        for icon_name, label, color, tooltip in statistic_configs:
            statistic_item = CompactStatisticItem(icon_name, label, color, tooltip)
            self._statistic_widgets[label.lower()] = statistic_item
            stats_layout.addWidget(statistic_item)
        
        parent_layout.addLayout(stats_layout)

    def _create_right_panel(self):
        """Create the right panel optimized for web content with glassmorphism."""
        self._right_panel = GlassPanel()
        self._right_panel.setObjectName("rightPanel")
        
        right_layout = QtWidgets.QVBoxLayout(self._right_panel)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(16, 12, 16, 12)
        
        # Progress section (initially hidden)
        self._create_progress_section(right_layout)
        
        # Web view area (maximized)
        self._create_web_area(right_layout)
        
        # Log area (compact but functional)
        self._create_log_area(right_layout)

    def _create_progress_section(self, parent_layout):
        """Create compact progress section."""
        self._progress_container = QtWidgets.QWidget()
        self._progress_container.setObjectName("progressContainer")
        self._progress_container.hide()  # Initially hidden
        
        progress_layout = QtWidgets.QVBoxLayout(self._progress_container)
        progress_layout.setSpacing(8)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress title
        progress_title = SectionTitle("📊 Progresso Elaborazione")
        
        # Status label
        self._status_label = QtWidgets.QLabel("Pronto per l'elaborazione")
        self._status_label.setObjectName("statusLabel")
        self._status_label.setStyleSheet(f"""
            QLabel#statusLabel {{
                color: {COLORS['text_primary']};
                font-size: 11px;
                padding: 8px;
                background: {COLORS['glass_white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-weight: 500;
            }}
        """)
        
        # Progress bar
        self._progress_bar = ModernProgressBar()
        
        progress_layout.addWidget(progress_title)
        progress_layout.addWidget(self._status_label)
        progress_layout.addWidget(self._progress_bar)
        
        parent_layout.addWidget(self._progress_container)

    def _create_web_area(self, parent_layout):
        """Create web view area with QtAwesome navigation controls and improved spacing."""
        # Web title
        web_title = SectionTitle("🌐 Browser NSIS")
        parent_layout.addWidget(web_title)
        
        # Web navigation controls with bottom margin
        nav_container = QtWidgets.QWidget()
        nav_container.setObjectName("navContainer")
        nav_container.setStyleSheet("""
            QWidget#navContainer {
                background: transparent;
                border: none;
            }
        """)
        nav_layout = QtWidgets.QHBoxLayout(nav_container)
        nav_layout.setSpacing(8)  # Increased spacing between buttons
        nav_layout.setContentsMargins(0, 0, 0, 12)  # Bottom margin to separate from web view
        
        # Navigation buttons with QtAwesome icons
        self._back_btn = WebNavButton(ICONS['arrow_left'])
        self._forward_btn = WebNavButton(ICONS['arrow_right'])
        self._reload_btn = WebNavButton(ICONS['rotate'])
        
        nav_layout.addWidget(self._back_btn)
        nav_layout.addWidget(self._forward_btn)
        nav_layout.addWidget(self._reload_btn)
        nav_layout.addStretch()
        
        # Web view placeholder - simplified since styling is now handled by RoundedWebContainer
        self._web_view_placeholder = QtWidgets.QWidget()
        self._web_view_placeholder.setObjectName("webViewPlaceholder")
        self._web_view_placeholder.setMinimumHeight(300)
        self._web_view_placeholder.setStyleSheet("""
            QWidget#webViewPlaceholder {
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)
        
        parent_layout.addWidget(nav_container)
        parent_layout.addWidget(self._web_view_placeholder, 3)  # Give it maximum space

    def _create_log_area(self, parent_layout):
        """Create compact but functional log area."""
        # Log title
        log_title = SectionTitle("📝 Log Attività")
        parent_layout.addWidget(log_title)
        
        # Log text area
        self._log_text = QtWidgets.QTextEdit()
        self._log_text.setObjectName("logText")
        self._log_text.setMinimumHeight(120)
        self._log_text.setMaximumHeight(150)
        self._log_text.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 12px;
                color: {COLORS['text_primary']};
                font-size: 11px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                padding: 10px;
                selection-background-color: {COLORS['accent_primary']};
            }}
            QTextEdit QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.15);
                width: 12px;
                border-radius: 6px;
                border: none;
                margin: 3px;
            }}
            QTextEdit QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(130, 170, 255, 0.9),
                    stop:1 rgba(195, 232, 141, 0.9));
                border-radius: 6px;
                min-height: 40px;
                border: none;
                margin: 2px;
            }}
            QTextEdit QScrollBar::handle:vertical:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(130, 170, 255, 1.0),
                    stop:1 rgba(195, 232, 141, 1.0));
            }}
            QTextEdit QScrollBar::handle:vertical:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 150, 255, 1.0),
                    stop:1 rgba(175, 212, 121, 1.0));
            }}
            QTextEdit QScrollBar::add-line:vertical,
            QTextEdit QScrollBar::sub-line:vertical {{
                height: 0px;
                background: transparent;
            }}
            QTextEdit QScrollBar::add-page:vertical,
            QTextEdit QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)
        
        parent_layout.addWidget(self._log_text, 1)

    def _setup_global_styles(self):
        """Setup global styles with Glassmorphism design."""
        global_style = f"""
            /* Global Application Styles - Glassmorphism Design */
            QWidget {{
                background: transparent;
                color: {COLORS['text_primary']};
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
            }}
            
            /* Remove backgrounds from all text elements */
            QLabel {{
                background: transparent;
                border: none;
            }}
            
            QLineEdit {{
                background: transparent;
                border: none;
            }}
            
            QTextEdit {{
                background: transparent;
                border: none;
            }}
            
            QFrame {{
                background: transparent;
                border: none;
            }}
            
            QGroupBox {{
                background: transparent;
                border: none;
            }}
            
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            
            QSplitter {{
                background: transparent;
                border: none;
            }}
            
            QSplitter::handle {{
                background: transparent;
            }}
            
            /* Remove any borders from layouts and containers */
            QHBoxLayout, QVBoxLayout {{
                border: none;
                background: transparent;
            }}
            
            QWidget[objectName*="button"] {{
                border: none;
            }}
            
            /* Remove backgrounds from all statistic elements */
            QWidget[objectName*="compactStatisticItem"] QLabel {{
                background: transparent !important;
                border: none !important;
            }}
            
            /* Remove backgrounds from spacer widgets */
            QWidget[objectName*="compactStatisticItem"] QWidget {{
                background: transparent !important;
                border: none !important;
            }}
            
            /* Remove backgrounds from layout items */
            QHBoxLayout QWidget {{
                background: transparent !important;
                border: none !important;
            }}
            
            /* Remove backgrounds from navigation buttons */
            QPushButton[objectName*="webNavButton"] {{
                background: transparent !important;
                border: none !important;
            }}
            
            /* Remove backgrounds from all icons */
            QLabel[objectName*="icon"] {{
                background: transparent !important;
                border: none !important;
            }}
            
            /* Navigation container transparency */
            QWidget[objectName*="navContainer"] {{
                background: transparent !important;
                border: none !important;
            }}
            
            /* Glass Panel Style */
            QFrame#glassPanel {{
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.35);
            }}
            
            /* Main Window */
            QMainWindow {{
                background: transparent;
                border: none;
            }}
            
            /* Left Panel */
            QWidget#leftPanel {{
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 15px;
            }}
            
            /* Right Panel */
            QWidget#rightPanel {{
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 15px;
            }}
            
            /* Web Browser and Log Areas with Rounded Corners */
            QTextEdit {{
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 12px;
            }}
            
            QWidget#webViewPlaceholder {{
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 12px;
                padding: 8px;
            }}
            
            /* QWebEngineView with elegant integration */
            QWebEngineView {{
                background: transparent;
                border: none;
                margin: 0px;
            }}
            
            /* Modern Scrollbars */
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.1);
                width: 10px;
                border-radius: 5px;
                border: none;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(130, 170, 255, 0.8),
                    stop:1 rgba(195, 232, 141, 0.8));
                border-radius: 5px;
                min-height: 30px;
                border: none;
                margin: 1px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(130, 170, 255, 1.0),
                    stop:1 rgba(195, 232, 141, 1.0));
                transform: scale(1.1);
            }}
            
            QScrollBar::handle:vertical:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 150, 255, 1.0),
                    stop:1 rgba(175, 212, 121, 1.0));
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                background: transparent;
            }}
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            
            /* Horizontal Scrollbar */
            QScrollBar:horizontal {{
                background: rgba(255, 255, 255, 0.1);
                height: 10px;
                border-radius: 5px;
                border: none;
                margin: 2px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(130, 170, 255, 0.8),
                    stop:1 rgba(195, 232, 141, 0.8));
                border-radius: 5px;
                min-width: 30px;
                border: none;
                margin: 1px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(130, 170, 255, 1.0),
                    stop:1 rgba(195, 232, 141, 1.0));
            }}
            
            QScrollBar::handle:horizontal:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 150, 255, 1.0),
                    stop:1 rgba(175, 212, 121, 1.0));
            }}
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
                background: transparent;
            }}
            
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {{
                background: transparent;
            }}
            
            /* Tooltips */
            /* Text Edit (Log) specific scrollbar */
            QTextEdit QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.15);
                width: 12px;
                border-radius: 6px;
                border: none;
                margin: 3px;
            }}
            
            QTextEdit QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(130, 170, 255, 0.9),
                    stop:1 rgba(195, 232, 141, 0.9));
                border-radius: 6px;
                min-height: 40px;
                border: none;
                margin: 2px;
            }}
            
            QTextEdit QScrollBar::handle:vertical:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(130, 170, 255, 1.0),
                    stop:1 rgba(195, 232, 141, 1.0));
            }}
            
            /* Web View specific scrollbar */
            QWebEngineView QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.15);
                width: 12px;
                border-radius: 6px;
                border: none;
                margin: 3px;
            }}
            
            QWebEngineView QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(130, 170, 255, 0.9),
                    stop:1 rgba(195, 232, 141, 0.9));
                border-radius: 6px;
                min-height: 40px;
                border: none;
                margin: 2px;
            }}
            
            QWebEngineView QScrollBar::handle:vertical:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(130, 170, 255, 1.0),
                    stop:1 rgba(195, 232, 141, 1.0));
            }}
            

            
            /* Global Button Styles - Windows 11 Professional */
            QPushButton {{
                border-radius: 6px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                border-radius: 6px;
            }}
            
            QPushButton:pressed {{
                border-radius: 6px;
            }}
            
            /* Force hover effects on ALL buttons */
            QPushButton {{
                border-radius: 6px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                border-radius: 6px;
            }}
            
            QPushButton:pressed {{
                border-radius: 6px;
            }}
            
            /* Force ALL button hover effects with maximum priority */
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.3) !important;
                border: 1px solid rgba(255, 255, 255, 0.5) !important;
                color: #212529 !important;
            }}
            
            /* Specific overrides for different button types */
            QPushButton[objectName*="modernButton_primary"]:hover {{
                background: {COLORS['accent_primary_alt']} !important;
                color: white !important;
            }}
            
            QPushButton[objectName*="modernButton_success"]:hover {{
                background: {COLORS['accent_secondary_alt']} !important;
                color: white !important;
            }}
            
            QPushButton[objectName*="modernButton_danger"]:hover {{
                background: {COLORS['accent_error_alt']} !important;
                color: white !important;
            }}
            
            QPushButton[objectName*="modernButton_secondary"]:hover {{
                background: rgba(255, 255, 255, 0.4) !important;
                border: 1px solid rgba(255, 255, 255, 0.6) !important;
                color: #212529 !important;
            }}
            
            QPushButton[objectName*="webNavButton"]:hover {{
                background: rgba(255, 255, 255, 0.4) !important;
                border: 1px solid rgba(255, 255, 255, 0.6) !important;
                color: #212529 !important;
            }}
            
            QPushButton[objectName*="minimizeButton"]:hover {{
                background: rgba(255, 255, 255, 0.4) !important;
                color: #212529 !important;
            }}
            
            QPushButton[objectName*="closeButton"]:hover {{
                background: rgba(220, 53, 69, 0.9) !important;
                color: white !important;
            }}
            
            /* Tooltips */
            QToolTip {{
                background: {COLORS['glass_white']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px;
                font-size: 10px;
            }}
        """
        
        self._parent.setStyleSheet(global_style)

    def _connect_signals(self):
        """Connect UI signals to slots."""
        if self._select_file_button:
            print("DEBUG: Connessione segnale per pulsante Seleziona File")
            self._select_file_button.clicked.connect(self._on_select_file_clicked)
            # Verify button is enabled and visible
            print(f"DEBUG: Pulsante abilitato: {self._select_file_button.isEnabled()}")
            print(f"DEBUG: Pulsante visibile: {self._select_file_button.isVisible()}")
        else:
            print("DEBUG: ERRORE - Pulsante Seleziona File non trovato!")
        
        if self._start_button:
            self._start_button.clicked.connect(self.startButtonClicked.emit)
        
        if self._stop_button:
            self._stop_button.clicked.connect(self.stopButtonClicked.emit)
        
        if self._clear_log_button:
            self._clear_log_button.clicked.connect(self.clearLogClicked.emit)
        
        if self._open_nsis_button:
            self._open_nsis_button.clicked.connect(self.openNsisClicked.emit)
        
        # Connect web navigation buttons
        if self._back_btn:
            self._back_btn.clicked.connect(self.webBackClicked.emit)
        
        if self._forward_btn:
            self._forward_btn.clicked.connect(self.webForwardClicked.emit)
        
        if self._reload_btn:
            self._reload_btn.clicked.connect(self.webReloadClicked.emit)
    
    def _on_select_file_clicked(self):
        """Handle file selection button click."""
        print("DEBUG: Pulsante Seleziona File Excel cliccato!")
        
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self._parent,
            "Seleziona File Excel",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        print(f"DEBUG: File selezionato: {file_path}")
        
        if file_path:
            self.fileSelected.emit(file_path)
        else:
            print("DEBUG: Nessun file selezionato (utente ha annullato)")
    
    def set_file_path(self, file_path: str):
        """Show selected file in the elegant display area."""
        print(f"DEBUG: set_file_path chiamato con: {file_path}")
        
        if self._file_name_label and self._file_display_area:
            # Show only filename, not full path
            filename = os.path.basename(file_path)
            print(f"DEBUG: Mostrando file: {filename}")
            
            # Set tooltip with full path
            self._file_display_area.setToolTip(file_path)
            
            # Update file name
            self._file_name_label.setText(filename)
            
            # Show the display area with animation
            self._show_file_display_animation()
            
            # Show success indicator temporarily
            self._show_success_indicator()
            
            # Update button state
            if self._start_button:
                self._start_button.setEnabled(True)
                self._start_button.setText("Avvia Elaborazione")
        else:
            print("DEBUG: ERRORE - Elementi file display non trovati!")
    
    def _show_file_display_animation(self):
        """Show the file display area with smooth animation."""
        if not self._file_display_area:
            return
        
        # Create fade-in animation
        self._display_animation = QtCore.QPropertyAnimation(self._file_display_area, b"windowOpacity")
        self._display_animation.setDuration(300)
        self._display_animation.setStartValue(0.0)
        self._display_animation.setEndValue(1.0)
        
        # Show the area and start animation
        self._file_display_area.show()
        self._display_animation.start()
        
        # Also animate the background color
        self._background_animation = QtCore.QPropertyAnimation(self._file_display_area, b"styleSheet")
        self._background_animation.setDuration(300)
        
        self._background_animation.setStartValue(f"""
            QFrame#fileDisplayArea {{
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        self._background_animation.setEndValue(f"""
            QFrame#fileDisplayArea {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        self._background_animation.start()
    
    def _show_success_indicator(self):
        """Show success indicator with animation."""
        if not self._success_indicator:
            return
        
        # Show the indicator
        self._success_indicator.show()
        
        # Create pulse animation
        self._success_animation = QtCore.QPropertyAnimation(self._success_indicator, b"styleSheet")
        self._success_animation.setDuration(800)
        self._success_animation.setLoopCount(2)
        
        self._success_animation.setStartValue(f"""
            QLabel {{
                color: {COLORS['accent_secondary']};
                font-size: 10px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        
        self._success_animation.setEndValue(f"""
            QLabel {{
                color: {COLORS['accent_primary']};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        
        self._success_animation.start()
        
        # Hide after animation
        QtCore.QTimer.singleShot(2000, self._success_indicator.hide)
    

    
    def reset_file_path(self):
        """Reset file display to default state."""
        if self._file_name_label and self._file_display_area:
            # Reset file name
            self._file_name_label.setText("Nessun file selezionato")
            
            # Clear tooltip
            self._file_display_area.setToolTip("")
            
            # Hide the display area
            self._file_display_area.hide()
            
            # Hide success indicator
            if self._success_indicator:
                self._success_indicator.hide()
            
            # Disable start button
            if self._start_button:
                self._start_button.setEnabled(False)
                self._start_button.setText("Avvia Elaborazione")
    
    def update_progress(self, current: int, maximum: int):
        """Update progress bar."""
        if self._progress_bar:
            self._progress_bar.setMaximum(maximum)
            self._progress_bar.setValue(current)
            
            # Show progress container when needed
            if not self._progress_container.isVisible():
                self._progress_container.show()
    
    def update_status(self, message: str):
        """Update status label."""
        if self._status_label:
            self._status_label.setText(message)
    
    def add_log_message(self, message: str):
        """Add message to log with timestamp."""
        if self._log_text:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            # Append to log
            self._log_text.append(formatted_message)
            
            # Auto-scroll to bottom
            scrollbar = self._log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """Clear the log area."""
        if self._log_text:
            self._log_text.clear()
            self.add_log_message("🗑️ Log pulito")
    
    def update_badge(self, badge_prefix: str, count: int):
        """Update statistic count."""
        badge_key = badge_prefix.lower()
        if badge_key in self._statistic_widgets:
            self._statistic_widgets[badge_key].set_count(count)
    
    def reset_badges(self):
        """Reset all statistics to zero."""
        for statistic in self._statistic_widgets.values():
            statistic.set_count(0)
    
    def set_processing_state(self, is_processing: bool):
        """Set the UI to processing or idle state."""
        if self._start_button:
            self._start_button.setEnabled(not is_processing)
            self._start_button.setText("Elaborazione..." if is_processing else "Avvia Elaborazione")
        
        if self._stop_button:
            self._stop_button.setEnabled(is_processing)
        
        if self._select_file_button:
            self._select_file_button.setEnabled(not is_processing)
        
        if self._clear_log_button:
            self._clear_log_button.setEnabled(not is_processing)
        
        if self._open_nsis_button:
            self._open_nsis_button.setEnabled(not is_processing)
        
        # Show/hide progress container
        if self._progress_container:
            if is_processing and not self._progress_container.isVisible():
                self._progress_container.show()
            elif not is_processing and self._progress_container.isVisible():
                self._progress_container.hide()
    
    def set_web_view(self, web_view: QtWidgets.QWidget):
        """Set the web view in the placeholder with elegant integration and forced rounded corners."""
        if self._web_view_placeholder and web_view:
            # Clear existing layout
            if self._web_view_placeholder.layout():
                QtWidgets.QWidget().setLayout(self._web_view_placeholder.layout())
            
            # Create new layout with small padding for visual separation
            layout = QtWidgets.QVBoxLayout(self._web_view_placeholder)
            layout.setContentsMargins(4, 4, 4, 4)
            
            # Create a decorative frame first with much more pronounced border
            decorative_frame = QtWidgets.QFrame()
            decorative_frame.setObjectName("decorativeFrame")
            decorative_frame.setStyleSheet("""
                QFrame#decorativeFrame {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(255, 255, 255, 0.8),
                        stop:1 rgba(255, 255, 255, 0.6));
                    border: 4px solid rgba(255, 255, 255, 0.9);
                    border-radius: 18px;
                    padding: 4px;
                }
            """)
            
            # Create layout for decorative frame with more padding
            frame_layout = QtWidgets.QVBoxLayout(decorative_frame)
            frame_layout.setContentsMargins(6, 6, 6, 6)
            
            # Create rounded container for the web view with more aggressive masking
            rounded_container = RoundedWebContainer(web_view, radius=16)
            frame_layout.addWidget(rounded_container)
            
            # Apply elegant styling to the web view
            web_view.setStyleSheet("""
                QWebEngineView {
                    background: transparent;
                    border: none;
                    margin: 0px;
                }
                QWebEngineView QWidget {
                    background: transparent;
                    border: none;
                }
                QWebEngineView QWebEnginePage {
                    background: transparent;
                }
                QWebEngineView QScrollBar:vertical {
                    background: rgba(255, 255, 255, 0.15);
                    width: 12px;
                    border-radius: 6px;
                    border: none;
                    margin: 3px;
                }
                QWebEngineView QScrollBar::handle:vertical {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(130, 170, 255, 0.9),
                        stop:1 rgba(195, 232, 141, 0.9));
                    border-radius: 6px;
                    min-height: 40px;
                    border: none;
                    margin: 2px;
                }
                QWebEngineView QScrollBar::handle:vertical:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(130, 170, 255, 1.0),
                        stop:1 rgba(195, 232, 141, 1.0));
                }
                QWebEngineView QScrollBar::handle:vertical:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(100, 150, 255, 1.0),
                        stop:1 rgba(175, 212, 121, 1.0));
                }
                QWebEngineView QScrollBar::add-line:vertical,
                QWebEngineView QScrollBar::sub-line:vertical {
                    height: 0px;
                    background: transparent;
                }
                QWebEngineView QScrollBar::add-page:vertical,
                QWebEngineView QScrollBar::sub-page:vertical {
                    background: transparent;
                }
                QWebEngineView QScrollBar:horizontal {
                    background: rgba(255, 255, 255, 0.15);
                    height: 12px;
                    border-radius: 6px;
                    border: none;
                    margin: 3px;
                }
                QWebEngineView QScrollBar::handle:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(130, 170, 255, 0.9),
                        stop:1 rgba(195, 232, 141, 0.9));
                    border-radius: 6px;
                    min-width: 40px;
                    border: none;
                    margin: 2px;
                }
                QWebEngineView QScrollBar::handle:horizontal:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(130, 170, 255, 1.0),
                        stop:1 rgba(195, 232, 141, 1.0));
                }
                QWebEngineView QScrollBar::add-line:horizontal,
                QWebEngineView QScrollBar::sub-line:horizontal {
                    width: 0px;
                    background: transparent;
                }
            """)
            
            # Add the decorative frame to the layout
            layout.addWidget(decorative_frame)
            
            # Store references
            self._web_view = web_view
            self._rounded_container = rounded_container
            self._decorative_frame = decorative_frame
            
            # Force update after a short delay to ensure proper rendering
            QtCore.QTimer.singleShot(200, self._force_web_view_update)
            
            self._logger.info("Web view set in UI with rounded corners")
    
    def _force_web_view_update(self):
        """Force web view update to ensure rounded corners are applied."""
        if hasattr(self, '_rounded_container') and self._rounded_container:
            self._rounded_container._apply_rounded_mask()
            self._rounded_container.update()
            if hasattr(self, '_decorative_frame') and self._decorative_frame:
                self._decorative_frame.update()
            if self._web_view:
                self._web_view.update()
    

    
    @property
    def web_view_placeholder(self) -> QtWidgets.QWidget:
        """Get the web view placeholder widget."""
        return self._web_view_placeholder
    
    def update_layout_on_resize(self):
        """Update layout when window is resized."""
        if self._splitter:
            # Maintain optimized proportions (20% left, 80% right)
            total_width = self._splitter.width()
            left_width = min(280, max(220, total_width * 0.2))
            right_width = total_width - left_width
            self._splitter.setSizes([int(left_width), int(right_width)])
        
        # Update signature label position
        if self._signature_label:
            self._signature_label.setGeometry(
                self._parent.width() - 120, 
                self._parent.height() - 30, 
                110, 
                20
            )
    
    def _handle_resize_event(self, event):
        """Handle window resize events."""
        self.update_layout_on_resize()
        event.accept() 