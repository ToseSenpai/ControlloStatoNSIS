# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — build **ONEDIR** con splash nativo e font personalizzati

✔️  Onedir (dist/ControlloStatoNSIS)
✔️  Splash.png mostrato (GUI, no console)
✔️  DLL Tcl/Tk incluse per lo splash
✔️  Cartella *fonts* copiata in _internal/fonts così Qt trova Inter.ttc

Per il debug (log in console) metti `console=True` e/o `debug=True` nell’oggetto EXE.
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_dynamic_libs
import os

# -----------------------------------------------------------------------------
# Percorsi principali
# -----------------------------------------------------------------------------
root = Path(__file__).parent.resolve() if "__file__" in globals() else Path(os.getcwd())
main_script  = root / "main.py"
splash_image = root / "splash.png"
fonts_dir    = root / "fonts"          # ↙ contiene Inter.ttc e altri font
icon_file    = None  # es: root / "app.ico" se serve un'icona

# -----------------------------------------------------------------------------
# Risorse extra (splash + fonts)
# -----------------------------------------------------------------------------

datas = [(splash_image, ".")]

# Copia tutta la cartella "fonts" dentro _internal/fonts nel runtime,
# così Qt6 troverà Inter.ttc senza warning.
if fonts_dir.exists():
    datas.append((str(fonts_dir), "_internal/fonts"))

# -----------------------------------------------------------------------------
# DLL Tcl/Tk indispensabili per il bootloader splash
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
# Executable (stub) – ONEDIR, GUI, splash
# -----------------------------------------------------------------------------

exe = EXE(
    pyz,
    a.scripts,
    [],                 # i binari veri sono raccolti da COLLECT
    exclude_binaries=True,
    name="ControlloStatoNSIS",
    debug=False,        # ➜ True se vuoi log
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,      # GUI subsystem
    icon=str(icon_file) if icon_file else None,
    splash=str(splash_image),
)

# -----------------------------------------------------------------------------
# COLLECT – crea la cartella dist/ControlloStatoNSIS (build ONEDIR)
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
