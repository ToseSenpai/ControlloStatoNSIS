#!/usr/bin/env python3
# deploy_windows.py
# Windows-specific deployment script for ControlloStatoNSIS

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completato")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore in {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def clean_build():
    """Clean build artifacts for Windows."""
    print("🧹 Pulizia build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__', 'main_window\\__pycache__', 'tests\\__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ Rimosso {dir_name}")
    
    # Clean Python cache files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass
    
    for pattern in files_to_clean:
        for file_path in Path('.').glob(pattern):
            try:
                file_path.unlink()
                print(f"✅ Rimosso {file_path}")
            except:
                pass

def install_dependencies():
    """Install production dependencies."""
    return run_command("pip install -r requirements.txt", "Installazione dipendenze")

def run_tests():
    """Run tests."""
    return run_command("python -m pytest tests/ -v", "Esecuzione test")

def lint_code():
    """Run linting checks."""
    return run_command("flake8 main_window/ config.py main.py", "Controllo qualità codice")

def format_code():
    """Format code with black."""
    return run_command("black main_window/ config.py main.py", "Formattazione codice")

def build_executable():
    """Build executable with PyInstaller."""
    return run_command("pyinstaller main.spec", "Build eseguibile")

def create_release_package():
    """Create release package for Windows."""
    print("📦 Creazione pacchetto release...")
    
    release_dir = "release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    
    os.makedirs(release_dir)
    
    # Copy executable
    if os.path.exists("dist/ControlloStatoNSIS.exe"):
        shutil.copy2("dist/ControlloStatoNSIS.exe", release_dir)
        print("✅ Copiato eseguibile")
    
    # Copy assets
    assets_dirs = ['assets', 'fonts', 'icons']
    for asset_dir in assets_dirs:
        if os.path.exists(asset_dir):
            shutil.copytree(asset_dir, os.path.join(release_dir, asset_dir))
            print(f"✅ Copiato {asset_dir}")
    
    # Copy config files
    config_files = ['config.py', 'logging_config.py', 'windows_config.py']
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, release_dir)
            print(f"✅ Copiato {config_file}")
    
    # Copy documentation
    if os.path.exists("docs"):
        shutil.copytree("docs", os.path.join(release_dir, "docs"))
        print("✅ Copiata documentazione")
    
    # Copy README
    if os.path.exists("readme.md"):
        shutil.copy2("readme.md", release_dir)
        print("✅ Copiato README")
    
    print(f"✅ Pacchetto release creato in {release_dir}")

def create_installer():
    """Create Windows installer with Inno Setup."""
    print("🔧 Creazione installer Windows...")
    
    inno_compiler_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    
    inno_compiler = None
    for path in inno_compiler_paths:
        if os.path.exists(path):
            inno_compiler = path
            break
    
    if not inno_compiler:
        print("⚠️ Inno Setup non trovato. Installare Inno Setup 6 per creare l'installer.")
        return False
    
    if not os.path.exists("dist/ControlloStatoNSIS.exe"):
        print("❌ Eseguibile non trovato. Eseguire prima il build.")
        return False
    
    # Create installer directory
    installer_dir = "installer"
    if not os.path.exists(installer_dir):
        os.makedirs(installer_dir)
    
    # Run Inno Setup
    command = f'"{inno_compiler}" installer_config.iss'
    success = run_command(command, "Compilazione installer")
    
    if success:
        installer_file = "installer/ControlloStatoNSIS-Setup-2.0.0.exe"
        if os.path.exists(installer_file):
            file_size = os.path.getsize(installer_file) / (1024 * 1024)  # MB
            print(f"✅ Installer creato: {installer_file} ({file_size:.1f} MB)")
            return True
    
    return False

def create_portable_package():
    """Create portable package for Windows."""
    print("💼 Creazione pacchetto portable...")
    
    portable_dir = "portable"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    os.makedirs(portable_dir)
    
    # Copy executable
    if os.path.exists("dist/ControlloStatoNSIS.exe"):
        shutil.copy2("dist/ControlloStatoNSIS.exe", portable_dir)
        print("✅ Copiato eseguibile")
    
    # Copy assets
    assets_dirs = ['assets', 'fonts', 'icons']
    for asset_dir in assets_dirs:
        if os.path.exists(asset_dir):
            shutil.copytree(asset_dir, os.path.join(portable_dir, asset_dir))
            print(f"✅ Copiato {asset_dir}")
    
    # Copy config files
    config_files = ['config.py', 'logging_config.py', 'windows_config.py']
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, portable_dir)
            print(f"✅ Copiato {config_file}")
    
    # Create portable launcher
    launcher_content = '''@echo off
REM Portable launcher for ControlloStatoNSIS
echo Avvio ControlloStatoNSIS...
start "" "ControlloStatoNSIS.exe"
'''
    
    with open(os.path.join(portable_dir, "Avvia.bat"), "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("✅ Copiato launcher portable")
    
    # Create README for portable
    portable_readme = '''# ControlloStatoNSIS - Versione Portable

Questa è la versione portable di ControlloStatoNSIS.

## Utilizzo
1. Estrarre tutti i file in una cartella
2. Fare doppio click su "Avvia.bat" o "ControlloStatoNSIS.exe"
3. L'applicazione si avvierà senza installazione

## Note
- I log vengono salvati nella cartella "logs" locale
- Non sono necessari permessi di amministratore
- Può essere eseguita da USB o cartelle condivise

## Requisiti
- Windows 10/11 (64-bit)
- Nessuna installazione aggiuntiva richiesta
'''
    
    with open(os.path.join(portable_dir, "README_Portable.md"), "w", encoding="utf-8") as f:
        f.write(portable_readme)
    
    print(f"✅ Pacchetto portable creato in {portable_dir}")

def main():
    """Main deployment process for Windows."""
    print("🚀 Avvio processo di deployment Windows per ControlloStatoNSIS")
    print("=" * 70)
    
    steps = [
        ("Pulizia build", clean_build),
        ("Installazione dipendenze", install_dependencies),
        ("Esecuzione test", run_tests),
        ("Controllo qualità codice", lint_code),
        ("Formattazione codice", format_code),
        ("Build eseguibile", build_executable),
        ("Creazione pacchetto release", create_release_package),
        ("Creazione pacchetto portable", create_portable_package),
        ("Creazione installer", create_installer),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        print("-" * 50)
        
        if not step_func():
            failed_steps.append(step_name)
            print(f"⚠️ Step '{step_name}' fallito")
        else:
            print(f"✅ Step '{step_name}' completato con successo")
    
    print("\n" + "=" * 70)
    print("🏁 Deployment Windows completato")
    
    if failed_steps:
        print(f"❌ Step falliti: {', '.join(failed_steps)}")
        sys.exit(1)
    else:
        print("✅ Tutti gli step completati con successo!")
        print("📦 I pacchetti sono pronti:")
        print("   - release/ (pacchetto completo)")
        print("   - portable/ (versione portable)")
        if os.path.exists("installer/ControlloStatoNSIS-Setup-2.0.0.exe"):
            print("   - installer/ (installer Windows)")

if __name__ == "__main__":
    main() 