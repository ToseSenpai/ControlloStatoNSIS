# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — ONEDIR build con splash, console, fonts, icona e immagine extra

✔️  Cartella dist/ControlloStatoNSIS (modalità onedir)
✔️  Splash.png mostrato dal bootloader
✔️  Console visibile all’avvio (metti console=False per GUI pura)
✔️  Font personalizzati copiati in _internal/fonts
✔️  Icona dell’app incorporata (icon.ico)
✔️  Immagine aggiuntiva ilovecustoms.png nella root di runtime
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_dynamic_libs
import os

# -----------------------------------------------------------------------------
# Percorsi progetto
# -----------------------------------------------------------------------------
root = Path(__file__).parent.resolve() if "__file__" in globals() else Path(os.getcwd())

main_script  = root / "main.py"
splash_image = root / "splash.png"
fonts_dir    = root / "fonts"           # cartella con .ttf/.ttc
icon_file    = root / "icon.ico"        # icona Windows
extra_img    = root / "ilovecustoms.png"# immagine extra

# -----------------------------------------------------------------------------
# File dati da includere
# -----------------------------------------------------------------------------

datas = [
    (splash_image, "."),  # splash
    (extra_img,   "."),   # immagine extra
]

# Copia ogni file font → _internal/fonts
if fonts_dir.exists():
    for font_file in fonts_dir.iterdir():
        if font_file.is_file():
            datas.append((str(font_file), "fonts"))

# -----------------------------------------------------------------------------
# DLL necessarie (Tcl/Tk per splash)
# -----------------------------------------------------------------------------

binaries = collect_dynamic_libs("tkinter")

# -----------------------------------------------------------------------------
# Analysis
# -----------------------------------------------------------------------------

a = Analysis(
    [str(main_script)],
    pathex=[str(root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# -----------------------------------------------------------------------------
# Executable (stub) – onedir
# -----------------------------------------------------------------------------

exe = EXE(
    pyz,
    a.scripts,
    [],                 # binari veri aggiunti da COLLECT
    exclude_binaries=True,
    name="ControlloStatoNSIS",
    debug=False,        # True per log bootloader
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,       # console aperta (nascondila via hide_console())
    icon=str(icon_file) if icon_file.exists() else None,
    splash=str(splash_image),
)

# -----------------------------------------------------------------------------
# COLLECT – crea dist/ControlloStatoNSIS
# -----------------------------------------------------------------------------

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="ControlloStatoNSIS",
)
