#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script per barra di progresso corretta con colori visibili
"""

import sys
from PyQt6 import QtWidgets, QtCore, QtGui

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
        
        # Progress info label with modern styling - DARK TEXT
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
            gif_path = os.path.join(os.path.dirname(__file__), "icons", "loading.gif")
            if os.path.exists(gif_path):
                from PyQt6.QtGui import QMovie
                self._movie = QMovie(gif_path)
                self._movie.setScaledSize(QtCore.QSize(24, 24))
                self._loading_gif.setMovie(self._movie)
                self._movie.start()
        except Exception as e:
            print(f"Errore caricamento GIF: {e}")
        
        # Title text - DARK TEXT
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
        
        # Status text - DARK TEXT
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
        
        # Set up the glassmorphism background - LIGHT BACKGROUND
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

class TestWindow(QtWidgets.QWidget):
    """Test window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Barra di Progresso Corretta")
        self.setFixedSize(500, 300)
        
        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QtWidgets.QLabel("Test Barra di Progresso Corretta - Colori Visibili")
        title.setStyleSheet("""
            QLabel {
                color: #3B82F6;
                font-size: 16px;
                font-weight: 700;
                text-align: center;
            }
        """)
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Progress overlay
        self._progress_overlay = CentralProgressOverlay()
        
        # Control buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self._start_button = QtWidgets.QPushButton("Avvia Test")
        self._start_button.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563EB;
            }
            QPushButton:pressed {
                background: #1D4ED8;
            }
        """)
        self._start_button.clicked.connect(self._start_test)
        
        self._reset_button = QtWidgets.QPushButton("Reset")
        self._reset_button.setStyleSheet("""
            QPushButton {
                background: #6B7280;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #4B5563;
            }
            QPushButton:pressed {
                background: #374151;
            }
        """)
        self._reset_button.clicked.connect(self._reset_test)
        
        button_layout.addWidget(self._start_button)
        button_layout.addWidget(self._reset_button)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self._progress_overlay)
        layout.addLayout(button_layout)
        
        # Timer for progress simulation
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._update_progress)
        self._current_progress = 0
        self._max_progress = 100
        
        # Set initial progress
        self._progress_overlay.set_progress(0, 100)
        self._progress_overlay.set_status("Pronto per il test")
    
    def _start_test(self):
        """Start the progress test."""
        self._current_progress = 0
        self._progress_overlay.set_progress(0, 100)
        self._progress_overlay.set_status("Test in corso...")
        self._progress_overlay.show_overlay()
        self._timer.start(50)  # Update every 50ms for smoother animation
        self._start_button.setEnabled(False)
    
    def _reset_test(self):
        """Reset the progress test."""
        self._timer.stop()
        self._current_progress = 0
        self._progress_overlay.set_progress(0, 100)
        self._progress_overlay.set_status("Pronto per il test")
        self._progress_overlay.hide_overlay()
        self._start_button.setEnabled(True)
    
    def _update_progress(self):
        """Update progress value."""
        self._current_progress += 1
        if self._current_progress <= self._max_progress:
            self._progress_overlay.set_progress(self._current_progress, self._max_progress)
            self._progress_overlay.set_status(f"Elaborazione... {self._current_progress}%")
        else:
            self._timer.stop()
            self._progress_overlay.set_status("Test completato!")
            self._start_button.setEnabled(True)

def main():
    """Main function."""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 