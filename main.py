# main.py
# Splash screen con testo disegnato SOTTO l'immagine ridimensionata.

import sys
import os
import time
import traceback
from PyQt6 import QtWidgets, QtGui, QtCore

# --- Importa la classe App e altre dipendenze ---
# (codice invariato)
try:
    from main_window import App
except ImportError as e:
    print(f"ERRORE CRITICO: Impossibile importare 'App' da 'main_window': {e}", file=sys.stderr)
    app_temp = QtWidgets.QApplication.instance()
    if not app_temp: app_temp = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "Errore Import", f"Modulo App non trovato:\n{e}")
    sys.exit(1)

# --- Funzione per caricare i font ---
# (codice invariato)
def load_fonts():
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    main_family_name = "Arial"
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
                print(f"WARNING: Font TTC '{ttc_file}' caricato ma nessuna famiglia trovata.")
                main_family_name = "Arial"
        else:
            print(f"WARNING: Impossibile caricare font TTC '{ttc_file}'.")
            main_family_name = "Arial"
    else:
        print(f"WARNING: File font TTC non trovato: '{ttc_file}' in '{font_dir}'")
        main_family_name = "Arial"
    print(f"INFO: Famiglia font selezionata per UI: '{main_family_name}'")
    return main_family_name

# --- Verifica preliminare moduli WebEngine ---
# (codice invariato)
try:
    from PyQt6 import QtWebEngineWidgets, QtWebEngineCore, QtWebChannel
    _ = QtWebEngineWidgets.QWebEngineView; _ = QtWebEngineCore.QWebEnginePage; _ = QtWebChannel.QWebChannel
    print("INFO: Moduli QtWebEngine OK.")
except ImportError:
    print("ERRORE CRITICO: PyQt6-WebEngine non installato.", file=sys.stderr); print("Installa con: pip install PyQt6-WebEngine", file=sys.stderr)
    app_temp = QtWidgets.QApplication.instance();
    if not app_temp: app_temp = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None,"Errore Moduli","PyQt6-WebEngine mancante."); sys.exit(1)


# --- Esecuzione Applicazione ---
if __name__ == '__main__':

    # Imposta attributi DPI
    # (codice invariato)
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        print("INFO: Abilitato AA_EnableHighDpiScaling.")
    if hasattr(QtCore.Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        print("INFO: Abilitato AA_UseHighDpiPixmaps.")

    # Crea QApplication
    app = QtWidgets.QApplication(sys.argv)

    # --- Mostra lo Splash Screen con Testo Disegnato Sotto ---
    splash = None
    final_pixmap = None # La pixmap combinata (immagine + testo)
    try:
        image_filename = "splash.png"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, image_filename)

        print(f"INFO: Checking for splash image at: {image_path}")

        if os.path.exists(image_path):
            original_pixmap = QtGui.QPixmap(image_path)

            if not original_pixmap.isNull():
                # 1. Ridimensiona l'immagine come prima
                original_size = original_pixmap.size()
                new_width = int(original_size.width() * 0.5)
                new_height = int(original_size.height() * 0.5)
                scaled_pixmap = original_pixmap.scaled(
                    new_width, new_height,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                )
                print(f"INFO: Base image resized to {scaled_pixmap.width()}x{scaled_pixmap.height()}")

                # --- Disegna Testo sul Pixmap ---
                # 2. Definisci parametri testo
                text_to_draw = "Caricamento applicazione..."
                text_color = QtGui.QColor("white")
                text_padding_bottom = 5  # Spazio tra immagine e testo
                text_area_height = 30  # Altezza area dedicata al testo
                text_font = QtGui.QFont("Arial", 10) # Imposta font e dimensione

                # 3. Crea il pixmap finale più alto
                final_height = scaled_pixmap.height() + text_area_height
                final_pixmap = QtGui.QPixmap(scaled_pixmap.width(), final_height)
                # Riempi con sfondo trasparente (importante!)
                final_pixmap.fill(QtCore.Qt.GlobalColor.transparent)

                # 4. Prepara il QPainter
                painter = QtGui.QPainter(final_pixmap)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing)

                # 5. Disegna l'immagine ridimensionata in cima
                painter.drawPixmap(0, 0, scaled_pixmap)

                # 6. Imposta font e colore per il testo
                painter.setFont(text_font)
                painter.setPen(text_color)

                # 7. Definisci il rettangolo per il testo (sotto l'immagine)
                text_rect = QtCore.QRect(
                    0,
                    scaled_pixmap.height() + text_padding_bottom, # Y iniziale sotto l'immagine + padding
                    final_pixmap.width(),                        # Larghezza completa
                    text_area_height - text_padding_bottom       # Altezza rimanente
                )

                # 8. Disegna il testo centrato nel rettangolo
                painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignCenter, text_to_draw)

                # 9. Finalizza il disegno
                painter.end()
                print(f"INFO: Text drawn onto pixmap. Final size: {final_pixmap.width()}x{final_pixmap.height()}")
                # --- Fine Disegno Testo ---

                # 10. Crea lo QSplashScreen usando il Pixmap FINALE (con testo)
                splash = QtWidgets.QSplashScreen(final_pixmap)

                # (Opzionale) Maschera per trasparenza basata sul Pixmap FINALE
                # splash.setMask(final_pixmap.mask())

                # !!! RIMUOVI splash.showMessage() !!!
                # splash.showMessage(...) # Questa riga NON serve più

                # Mostra lo splash combinato
                splash.show()
                print("INFO: Combined (image+text) QSplashScreen shown.")
                app.processEvents()
            else:
                print(f"WARNING: Failed to load QPixmap from '{image_path}'.")
        else:
            print(f"WARNING: Static splash image file not found at: '{image_path}'.")

    except Exception as e_splash:
        print(f"WARNING: Error creating/drawing static QSplashScreen: {e_splash}")
        traceback.print_exc()
        splash = None
        final_pixmap = None # Assicura sia None

    # --- Carica Font e Crea Finestra Principale ---
    # (Il resto del codice rimane invariato, userà la variabile 'splash' correttamente)
    try:
        ui_font_family_name = load_fonts()
        print("INFO: Creating main application window...")
        window = App(ui_font_family=ui_font_family_name)
        print("INFO: Main window created.")
        window.show()
        print("INFO: Main window shown.")

        if splash:
             print("INFO: Applying brief delay for splash visibility...")
             REQUIRED_SPLASH_DURATION_SEC = 0.5
             time.sleep(REQUIRED_SPLASH_DURATION_SEC)
             print("INFO: Delay finished.")

        if splash:
            print("INFO: Closing combined splash screen...")
            splash.finish(window)
            print("INFO: Combined splash screen closed.")
        else:
             app.processEvents()

        print("INFO: Starting application event loop...")
        exit_code = app.exec()
        print(f"INFO: Application finished with exit code {exit_code}.")
        sys.exit(exit_code)

    except Exception as e_main:
        print(f"ERRORE CRITICO nell'applicazione: {e_main}", file=sys.stderr)
        traceback.print_exc()
        if splash and not splash.isHidden():
            splash.close()
        try:
            error_dialog = QtWidgets.QMessageBox(); error_dialog.setIcon(QtWidgets.QMessageBox.Icon.Critical); error_dialog.setWindowTitle("Errore Applicazione"); error_dialog.setText(f"Si è verificato un errore critico:\n\n{e_main}"); error_dialog.setDetailedText(traceback.format_exc()); error_dialog.exec()
        except Exception as e_dialog: print(f"Errore nel mostrare il dialogo di errore: {e_dialog}")
        sys.exit(1)