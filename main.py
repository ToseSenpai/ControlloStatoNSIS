# main.py
# Punto di ingresso con splash screen personalizzata.

import sys
import os
import traceback
from PyQt6 import QtWidgets, QtGui, QtCore

# Importa la classe App dal nuovo modulo
try:
    from main_window.app import App
except ImportError as e:
    print(f"ERRORE CRITICO: Impossibile importare 'App' da 'main_window.app': {e}", file=sys.stderr)
    app_temp = QtWidgets.QApplication.instance()
    if not app_temp: app_temp = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "Errore Import", f"Modulo App non trovato o errato:\n{e}\n\nControllare main_window/app.py.")
    sys.exit(1)

# Importa la splash screen personalizzata
try:
    from splash_screen_simple import show_splash_screen_simple
except ImportError as e:
    print(f"WARNING: Impossibile importare splash screen: {e}")
    show_splash_screen = None

# Funzione per caricare i font (invariata)
def load_fonts():
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    main_family_name = "Arial" # Fallback font
    ttc_file = "Inter.ttc"
    full_path = os.path.join(font_dir, ttc_file)
    if os.path.exists(full_path):
        font_id = QtGui.QFontDatabase.addApplicationFont(full_path)
        if font_id != -1:
            families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
            if families:
                main_family_name = families[0]
                print(f"INFO: Font TTC '{ttc_file}' caricato. Famiglia: '{main_family_name}'")
            else:
                print(f"WARNING: Font TTC '{ttc_file}' caricato ma nessuna famiglia trovata. Uso '{main_family_name}'.")
        else:
            print(f"WARNING: Impossibile caricare font TTC '{ttc_file}'. Uso '{main_family_name}'.")
    else:
        print(f"WARNING: File font TTC non trovato: '{ttc_file}' in '{font_dir}'. Uso '{main_family_name}'.")
    print(f"INFO: Famiglia font selezionata per UI: '{main_family_name}'")
    return main_family_name

# Verifica preliminare moduli WebEngine (invariata)
try:
    from PyQt6 import QtWebEngineWidgets, QtWebEngineCore, QtWebChannel
    _ = QtWebEngineWidgets.QWebEngineView
    _ = QtWebEngineCore.QWebEnginePage
    _ = QtWebChannel.QWebChannel
    print("INFO: Moduli QtWebEngine OK.")
except ImportError:
    print("ERRORE CRITICO: PyQt6-WebEngine non installato.", file=sys.stderr)
    print("Installa con: pip install PyQt6-WebEngine", file=sys.stderr)
    app_temp = QtWidgets.QApplication.instance()
    if not app_temp: app_temp = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "Errore Moduli", "PyQt6-WebEngine mancante.\nL'applicazione non può avviarsi.")
    sys.exit(1)

# --- Esecuzione Applicazione ---
if __name__ == '__main__':

    # Setup Windows-specific environment
    try:
        from windows_config import setup_windows_environment
        setup_windows_environment()
    except ImportError:
        pass  # Continue without Windows-specific setup
    
    # Imposta attributi DPI (invariato)
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        print("INFO: Abilitato AA_EnableHighDpiScaling.")
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        print("INFO: Abilitato AA_UseHighDpiPixmaps.")

    # Crea QApplication
    app = QtWidgets.QApplication(sys.argv)

    # Mostra splash screen personalizzata
    splash = None
    try:
        splash = show_splash_screen_simple()
        print("INFO: Splash screen semplice mostrata.")
    except Exception as e:
        print(f"WARNING: Errore nel mostrare splash screen semplice: {e}")
        splash = None

    # Funzione per caricare e mostrare l'app quando la splash screen è completata
    def load_and_show_main_app():
        try:
            print("INFO: Inizio caricamento applicazione principale...")
            ui_font_family_name = load_fonts()
            print("INFO: Creazione finestra principale applicazione...")
            # Crea l'istanza della classe App (da main_window.py)
            window = App(ui_font_family=ui_font_family_name)
            print("INFO: Finestra principale creata.")

            # Mostra la finestra principale
            window.show()
            print("INFO: Finestra principale mostrata.")
            
            if splash:
                splash.finish(window)
                print("INFO: Splash screen chiusa.")
        except Exception as e:
            print(f"ERRORE nel caricamento dell'app: {e}")
            if splash:
                splash.close()

    # Aspetta che la splash screen arrivi al 100% prima di caricare l'app
    if splash:
        # Connetti il segnale di completamento
        splash.splash_completed.connect(load_and_show_main_app)
    else:
        # Se non c'è splash screen, carica subito l'app
        load_and_show_main_app()

    try:
        print("INFO: Avvio event loop applicazione...")
        exit_code = app.exec()
        print(f"INFO: Applicazione terminata con codice {exit_code}.")
        sys.exit(exit_code)

    except Exception as e_main:
        print(f"ERRORE CRITICO nell'applicazione principale: {e_main}", file=sys.stderr)
        traceback.print_exc()
        # Nessun QSplashScreen Python da chiudere
        try:
            # Mostra un messaggio di errore all'utente
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            error_dialog.setWindowTitle("Errore Applicazione")
            error_dialog.setText(f"Si è verificato un errore critico:\n\n{e_main}")
            error_dialog.setDetailedText(traceback.format_exc())
            error_dialog.exec()
        except Exception as e_dialog:
            print(f"Errore nel mostrare il dialogo di errore finale: {e_dialog}")
        sys.exit(1)