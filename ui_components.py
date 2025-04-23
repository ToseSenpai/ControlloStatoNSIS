# ui_components.py
# Contiene widget UI personalizzati

from PyQt6 import QtCore, QtGui, QtWidgets

class CustomProgressBar(QtWidgets.QProgressBar):
    """Barra di progresso personalizzata senza animazione aereo, con colori aggiornati."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Stile base per rimuovere chunk e impostare testo (nascosto)
        self.setStyleSheet("""
            QProgressBar {
                border: none; /* Gestito dallo stylesheet genitore ora */
                border-radius: 4px; /* Sarà sovrascritto da Luma */
                background-color: transparent; /* Sfondo gestito da stylesheet genitore */
                text-align: center;
                color: transparent; /* Nasconde testo originale % */
            }
            QProgressBar::chunk {
                 background-color: transparent; /* Chunk disegnato in paintEvent */
            }
        """)
        self.setTextVisible(False)
        # Imposta colori di default (verranno usati se non sovrascritti)
        self._chunkColor = QtGui.QColor("#6759FF") # Viola Luma primario di default
        self._borderColor = QtGui.QColor("#E5E7EB") # Grigio Luma 30
        self._backgroundColor = QtGui.QColor("#E5E7EB") # Grigio Luma 30 per sfondo

    # === METODO AGGIUNTO ===
    def setChunkColor(self, color: QtGui.QColor):
        """Imposta il colore usato per la parte riempita (chunk)."""
        if not hasattr(self, '_chunkColor') or self._chunkColor != color:
            self._chunkColor = color
            self.update() # Richiede un aggiornamento del disegno
    # === FINE METODO AGGIUNTO ===

    def paintEvent(self, event: QtGui.QPaintEvent):
        """Disegna la barra di progresso personalizzata."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        opt = QtWidgets.QStyleOptionProgressBar()
        self.initStyleOption(opt)
        # Usiamo l'area disponibile del widget come rettangolo principale
        # L'altezza è già definita dallo stylesheet generale (height: 8px)
        rect = self.rect()

        # Determina il raggio - potremmo prenderlo dallo stile o fissarlo
        # Usiamo 4px per far combaciare con altezza 8px e stile Luma
        borderRadius = min(rect.width() / 2, rect.height() / 2, 4) # Calcola raggio

        # Disegna sfondo arrotondato (parte "vuota")
        painter.setBrush(QtGui.QBrush(self._backgroundColor))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QtCore.QRectF(rect), borderRadius, borderRadius)

        # Disegna chunk (parte riempita)
        if self.maximum() > self.minimum():
            value_range = self.maximum() - self.minimum()
            current_value = max(self.minimum(), min(self.value(), self.maximum()))

            if value_range > 0 :
                chunkWidth = ((current_value - self.minimum()) / value_range) * rect.width()
                if chunkWidth > 0:
                    # Rettangolo per il chunk
                    chunkRect = QtCore.QRectF(rect.left(), rect.top(), chunkWidth, rect.height())

                    # Crea un path di clipping arrotondato
                    clipPath = QtGui.QPainterPath()
                    # Usiamo un rettangolo leggermente interno per il clip per sicurezza? No, usiamo rect
                    clipPath.addRoundedRect(QtCore.QRectF(rect), borderRadius, borderRadius)
                    painter.setClipPath(clipPath) # Applica clipping

                    # Disegna il chunk effettivo (verrà clippato)
                    painter.setBrush(QtGui.QBrush(self._chunkColor))
                    painter.setPen(QtCore.Qt.PenStyle.NoPen)
                    painter.drawRect(chunkRect)

                    # Rimuovi il clip per eventuali disegni futuri (buona pratica)
                    painter.setClipping(False)

# --- Classe SpinnerWidget (invariata) ---
class SpinnerWidget(QtWidgets.QWidget):
    """Widget che disegna uno spinner animato (arco rotante)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._updateAngle)
        self._timer.setInterval(20) # Aggiorna angolo ogni 20ms per fluidità
        self._spinnerColor = QtGui.QColor("#6759FF") # Colore Luma viola di default
        self.setFixedSize(20, 20) # Dimensione predefinita
        self.hide() # Nascosto all'inizio

    def _updateAngle(self):
        self._angle = (self._angle + 10) % 360
        self.update() # Richiede repaint

    def startAnimation(self):
        if not self._timer.isActive():
            self._angle = 0
            self._timer.start()
            self.show()

    def stopAnimation(self):
        if self._timer.isActive():
            self._timer.stop()
            self.hide()

    def setColor(self, color: QtGui.QColor):
        """Imposta il colore dello spinner."""
        self._spinnerColor = color
        if self.isVisible(): # Aggiorna subito solo se visibile
            self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        """Disegna l'arco rotante."""
        if not self._timer.isActive():
             return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        thickness = 2 # Spessore della linea dello spinner
        # Riduci leggermente il rettangolo per il disegno per non toccare i bordi
        drawRect = QtCore.QRectF(rect).adjusted(thickness, thickness, -thickness, -thickness)

        if drawRect.width() <= 0 or drawRect.height() <= 0:
            return # Non disegnare se l'area è troppo piccola

        pen = QtGui.QPen(self._spinnerColor)
        pen.setWidth(thickness)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap) # Estremità arrotondate
        painter.setPen(pen)

        # Disegna un arco. L'angolo iniziale ruota.
        # Gli angoli sono in 1/16 di grado.
        startAngle = self._angle * 16
        spanAngle = 120 * 16  # Disegna un arco di 120 gradi
        painter.drawArc(drawRect, startAngle, spanAngle)

    def sizeHint(self) -> QtCore.QSize:
        """Suggerisce una dimensione predefinita."""
        return QtCore.QSize(20, 20)