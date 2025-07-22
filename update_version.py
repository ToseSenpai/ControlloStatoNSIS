#!/usr/bin/env python3
# update_version.py
# Script to update version across all project files

import re
import os
from datetime import datetime

def update_version_files(new_version):
    """Update version in all relevant files."""
    
    files_to_update = [
        ('version.py', r'__version__ = "([^"]+)"', f'__version__ = "{new_version}"'),
        ('pyproject.toml', r'version = "([^"]+)"', f'version = "{new_version}"'),
        ('setup.py', r'version=get_version\(\)', f'version=get_version()'),
        ('installer_config.iss', r'AppVersion=([^\r\n]+)', f'AppVersion={new_version}'),
        ('installer_config.iss', r'OutputBaseFilename=ControlloStatoNSIS-Setup-([^\.]+)', f'OutputBaseFilename=ControlloStatoNSIS-Setup-{new_version}'),
        ('readme.md', r'# Controllo Stato Richiesta NSIS \(v([^)]+)\)', f'# Controllo Stato Richiesta NSIS (v{new_version})'),
    ]
    
    for file_path, pattern, replacement in files_to_update:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = re.sub(pattern, replacement, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Aggiornato {file_path}")

def update_changelog(new_version):
    """Update changelog with new version."""
    changelog_path = "docs/CHANGELOG.md"
    
    if not os.path.exists(changelog_path):
        print(f"⚠️ Changelog non trovato: {changelog_path}")
        return
    
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new version entry
    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"""## [{new_version}] - {today}

### Added
- 🆕 Nuove funzionalità aggiunte

### Changed
- 🔄 Modifiche apportate

### Fixed
- 🐛 Bug risolti

"""
    
    # Insert after the first ## [version] line
    lines = content.split('\n')
    insert_index = None
    
    for i, line in enumerate(lines):
        if line.startswith('## [') and '] - ' in line:
            insert_index = i
            break
    
    if insert_index is not None:
        lines.insert(insert_index, new_entry)
        new_content = '\n'.join(lines)
        
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Aggiornato {changelog_path}")

def main():
    """Main function to update version."""
    import sys
    
    if len(sys.argv) != 2:
        print("Utilizzo: python update_version.py <nuova_versione>")
        print("Esempio: python update_version.py 2.1.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("❌ Formato versione non valido. Usare formato MAJOR.MINOR.PATCH (es. 2.1.0)")
        sys.exit(1)
    
    print(f"🔄 Aggiornamento versione a {new_version}...")
    
    update_version_files(new_version)
    update_changelog(new_version)
    
    print(f"✅ Versione aggiornata a {new_version} in tutti i file")

if __name__ == "__main__":
    main() 