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

# Import Fluent Widgets for modern components
try:
    from qfluentwidgets import ProgressBar, FluentIcon, InfoBar, InfoBarPosition
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    print("PyQt6-Fluent-Widgets not available, using fallback components")

# Glassmorphism Design Color Palette (Light Theme)
COLORS = {
    'bg_primary': '#ffffff',      # Pure white background
    'bg_secondary': '#f8f9fa',    # Light gray background
    'bg_tertiary': '#e9ecef',     # Lighter gray background
    'text_primary': '#212529',    # Dark text for high contrast
    'text_secondary': '#6c757d',  # Medium gray text
    'text_muted': '#adb5bd',      # Light gray text
    'accent_primary': '#3B82F6',  # Modern blue (unified button color)
    'accent_primary_alt': '#2563EB', # Darker blue for hover
    'accent_primary_light': '#60A5FA', # Lighter blue for pressed
    'accent_secondary': '#3B82F6', # Same as primary for consistency
    'accent_secondary_alt': '#2563EB', # Same as primary alt
    'accent_error': '#3B82F6',    # Same as primary for consistency
    'accent_error_alt': '#2563EB', # Same as primary alt
    'accent_warning': '#3B82F6',  # Same as primary for consistency
    'accent_warning_alt': '#2563EB', # Same as primary alt
    'accent_info': '#3B82F6',     # Same as primary for consistency
    'accent_info_alt': '#2563EB', # Same as primary alt
    'border': 'rgba(255, 255, 255, 0.25)', # Glass border
    'border_light': 'rgba(255, 255, 255, 0.15)', # Light glass border
    'shadow': 'rgba(0, 0, 0, 0.1)', # Subtle shadow
    'signature': '#6c757d',       # Signature text color
    'glass_white': 'rgba(255, 255, 255, 0.15)', # Glass white overlay
    'glass_highlight': 'rgba(255, 255, 255, 0.25)', # Glass highlight
    'title_accent': '#3B82F6',    # Same as primary for consistency
    'title_accent_light': '#60A5FA',  # Lighter blue for gradients
    'dhl_yellow': '#3B82F6',      # Same as primary for consistency
    'dhl_yellow_dark': '#2563EB', # Same as primary alt
    'dhl_red': '#3B82F6',         # Same as primary for consistency
}

# Icon mapping with QtAwesome professional icons - Enhanced
ICONS = {
    'play': 'start',                 # Custom start icon from icons/start.png
    'stop': 'stop',                  # Custom stop icon from icons/stop.png
    'trash': 'trash',                # Custom trash icon from icons/trash.png
    'home': 'home',                  # Custom home icon from icons/home.png
    'folder': 'folder',              # Custom folder icon from icons/folder.png
    'check': 'fa5s.check-square',
    'settings': 'fa5s.cog',
    'send': 'fa5s.paper-plane',
    'alert': 'fa5s.exclamation-triangle',
    'arrow_left': 'left',
    'arrow_right': 'right',
    'rotate': 'reload',
    'file': 'fa5s.table',            # Table icon for Excel files
    'excel': 'excel',                # Custom Excel icon from icons/excel.png
    'chrome': 'chrome',              # Custom Chrome icon from icons/chrome.png
    'controls': 'controls',          # Custom controls icon from icons/controls.png
    'statistics': 'statistics',      # Custom statistics GIF from icons/statistics.gif
    'eye_open': 'fa5s.eye',          # Eye open for visible log
    'eye_closed': 'fa5s.eye-slash',  # Eye closed for hidden log
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

class Windows11ProgressBar(QtWidgets.QProgressBar):
    """Windows 11 style progress bar with smooth animations."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
        self.setStyleSheet(f"""
            QProgressBar {{
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 3px;
                text-align: center;
                color: transparent;
                margin: 8px 0;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078D4,
                    stop:0.5 #40E0D0,
                    stop:1 #0078D4);
                border-radius: 3px;
                margin: 0px;
            }}
        """)
        
        # Animation properties
        self._animation = QtCore.QPropertyAnimation(self, b"value")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)

    def setValue(self, value):
        """Animate value changes."""
        self._animation.setStartValue(self.value())
        self._animation.setEndValue(value)
        self._animation.start()

class ModernFluentProgressBar(QtWidgets.QWidget):
    """Modern progress bar with blue gradient and animated truck."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernFluentProgressBar")
        self.setFixedHeight(60)
        
        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Progress info label with modern styling - CHANGED TO DARK TEXT
        self._progress_info = QtWidgets.QLabel("0%")
        self._progress_info.setObjectName("progressInfo")
        self._progress_info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._progress_info.setStyleSheet("""
            QLabel#progressInfo {
                color: #1E3A8A;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                letter-spacing: 0.5px;
            }
        """)
        
        # Progress bar container with better contrast
        self._progress_container = QtWidgets.QWidget()
        self._progress_container.setObjectName("progressContainer")
        self._progress_container.setFixedHeight(12)
        self._progress_container.setStyleSheet("""
            QWidget#progressContainer {
                background: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(59, 130, 246, 0.4);
                border-radius: 6px;
                margin: 0px;
            }
        """)
        
        # Progress fill widget with bright blue gradient
        self._progress_fill = QtWidgets.QWidget(self._progress_container)
        self._progress_fill.setObjectName("progressFill")
        self._progress_fill.setFixedHeight(8)
        self._progress_fill.setStyleSheet("""
            QWidget#progressFill {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60A5FA,
                    stop:0.25 #3B82F6,
                    stop:0.5 #2563EB,
                    stop:0.75 #1D4ED8,
                    stop:1 #1E40AF);
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
        """)
        
        # Set initial width
        self._progress_fill.setFixedWidth(0)
        
        # Animated truck widget
        self._truck_widget = QtWidgets.QWidget(self._progress_container)
        self._truck_widget.setObjectName("truckWidget")
        self._truck_widget.setFixedSize(20, 16)
        self._truck_widget.setStyleSheet("""
            QWidget#truckWidget {
                background: transparent;
                border: none;
            }
        """)
        
        layout.addWidget(self._progress_info)
        layout.addWidget(self._progress_container)
        
        # Animation for smooth progress changes
        self._width_animation = QtCore.QPropertyAnimation(self._progress_fill, b"minimumWidth")
        self._width_animation.setDuration(800)
        self._width_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutQuart)
        
        # Truck animation
        self._truck_animation = QtCore.QPropertyAnimation(self._truck_widget, b"geometry")
        self._truck_animation.setDuration(2000)
        self._truck_animation.setLoopCount(-1)
        self._truck_animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)
        
        # Gradient animation for shimmer effect - BRIGHTER COLORS
        self._gradient_animation = QtCore.QPropertyAnimation(self._progress_fill, b"styleSheet")
        self._gradient_animation.setDuration(3000)
        self._gradient_animation.setLoopCount(-1)
        self._gradient_animation.setStartValue("""
            QWidget#progressFill {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60A5FA,
                    stop:0.25 #3B82F6,
                    stop:0.5 #2563EB,
                    stop:0.75 #1D4ED8,
                    stop:1 #1E40AF);
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
        """)
        self._gradient_animation.setEndValue("""
            QWidget#progressFill {
                background: qlineargradient(x1:1, y1:0, x2:0, y2:0,
                    stop:0 #60A5FA,
                    stop:0.25 #3B82F6,
                    stop:0.5 #2563EB,
                    stop:0.75 #1D4ED8,
                    stop:1 #1E40AF);
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
        """)
        
        # Start animations
        self._gradient_animation.start()
        
        # Current progress
        self._current_progress = 0
        self._max_progress = 100
        
        # Truck position
        self._truck_x = 0
    
    def setMaximum(self, maximum):
        """Set maximum progress value."""
        self._max_progress = maximum
    
    def setValue(self, value):
        """Set progress value with animation."""
        self._current_progress = value
        
        # Calculate percentage and width
        percentage = int((value / self._max_progress) * 100) if self._max_progress > 0 else 0
        container_width = self._progress_container.width() - 4  # Account for margins
        target_width = int((percentage / 100) * container_width)
        
        # Update info label
        self._progress_info.setText(f"{percentage}%")
        
        # Animate width change
        self._width_animation.setStartValue(self._progress_fill.width())
        self._width_animation.setEndValue(target_width)
        self._width_animation.start()
        
        # Update truck animation
        self._update_truck_animation()
    
    def _update_truck_animation(self):
        """Update truck animation based on current progress."""
        if self._max_progress > 0:
            percentage = (self._current_progress / self._max_progress) * 100
            container_width = self._progress_container.width() - 4
            max_truck_x = container_width - 20  # Truck width
            
            # Set truck animation with proper positioning
            start_rect = QtCore.QRect(2, 2, 20, 16)
            end_rect = QtCore.QRect(max_truck_x, 2, 20, 16)
            
            self._truck_animation.setStartValue(start_rect)
            self._truck_animation.setEndValue(end_rect)
            self._truck_animation.start()
            
            # Ensure truck is visible and on top
            self._truck_widget.raise_()
            self._truck_widget.show()
    
    def paintEvent(self, event):
        """Custom paint event to draw the animated truck."""
        super().paintEvent(event)
        
        # Only paint truck if this is the truck widget
        if self.objectName() == "truckWidget":
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            
            # Draw truck body with blue color to match theme
            truck_rect = self.rect()
            painter.fillRect(truck_rect, QtGui.QColor(59, 130, 246))  # Blue color
            
            # Draw truck outline
            painter.setPen(QtGui.QPen(QtGui.QColor(30, 58, 138), 2))  # Darker blue outline
            painter.drawRect(truck_rect)
            
            # Draw truck cabin
            cabin_rect = QtCore.QRect(12, 2, 8, 8)
            painter.fillRect(cabin_rect, QtGui.QColor(96, 165, 250))  # Lighter blue cabin
            painter.drawRect(cabin_rect)
            
            # Draw wheels (larger and more visible)
            wheel_rect1 = QtCore.QRect(3, 10, 5, 5)
            wheel_rect2 = QtCore.QRect(12, 10, 5, 5)
            painter.fillEllipse(wheel_rect1, QtGui.QColor(30, 58, 138))  # Dark blue wheels
            painter.fillEllipse(wheel_rect2, QtGui.QColor(30, 58, 138))
            
            # Draw wheel details
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
            painter.drawEllipse(wheel_rect1)
            painter.drawEllipse(wheel_rect2)
    
    def resizeEvent(self, event):
        """Handle resize events to update progress bar width."""
        super().resizeEvent(event)
        # Update progress fill width when container is resized
        if self._max_progress > 0:
            percentage = (self._current_progress / self._max_progress) * 100
            container_width = self._progress_container.width() - 4
            target_width = int((percentage / 100) * container_width)
            self._progress_fill.setFixedWidth(target_width)
            self._update_truck_animation()
    
    def stop_animation(self):
        """Stop all animations."""
        self._gradient_animation.stop()
        self._truck_animation.stop()

class CentralProgressOverlay(QtWidgets.QWidget):
    """Central progress overlay with beautiful animations."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("centralProgressOverlay")
        self.setFixedSize(400, 200)
        
        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title container with icon and text
        title_container = QtWidgets.QWidget()
        title_container.setObjectName("titleContainer")
        title_container.setStyleSheet("""
            QWidget#titleContainer {
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        title_layout = QtWidgets.QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)
        title_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Loading GIF
        self._loading_gif = QtWidgets.QLabel()
        self._loading_gif.setObjectName("loadingGif")
        self._loading_gif.setFixedSize(24, 24)
        self._loading_gif.setScaledContents(True)
        self._loading_gif.setStyleSheet("""
            QLabel#loadingGif {
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        # Load and start the GIF animation
        try:
            import os
            gif_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "loading.gif")
            if os.path.exists(gif_path):
                from PyQt6.QtGui import QMovie
                self._movie = QMovie(gif_path)
                self._movie.setScaledSize(QtCore.QSize(24, 24))
                self._loading_gif.setMovie(self._movie)
                self._movie.start()
        except Exception as e:
            print(f"Errore caricamento GIF: {e}")
        
        # Title text - CHANGED TO DARK TEXT
        self._title_label = QtWidgets.QLabel("Elaborazione in Corso")
        self._title_label.setObjectName("overlayTitle")
        self._title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet("""
            QLabel#overlayTitle {
                color: #1E3A8A;
                font-size: 18px;
                font-weight: 700;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                letter-spacing: 0.8px;
            }
        """)
        
        # Add GIF and text to title layout
        title_layout.addWidget(self._loading_gif)
        title_layout.addWidget(self._title_label)
        
        # Progress bar
        self._progress_bar = ModernFluentProgressBar()
        
        # Status text - CHANGED TO DARK TEXT
        self._status_label = QtWidgets.QLabel("Inizializzazione...")
        self._status_label.setObjectName("overlayStatus")
        self._status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("""
            QLabel#overlayStatus {
                color: #374151;
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        layout.addWidget(title_container)
        layout.addWidget(self._progress_bar)
        layout.addWidget(self._status_label)
        
        # Set up the glassmorphism background - CHANGED TO LIGHT BACKGROUND
        self.setStyleSheet("""
            QWidget#centralProgressOverlay {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(248, 250, 252, 0.95));
                border: 2px solid rgba(59, 130, 246, 0.3);
                border-radius: 20px;
            }
        """)
        
        # Animations
        self._fade_in_animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self._fade_in_animation.setDuration(500)
        self._fade_in_animation.setStartValue(0.0)
        self._fade_in_animation.setEndValue(1.0)
        self._fade_in_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        
        self._fade_out_animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self._fade_out_animation.setDuration(300)
        self._fade_out_animation.setStartValue(1.0)
        self._fade_out_animation.setEndValue(0.0)
        self._fade_out_animation.setEasingCurve(QtCore.QEasingCurve.Type.InCubic)
        
        # Scale animation for entrance
        self._scale_animation = QtCore.QPropertyAnimation(self, b"geometry")
        self._scale_animation.setDuration(400)
        self._scale_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutBack)
        
        # Initially hidden
        self.hide()
    
    def show_overlay(self):
        """Show overlay with beautiful entrance animation."""
        # Center the overlay on parent
        if self.parent():
            parent_rect = self.parent().rect()
            x = parent_rect.center().x() - self.width() // 2
            y = parent_rect.center().y() - self.height() // 2
            self.move(x, y)
        
        # Start scale animation from smaller size
        start_rect = self.geometry()
        start_rect.setSize(start_rect.size() * 0.8)
        start_rect.moveCenter(self.geometry().center())
        
        self._scale_animation.setStartValue(start_rect)
        self._scale_animation.setEndValue(self.geometry())
        
        # Hide web view and navigation controls if they exist
        if hasattr(self.parent(), '_ui_manager'):
            ui_manager = self.parent()._ui_manager
            if hasattr(ui_manager, '_web_view_placeholder'):
                ui_manager._web_view_placeholder.hide()
            # Hide navigation container (contains back, forward, reload buttons and log toggle)
            if hasattr(ui_manager, '_back_btn') and ui_manager._back_btn.parent():
                ui_manager._back_btn.parent().hide()
            # Hide web title (Browser NSIS)
            if hasattr(ui_manager, '_log_text') and ui_manager._log_text.parent():
                # Find the web title by looking at siblings
                parent_layout = ui_manager._log_text.parent().layout()
                if parent_layout:
                    for i in range(parent_layout.count()):
                        widget = parent_layout.itemAt(i).widget()
                        if widget and hasattr(widget, 'text') and "Browser NSIS" in widget.text():
                            widget.hide()
                            break
        
        # Ensure it's on top
        self.raise_()
        self.show()
        self._fade_in_animation.start()
        self._scale_animation.start()
    
    def hide_overlay(self):
        """Hide overlay with fade out animation."""
        self._fade_out_animation.start()
        self._fade_out_animation.finished.connect(self._on_hide_finished)
    
    def _on_hide_finished(self):
        """Called when hide animation is finished."""
        self.hide()
        # Show web view and navigation controls again
        if hasattr(self.parent(), '_ui_manager'):
            ui_manager = self.parent()._ui_manager
            if hasattr(ui_manager, '_web_view_placeholder'):
                ui_manager._web_view_placeholder.show()
            # Show navigation container (contains back, forward, reload buttons and log toggle)
            if hasattr(ui_manager, '_back_btn') and ui_manager._back_btn.parent():
                ui_manager._back_btn.parent().show()
            # Show web title (Browser NSIS)
            if hasattr(ui_manager, '_log_text') and ui_manager._log_text.parent():
                # Find the web title by looking at siblings
                parent_layout = ui_manager._log_text.parent().layout()
                if parent_layout:
                    for i in range(parent_layout.count()):
                        widget = parent_layout.itemAt(i).widget()
                        if widget and hasattr(widget, 'text') and "Browser NSIS" in widget.text():
                            widget.show()
                            break
    
    def set_progress(self, current: int, maximum: int):
        """Set progress with animation."""
        self._progress_bar.setMaximum(maximum)
        self._progress_bar.setValue(current)
    
    def set_status(self, status: str):
        """Set status text."""
        self._status_label.setText(status)
    
    def stop_animations(self):
        """Stop all animations."""
        self._progress_bar.stop_animation()
        # Stop GIF animation
        if hasattr(self, '_movie') and self._movie:
            self._movie.stop()

class Windows11StatusDisplay(QtWidgets.QWidget):
    """Windows 11 style status display with modern animations."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("windows11StatusDisplay")
        self.setFixedHeight(60)
        
        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Status icon with animation
        self._status_icon = QtWidgets.QLabel("⚡")
        self._status_icon.setObjectName("statusIcon")
        self._status_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._status_icon.setStyleSheet("""
            QLabel#statusIcon {
                color: #0078D4;
                font-size: 20px;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # Status text
        self._status_text = QtWidgets.QLabel("Pronto per l'elaborazione")
        self._status_text.setObjectName("statusText")
        self._status_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._status_text.setStyleSheet("""
            QLabel#statusText {
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # Progress info
        self._progress_info = QtWidgets.QLabel("")
        self._progress_info.setObjectName("progressInfo")
        self._progress_info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._progress_info.setStyleSheet("""
            QLabel#progressInfo {
                color: rgba(255, 255, 255, 0.6);
                font-size: 10px;
                font-weight: 400;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        layout.addWidget(self._status_icon)
        layout.addWidget(self._status_text)
        layout.addWidget(self._progress_info)
        
        # Animation for icon
        self._icon_animation = QtCore.QPropertyAnimation(self._status_icon, b"styleSheet")
        self._icon_animation.setDuration(1000)
        self._icon_animation.setLoopCount(-1)
        self._icon_animation.setStartValue("""
            QLabel#statusIcon {
                color: #0078D4;
                font-size: 20px;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        self._icon_animation.setEndValue("""
            QLabel#statusIcon {
                color: #40E0D0;
                font-size: 22px;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
    
    def set_status(self, status: str, icon: str = "⚡"):
        """Set status with animation."""
        self._status_text.setText(status)
        self._status_icon.setText(icon)
        
        # Start icon animation
        self._icon_animation.start()
    
    def set_progress_info(self, info: str):
        """Set progress information."""
        self._progress_info.setText(info)
    
    def stop_animation(self):
        """Stop icon animation."""
        self._icon_animation.stop()
        self._status_icon.setStyleSheet("""
            QLabel#statusIcon {
                color: #0078D4;
                font-size: 20px;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)

class ModernProgressBar(QtWidgets.QProgressBar):
    """Modern liquid glass progress bar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QProgressBar {{
                background: transparent;
                border: none;
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
            # Check if it's a custom icon from icons folder
            custom_icons = ["excel", "start", "stop", "trash", "home", "folder", "chrome", "controls", "statistics", "left", "right", "reload"]
            if icon_name in custom_icons:
                import os
                # Handle GIF for statistics
                if icon_name == "statistics":
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", f"{icon_name}.gif")
                    if os.path.exists(icon_path):
                        from PyQt6.QtGui import QMovie
                        movie = QMovie(icon_path)
                        movie.setScaledSize(QtCore.QSize(16, 16))
                        self._icon_label.setMovie(movie)
                        movie.start()
                        return
                else:
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", f"{icon_name}.png")
                    if os.path.exists(icon_path):
                        from PyQt6.QtGui import QIcon, QPixmap
                        icon = QIcon(icon_path)
                        pixmap = icon.pixmap(16, 16)
                        self._icon_label.setPixmap(pixmap)
                        return
            
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
        
        # Define unified modern button styles with elegant hover effects
        styles = {
            "primary": f"""
                QPushButton#modernButton_primary {{
                    background: {COLORS['accent_primary']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 10px 24px;
                    min-height: 36px;
                }}
                QPushButton#modernButton_primary:hover {{
                    background: {COLORS['accent_primary_alt']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_primary:pressed {{
                    background: {COLORS['accent_primary_light']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_primary:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                    border-radius: 10px;
                }}
            """,
            "success": f"""
                QPushButton#modernButton_success {{
                    background: {COLORS['accent_primary']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 10px 24px;
                    min-height: 36px;
                }}
                QPushButton#modernButton_success:hover {{
                    background: {COLORS['accent_primary_alt']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_success:pressed {{
                    background: {COLORS['accent_primary_light']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_success:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                    border-radius: 10px;
                }}
            """,
            "danger": f"""
                QPushButton#modernButton_danger {{
                    background: {COLORS['accent_primary']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 10px 24px;
                    min-height: 36px;
                }}
                QPushButton#modernButton_danger:hover {{
                    background: {COLORS['accent_primary_alt']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_danger:pressed {{
                    background: {COLORS['accent_primary_light']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_danger:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                    border-radius: 10px;
                }}
            """,
            "secondary": f"""
                QPushButton#modernButton_secondary {{
                    background: {COLORS['accent_primary']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 10px 18px;
                    min-height: 36px;
                }}
                QPushButton#modernButton_secondary:hover {{
                    background: {COLORS['accent_primary_alt']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_secondary:pressed {{
                    background: {COLORS['accent_primary_light']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_secondary:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                    border-radius: 10px;
                }}
            """,
            "dhl": f"""
                QPushButton#modernButton_dhl {{
                    background: {COLORS['accent_primary']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: 700;
                    padding: 10px 24px;
                    min-height: 36px;
                }}
                QPushButton#modernButton_dhl:hover {{
                    background: {COLORS['accent_primary_alt']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_dhl:pressed {{
                    background: {COLORS['accent_primary_light']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_dhl:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                    border-radius: 10px;
                }}
            """,
            "dhl_red": f"""
                QPushButton#modernButton_dhl_red {{
                    background: {COLORS['accent_primary']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: 700;
                    padding: 10px 24px;
                    min-height: 36px;
                }}
                QPushButton#modernButton_dhl_red:hover {{
                    background: {COLORS['accent_primary_alt']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_dhl_red:pressed {{
                    background: {COLORS['accent_primary_light']};
                    border-radius: 10px;
                }}
                QPushButton#modernButton_dhl_red:disabled {{
                    background: {COLORS['text_muted']};
                    color: {COLORS['bg_secondary']};
                    border-radius: 10px;
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
            # Check if it's a custom icon from icons folder
            custom_icons = ["excel", "start", "stop", "trash", "home", "folder", "chrome", "controls", "statistics", "left", "right", "reload"]
            if icon_name in custom_icons:
                import os
                # Handle GIF for statistics
                if icon_name == "statistics":
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", f"{icon_name}.gif")
                else:
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", f"{icon_name}.png")
                if os.path.exists(icon_path):
                    from PyQt6.QtGui import QIcon
                    icon = QIcon(icon_path)
                    self.setIcon(icon)
                    return
            
            # Choose color based on button type
            if button_type in ["primary", "success", "danger", "dhl", "dhl_red"]:
                icon_color = "white"  # White for filled buttons including DHL
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
        
        # Store icon name
        self._icon_name = icon_name
        
        # Load QtAwesome icon
        self._load_qtawesome_icon(icon_name)
        
        self.setStyleSheet(f"""
            QPushButton#webNavButton {{
                background: transparent;
                color: {COLORS['text_primary']};
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                padding: 0px;
                min-width: 40px;
                min-height: 36px;
            }}
        """)
    

    
    def _load_qtawesome_icon(self, icon_name: str):
        """Load QtAwesome icon for navigation button."""
        try:
            # Check if it's a custom icon from icons folder
            custom_icons = ["excel", "start", "stop", "trash", "home", "folder", "chrome", "controls", "statistics", "left", "right", "reload"]
            if icon_name in custom_icons:
                import os
                # Handle GIF for statistics
                if icon_name == "statistics":
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", f"{icon_name}.gif")
                else:
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", f"{icon_name}.png")
                if os.path.exists(icon_path):
                    from PyQt6.QtGui import QIcon, QPixmap
                    icon = QIcon(icon_path)
                    # Scale icon to 24x24
                    pixmap = icon.pixmap(24, 24)
                    self.setIcon(QIcon(pixmap))
                    return
            
            icon = qta.icon(icon_name, color=COLORS['text_primary'])
            # Scale QtAwesome icon to 24x24
            pixmap = icon.pixmap(24, 24)
            self.setIcon(QIcon(pixmap))
        except Exception as e:
            pass  # Fallback to text only
    
    def get_qtawesome_icon(self, icon_name: str):
        """Get QtAwesome icon without setting it."""
        try:
            # Check if it's a custom icon from icons folder
            custom_icons = ["excel", "start", "stop", "trash", "home", "folder", "chrome", "controls", "statistics", "left", "right", "reload"]
            if icon_name in custom_icons:
                import os
                # Handle GIF for statistics
                if icon_name == "statistics":
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", f"{icon_name}.gif")
                else:
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", f"{icon_name}.png")
                if os.path.exists(icon_path):
                    from PyQt6.QtGui import QIcon
                    return QIcon(icon_path)
            
            return qta.icon(icon_name, color=COLORS['text_primary'])
        except Exception as e:
            return None

class SignatureLabel(QtWidgets.QWidget):
    """Simple signature label with love.gif icon."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("signatureLabel")

        # Create horizontal layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # "Made with" text
        made_with_label = QtWidgets.QLabel("Made with")
        made_with_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: rgba(0, 0, 0, 0.9);
                font-size: 10px;
                font-weight: 600;
                padding: 0px;
                border: none;
                border-radius: 0px;
            }}
        """)

        # Love GIF icon
        love_icon_label = QtWidgets.QLabel()
        love_icon_label.setFixedSize(12, 12)
        love_icon_label.setStyleSheet("background: transparent; border: none; padding: 0; margin: 0;")
        love_icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Load love.gif
        try:
            import os
            love_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "love.gif")
            if os.path.exists(love_icon_path):
                from PyQt6.QtGui import QMovie
                movie = QMovie(love_icon_path)
                movie.setScaledSize(QtCore.QSize(12, 12))
                love_icon_label.setMovie(movie)
                movie.start()
        except Exception as e:
            # Fallback to heart emoji
            love_icon_label.setText("❤️")

        # "by ST" text
        by_st_label = QtWidgets.QLabel("by ST")
        by_st_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: rgba(0, 0, 0, 0.9);
                font-size: 10px;
                font-weight: 600;
                padding: 0px;
                border: none;
                border-radius: 0px;
            }}
        """)

        # Add widgets to layout
        layout.addWidget(made_with_label)
        layout.addWidget(love_icon_label)
        layout.addWidget(by_st_label)

        # Set widget style
        self.setStyleSheet(f"""
            QWidget#signatureLabel {{
                background: transparent;
                border: none;
                border-radius: 0px;
            }}
        """)

class SpinnerWidget(QtWidgets.QWidget):
    """Custom spinner widget for loading states."""
    def __init__(self, parent=None): 
        super().__init__(parent)
        self.hide()
    def startAnimation(self): self.show()
    def stopAnimation(self): self.hide()
    def setColor(self, color): pass

class FluentWebContainer(QtWidgets.QWidget):
    """Modern Fluent Design container for web view with elegant styling."""
    
    def __init__(self, web_view: QtWidgets.QWidget, parent=None):
        super().__init__(parent)
        self._web_view = web_view
        
        # Setup layout with elegant padding
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)  # Elegant padding
        layout.setSpacing(0)
        layout.addWidget(web_view)
        
        # Apply clean, modern styling
        self.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.95);
                border: none;
                border-radius: 16px;
            }
            QWebEngineView {
                background: transparent;
                border: none;
                border-radius: 12px;
            }
        """)
        
        # Apply rounded corner mask
        self._apply_rounded_mask()
        
        # Force mask update after widget is shown
        QtCore.QTimer.singleShot(100, self._apply_rounded_mask)
    
    def _apply_rounded_mask(self):
        """Apply rounded corner mask to the container."""
        try:
            # Create rounded mask for container
            path = QtGui.QPainterPath()
            rect = self.rect()
            rect_f = QtCore.QRectF(rect)
            path.addRoundedRect(rect_f, 16, 16)
            
            # Create and apply the mask
            mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
            self.setMask(mask)
            
            # Apply rounded mask to web view
            if hasattr(self._web_view, 'setMask'):
                web_rect = self._web_view.rect()
                web_rect_f = QtCore.QRectF(web_rect)
                web_path = QtGui.QPainterPath()
                web_path.addRoundedRect(web_rect_f, 12, 12)
                web_mask = QtGui.QRegion(web_path.toFillPolygon().toPolygon())
                self._web_view.setMask(web_mask)
                
        except Exception as e:
            pass  # Fallback to no mask
    
    def resizeEvent(self, event):
        """Handle resize events to update masks."""
        super().resizeEvent(event)
        QtCore.QTimer.singleShot(10, self._apply_rounded_mask)
    
    def showEvent(self, event):
        """Handle show events to ensure masks are applied."""
        super().showEvent(event)
        QtCore.QTimer.singleShot(50, self._apply_rounded_mask)
    
    def paintEvent(self, event):
        """Custom paint event with clean, modern design."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # Create rounded rectangle path
        rect = self.rect()
        rect_f = QtCore.QRectF(rect)
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect_f, 16, 16)
        
        # Draw subtle shadow for depth
        shadow_color = QtGui.QColor(0, 0, 0, 15)
        shadow_offset = 2
        
        # Draw shadow
        shadow_rect = rect.adjusted(shadow_offset, shadow_offset, shadow_offset, shadow_offset)
        shadow_rect_f = QtCore.QRectF(shadow_rect)
        shadow_path = QtGui.QPainterPath()
        shadow_path.addRoundedRect(shadow_rect_f, 16, 16)
        painter.fillPath(shadow_path, shadow_color)
        
        # Draw main container with clean white background
        painter.fillPath(path, QtGui.QColor(255, 255, 255, 240))
        
        # Draw single, elegant border
        border_pen = QtGui.QPen(QtGui.QColor(200, 200, 200, 180), 1)
        painter.setPen(border_pen)
        painter.drawPath(path)

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
        
        # Add signature label at the bottom of left panel
        self._signature_label = SignatureLabel(self._left_panel)
        left_layout.addWidget(self._signature_label)

    def _create_file_section(self, parent_layout):
        """Create file selection section with elegant design."""
        # File selection title
        file_title = SectionTitle("Selezione File")
        # Add folder icon to the title
        file_title.setStyleSheet(f"""
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
        
        # Create icon label
        icon_label = QtWidgets.QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setScaledContents(True)
        icon_label.setStyleSheet("background: transparent; border: none; margin: 2px 0 0 0; padding: 0;")
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Load folder icon
        try:
            import os
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "folder.png")
            if os.path.exists(icon_path):
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(icon_path)
                icon_label.setPixmap(pixmap.scaled(20, 20, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            pass
        
        # Create a container for title with icon
        title_container = QtWidgets.QWidget()
        title_container.setStyleSheet("background: transparent; border: none; margin: 0; padding: 0;")
        title_layout = QtWidgets.QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        title_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(file_title)
        title_layout.addStretch()
        
        parent_layout.addWidget(title_container)
        
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
        self._select_file_button = ModernButton("Seleziona File Excel", "primary", ICONS['excel'])
        
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
        controls_title = SectionTitle("Controlli")
        # Add controls icon to the title
        controls_title.setStyleSheet(f"""
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
        
        # Create icon label
        controls_icon_label = QtWidgets.QLabel()
        controls_icon_label.setFixedSize(20, 20)
        controls_icon_label.setScaledContents(True)
        controls_icon_label.setStyleSheet("background: transparent; border: none; margin: 2px 0 0 0; padding: 0;")
        controls_icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Load controls icon
        try:
            import os
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "controls.png")
            if os.path.exists(icon_path):
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(icon_path)
                controls_icon_label.setPixmap(pixmap.scaled(20, 20, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            pass
        
        # Create a container for title with icon
        controls_title_container = QtWidgets.QWidget()
        controls_title_container.setStyleSheet("background: transparent; border: none; margin: 0; padding: 0;")
        controls_title_layout = QtWidgets.QHBoxLayout(controls_title_container)
        controls_title_layout.setContentsMargins(0, 0, 0, 0)
        controls_title_layout.setSpacing(8)
        controls_title_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        
        controls_title_layout.addWidget(controls_icon_label)
        controls_title_layout.addWidget(controls_title)
        controls_title_layout.addStretch()
        
        parent_layout.addWidget(controls_title_container)
        
        # Create grid layout for 4 equal-sized buttons (2x2)
        button_grid = QtWidgets.QGridLayout()
        button_grid.setSpacing(8)  # Consistent spacing between all buttons
        button_grid.setContentsMargins(0, 0, 0, 0)
        
        # Start button with DHL yellow and plane icon
        self._start_button = ModernButton("Start", "dhl", ICONS['play'])
        
        # Stop button with DHL red
        self._stop_button = ModernButton("Stop", "dhl_red", ICONS['stop'])
        
        # Clear log button with QtAwesome icon
        self._clear_log_button = ModernButton("Pulisci", "secondary", ICONS['trash'])
        
        # Open NSIS button with QtAwesome icon
        self._open_nsis_button = ModernButton("NSIS", "secondary", ICONS['home'])  # Use home icon
        
        # Add buttons to grid (2x2 layout)
        button_grid.addWidget(self._start_button, 0, 0)      # Top-left
        button_grid.addWidget(self._stop_button, 0, 1)       # Top-right
        button_grid.addWidget(self._clear_log_button, 1, 0)  # Bottom-left
        button_grid.addWidget(self._open_nsis_button, 1, 1)  # Bottom-right
        
        parent_layout.addLayout(button_grid)

    def _create_statistics_section(self, parent_layout):
        """Create statistics section with QtAwesome icons."""
        # Statistics title with stati.gif icon
        stats_title_layout = QtWidgets.QHBoxLayout()
        stats_title_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        
        # Add stati.gif icon
        stati_icon_label = QtWidgets.QLabel()
        import os
        stati_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "stati.gif")
        if os.path.exists(stati_icon_path):
            from PyQt6.QtGui import QMovie
            movie = QMovie(stati_icon_path)
            movie.setScaledSize(QtCore.QSize(20, 20))
            stati_icon_label.setMovie(movie)
            movie.start()
        stati_icon_label.setFixedSize(20, 20)
        stati_icon_label.setStyleSheet("background: transparent; border: none; margin: 2px 0 0 0; padding: 0;")
        stati_icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        stats_title = SectionTitle("Statistiche")
        
        stats_title_layout.addWidget(stati_icon_label)
        stats_title_layout.addWidget(stats_title)
        parent_layout.addLayout(stats_title_layout)
        
        # Create compact statistics in a vertical list
        stats_layout = QtWidgets.QVBoxLayout()
        stats_layout.setSpacing(4)  # Increased spacing between items
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create statistics with QtAwesome icons
        statistic_configs = [
            (ICONS['statistics'], "Annullate", COLORS['accent_warning'], "Richieste annullate"),
            (ICONS['statistics'], "Aperte", COLORS['accent_secondary'], "Richieste aperte"),
            (ICONS['statistics'], "Chiuse", COLORS['accent_secondary'], "Richieste chiuse"),
            (ICONS['statistics'], "Lavorazione", COLORS['accent_warning'], "Richieste in lavorazione"),
            (ICONS['statistics'], "Inviate", COLORS['accent_info'], "Richieste inviate"),
            (ICONS['statistics'], "Eccezioni", COLORS['accent_error'], "Errori ed eccezioni")
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
        """Create central progress overlay."""
        # Create central progress overlay
        self._progress_overlay = CentralProgressOverlay(self._parent)
        
        # Create a placeholder widget (hidden) for the old progress section
        self._progress_container = QtWidgets.QWidget()
        self._progress_container.hide()
        parent_layout.addWidget(self._progress_container)
        
        # Ensure overlay is created but hidden initially
        self._progress_overlay.hide()

    def _create_web_area(self, parent_layout):
        """Create web view area with QtAwesome navigation controls and improved spacing."""
        # Web title
        web_title = SectionTitle("Browser NSIS")
        # Add chrome icon to the title
        web_title.setStyleSheet(f"""
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
        
        # Create icon label
        chrome_icon_label = QtWidgets.QLabel()
        chrome_icon_label.setFixedSize(20, 20)
        chrome_icon_label.setScaledContents(True)
        chrome_icon_label.setStyleSheet("background: transparent; border: none; margin: 2px 0 0 0; padding: 0;")
        chrome_icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Load chrome icon
        try:
            import os
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "chrome.png")
            if os.path.exists(icon_path):
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(icon_path)
                chrome_icon_label.setPixmap(pixmap.scaled(20, 20, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            pass
        
        # Create a container for title with icon
        chrome_title_container = QtWidgets.QWidget()
        chrome_title_container.setStyleSheet("background: transparent; border: none; margin: 0; padding: 0;")
        chrome_title_layout = QtWidgets.QHBoxLayout(chrome_title_container)
        chrome_title_layout.setContentsMargins(0, 0, 0, 0)
        chrome_title_layout.setSpacing(8)
        chrome_title_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        
        chrome_title_layout.addWidget(chrome_icon_label)
        chrome_title_layout.addWidget(web_title)
        chrome_title_layout.addStretch()
        
        parent_layout.addWidget(chrome_title_container)
        
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
        
        # Navigation buttons with custom icons
        self._back_btn = WebNavButton('left')  # Use custom left icon
        self._forward_btn = WebNavButton('right')  # Use custom right icon
        self._reload_btn = WebNavButton('reload')  # Use custom reload icon
        
        nav_layout.addWidget(self._back_btn)
        nav_layout.addWidget(self._forward_btn)
        nav_layout.addWidget(self._reload_btn)
        nav_layout.addStretch()
        
        # Log toggle button
        self._log_toggle_btn = WebNavButton(ICONS['eye_closed'])
        self._log_toggle_btn.setToolTip("Mostra Log Attività")
        self._log_toggle_btn.clicked.connect(self._toggle_log_visibility)
        # Set initial style for hidden state
        self._log_toggle_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
                font-weight: 500;
                min-width: 32px;
                min-height: 32px;
                max-width: 32px;
                max-height: 32px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        nav_layout.addWidget(self._log_toggle_btn)
        
        # Web view placeholder - simplified since styling is now handled by FluentWebContainer
        self._web_view_placeholder = QtWidgets.QWidget()
        self._web_view_placeholder.setObjectName("webViewPlaceholder")
        self._web_view_placeholder.setMinimumHeight(400)  # More space since log is hidden by default
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
        self._log_title = SectionTitle("📝 Log Attività")
        parent_layout.addWidget(self._log_title)
        
        # Log text area
        self._log_text = QtWidgets.QTextEdit()
        self._log_text.setObjectName("logText")
        self._log_text.setMinimumHeight(120)
        self._log_text.setMaximumHeight(150)
        
        # Initialize log as hidden by default
        self._log_visible = False
        self._log_title.hide()
        self._log_text.hide()
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
            self._select_file_button.clicked.connect(self._on_select_file_clicked)
        
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
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self._parent,
            "Seleziona File Excel",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self.fileSelected.emit(file_path)
    
    def _toggle_log_visibility(self):
        """Toggle log area visibility."""
        if hasattr(self, '_log_text'):
            if self._log_visible:
                # Hide log
                self._log_text.hide()
                if hasattr(self, '_log_title'):
                    self._log_title.hide()
                self._log_visible = False
                # Update button icon, tooltip and style
                icon = self._log_toggle_btn.get_qtawesome_icon(ICONS['eye_closed'])
                if icon:
                    self._log_toggle_btn.setIcon(icon)
                self._log_toggle_btn.setToolTip("Mostra Log Attività")
                self._log_toggle_btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(255, 255, 255, 0.15);
                        border: 1px solid rgba(255, 255, 255, 0.3);
                        border-radius: 8px;
                        color: rgba(255, 255, 255, 0.8);
                        font-size: 12px;
                        font-weight: 500;
                        min-width: 32px;
                        min-height: 32px;
                        max-width: 32px;
                        max-height: 32px;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 0.25);
                        border: 1px solid rgba(255, 255, 255, 0.4);
                    }
                    QPushButton:pressed {
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }
                """)
                # Give more space to web view
                if hasattr(self, '_web_view_placeholder'):
                    self._web_view_placeholder.setMinimumHeight(400)
            else:
                # Show log
                self._log_text.show()
                if hasattr(self, '_log_title'):
                    self._log_title.show()
                self._log_visible = True
                # Update button icon, tooltip and restore style
                icon = self._log_toggle_btn.get_qtawesome_icon(ICONS['eye_open'])
                if icon:
                    self._log_toggle_btn.setIcon(icon)
                self._log_toggle_btn.setToolTip("Nascondi Log Attività")
                self._log_toggle_btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        border-radius: 8px;
                        color: rgba(255, 255, 255, 0.8);
                        font-size: 12px;
                        font-weight: 500;
                        min-width: 32px;
                        min-height: 32px;
                        max-width: 32px;
                        max-height: 32px;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.3);
                    }
                    QPushButton:pressed {
                        background: rgba(255, 255, 255, 0.05);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }
                """)
                # Restore web view height
                if hasattr(self, '_web_view_placeholder'):
                    self._web_view_placeholder.setMinimumHeight(300)
    
    def set_file_path(self, file_path: str):
        """Show selected file in the elegant display area."""
        if self._file_name_label and self._file_display_area:
            # Show only filename, not full path
            filename = os.path.basename(file_path)
            
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
                self._start_button.setText("Start")
    
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
                self._start_button.setText("Start")
    
    def update_progress(self, current: int, maximum: int):
        """Update central progress overlay with animations."""
        if hasattr(self, '_progress_overlay'):
            self._progress_overlay.set_progress(current, maximum)
            
            # Show overlay when needed
            if not self._progress_overlay.isVisible():
                self._progress_overlay.show_overlay()
    

    
    def update_progress_status(self, status: str):
        """Update progress overlay status."""
        if hasattr(self, '_progress_overlay'):
            self._progress_overlay.set_status(status)
    
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
        # Extract the text part after emoji (e.g., "🟡 Annullate" -> "annullate")
        import re
        from PyQt6 import QtWidgets
        
        # Remove emoji and extract text, then convert to lowercase
        text_part = re.sub(r'[^\w\s]', '', badge_prefix).strip().lower()
        
        if text_part in self._statistic_widgets:
            self._statistic_widgets[text_part].set_count(count)
            # Force UI update
            QtWidgets.QApplication.processEvents()
        else:
            # Fallback: try to find by partial match
            for key in self._statistic_widgets.keys():
                if key in text_part or text_part in key:
                    self._statistic_widgets[key].set_count(count)
                    # Force UI update
                    QtWidgets.QApplication.processEvents()
                    break
    
    def reset_badges(self):
        """Reset all statistics to zero."""
        for statistic in self._statistic_widgets.values():
            statistic.set_count(0)
    
    def set_processing_state(self, is_processing: bool):
        """Set the UI to processing or idle state."""
        if self._start_button:
            self._start_button.setEnabled(not is_processing)
            self._start_button.setText("Elaborazione..." if is_processing else "Start")
        
        if self._stop_button:
            self._stop_button.setEnabled(is_processing)
        
        if self._select_file_button:
            self._select_file_button.setEnabled(not is_processing)
        
        if self._clear_log_button:
            self._clear_log_button.setEnabled(not is_processing)
        
        if self._open_nsis_button:
            self._open_nsis_button.setEnabled(not is_processing)
        
        # Show/hide progress overlay and manage animations
        if hasattr(self, '_progress_overlay'):
            if is_processing and not self._progress_overlay.isVisible():
                self._progress_overlay.show_overlay()
            elif not is_processing and self._progress_overlay.isVisible():
                # Stop animations and hide overlay
                self._progress_overlay.stop_animations()
                self._progress_overlay.hide_overlay()
        
        # Also manage web view and navigation controls visibility
        if is_processing:
            # These will be hidden by overlay
            pass
        else:
            # Ensure all web elements are visible when not processing
            if hasattr(self, '_web_view_placeholder'):
                self._web_view_placeholder.show()
            # Show navigation container (contains back, forward, reload buttons and log toggle)
            if hasattr(self, '_back_btn') and self._back_btn.parent():
                self._back_btn.parent().show()
            # Show web title (Browser NSIS)
            if hasattr(self, '_log_text') and self._log_text.parent():
                # Find the web title by looking at siblings
                parent_layout = self._log_text.parent().layout()
                if parent_layout:
                    for i in range(parent_layout.count()):
                        widget = parent_layout.itemAt(i).widget()
                        if widget and hasattr(widget, 'text') and "Browser NSIS" in widget.text():
                            widget.show()
                            break
    

    
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
            rounded_container = FluentWebContainer(web_view)
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
                QWebEngineView QWebEnginePage QWidget {
                    background: transparent;
                }
                QWebEngineView QWebEnginePage QWebEngineView {
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
        
        # Update signature label position (bottom-left)
        if self._signature_label:
            self._signature_label.setGeometry(
                10, 
                self._parent.height() - 30, 
                140, 
                20
            )
    
    def _handle_resize_event(self, event):
        """Handle window resize events."""
        self.update_layout_on_resize()
        event.accept() 