# ControlloStatoNSIS

![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Applicazione desktop Electron per il controllo automatizzato dello stato delle pratiche NSIS (Nucleo Speciale Importazioni Speciali) su **impresa.gov.it**.

## 🎯 Caratteristiche Principali

### Automazione Completa
- ⚡ **Controllo automatico pratiche NSIS** - Elaborazione batch di codici pratiche
- 📊 **Gestione Excel integrata** - Lettura e scrittura automatica con ExcelJS
- 🌐 **Web automation** - Navigazione automatica su impresa.gov.it
- 🔄 **Auto-update** - Sistema di aggiornamento automatico via GitHub Releases

### Interfaccia Moderna
- 🎨 **Windows 11 Fluent Design** - Interfaccia nativa con effetti acrilici
- 🌙 **Dark theme Discord-inspired** - Design moderno con glassmorphism
- 📱 **Dashboard interattiva** - Statistiche in tempo reale con animazioni smooth
- 🏷️ **Icona CHECK NOS brandizzata** - Logo DHL-inspired giallo e rosso

### Sistema Robusto
- 🔐 **Esecuzione senza privilegi admin** - Installazione user-level
- 📦 **Package NSIS ottimizzato** - Installer moderno con scelta directory
- 🛡️ **Error logging avanzato** - Crash log e debug completo
- 🔄 **Persistent/Memory session fallback** - Resiliente a problemi di permessi

## 📸 Screenshot

> Interfaccia principale con dashboard statistiche e webview integrato

## 🚀 Installazione

### Download

Scarica l'installer dall'ultima release:

**[📥 Download ControlloStatoNSIS v1.0.3](https://github.com/ToseSenpai/ControlloStatoNSIS/releases/latest)**

### Installazione Rapida

1. Esegui `ControlloStatoNSIS-1.0.3-Setup.exe`
2. Scegli la directory di installazione (opzionale)
3. Attendi il completamento
4. L'app si avvierà automaticamente

> **Nota**: Non sono richiesti privilegi amministrativi

## 📖 Come Usare

1. **Avvia l'applicazione** - Click sull'icona desktop o menu Start
2. **Carica file Excel** - Click su "Scegli File Excel" e seleziona il file con i codici pratiche
3. **Avvia elaborazione** - L'app legge i codici dalla colonna "ricerca"
4. **Monitora progresso** - Dashboard mostra statistiche in tempo reale (Aperte, Chiuse, In Lavorazione, ecc.)
5. **Risultati automatici** - I dati vengono scritti automaticamente nel file Excel

### Colonne Excel Elaborate

L'app scrive questi dati per ogni pratica:
- Taric
- Stato
- Protocollo ingresso
- Inserita il
- Protocollo uscita
- Provvedimento
- Data Provvedimento
- Codice richiesta
- Tipo pratica
- Note USMAF
- Invio SUD

## 🛠️ Sviluppo

### Requisiti

- Node.js 18+ e npm
- Python 3.8+ (per generazione icone)
- Windows 10/11

### Setup

```bash
# Clona il repository
git clone https://github.com/ToseSenpai/ControlloStatoNSIS.git
cd ControlloStatoNSIS

# Naviga nell'app Electron
cd electron-nsis-app

# Installa dipendenze
npm install

# Avvia in modalità sviluppo
npm start
```

### Build

```bash
# Build completo (main + renderer)
npm run build

# Package installer Windows
npm run package

# L'installer sarà in: electron-nsis-app/release/
```

### Generazione Icone

```bash
# Genera icone Windows da logo sorgente
cd electron-nsis-app/scripts
python generate_app_icons.py

# Output: assets/icon.ico, assets/icons/*.png
```

## 🏗️ Architettura

### Stack Tecnologico

| Tecnologia | Versione | Uso |
|------------|----------|-----|
| **Electron** | 28.3.3 | Desktop framework |
| **React** | 18.2.0 | UI library |
| **TypeScript** | 5.3.0 | Type safety |
| **Redux Toolkit** | 2.0.0 | State management |
| **Webpack** | 5.89.0 | Module bundler |
| **ExcelJS** | 4.4.0 | Excel processing |
| **electron-updater** | 6.6.2 | Auto-update system |
| **Lucide React** | 0.552.0 | Icon library |

### Struttura Progetto

```
ControlloStatoNSIS/
├── electron-nsis-app/              # App Electron principale
│   ├── main/                       # Processo main Electron
│   │   ├── index.ts               # Entry point
│   │   ├── ipc-handlers.ts        # IPC communication
│   │   ├── browser-view-manager.ts # WebView automation
│   │   ├── excel/                 # Excel handler
│   │   └── workers/               # Worker threads
│   ├── renderer/                   # Processo renderer (UI)
│   │   ├── src/
│   │   │   ├── components/        # React components
│   │   │   │   ├── MainWindow.tsx
│   │   │   │   ├── SplashScreen.tsx
│   │   │   │   └── UpdateModal.tsx # Auto-update UI
│   │   │   ├── store/             # Redux store
│   │   │   │   └── slices/
│   │   │   │       └── update-slice.ts
│   │   │   └── styles/            # Global CSS
│   │   └── index.html
│   ├── shared/                     # Codice condiviso
│   │   ├── constants/config.ts
│   │   └── types/update-types.ts
│   ├── assets/                     # Icone e risorse
│   │   ├── icon.ico               # Icon CHECK NOS
│   │   └── icons/                 # Multi-size icons
│   ├── scripts/                    # Build scripts
│   │   └── generate_app_icons.py
│   └── package.json
├── AUTO_UPDATE_README.md           # Documentazione auto-update
├── AUTO_UPDATE_GUIDE.md            # Guida completa (1600 righe)
└── readme.md                       # Questo file
```

## 🔄 Sistema Auto-Update

L'applicazione controlla automaticamente gli aggiornamenti all'avvio:

1. **Check automatico** - Dopo 3 secondi dall'avvio (solo in production)
2. **Download in background** - Progress bar con percentuale
3. **Notifica utente** - Modal con "Installa e Riavvia"
4. **Installazione automatica** - Update e restart trasparente

### Per Sviluppatori

Vedi la documentazione completa in [AUTO_UPDATE_README.md](electron-nsis-app/AUTO_UPDATE_README.md)

**Processo di release:**

```bash
# 1. Incrementa versione in package.json
# 2. Build e package
npm run build && npm run package

# 3. Crea release su GitHub con tag vX.X.X
# 4. Carica Setup.exe e latest.yml
# 5. Gli utenti ricevono l'update automaticamente
```

## 🎨 Design System

### Colori Brand (DHL-inspired)

- **Primary Yellow**: `#FFC107` - Pulsanti, highlights
- **Accent Red**: `#F04747` - Badges, errori
- **Dark Background**: `#36393f` - Sfondo principale
- **Card Background**: `#2f3136` - Pannelli e card

### Design Patterns

- **Status strips** - Barre orizzontali 36px con bordo colorato
- **Glassmorphism** - Effetti acrilici con backdrop-blur
- **Animated counters** - Numeri con transizione smooth 500ms
- **Progress overlay** - Fullscreen con blur e GIF loading

## 📝 Script Disponibili

```bash
npm start                  # Dev mode (webpack-dev-server + Electron)
npm run build              # Build completo (main + renderer)
npm run build:main         # Build solo main process
npm run build:renderer     # Build solo renderer
npm run package            # Crea installer Windows (release/)
npm run package:publish    # Package e pubblica su GitHub
```

## 🐛 Troubleshooting

### L'app non si avvia senza admin

Se l'app richiede privilegi amministrativi:

1. Disinstalla completamente
2. Pulisci cache icone Windows:
   ```powershell
   ie4uinit.exe -show
   ie4uinit.exe -ClearIconCache
   ```
3. Riavvia Windows Explorer: `taskkill /f /im explorer.exe && start explorer.exe`
4. Reinstalla la versione più recente

### Auto-update non funziona

- Verifica che il repository GitHub sia pubblico
- Controlla che la release sia marcata come "Latest"
- Assicurati che `latest.yml` sia caricato negli assets
- Controlla console browser (F12) per errori

### Icone non aggiornate

Windows cacha pesantemente le icone. Soluzioni:

1. Riavvia Windows
2. Pulisci cache: `del /F /Q "%localappdata%\IconCache.db"`
3. Disinstalla e reinstalla l'app

## 📄 Licenza

MIT License

Copyright (c) 2024 ST

## 🙏 Credits

- **Sviluppo**: ST
- **Icone**: CHECK NOS branding (DHL-inspired)
- **Framework**: Electron, React, TypeScript
- **Icons library**: Lucide React
- **Build con**: Claude Code

---

**Made with ❤️ using Electron + React + TypeScript**

> Per domande o supporto, apri un issue su GitHub
