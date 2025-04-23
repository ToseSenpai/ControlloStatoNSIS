# main.py
# Entry point for the application with Animated GIF SplashScreen and correct paths

import sys
import os
import time # Solo per eventuali debug con pause
import traceback # Per gestione errori dettagliata
from PyQt6 import QtWidgets, QtGui, QtCore

# --- INIZIO AnimatedSplashScreen Class ---
class AnimatedSplashScreen(QtWidgets.QWidget):
    """Una finestra splash semplice che mostra una GIF animata."""
    def __init__(self, gif_path):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowType.SplashScreen |
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        self.movie = QtGui.QMovie(gif_path)
        if self.movie.isValid():
            self.label.setMovie(self.movie)
            self.movie.start()
            print(f"INFO: GIF Splash '{os.path.basename(gif_path)}' caricata e avviata.")
        else:
            error_msg = f"Errore caricamento GIF: '{os.path.basename(gif_path)}'."
            self.label.setText(error_msg); self.label.setStyleSheet("color: red; font-weight: bold;")
            print(f"WARNING: {error_msg.replace('/n', ' ')}")

    def center_on_screen(self):
        """Centra la finestra splash sullo schermo primario."""
        try:
             primary_screen = QtWidgets.QApplication.primaryScreen()
             if primary_screen:
                 screen_geometry = primary_screen.availableGeometry()
                 splash_geometry = self.frameGeometry()
                 self.move( screen_geometry.left() + (screen_geometry.width() - splash_geometry.width()) // 2, screen_geometry.top() + (screen_geometry.height() - splash_geometry.height()) // 2 )
             else: print("WARNING: Impossibile ottenere schermo primario.")
        except Exception as e_screen: print(f"WARNING: Eccezione centramento splash: {e_screen}")

    def closeEvent(self, event):
        """Ferma il QMovie quando la finestra viene chiusa."""
        if hasattr(self, 'movie') and self.movie and self.movie.state() == QtGui.QMovie.MovieState.Running:
            self.movie.stop(); print("INFO: Animazione GIF splash fermata.")
        event.accept()
# --- FINE AnimatedSplashScreen Class ---

# Inserisci QUESTA versione corretta della funzione load_fonts in main.py

def load_fonts():
    """Carica il font Inter dal file TrueType Collection (TTC) usando metodi statici."""
    font_dir = os.path.join(os.path.dirname(__file__), "fonts") # Cartella 'fonts'
    main_family_name = "Arial" # Fallback predefinito
    ttc_file = "Inter.ttc" # Nome del file TTC
    full_path = os.path.join(font_dir, ttc_file)

    # Livello 1: Controlla se il file esiste
    if os.path.exists(full_path):
        print(f"INFO: Tentativo di caricare il font TTC: {full_path}")
        font_id = QtGui.QFontDatabase.addApplicationFont(full_path)

        # Livello 2: Controlla se il caricamento è riuscito (font_id valido)
        if font_id != -1:
            # Livello 3: Controlla se sono state trovate famiglie
            families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
            if families:
                # Caricato con successo e trovate famiglie
                main_family_name = families[0] # Usa la prima famiglia trovata
                print(f"INFO: Font TTC '{ttc_file}' caricato. Famiglia: '{main_family_name}'")
            # Else corrispondente a 'if families:'
            else:
                # Caricato (font_id valido) ma nessuna famiglia associata? Strano.
                print(f"WARNING: Font TTC '{ttc_file}' caricato (ID: {font_id}) ma nessuna famiglia trovata.")
                main_family_name = "Arial" # Torna al fallback per sicurezza
        # Else corrispondente a 'if font_id != -1:' (Caricamento fallito)
        else:
            print(f"WARNING: Impossibile caricare font TTC '{ttc_file}'. File non valido o corrotto? ID={font_id}.")
            main_family_name = "Arial" # Fallback
    # Else corrispondente a 'if os.path.exists(full_path):' (File non trovato)
    else:
        print(f"WARNING: File font TTC non trovato: '{ttc_file}' in '{font_dir}'")
        main_family_name = "Arial" # Fallback

    # Stampa finale della famiglia che verrà usata
    print(f"INFO: Famiglia font selezionata per UI: '{main_family_name}'")
    return main_family_name

# --- Verifica preliminare moduli WebEngine ---
try:
    from PyQt6 import QtWebEngineWidgets, QtWebEngineCore, QtWebChannel
    _ = QtWebEngineWidgets.QWebEngineView; _ = QtWebEngineCore.QWebEnginePage; _ = QtWebChannel.QWebChannel
    print("INFO: Moduli QtWebEngine OK.")
except ImportError:
    print("ERRORE CRITICO: PyQt6-WebEngine non installato.", file=sys.stderr); print("Installa con: pip install PyQt6-WebEngine", file=sys.stderr)
    app_temp = QtWidgets.QApplication.instance();
    if not app_temp: app_temp = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None,"Errore Moduli","PyQt6-WebEngine mancante."); sys.exit(1)
# --- Fine Verifica WebEngine ---

# --- Importa la classe App ---
try:
    from main_window import App
except ImportError as e:
    print(f"ERRORE CRITICO: Impossibile importare 'App' da 'main_window': {e}", file=sys.stderr)
    app_temp = QtWidgets.QApplication.instance();
    if not app_temp: app_temp = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None,"Errore Import", f"Modulo App non trovato:\n{e}"); sys.exit(1)
# --- Fine Import App ---

# --- Esecuzione Applicazione ---
if __name__ == '__main__':

    # Imposta attributi per rendering alta DPI
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'): QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True); print("INFO: Abilitato AA_EnableHighDpiScaling.")
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'): QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True); print("INFO: Abilitato AA_UseHighDpiPixmaps.")

    # Crea QApplication
    app = QtWidgets.QApplication(sys.argv)

    # --- Mostra lo Splash Screen ANIMATO ---
    splash = None
    try:
        # Percorso GIF corretto (nella stessa cartella di main.py)
        gif_filename = "splash.gif"
        gif_path = gif_filename # Percorso relativo semplice

        if os.path.exists(gif_path):
            splash = AnimatedSplashScreen(gif_path) # Passa percorso corretto
            if splash.movie.isValid():
                 splash.adjustSize()
                 splash.center_on_screen()
                 splash.show()
                 app.processEvents() # Forza disegno iniziale
                 print("INFO: Animated GIF Splash mostrato.")
            else:
                 print(f"WARNING: GIF in '{gif_path}' non valida, splash non mostrato.")
                 splash = None # Resetta splash se gif non valida
        else:
            print(f"WARNING: File GIF splash non trovato in: '{gif_path}'.")

    except Exception as e_splash:
        print(f"WARNING: Errore creazione AnimatedSplashScreen: {e_splash}")
        splash = None
    # --- Fine Splash Screen Animato ---

    # --- Carica Font e Crea Finestra Principale ---
    try:
        # Carica fonts
        ui_font_family_name = load_fonts()

        # Crea finestra principale
        window = App(ui_font_family=ui_font_family_name)

        # === MOSTRA LA FINESTRA PRINCIPALE PRIMA DI CHIUDERE LO SPLASH ===
        window.show()
        app.processEvents() # Aiuta a far partire il rendering

        # === ORA CHIUDI LO SPLASH SCREEN ===
        if splash:
            splash.close() # Chiude la finestra dello splash
            print("INFO: Animated Splash chiuso.")
            # Il timer singleShot non è più necessario qui perché la chiusura avviene
            # dopo che la finestra principale è visibile.

        # Avvia il ciclo eventi principale
        sys.exit(app.exec())

    except Exception as e_main:
        # Cattura errori critici durante avvio o esecuzione
        print(f"ERRORE CRITICO nell'applicazione: {e_main}", file=sys.stderr)
        traceback.print_exc() # Stampa traceback completo
        if splash and not splash.isHidden(): splash.close() # Chiudi splash se errore
        try: # Mostra dialogo di errore
            error_dialog=QtWidgets.QMessageBox(); error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Critical); error_dialog.setWindowTitle("Errore Applicazione"); error_dialog.setText(f"Errore avvio:\n\n{e_main}"); error_dialog.setDetailedText(traceback.format_exc()); error_dialog.exec()
        except: pass
        sys.exit(1) # Esci con errore