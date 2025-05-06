# main.py
# Punto di ingresso dell'applicazione con splash screen ottimizzato.
# MODIFICATO: Rimosso time.sleep e semplificato caricamento splash.

import sys
import os
# 'time' non è più necessario qui se non per altre ragioni
import traceback
from PyQt6 import QtWidgets, QtGui, QtCore

# --- Importa la classe App (presumibilmente già modificata con import differiti) ---
try:
    # Assicurati che main_window contenga la classe App aggiornata
    from main_window import App
except ImportError as e:
    print(f"ERRORE CRITICO: Impossibile importare 'App' da 'main_window': {e}", file=sys.stderr)
    # Tenta di mostrare un messaggio di errore anche se l'app principale fallisce
    app_temp = QtWidgets.QApplication.instance()
    if not app_temp: app_temp = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "Errore Import", f"Modulo App non trovato o errato:\n{e}\n\nControllare main_window.py.")
    sys.exit(1)

# --- Funzione per caricare i font ---
# (Questa funzione rimane invariata, assumendo che tu voglia ancora caricare i font)
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

# --- Verifica preliminare moduli WebEngine ---
# (Questo controllo è importante e rimane invariato)
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

    # Imposta attributi DPI (invariato)
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        print("INFO: Abilitato AA_EnableHighDpiScaling.")
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        print("INFO: Abilitato AA_UseHighDpiPixmaps.")

    # Crea QApplication
    app = QtWidgets.QApplication(sys.argv)

    # --- Mostra lo Splash Screen SEMPLIFICATO (da immagine statica) ---
    splash = None
    try:
        # Assicurati che questo nome file esista e sia nel .spec
        # Potrebbe essere 'splash.png' o 'splash.gif' a seconda di cosa hai scelto
        image_filename = "splash.png"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, image_filename)

        print(f"INFO: Controllo splash image: {image_path}")

        if os.path.exists(image_path):
            pixmap = QtGui.QPixmap(image_path) # Carica direttamente

            if not pixmap.isNull():
                splash = QtWidgets.QSplashScreen(pixmap)
                # splash.setMask(pixmap.mask()) # Opzionale per trasparenza
                splash.show()
                print(f"INFO: Splash screen statico ('{image_filename}') mostrato.")
                app.processEvents() # Permetti allo splash di apparire subito
            else:
                print(f"WARNING: Impossibile caricare QPixmap da '{image_path}'.")
        else:
            print(f"WARNING: File immagine splash statico non trovato: '{image_path}'.")

    except Exception as e_splash:
        print(f"WARNING: Errore durante la creazione dello splash screen: {e_splash}")
        traceback.print_exc()
        splash = None
    # --- Fine Blocco Splash Semplificato ---

    # --- Carica Font e Crea Finestra Principale ---
    try:
        ui_font_family_name = load_fonts()
        print("INFO: Creazione finestra principale applicazione...")
        window = App(ui_font_family=ui_font_family_name) # Usa la classe App da main_window.py
        print("INFO: Finestra principale creata.")
        window.show()
        print("INFO: Finestra principale mostrata.")

        # NESSUN time.sleep() qui!

        # Chiudi lo splash screen non appena la finestra principale è pronta
        if splash:
            print("INFO: Chiusura splash screen...")
            splash.finish(window)
            print("INFO: Splash screen chiuso.")
        else:
             # Se non c'era splash, processa eventi iniziali comunque
             app.processEvents()

        print("INFO: Avvio event loop applicazione...")
        exit_code = app.exec()
        print(f"INFO: Applicazione terminata con codice {exit_code}.")
        sys.exit(exit_code)

    except Exception as e_main:
        print(f"ERRORE CRITICO nell'applicazione principale: {e_main}", file=sys.stderr)
        traceback.print_exc()
        # Tenta di chiudere lo splash se ancora aperto
        if splash and not splash.isHidden():
            splash.close()
        # Tenta di mostrare un dialogo di errore
        try:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            error_dialog.setWindowTitle("Errore Applicazione")
            error_dialog.setText(f"Si è verificato un errore critico:\n\n{e_main}")
            error_dialog.setDetailedText(traceback.format_exc())
            error_dialog.exec()
        except Exception as e_dialog:
            print(f"Errore nel mostrare il dialogo di errore finale: {e_dialog}")
        sys.exit(1)