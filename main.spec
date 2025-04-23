# File: main.spec (Versione Riconfermata)

# -*- mode: python ; coding: utf-8 -*-

# Lista dei file di dati - Percorsi relativi a questo file .spec
datas_list = [
    ('fonts', 'fonts'),               # Sorgente 'fonts' -> Destinazione 'fonts'
    ('ilovecustoms.png', '.'),        # Sorgente 'ilovecustoms.png' -> Destinazione '.' (root)
    ('icon.ico', '.'),                # Sorgente 'icon.ico' -> Destinazione '.' (root)
    ('splash.gif', '.')               # Sorgente 'splash.gif' -> Destinazione '.' (root)
]

# Import nascosti
hidden_imports_list = [
    'PyQt6.QtSvg',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtPrintSupport',
    'qtawesome',
    'openpyxl',
]

# Analisi
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas_list,                 # <--- Assicurati che sia qui
    hiddenimports=hidden_imports_list,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=None,
    noarchive=False
)

# PYZ
pyz = PYZ(a.pure)

# Eseguibile
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,                        # <--- Passa datas anche a EXE (per compatibilità/onefile futuro)
    [],
    name='ControlloStatoNSIS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                  # GUI App
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'                 # Icona EXE
)

# Raccolta in Cartella
coll = COLLECT(
    exe,
    a.zipfiles,
    a.datas,                        # <--- CRUCIALE: Assicurati che a.datas sia passato qui!
    a.binaries,                     # <--- Aggiungi anche i binari qui per sicurezza
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ControlloStatoNSIS'       # Nome cartella in dist/
)