# ui_components.py
# Contiene widget UI personalizzati

from PyQt6 import QtCore, QtGui, QtWidgets

class CustomProgressBar(QtWidgets.QProgressBar):
    """Barra di progresso personalizzata senza animazione aereo, con colori aggiornati."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Stile base per rimuovere chunk di default e impostare testo (nascosto)
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0; /* Bordo grigio chiaro (come pulsanti non primari) */
                border-radius: 5px;
                background-color: #F9F9F9; /* Sfondo grigio chiarissimo (come pulsanti non primari) */
                text-align: center;
                color: #333333; /* Colore testo % (nascosto) */
            }
            QProgressBar::chunk {
                 background-color: transparent; /* Deve essere trasparente, lo disegniamo noi */
            }
        """)
        self.setTextVisible(False)

    def paintEvent(self, event: QtGui.QPaintEvent):
        """Disegna la barra di progresso personalizzata con colori aggiornati."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        # Raggio angoli coerente con i pulsanti
        borderRadius = 4

        # Colori aggiornati (ispirati al tema)
        backgroundColor = QtGui.QColor("#F9F9F9") # Sfondo grigio chiarissimo
        borderColor = QtGui.QColor("#E0E0E0") # Bordo grigio chiaro
        chunkColor = QtGui.QColor("#0078D4") # Blu primario Fluent

        # Disegna sfondo arrotondato e bordo
        painter.setBrush(QtGui.QBrush(backgroundColor))
        painter.setPen(QtGui.QPen(borderColor, 1))
        # Usiamo drawRoundedRect direttamente sul painter per sfondo/bordo
        # adjusted serve per disegnare il bordo correttamente all'interno del rettangolo
        painter.drawRoundedRect(QtCore.QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), borderRadius, borderRadius)

        # Disegna chunk (parte riempita)
        if self.maximum() > self.minimum():
            value_range = self.maximum() - self.minimum()
            # Assicura che il valore sia nel range valido
            current_value = max(self.minimum(), min(self.value(), self.maximum()))

            # Calcola la larghezza proporzionale del chunk
            # Sottraiamo 2 per tenere conto del bordo (1px per lato)
            barWidth = rect.width() - 2
            chunkWidth = 0
            if value_range > 0 :
                chunkWidth = int(((current_value - self.minimum()) / value_range) * barWidth)

            if chunkWidth > 0:
                # Rettangolo interno per il chunk, spostato di 1px dal bordo
                chunkFillRect = QtCore.QRectF(rect.left() + 1, rect.top() + 1, chunkWidth, rect.height() - 2)

                # Prepariamo un path arrotondato per clippare il disegno del chunk
                # Questo assicura che il riempimento rispetti gli angoli arrotondati del bordo
                clipPath = QtGui.QPainterPath()
                # Usiamo un raggio leggermente inferiore per il clip interno
                clipRect = QtCore.QRectF(rect.left() + 1, rect.top() + 1, rect.width() - 2, rect.height() - 2)
                clipPath.addRoundedRect(clipRect, borderRadius -1 if borderRadius > 0 else 0, borderRadius -1 if borderRadius > 0 else 0)

                painter.save() # Salva lo stato del painter (incluso il non-clipping)
                # Applica il clipping path: tutto ciò che verrà disegnato ora sarà confinato dentro questo path
                painter.setClipPath(clipPath)

                # Disegna il chunk con il colore primario
                painter.setBrush(QtGui.QBrush(chunkColor))
                painter.setPen(QtCore.Qt.PenStyle.NoPen) # Nessun bordo per il chunk stesso
                # Disegna un rettangolo semplice; sarà clippato automaticamente nella forma arrotondata
                painter.drawRect(chunkFillRect)

                painter.restore() # Rimuove il clipping e ripristina lo stato precedente del painter


# --- NUOVO WIDGET SPINNER ---
class SpinnerWidget(QtWidgets.QWidget):
    """Widget che disegna uno spinner animato (arco rotante)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._updateAngle)
        self._timer.setInterval(20) # Aggiorna angolo ogni 20ms per fluidità
        self._spinnerColor = QtGui.QColor("#0078D4") # Blu primario
        self.setFixedSize(20, 20) # Imposta una dimensione fissa (puoi renderla configurabile)
        self.hide() # Nascosto all'inizio

    def _updateAngle(self):
        """Aggiorna l'angolo di rotazione e richiede un repaint."""
        self._angle = (self._angle + 10) % 360 # Incrementa l'angolo
        self.update() # Schedula un repaint

    def startAnimation(self):
        """Avvia l'animazione dello spinner."""
        if not self._timer.isActive():
            self._angle = 0
            self._timer.start()
            self.show()

    def stopAnimation(self):
        """Ferma l'animazione dello spinner."""
        if self._timer.isActive():
            self._timer.stop()
            self.hide()

    def setColor(self, color: QtGui.QColor):
        """Imposta il colore dello spinner."""
        self._spinnerColor = color
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        """Disegna l'arco rotante."""
        if not self._timer.isActive(): # Non disegnare se non attivo
             return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        # Riduci leggermente il rettangolo per non toccare i bordi
        drawRect = QtCore.QRectF(rect).adjusted(2, 2, -2, -2)

        pen = QtGui.QPen(self._spinnerColor)
        pen.setWidth(2) # Spessore della linea dell'arco
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