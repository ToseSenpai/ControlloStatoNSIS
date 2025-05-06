# File: main.spec (Versione Aggiornata)

# -*- mode: python ; coding: utf-8 -*-

# Lista dei file di dati - Percorsi relativi a questo file .spec
# AGGIORNATO: Usa 'splash.png' invece di 'splash.gif'
datas_list = [
    ('fonts', 'fonts'),               # Sorgente 'fonts' -> Destinazione 'fonts'
    ('ilovecustoms.png', '.'),        # Sorgente 'ilovecustoms.png' -> Destinazione '.' (root)
    ('icon.ico', '.'),                # Sorgente 'icon.ico' -> Destinazione '.' (root)
    ('splash.png', '.')               # <--- MODIFICATO: Usa il nome file corretto
]

# Import nascosti
# (Nessuna modifica necessaria qui rispetto alla versione precedente)
hidden_imports_list = [
    'PyQt6.QtSvg',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtPrintSupport',
    'qtawesome',
    'openpyxl',
]

# Analisi
# (Nessuna modifica necessaria qui rispetto alla versione precedente)
a = Analysis(
    ['main.py'], # Assicurati che usi il file main.py aggiornato
    pathex=[],
    binaries=[],
    datas=datas_list,                 # Usa la lista dati aggiornata
    hiddenimports=hidden_imports_list,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],                      # Lasciato vuoto per ora
    cipher=None,
    noarchive=False
)

# PYZ
# (Nessuna modifica necessaria qui rispetto alla versione precedente)
pyz = PYZ(a.pure)

# Eseguibile
# (Nessuna modifica necessaria qui rispetto alla versione precedente)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,                          # Passa i dati aggiornati
    [],
    name='ControlloStatoNSIS',        # Nome dell'eseguibile
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                         # Compressione UPX attiva
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                    # Applicazione GUI (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'                   # Icona dell'eseguibile
)

# Raccolta in Cartella (modalità --onedir)
# (Nessuna modifica necessaria qui rispetto alla versione precedente)
coll = COLLECT(
    exe,
    a.zipfiles,
    a.datas,                          # Includi i dati aggiornati nella cartella finale
    a.binaries,                       # Includi i binari
    strip=False,
    upx=True,                         # Comprimi anche i file nella cartella
    upx_exclude=[],
    name='ControlloStatoNSIS'         # Nome della cartella in dist/
)