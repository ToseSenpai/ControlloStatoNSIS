# main.py
# Entry point for the application

import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore # Assicurati QtCore e QtGui siano importati

# --- INIZIO BLOCCO CARICAMENTO FONT AGGIORNATO PER TTC ---
def load_fonts():
    """Carica il font Inter dal file TrueType Collection (TTC)."""
    font_dir = os.path.join(os.path.dirname(__file__), "fonts") # Cartella 'fonts'
    main_family_name = "Arial" # Fallback
    ttc_file = "Inter.ttc" # Nome del file TTC
    full_path = os.path.join(font_dir, ttc_file)

    if os.path.exists(full_path):
        print(f"INFO: Tentativo di caricare il font TTC: {full_path}")
        # Usa il metodo statico addApplicationFont
        font_id = QtGui.QFontDatabase.addApplicationFont(full_path)

        if font_id != -1:
            # Ottieni tutte le famiglie caricate da QUESTO file
            families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
            if families:
                main_family_name = families[0] # Prendi la prima famiglia ("Inter")
                print(f"INFO: Font TTC '{ttc_file}' caricato. Famiglia Principale: '{main_family_name}'")
                # Opzionale: Verifica stili caricati
                # styles = QtGui.QFontDatabase().styles(main_family_name)
                # print(f"INFO: Stili disponibili per '{main_family_name}': {styles}")
            else:
                 print(f"WARNING: Font TTC '{ttc_file}' caricato (ID: {font_id}) ma nessuna famiglia trovata.")
                 main_family_name = "Arial" # Torna al fallback se non trova famiglie
        else:
            # Se font_id è -1, il caricamento è fallito
            print(f"WARNING: Impossibile caricare font TTC '{ttc_file}'. Verificare file.")
            main_family_name = "Arial" # Fallback
    else:
        print(f"WARNING: File font TTC non trovato: '{ttc_file}' in '{font_dir}'")
        main_family_name = "Arial" # Fallback se il file non esiste

    print(f"INFO: Famiglia font da usare per UI: '{main_family_name}'")
    return main_family_name

# --- FINE BLOCCO CARICAMENTO FONT ---

# Verifica preliminare moduli WebEngine
try:
    from PyQt6 import QtWebEngineWidgets, QtWebEngineCore, QtWebChannel
    _ = QtWebEngineWidgets.QWebEngineView
    _ = QtWebEngineCore.QWebEnginePage
    _ = QtWebChannel.QWebChannel
    print("INFO: Moduli QtWebEngine verificati.")
except ImportError:
    # Mostra un errore più user-friendly prima di sollevare l'eccezione tecnica
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("Errore Moduli Mancanti")
    msg_box.setText(
        "I moduli PyQt6 WebEngine non sono installati.\n\n"
        "Per favore, installali eseguendo nel terminale:\n"
        "pip install PyQt6-WebEngine"
    )
    msg_box.exec()
    # Solleva l'eccezione per terminare se non è interattivo
    raise ImportError(
        "PyQt6-WebEngine non trovato. Vedi messaggio GUI."
    )

# Importa la classe principale DOPO il setup dei font
from main_window import App

# --- Esecuzione Applicazione ---
if __name__ == '__main__':

    # Imposta attributi per rendering alta DPI
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        print("INFO: Abilitato AA_EnableHighDpiScaling.")
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        print("INFO: Abilitato AA_UseHighDpiPixmaps.")

    # Crea QApplication
    app = QtWidgets.QApplication(sys.argv)

    # Carica i font e ottieni il nome della famiglia principale ("Inter" o fallback)
    ui_font_family_name = load_fonts()

    # Crea la finestra principale passando il nome della famiglia font
    try:
        window = App(ui_font_family=ui_font_family_name)
        window.show()
        # Avvia il ciclo eventi dell'applicazione
        sys.exit(app.exec())
    except Exception as e:
        # Cattura eccezioni durante l'inizializzazione della finestra o l'esecuzione
        print(f"ERRORE CRITICO nell'applicazione: {e}", file=sys.stderr)
        # Prova a mostrare un messaggio di errore se possibile
        try:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            error_dialog.setWindowTitle("Errore Applicazione")
            error_dialog.setText(f"Si è verificato un errore imprevisto:\n\n{e}\n\nL'applicazione verrà chiusa.")
            # Potrebbe non funzionare se QApplication ha problemi
            error_dialog.exec()
        except:
            pass # Ignora errori nel mostrare il dialogo di errore
        sys.exit(1) # Esci con codice di errore