# Controllo Stato NSIS - Electron Edition

Applicazione desktop per il controllo dello stato delle spedizioni NSIS con interfaccia moderna Electron + React.

## 🚀 Caratteristiche

- **Interfaccia Moderna**: Design glassmorphism con React + TypeScript
- **Splash Screen Elegante**: Barra di caricamento animata con transizioni fluide
- **Web Automation**: Playwright per controllo spedizioni automatizzato
- **Gestione Excel**: ExcelJS per lettura/scrittura file Excel
- **State Management**: Redux Toolkit per gestione stato applicazione
- **IPC Communication**: Comunicazione sicura tra main e renderer process
- **Frameless Window**: Finestra personalizzata con controlli custom

## 📦 Tecnologie

### Frontend (Renderer Process)
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Redux Toolkit** - State management
- **CSS Modules** - Styling con glassmorphism

### Backend (Main Process)
- **Electron 28** - Desktop framework
- **Playwright** - Web automation
- **ExcelJS** - Excel manipulation
- **Node.js** - Runtime

### Build Tools
- **Webpack** - Module bundler
- **electron-builder** - Packaging e distribuzione
- **TypeScript Compiler** - Transpilation

## 🛠️ Setup Sviluppo

### Prerequisiti
- Node.js 18+ (consigliato 20+)
- npm o yarn
- Windows 10/11

### Installazione Dipendenze

```bash
cd electron-nsis-app
npm install
```

### Avvio in Modalità Sviluppo

```bash
# Terminal 1: Compila main process in watch mode
npm run dev:main

# Terminal 2: Avvia webpack dev server per renderer
npm run dev:renderer

# Terminal 3: Avvia Electron
npm start
```

Oppure usa concurrently (avvia tutto insieme):

```bash
npm run dev
```

## 🏗️ Struttura Progetto

```
electron-nsis-app/
├── main/                      # Main process (Node.js)
│   ├── index.ts              # Entry point Electron
│   ├── preload.ts            # Preload script per context isolation
│   ├── ipc-handlers.ts       # IPC message handlers
│   ├── automation/           # Web automation con Playwright
│   ├── excel/                # Gestione Excel con ExcelJS
│   ├── workers/              # Worker threads
│   └── state/                # State management
│
├── renderer/                  # Renderer process (React)
│   ├── index.html            # HTML entry point
│   └── src/
│       ├── index.tsx         # React entry point
│       ├── App.tsx           # App principale
│       ├── components/       # Componenti React
│       │   ├── SplashScreen.tsx
│       │   ├── MainWindow.tsx
│       │   ├── WindowControls.tsx
│       │   ├── FileSection.tsx       (TODO)
│       │   ├── ControlsSection.tsx   (TODO)
│       │   ├── StatisticsSection.tsx (TODO)
│       │   ├── ProgressOverlay.tsx   (TODO)
│       │   └── WebView.tsx           (TODO)
│       ├── store/            # Redux store
│       │   ├── store.ts
│       │   └── slices/
│       │       ├── app-slice.ts
│       │       ├── ui-slice.ts
│       │       └── data-slice.ts
│       ├── hooks/            # Custom React hooks
│       ├── styles/           # CSS files
│       │   └── global.css
│       └── utils/            # Utility functions
│
├── shared/                    # Codice condiviso
│   ├── types/                # TypeScript types
│   └── constants/            # Costanti condivise
│
├── assets/                    # Risorse
│   ├── fonts/
│   ├── icons/
│   └── splash/
│
├── package.json
├── tsconfig.json
├── tsconfig.main.json
├── tsconfig.renderer.json
├── webpack.config.js
└── README.md
```

## 🔧 Build e Packaging

### Build Completo

```bash
npm run build
```

Compila sia main che renderer process nella cartella `dist/`.

### Creazione Eseguibile Windows

```bash
npm run package
```

Crea installer nella cartella `release/`.

### Build Solo Directory (per testing)

```bash
npm run package:dir
```

Crea build unpacked in `release/` senza creare installer.

## 📝 Comandi Disponibili

| Comando | Descrizione |
|---------|-------------|
| `npm start` | Avvia Electron in modalità produzione |
| `npm run dev` | Avvia tutti i servizi dev (main + renderer + electron) |
| `npm run dev:main` | Compila main process in watch mode |
| `npm run dev:renderer` | Avvia webpack-dev-server per renderer |
| `npm run build` | Build completo (main + renderer) |
| `npm run build:main` | Build solo main process |
| `npm run build:renderer` | Build solo renderer process |
| `npm run package` | Crea installer Windows |
| `npm run package:dir` | Crea build unpacked |
| `npm test` | Esegui test con Jest |
| `npm run lint` | Lint con ESLint |

## 🎨 Design System

### Colori
- **DHL Yellow**: `#FFB800` (accent color principale)
- **White**: `#FFFFFF` (background)
- **Gray Scale**: Da `#F8F9FA` a `#212529`

### Glassmorphism
- Backdrop filter con blur(10-15px)
- Background rgba con opacity 0.7-0.9
- Bordi bianchi semi-trasparenti
- Shadow elevate per depth

### Animazioni
- Durate: 150ms (fast), 250ms (base), 350ms (slow)
- Easing: cubic-bezier per transizioni smooth
- Fade in, slide up, pulse per elementi chiave

## 📋 Roadmap

### Fase 1: Setup Base ✅
- [x] Struttura progetto Electron
- [x] Configurazione TypeScript
- [x] Setup React + Redux
- [x] Splash screen funzionante
- [x] Main window base con frameless

### Fase 2: Componenti UI (In Progress)
- [ ] FileSection - selezione file Excel
- [ ] ControlsSection - avvia/ferma processing
- [ ] StatisticsSection - badge con conteggi
- [ ] ProgressOverlay - overlay durante processing
- [ ] WebView - visualizzazione browser (opzionale)
- [ ] LogArea - area log con toggle

### Fase 3: Excel Handler
- [ ] Lettura file Excel con ExcelJS
- [ ] Ricerca colonna "PRATICA"
- [ ] Estrazione codici
- [ ] Scrittura risultati
- [ ] Gestione errori file

### Fase 4: Web Automation
- [ ] Setup Playwright
- [ ] Navigazione sito NSIS
- [ ] Form filling automatico
- [ ] Estrazione dati risultati
- [ ] Retry logic e error handling

### Fase 5: Processing Logic
- [ ] Worker thread per processing
- [ ] Loop codici con progress tracking
- [ ] IPC events per UI updates
- [ ] Aggregazione statistiche
- [ ] Save risultati in Excel

### Fase 6: Testing & Refinement
- [ ] Unit tests (Jest)
- [ ] Integration tests
- [ ] E2E tests (Playwright)
- [ ] Performance optimization
- [ ] Bug fixes

### Fase 7: Packaging & Deploy
- [ ] electron-builder config finale
- [ ] Icone e assets
- [ ] Installer Windows
- [ ] Auto-update (opzionale)
- [ ] Documentazione utente

## 🐛 Debug

### Electron DevTools
In modalità sviluppo, le DevTools si aprono automaticamente. Per aprirle manualmente:

```javascript
mainWindow.webContents.openDevTools();
```

### Main Process Debug
Usa VS Code debugger con configurazione:

```json
{
  "type": "node",
  "request": "launch",
  "name": "Electron Main",
  "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/electron",
  "args": ["./dist/main/index.js"],
  "outputCapture": "std"
}
```

## 🤝 Contributi

Progetto sviluppato da ST per migrazione da PyQt6 a Electron.

## 📞 Supporto

Per supporto tecnico o segnalazione bug, contatta lo sviluppatore.

## 📄 Licenza

MIT
