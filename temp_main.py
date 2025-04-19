# main.py
# Entry point for the application

import sys
from PyQt6 import QtWidgets
from main_window import App

# Verifica preliminare moduli WebEngine
try:
    from PyQt6 import QtWebEngineWidgets, QtWebEngineCore, QtWebChannel
    _ = QtWebEngineWidgets.QWebEngineView
    _ = QtWebEngineCore.QWebEnginePage
    _ = QtWebChannel.QWebChannel
except ImportError:
    raise ImportError(
        "I moduli PyQt6 WebEngine e WebChannel non sono installati.\n"
        "Installa eseguendo: pip install PyQt6 PyQt6-WebEngine"
    )

# --- Esecuzione Applicazione ---
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())