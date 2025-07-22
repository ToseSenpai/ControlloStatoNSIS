#!/usr/bin/env python3
# deploy.py
# Deployment script for ControlloStatoNSIS

import os
import sys
import shutil
import subprocess
from pathlib import Path

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
    """Clean build artifacts."""
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
    """Create release package."""
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
    config_files = ['config.py', 'logging_config.py']
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

def main():
    """Main deployment process."""
    print("🚀 Avvio processo di deployment per ControlloStatoNSIS")
    print("=" * 60)
    
    steps = [
        ("Pulizia build", clean_build),
        ("Installazione dipendenze", install_dependencies),
        ("Esecuzione test", run_tests),
        ("Controllo qualità codice", lint_code),
        ("Formattazione codice", format_code),
        ("Build eseguibile", build_executable),
        ("Creazione pacchetto release", create_release_package),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        print("-" * 40)
        
        if not step_func():
            failed_steps.append(step_name)
            print(f"⚠️ Step '{step_name}' fallito")
        else:
            print(f"✅ Step '{step_name}' completato con successo")
    
    print("\n" + "=" * 60)
    print("🏁 Deployment completato")
    
    if failed_steps:
        print(f"❌ Step falliti: {', '.join(failed_steps)}")
        sys.exit(1)
    else:
        print("✅ Tutti gli step completati con successo!")
        print("📦 Il pacchetto release è pronto nella cartella 'release/'")

if __name__ == "__main__":
    main() 