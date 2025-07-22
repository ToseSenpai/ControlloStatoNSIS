# Controllo Stato NSIS

Applicazione desktop per il controllo dello stato delle spedizioni NSIS con interfaccia moderna e splash screen elegante.

## 🚀 Caratteristiche

- **Interfaccia Moderna**: Design pulito e professionale con PyQt6
- **Splash Screen**: Barra di caricamento elegante con animazioni fluide
- **Web Automation**: Integrazione con browser per controllo spedizioni
- **Gestione Excel**: Lettura e scrittura automatica di file Excel
- **Threading**: Operazioni asincrone per UI reattiva
- **Stato Machine**: Gestione avanzata degli stati dell'applicazione

## 📦 Installazione

### Prerequisiti
- Python 3.8+
- Windows 10/11

### Dipendenze
```bash
pip install -r requirements.txt
```

### Esecuzione
```bash
python main.py
```

## 🎯 Splash Screen

L'applicazione include una splash screen moderna con:
- **Barra di progresso** animata (5 secondi minimi)
- **Testi dinamici** che cambiano durante il caricamento
- **Design pulito** con colori DHL
- **Transizioni fluide** tra splash e applicazione principale

## 🏗️ Struttura del Progetto

```
ControlloStatoNSIS/
├── main.py                 # Entry point dell'applicazione
├── splash_screen_simple.py # Splash screen moderna
├── config.py              # Configurazione dell'applicazione
├── dati.xlsx              # File Excel per i dati
├── requirements.txt       # Dipendenze Python
├── main_window/           # Moduli dell'interfaccia principale
│   ├── app.py            # Applicazione principale
│   ├── ui_manager.py     # Gestione UI
│   ├── state_manager.py  # Gestione stati
│   ├── excel_handler.py  # Gestione Excel
│   ├── web_automation.py # Automazione web
│   └── worker.py         # Thread worker
├── assets/               # Risorse grafiche
├── fonts/               # Font personalizzati
├── icons/               # Icone SVG
└── dist/                # Eseguibile compilato
    └── ControlloStatoNSIS.exe
```

## 🔧 Compilazione

### Creazione Eseguibile
```bash
python -m PyInstaller --onefile --windowed --icon=icon.ico --name="ControlloStatoNSIS" --add-data="assets;assets" --add-data="fonts;fonts" --add-data="icons;icons" main.py
```

### Distribuzione
L'eseguibile è **portable** e può essere distribuito direttamente:
- Copia la cartella `dist/`
- Includi i file necessari (assets, fonts, icons, dati.xlsx, config.py)
- L'applicazione funziona senza installazione

## 🎨 Design

### Colori Principali
- **DHL Yellow**: #FFB800 (accent color)
- **Bianco**: #FFFFFF (background)
- **Grigio Scuro**: #212529 (text)
- **Grigio Chiaro**: #F8F9FA (progress background)

### Splash Screen
- **Dimensioni**: 400x250 pixel
- **Animazione**: 5 secondi con easing curve
- **Testi**: 7 step di caricamento dinamici
- **Progress Bar**: Gradiente giallo con bordi arrotondati

## 📝 Licenza

Progetto sviluppato da ST - Made with ❤️

## 🤝 Contributi

Per contribuire al progetto:
1. Fork del repository
2. Crea un branch per la feature
3. Commit delle modifiche
4. Push al branch
5. Crea una Pull Request

## 📞 Supporto

Per supporto tecnico o segnalazione bug, contatta lo sviluppatore.