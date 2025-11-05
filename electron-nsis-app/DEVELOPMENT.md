# Guida allo Sviluppo - Controllo Stato NSIS (Electron)

## Avvio dell'Applicazione in Sviluppo

### Problema Comune: ELECTRON_RUN_AS_NODE

Se durante l'avvio con `npm start` si verifica l'errore:

```
TypeError: Cannot read properties of undefined (reading 'on')
```

**Causa:** La variabile d'ambiente `ELECTRON_RUN_AS_NODE=1` è impostata nell'ambiente, facendo eseguire Electron come Node.js normale invece che come applicazione Electron. Questo causa `require('electron')` a restituire `undefined`.

**Soluzione Implementata:**

Il progetto include uno script PowerShell `start.ps1` che rimuove automaticamente la variabile prima di avviare Electron:

```bash
npm start
```

### Avvio Manuale (Alternativo)

Se preferisci avviare manualmente senza npm:

**PowerShell:**
```powershell
# Rimuovi la variabile
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue

# Avvia Electron
.\node_modules\.bin\electron.cmd .
```

**Bash (Git Bash su Windows):**
```bash
unset ELECTRON_RUN_AS_NODE
npm start
```

## Struttura del Progetto

```
electron-nsis-app/
├── main/                      # Main process (Node.js/Electron)
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
│       ├── store/            # Redux store
│       ├── hooks/            # Custom React hooks
│       ├── styles/           # CSS files
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
├── dist/                      # Build output (generato)
│   ├── main/                 # Main process compilato
│   └── renderer/             # Renderer bundle
│
├── start.ps1                  # Script avvio PowerShell
├── package.json
├── tsconfig.json
├── webpack.config.js
└── README.md
```

## Comandi Disponibili

### Sviluppo

```bash
# Avvia applicazione (usa start.ps1)
npm start

# Sviluppo con hot reload (3 terminali)
npm run dev

# O separatamente:
npm run dev:main      # Compila main in watch mode
npm run dev:renderer  # Avvia webpack-dev-server
npm start             # Avvia Electron
```

### Build

```bash
# Build completo
npm run build

# Build separati
npm run build:main      # Compila solo main process
npm run build:renderer  # Bundle solo renderer
```

### Packaging

```bash
# Crea installer Windows
npm run package

# Crea build unpacked (per testing)
npm run package:dir
```

### Testing

```bash
# Esegui tutti i test
npm test

# Test in watch mode
npm run test:watch

# Lint
npm run lint
```

## Workflow di Sviluppo

### Setup Iniziale

1. **Installa dipendenze:**
   ```bash
   npm install
   ```

2. **Verifica installazione Electron:**
   ```bash
   npx electron --version  # Dovrebbe mostrare v28.x.x
   ```

3. **Build iniziale:**
   ```bash
   npm run build
   ```

4. **Avvia applicazione:**
   ```bash
   npm start
   ```

### Sviluppo Quotidiano

1. **Apri 3 terminali:**

   **Terminal 1 - Main Process:**
   ```bash
   npm run dev:main
   ```
   Compila TypeScript del main process in watch mode.

   **Terminal 2 - Renderer:**
   ```bash
   npm run dev:renderer
   ```
   Avvia webpack-dev-server su http://localhost:3000

   **Terminal 3 - Electron:**
   ```bash
   npm start
   ```
   Avvia l'applicazione Electron.

2. **Modifiche:**
   - **Main process:** Riavvia Electron (Ctrl+C e `npm start`)
   - **Renderer:** Hot reload automatico (salva file e vedi cambiamenti)

### Debug

#### DevTools

Le DevTools si aprono automaticamente in modalità sviluppo. Per aprirle manualmente, aggiungi in `main/index.ts`:

```typescript
mainWindow.webContents.openDevTools();
```

#### Main Process Debug

Usa VS Code debugger con questa configurazione (`.vscode/launch.json`):

```json
{
  "type": "node",
  "request": "launch",
  "name": "Electron Main",
  "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/electron",
  "runtimeArgs": [".", "--remote-debugging-port=9223"],
  "windows": {
    "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/electron.cmd"
  }
}
```

#### Renderer Process Debug

Usa Chrome DevTools (F12) o:

```javascript
// In renderer console
console.log('Current state:', window.electronAPI);
```

## Variabili d'Ambiente

- `ELECTRON_RUN_AS_NODE`: **NON DEVE ESSERE IMPOSTATA** durante lo sviluppo
- `NODE_ENV`: Rilevata automaticamente tramite `process.env.NODE_ENV`

## Problemi Comuni

### 1. Electron non si avvia

**Errore:** `Cannot read properties of undefined (reading 'on')`

**Soluzione:** La variabile ELECTRON_RUN_AS_NODE è impostata. Lo script `start.ps1` dovrebbe risolverlo automaticamente. Se persiste:

```powershell
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
npm start
```

### 2. electron.exe non trovato

**Errore:** `electron: command not found` o simile

**Soluzione:** Reinstalla Electron:

```bash
npm install electron --force
```

Verifica che esista:
```bash
ls node_modules/electron/dist/electron.exe
```

### 3. TypeScript errori di compilazione

**Errore:** `Property 'electronAPI' does not exist on type 'Window'`

**Soluzione:** Verifica che esista `renderer/src/global.d.ts` con le definizioni dei tipi.

### 4. Webpack build fallisce

**Errore:** `Module build failed`

**Soluzione:**
- Verifica `tsconfig.renderer.json` abbia `"noEmit": false`
- Pulisci build: `rm -rf dist && npm run build`

### 5. Hot reload non funziona

**Soluzione:**
- Verifica che webpack-dev-server sia in esecuzione (`npm run dev:renderer`)
- Riavvia webpack-dev-server
- Controlla che main/index.ts carichi da `http://localhost:3000` in dev mode

## Best Practices

### Sicurezza

1. **Context Isolation:** Sempre abilitata
   ```typescript
   webPreferences: {
     contextIsolation: true,
     nodeIntegration: false
   }
   ```

2. **Preload Script:** Usa solo API esplicite
   ```typescript
   contextBridge.exposeInMainWorld('electronAPI', { /* ... */ });
   ```

3. **IPC:** Valida sempre i messaggi
   ```typescript
   ipcMain.handle('action', async (event, data) => {
     if (!isValid(data)) throw new Error('Invalid data');
     // ...
   });
   ```

### Performance

1. **Lazy Loading:** Carica componenti pesanti solo quando necessari
2. **Memoization:** Usa `useMemo` e `useCallback` in React
3. **Web Workers:** Per operazioni CPU-intensive
4. **Playwright:** Riutilizza browser instance

### Code Quality

1. **TypeScript:** Usa strict mode
2. **ESLint:** Lint prima di commit
3. **Testing:** Test coverage > 70%
4. **Git Hooks:** Pre-commit lint e test

## Riferimenti

- [Electron Documentation](https://www.electronjs.org/docs)
- [React Documentation](https://react.dev/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Playwright](https://playwright.dev/)
- [ExcelJS](https://github.com/exceljs/exceljs)

## Supporto

Per problemi o domande:
1. Controlla questa documentazione
2. Verifica [README.md](README.md)
3. Consulta i log della console
4. Contatta lo sviluppatore

## Changelog

### v1.0.0 (2025-01-04)
- Setup iniziale progetto Electron
- Migrazione da PyQt6
- Splash screen animata
- Main window con glassmorphism design
- Redux state management
- Script PowerShell per fix ELECTRON_RUN_AS_NODE
