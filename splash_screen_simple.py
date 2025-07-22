import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont
from PyQt6.QtWidgets import QApplication, QSplashScreen

class SimpleSplashScreen(QSplashScreen):
    """Splash screen semplice con barra di caricamento pulita."""
    
    # Segnale quando la splash screen è completata
    splash_completed = QtCore.pyqtSignal()
    
    def __init__(self, pixmap=None):
        super().__init__(pixmap)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Dimensioni della splash screen
        self.setFixedSize(400, 250)
        
        # Colori e stili (coerenti con l'applicazione)
        self.colors = {
            'background': QColor(255, 255, 255),  # Bianco puro come l'app
            'accent': QColor(255, 255, 0),        # Giallo standard (#FFFF00)
            'text': QColor(33, 37, 41),           # Dark text (#212529)
            'progress_bg': QColor(248, 249, 250), # Light gray (#f8f9fa)
            'progress_fill': QColor(255, 255, 0), # Giallo standard
            'signature': QColor(0, 0, 0)          # Black text (#000000)
        }
        
        # Testo di caricamento
        self.loading_text = "Caricamento applicazione..."
        self.current_step = 0
        self.loading_steps = [
            "Inizializzazione...",
            "Caricamento moduli...",
            "Preparazione interfaccia...",
            "Configurazione WebEngine...",
            "Caricamento font...",
            "Preparazione UI...",
            "Avvio completato!"
        ]
        
        # Timer per aggiornare il testo
        self.text_timer = QTimer()
        self.text_timer.timeout.connect(self.update_loading_text)
        self.text_timer.start(1500)  # Cambia testo ogni 1.5 secondi
        
        # Progress bar animation (inizializzata ma non avviata)
        self._progress_value = 0
        self.progress_animation = QPropertyAnimation(self, b"progress_value")
        self.progress_animation.setDuration(5000)  # 5 secondi minimi garantiti
        self.progress_animation.setStartValue(0)
        self.progress_animation.setEndValue(100)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Flag per indicare se le animazioni sono state avviate
        self._animations_started = False
    
    def get_progress_value(self):
        return self._progress_value
    
    def set_progress_value(self, value):
        self._progress_value = value
        self.update()
        
        # Emetti il segnale quando arriva al 100%
        if value >= 100:
            self.splash_completed.emit()
    
    # Registra le proprietà per le animazioni
    progress_value = QtCore.pyqtProperty(float, get_progress_value, set_progress_value)
    
    def start_animations(self):
        """Avvia le animazioni quando la splash screen è visibile."""
        if not self._animations_started:
            self._animations_started = True
            self.progress_animation.start()
    
    def update_loading_text(self):
        """Aggiorna il testo di caricamento."""
        self.current_step = min(self.current_step + 1, len(self.loading_steps) - 1)
        self.loading_text = self.loading_steps[self.current_step]
        self.update()
    

    
    def paintEvent(self, event):
        """Disegna la splash screen semplice e pulita."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Sfondo bianco puro (come l'applicazione)
        painter.fillRect(self.rect(), self.colors['background'])
        
        # Testo del titolo
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.setPen(self.colors['text'])
        
        title_text = "Controllo Stato NSIS"
        title_rect = QtCore.QRect(0, 80, self.width(), 30)
        painter.drawText(title_rect, QtCore.Qt.AlignmentFlag.AlignCenter, title_text)
        
        # Testo di caricamento
        loading_font = QFont()
        loading_font.setPointSize(11)
        painter.setFont(loading_font)
        painter.setPen(QColor(108, 117, 125))  # Gray text
        
        loading_rect = QtCore.QRect(0, title_rect.bottom() + 20, self.width(), 20)
        painter.drawText(loading_rect, QtCore.Qt.AlignmentFlag.AlignCenter, self.loading_text)
        
        # Barra di progresso
        progress_rect = QtCore.QRect(50, loading_rect.bottom() + 30, self.width() - 100, 10)
        
        # Sfondo barra
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self.colors['progress_bg'])
        painter.drawRoundedRect(progress_rect, 5, 5)
        
        # Riempimento barra
        fill_width = int((progress_rect.width() * self._progress_value) / 100)
        if fill_width > 0:
            fill_rect = QtCore.QRect(progress_rect.x(), progress_rect.y(), fill_width, progress_rect.height())
            
            # Gradiente per il riempimento
            fill_gradient = QLinearGradient(fill_rect.x(), fill_rect.y(), fill_rect.x() + fill_rect.width(), fill_rect.y())
            fill_gradient.setColorAt(0, self.colors['progress_fill'])
            fill_gradient.setColorAt(1, QColor(255, 255, 100))  # Giallo standard più chiaro
            
            painter.setBrush(fill_gradient)
            painter.drawRoundedRect(fill_rect, 5, 5)
        
        # Percentuale
        percent_font = QFont()
        percent_font.setPointSize(10)
        painter.setFont(percent_font)
        painter.setPen(self.colors['accent'])
        
        percent_text = f"{int(self._progress_value)}%"
        percent_rect = QtCore.QRect(0, progress_rect.bottom() + 10, self.width(), 15)
        painter.drawText(percent_rect, QtCore.Qt.AlignmentFlag.AlignCenter, percent_text)
        
        # Signature in basso
        signature_font = QFont()
        signature_font.setPointSize(8)
        painter.setFont(signature_font)
        painter.setPen(self.colors['signature'])
        
        signature_text = "Made with ❤️ by ST"
        signature_rect = QtCore.QRect(0, percent_rect.bottom() + 15, self.width(), 20)
        painter.drawText(signature_rect, QtCore.Qt.AlignmentFlag.AlignCenter, signature_text)

def show_splash_screen_simple():
    """Mostra la splash screen semplice e restituisce l'istanza."""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    splash = SimpleSplashScreen()
    splash.show()
    
    # Centra la splash screen
    screen = app.primaryScreen().geometry()
    splash_rect = splash.geometry()
    x = (screen.width() - splash_rect.width()) // 2
    y = (screen.height() - splash_rect.height()) // 2
    splash.move(x, y)
    
    # Avvia le animazioni dopo un breve delay
    QTimer.singleShot(200, splash.start_animations)
    
    return splash

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = show_splash_screen_simple()
    
    # Simula il caricamento dell'applicazione
    def close_splash():
        splash.close()
        app.quit()
    
    # Chiudi dopo 6 secondi per il test
    QTimer.singleShot(6000, close_splash)
    
    sys.exit(app.exec()) 