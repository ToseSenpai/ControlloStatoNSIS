#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per generare icone multi-piattaforma per applicazione Electron
Genera: icon.ico (Windows), icon.png (Linux), icone tray, e icone multisize
"""

import os
import sys
import io
from pathlib import Path

# Fix encoding per Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    from PIL import Image
except ImportError:
    print("Errore: Pillow non installato. Installalo con: pip install Pillow")
    sys.exit(1)

# Percorsi
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = Path(__file__).parent / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
OLD_ICON = PROJECT_ROOT / "icon.ico"

# Dimensioni standard per Windows ICO
ICO_SIZES = [16, 32, 48, 64, 128, 256]

# Dimensioni per icone tray
TRAY_SIZES = [16, 32]

def ensure_directories():
    """Crea le directory necessarie"""
    ASSETS_DIR.mkdir(exist_ok=True)
    ICONS_DIR.mkdir(exist_ok=True)
    print(f"✓ Directory create: {ASSETS_DIR}, {ICONS_DIR}")

def extract_largest_icon(ico_path):
    """Estrae l'icona più grande dal file ICO"""
    try:
        img = Image.open(ico_path)
        # Ottieni tutte le dimensioni disponibili
        largest = None
        largest_size = 0

        # ICO files contengono multiple immagini
        if hasattr(img, 'n_frames'):
            for i in range(img.n_frames):
                img.seek(i)
                size = img.size[0] * img.size[1]
                if size > largest_size and img.size[0] == img.size[1]:  # Solo icone quadrate
                    largest_size = size
                    largest = img.copy()
        else:
            largest = img.copy()

        if largest is None:
            print(f"✗ Nessuna icona valida trovata in {ico_path}")
            return None

        # Converti in RGBA se necessario
        if largest.mode != 'RGBA':
            largest = largest.convert('RGBA')

        print(f"✓ Estratta icona {largest.size[0]}x{largest.size[1]} da {ico_path.name}")
        return largest

    except Exception as e:
        print(f"✗ Errore nell'estrarre icona: {e}")
        return None

def create_fallback_icon():
    """Crea un'icona di fallback se non esiste icon.ico"""
    print("⚠ Creazione icona di fallback...")
    # Crea un'icona semplice con sfondo blu e testo "NSIS"
    img = Image.new('RGBA', (512, 512), (45, 85, 255, 255))
    print("✓ Icona di fallback creata")
    return img

def generate_ico(base_image, output_path):
    """Genera file ICO con tutte le dimensioni standard"""
    try:
        sizes = [(size, size) for size in ICO_SIZES]
        icons = []

        for size in sizes:
            resized = base_image.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)

        # Salva come ICO multi-size
        icons[0].save(
            output_path,
            format='ICO',
            sizes=[icon.size for icon in icons],
            append_images=icons[1:]
        )

        sizes_str = ", ".join([f"{s}x{s}" for s in ICO_SIZES])
        print(f"✓ Generato {output_path.name} con dimensioni: {sizes_str}")
        return True

    except Exception as e:
        print(f"✗ Errore nella generazione ICO: {e}")
        return False

def generate_png(base_image, size, output_path, description=""):
    """Genera file PNG di dimensione specifica"""
    try:
        resized = base_image.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(output_path, format='PNG', optimize=True)
        desc = f" ({description})" if description else ""
        print(f"✓ Generato {output_path.name} {size}x{size}{desc}")
        return True

    except Exception as e:
        print(f"✗ Errore nella generazione PNG: {e}")
        return False

def generate_icns(base_image, output_path):
    """
    Genera file ICNS per macOS
    Nota: Richiede pillow-icns o genera PNG che può essere convertito manualmente
    """
    try:
        # Dimensioni richieste per ICNS
        icns_sizes = [16, 32, 64, 128, 256, 512, 1024]

        # Per ora genera solo un PNG 1024x1024 che può essere convertito in ICNS
        # con tools macOS (iconutil) o electron-builder lo farà automaticamente
        png_1024_path = output_path.with_suffix('.png')
        generate_png(base_image, 1024, png_1024_path, "base per ICNS")

        print(f"⚠ File ICNS: generato PNG 1024x1024")
        print(f"  electron-builder convertirà automaticamente in ICNS durante il build")
        print(f"  Oppure usa: iconutil -c icns icon.iconset (su macOS)")

        return True

    except Exception as e:
        print(f"✗ Errore nella generazione ICNS: {e}")
        return False

def generate_tray_icons(base_image, output_dir):
    """Genera icone per system tray (16x16 e 32x32)"""
    try:
        for size in TRAY_SIZES:
            filename = f"tray-icon-{size}.png"
            output_path = output_dir / filename
            generate_png(base_image, size, output_path, "tray icon")

        # Genera anche versione template per macOS (monocromatica)
        # Per ora usiamo la stessa icona, ma dovrebbe essere monocromatica
        for size in TRAY_SIZES:
            filename = f"tray-icon-{size}-Template.png"
            output_path = output_dir / filename
            generate_png(base_image, size, output_path, "tray template")

        print(f"✓ Icone tray generate ({len(TRAY_SIZES) * 2} file)")
        return True

    except Exception as e:
        print(f"✗ Errore nella generazione icone tray: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  GENERATORE ICONE ELECTRON - ControlloStatoNSIS")
    print("="*60 + "\n")

    # 1. Crea directory
    ensure_directories()
    print()

    # 2. Carica icona base
    base_image = None
    if OLD_ICON.exists():
        print(f"📁 Trovato {OLD_ICON.name}, estrazione immagine...")
        base_image = extract_largest_icon(OLD_ICON)

    if base_image is None:
        base_image = create_fallback_icon()

    # Assicurati che sia almeno 512x512 per qualità ottimale
    if base_image.size[0] < 512:
        print(f"⚠ Upscaling icona da {base_image.size[0]}x{base_image.size[1]} a 512x512")
        base_image = base_image.resize((512, 512), Image.Resampling.LANCZOS)

    print()

    # 3. Genera icon.ico per Windows
    print("🪟 Generazione icon.ico per Windows...")
    ico_path = ASSETS_DIR / "icon.ico"
    if generate_ico(base_image, ico_path):
        print()

    # 4. Genera icon.png per Linux
    print("🐧 Generazione icon.png per Linux...")
    png_path = ASSETS_DIR / "icon.png"
    if generate_png(base_image, 512, png_path, "Linux app icon"):
        print()

    # 5. Genera icone per macOS
    print("🍎 Preparazione icone per macOS...")
    icns_path = ASSETS_DIR / "icon.icns"
    if generate_icns(base_image, icns_path):
        print()

    # 6. Genera icone tray
    print("📌 Generazione icone system tray...")
    if generate_tray_icons(base_image, ICONS_DIR):
        print()

    # 7. Genera icone aggiuntive per diverse risoluzioni
    print("📐 Generazione icone aggiuntive...")
    extra_sizes = [64, 128, 256, 512]
    for size in extra_sizes:
        filename = f"icon-{size}.png"
        output_path = ICONS_DIR / filename
        generate_png(base_image, size, output_path, f"extra {size}x{size}")

    print("\n" + "="*60)
    print("  ✓ GENERAZIONE COMPLETATA")
    print("="*60)
    print(f"\nFile generati:")
    print(f"  • {ico_path} (Windows)")
    print(f"  • {png_path} (Linux)")
    print(f"  • {ASSETS_DIR / 'icon.png'} (macOS - convertire in ICNS)")
    print(f"  • {ICONS_DIR}/ (icone tray e aggiuntive)")
    print(f"\nProssimi passi:")
    print(f"  1. Verifica le icone generate")
    print(f"  2. Aggiorna package.json con i path corretti")
    print(f"  3. Testa il build con: npm run package")
    print()

if __name__ == "__main__":
    main()
