#!/usr/bin/env python3
"""
Script per generare icone dell'applicazione da logost.png
Genera tutte le dimensioni necessarie per Windows, macOS e Linux
"""

from PIL import Image
import os
import struct
import io

# Percorsi
LOGO_PATH = "../logochecknos_icon.png"  # NUOVO: Logo CHECK NOS per icone Windows
ASSETS_DIR = "../assets"
ICONS_DIR = "../assets/icons"

# Dimensioni icone necessarie
ICON_SIZES = {
    'icon-64.png': 64,
    'icon-128.png': 128,
    'icon-256.png': 256,
    'icon-512.png': 512,
}

TRAY_SIZES = {
    'tray-icon-16.png': 16,
    'tray-icon-32.png': 32,
    'tray-icon-16-Template.png': 16,  # macOS template
    'tray-icon-32-Template.png': 32,  # macOS template
}

def create_icon_with_padding(logo_img, size, padding_percent=10):
    """
    Crea un'icona quadrata con il logo centrato e padding

    Args:
        logo_img: Immagine PIL del logo
        size: Dimensione finale dell'icona (width & height)
        padding_percent: Percentuale di padding (default 10%)

    Returns:
        Immagine PIL ridimensionata con padding
    """
    # Calcola dimensioni con padding
    padding = int(size * padding_percent / 100)
    logo_size = size - (padding * 2)

    # Crea canvas trasparente
    icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))

    # Ridimensiona logo mantenendo proporzioni
    logo_copy = logo_img.copy()
    logo_copy.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Centra logo nel canvas
    x = (size - logo_copy.width) // 2
    y = (size - logo_copy.height) // 2
    icon.paste(logo_copy, (x, y), logo_copy if logo_copy.mode == 'RGBA' else None)

    return icon

def create_manual_ico(logo_img, output_path, sizes_with_padding):
    """
    Genera un file ICO multi-size manualmente (workaround per bug Pillow)

    Args:
        logo_img: Immagine PIL del logo originale
        output_path: Percorso del file ICO da creare
        sizes_with_padding: Lista di tuple (size, padding_percent)

    Returns:
        True se successo, False altrimenti
    """
    try:
        # Genera tutte le immagini con padding appropriato
        images = []
        for size, padding in sizes_with_padding:
            icon = create_icon_with_padding(logo_img, size, padding_percent=padding)
            images.append((size, icon))

        # Prepara i dati PNG per ogni immagine
        png_data_list = []
        for size, img in images:
            png_buffer = io.BytesIO()
            img.save(png_buffer, format='PNG', optimize=True)
            png_data = png_buffer.getvalue()
            png_data_list.append((size, png_data))

        # Scrivi il file ICO manualmente
        with open(output_path, 'wb') as f:
            # Header ICO: reserved(2) + type(2) + count(2)
            num_images = len(png_data_list)
            f.write(struct.pack('<HHH', 0, 1, num_images))

            # Calcola offset per i dati delle immagini
            header_size = 6  # ICO header
            entry_size = 16  # Per ogni entry
            offset = header_size + (entry_size * num_images)

            # Scrivi le entry del directory
            for size, png_data in png_data_list:
                width = size if size < 256 else 0  # 0 = 256 nel formato ICO
                height = size if size < 256 else 0
                f.write(struct.pack('<BBBB', width, height, 0, 0))  # width, height, colors, reserved
                f.write(struct.pack('<HH', 1, 32))  # color planes, bits per pixel
                f.write(struct.pack('<I', len(png_data)))  # size of image data
                f.write(struct.pack('<I', offset))  # offset to image data
                offset += len(png_data)

            # Scrivi i dati delle immagini PNG
            for size, png_data in png_data_list:
                f.write(png_data)

        return True

    except Exception as e:
        print(f"  [!] Errore nella generazione manuale ICO: {e}")
        return False

def generate_windows_unplated_assets(logo_img, output_dir):
    """
    Genera asset "unplated" per Windows taskbar (mostra icona a dimensione piena)

    Questi asset prevengono che Windows aggiunga padding/backplate all'icona,
    permettendole di apparire grande come Chrome, VS Code, ecc.

    Args:
        logo_img: Immagine PIL del logo originale
        output_dir: Directory dove salvare gli asset

    Returns:
        True se successo, False altrimenti
    """
    try:
        # Dimensioni richieste da Windows per taskbar/start menu
        # Usiamo 0% padding per massimizzare la dimensione visibile
        targetsize_specs = [
            (16, 0),   # System tray
            (24, 0),   # Taskbar Windows 11 (dimensione standard)
            (32, 0),   # Taskbar Windows 10
            (48, 0),   # Start menu tiles
            (256, 0),  # High-DPI displays
        ]

        for size, padding in targetsize_specs:
            # Genera icona con padding minimo
            icon = create_icon_with_padding(logo_img, size, padding_percent=padding)

            # Salva versione UNPLATED (nessun backplate aggiunto da Windows)
            unplated_filename = f"Square44x44Logo.targetsize-{size}_altform-unplated.png"
            unplated_path = os.path.join(output_dir, unplated_filename)
            icon.save(unplated_path, 'PNG', optimize=True)

            # Salva anche versione PLATED come fallback
            plated_filename = f"Square44x44Logo.targetsize-{size}.png"
            plated_path = os.path.join(output_dir, plated_filename)
            icon.save(plated_path, 'PNG', optimize=True)

        return True

    except Exception as e:
        print(f"  [!] Errore nella generazione asset unplated: {e}")
        return False

def generate_icons():
    """Genera tutte le icone necessarie per l'applicazione"""

    # Verifica esistenza directory
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(ICONS_DIR, exist_ok=True)

    # Carica logo originale
    print(f"[*] Caricamento logo da: {LOGO_PATH}")
    try:
        logo = Image.open(LOGO_PATH).convert('RGBA')
        print(f"[+] Logo caricato: {logo.size[0]}x{logo.size[1]}px")
    except FileNotFoundError:
        print(f"[-] ERRORE: File {LOGO_PATH} non trovato!")
        return False
    except Exception as e:
        print(f"[-] ERRORE nel caricamento: {e}")
        return False

    print("\n[*] Generazione icone applicazione...")

    # Genera icone standard
    for filename, size in ICON_SIZES.items():
        output_path = os.path.join(ICONS_DIR, filename)
        icon = create_icon_with_padding(logo, size, padding_percent=5)
        icon.save(output_path, 'PNG', optimize=True)
        print(f"  [+] {filename} ({size}x{size})")

    # Genera icona principale PNG (512x512)
    print("\n[*] Generazione icona principale...")
    main_icon_path = os.path.join(ASSETS_DIR, 'icon.png')
    main_icon = create_icon_with_padding(logo, 512, padding_percent=5)
    main_icon.save(main_icon_path, 'PNG', optimize=True)
    print(f"  [+] icon.png (512x512)")

    # Genera icone system tray
    print("\n[*] Generazione icone system tray...")
    for filename, size in TRAY_SIZES.items():
        output_path = os.path.join(ICONS_DIR, filename)
        # Tray icons con meno padding
        icon = create_icon_with_padding(logo, size, padding_percent=8)
        icon.save(output_path, 'PNG', optimize=True)
        print(f"  [+] {filename} ({size}x{size})")

    # Genera ICO multi-size per Windows (metodo manuale per bug Pillow)
    print("\n[*] Generazione icon.ico per Windows...")

    # Padding minimo per massimizzare dimensione visibile nella taskbar
    # - Dimensioni piccole/medie (16-64): 0% padding (massima area)
    # - Dimensioni grandi (128-256): 2% padding (minimo per evitare bordi tagliati)
    sizes_with_padding = [
        (16, 0),
        (32, 0),
        (48, 0),
        (64, 0),
        (128, 2),
        (256, 2)
    ]

    ico_path = os.path.join(ASSETS_DIR, 'icon.ico')
    success = create_manual_ico(logo, ico_path, sizes_with_padding)

    if success:
        print(f"  [+] icon.ico (multi-size: 16, 32, 48, 64, 128, 256)")
    else:
        print(f"  [!] Warning: Errore nella generazione ICO")
        print("  [i] Le icone PNG sono comunque disponibili")

    # Genera asset unplated per Windows taskbar
    print("\n[*] Generazione asset Windows unplated (previene backplate)...")
    unplated_success = generate_windows_unplated_assets(logo, ASSETS_DIR)

    if unplated_success:
        print(f"  [+] Asset unplated generati (16, 24, 32, 48, 256)")
        print(f"  [i] L'icona apparirà grande come Chrome/VS Code nella taskbar")
    else:
        print(f"  [!] Warning: Errore nella generazione asset unplated")

    print("\n[+] Generazione completata con successo!")
    print(f"\n[*] Icone salvate in:")
    print(f"   - {ASSETS_DIR}/")
    print(f"   - {ICONS_DIR}/")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("  Generatore Icone Applicazione - Controllo Stato NSIS")
    print("=" * 60)
    print()

    success = generate_icons()

    if not success:
        print("\n[-] Generazione icone fallita!")
        exit(1)

    print("\n" + "=" * 60)
    print("  Prossimi passi:")
    print("  1. Verifica le icone generate in assets/ e assets/icons/")
    print("  2. Ricompila l'applicazione con: npm run build")
    print("  3. L'icona apparira' nel menu Start e taskbar")
    print("=" * 60)
