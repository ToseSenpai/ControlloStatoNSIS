@echo off
REM build_windows.bat
REM Windows build script for ControlloStatoNSIS

echo ========================================
echo ControlloStatoNSIS - Windows Build
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python non trovato. Installare Python 3.8+ e riprovare.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip non trovato. Installare pip e riprovare.
    pause
    exit /b 1
)

echo.
echo 1. Pulizia build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist main_window\__pycache__ rmdir /s /q main_window\__pycache__
if exist tests\__pycache__ rmdir /s /q tests\__pycache__

echo.
echo 2. Installazione dipendenze...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Errore nell'installazione delle dipendenze.
    pause
    exit /b 1
)

echo.
echo 3. Esecuzione test...
python -m pytest tests/ -v
if errorlevel 1 (
    echo WARNING: Alcuni test sono falliti, ma continuo con il build...
)

echo.
echo 4. Controllo qualità codice...
pip install flake8
flake8 main_window/ config.py main.py
if errorlevel 1 (
    echo WARNING: Problemi di qualità del codice rilevati, ma continuo con il build...
)

echo.
echo 5. Build eseguibile con PyInstaller...
pip install pyinstaller
pyinstaller main.spec
if errorlevel 1 (
    echo ERROR: Errore nel build dell'eseguibile.
    pause
    exit /b 1
)

echo.
echo 6. Creazione pacchetto release...
if not exist release mkdir release

REM Copy executable
if exist dist\ControlloStatoNSIS.exe (
    copy dist\ControlloStatoNSIS.exe release\
    echo - Copiato eseguibile
)

REM Copy assets
if exist assets (
    xcopy assets release\assets\ /E /I /Y
    echo - Copiato assets
)

if exist fonts (
    xcopy fonts release\fonts\ /E /I /Y
    echo - Copiato fonts
)

if exist icons (
    xcopy icons release\icons\ /E /I /Y
    echo - Copiato icons
)

REM Copy config files
if exist config.py (
    copy config.py release\
    echo - Copiato config.py
)

if exist logging_config.py (
    copy logging_config.py release\
    echo - Copiato logging_config.py
)

REM Copy documentation
if exist docs (
    xcopy docs release\docs\ /E /I /Y
    echo - Copiata documentazione
)

if exist readme.md (
    copy readme.md release\
    echo - Copiato README
)

echo.
echo ========================================
echo BUILD COMPLETATO CON SUCCESSO!
echo ========================================
echo.
echo Il pacchetto release è disponibile nella cartella 'release/'
echo.
echo Contenuto del pacchetto:
dir release /B
echo.
echo.
echo Opzionale: Creazione installer Windows...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo Creazione installer con Inno Setup...
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_config.iss
    if exist "installer\ControlloStatoNSIS-Setup-2.0.0.exe" (
        echo Installer creato: installer\ControlloStatoNSIS-Setup-2.0.0.exe
    )
) else (
    echo Inno Setup non trovato. Installare Inno Setup 6 per creare l'installer.
)
echo.
pause 