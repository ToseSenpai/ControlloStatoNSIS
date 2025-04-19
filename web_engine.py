# web_engine.py
# Contains web engine related classes for the application

from PyQt6 import QtCore, QtWebEngineCore, QtWebChannel

class WebEnginePage(QtWebEngineCore.QWebEnginePage):
    """
    Pagina personalizzata per gestire richieste di navigazione e creazione finestre.
    Tenta di forzare l'apertura di tutti i link nella vista principale.
    """
    def __init__(self, parent=None):
         super().__init__(parent)
         print("WebEnginePage personalizzata inizializzata.")

    def acceptNavigationRequest(self, url: QtCore.QUrl, _type: QtWebEngineCore.QWebEnginePage.NavigationType, isMainFrame: bool):
        print(f"Richiesta acceptNavigationRequest: URL={url.toString()}, Tipo={_type}, MainFrame={isMainFrame}")
        print("Navigazione accettata in acceptNavigationRequest.")
        return True

    def createWindow(self, windowType: QtWebEngineCore.QWebEnginePage.WebWindowType):
        """
        Gestisce le richieste dalla pagina web per aprire una nuova finestra.
        Restituisce la pagina corrente ('self') sperando che Qt carichi
        l'URL richiesto in questa stessa pagina.
        """
        print(f"Richiesta createWindow: Tipo={windowType}. Tento di riutilizzare la pagina corrente (restituisco self).")
        return self

class JSBridge(QtCore.QObject):
    """Oggetto per la comunicazione tra Python e JavaScript via QWebChannel."""
    def __init__(self):
        super().__init__()
        self.result = None
        self._loop = None

    @QtCore.pyqtSlot(object)
    def receive(self, data):
        """Slot chiamato da JavaScript per inviare dati a Python."""
        self.result = data
        if self._loop and self._loop.isRunning():
            self._loop.quit()

    def evaluate(self, page, script):
        """Esegue uno script JS e attende il risultato tramite il bridge."""
        self.result = None
        loop = QtCore.QEventLoop()
        self._loop = loop
        if page:
            # Esegue lo script JS, il risultato verrà inviato a self.receive
            page.runJavaScript(script, self.receive)
            # Avvia un loop di eventi locale che attende fino a loop.quit()
            loop.exec()
        else:
            print("Errore: Tentativo di eseguire JS su una pagina non valida.")
        self._loop = None # Rilascia il riferimento al loop
        return self.result