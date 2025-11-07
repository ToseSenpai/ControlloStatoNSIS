# Sistema Auto-Update - Guida Rapida

## ✅ Implementazione Completata

Il sistema di auto-update è stato implementato con successo usando **electron-updater** e **GitHub Releases**.

---

## 📋 Componenti Implementati

### Main Process
- ✅ Import di `electron-updater`
- ✅ Configurazione autoUpdater in `main/index.ts`
- ✅ Event listeners per tutti gli eventi di update
- ✅ Check automatico all'avvio (solo in production mode)

### IPC Handlers
- ✅ `get-app-version` - Ottiene la versione corrente
- ✅ `download-update` - Download manuale (opzionale)
- ✅ `install-update` - Installa e riavvia l'app

### Preload Bridge
- ✅ APIs esposte per renderer process
- ✅ Event listeners per update events
- ✅ Type-safe con TypeScript

### Renderer UI
- ✅ UpdateModal component (dark theme Discord-inspired)
- ✅ Redux slice per state management
- ✅ Progress bar animata
- ✅ Integrazione in MainWindow

### Configuration
- ✅ package.json configurato con GitHub publish settings
- ✅ Script `npm run package:publish` per release

---

## 🚀 Come Usare il Sistema

### 1. Build dell'Applicazione

```bash
cd electron-nsis-app

# Build completo
npm run build

# Package (crea installer)
npm run package
```

**Output**: `release/ControlloStatoNSIS-1.0.0-Setup.exe` e `latest.yml`

---

### 2. Creare Prima Release su GitHub

1. Vai su: https://github.com/ToseSenpai/ControlloStatoNSIS/releases

2. Click **"Draft a new release"**

3. Compila:
   - **Tag version**: `v1.0.0` ⚠️ **DEVE iniziare con 'v'**
   - **Release title**: `ControlloStatoNSIS v1.0.0`
   - **Description**:
     ```markdown
     ## 🎉 Prima Release

     ### Funzionalità
     - Controllo stato spedizioni NSIS
     - Interfaccia moderna con dark theme
     - Sistema auto-update integrato

     ### Download
     Scarica l'installer qui sotto e installalo.
     ```

4. **Upload File**:
   - Trascina `ControlloStatoNSIS-1.0.0-Setup.exe` dall'explorer
   - Trascina `latest.yml` dall'explorer

5. Seleziona:
   - ✅ **Set as the latest release**
   - ❌ This is a pre-release (lascia deselezionato)

6. Click **"Publish release"**

---

### 3. Pubblicare Aggiornamenti Futuri

#### Step 1: Incrementa Versione

Modifica `package.json`:
```json
{
  "version": "1.0.1"  // Era 1.0.0
}
```

#### Step 2: Fai le Modifiche al Codice

Implementa nuove feature, fix bug, ecc.

#### Step 3: Commit e Push

```bash
git add .
git commit -m "Versione 1.0.1 - Fix bug X, Aggiunto feature Y"
git push
```

#### Step 4: Build e Package

```bash
npm run build
npm run package
```

#### Step 5: Crea Nuova Release su GitHub

1. Vai su Releases → Draft a new release
2. Tag: `v1.0.1`
3. Title: `ControlloStatoNSIS v1.0.1`
4. Upload `ControlloStatoNSIS-1.0.1-Setup.exe` e `latest.yml`
5. Publish

---

## 🎯 Comportamento Auto-Update

### In Development Mode (`npm start`)
- ❌ Auto-update **DISABILITATO**
- Console mostra: "🔧 Development mode - skipping update check"

### In Production Mode (app installata)
- ✅ Auto-update **ABILITATO**
- Check automatico 3 secondi dopo l'avvio
- Download automatico in background
- Modal appare quando update disponibile
- Progress bar mostra avanzamento download
- Bottone "Installa e Riavvia" quando pronto

---

## 🔄 Flusso Utente Completo

```
1. User apre l'app
   ↓
2. App controlla updates (background)
   ↓
3. Update trovato → Modal appare
   "Versione 1.0.1 disponibile!"
   [Progress Bar: 0%]
   ↓
4. Download automatico
   [Progress Bar: 15% → 50% → 100%]
   ↓
5. Download completo
   ✅ "Aggiornamento pronto"
   [Bottone: Installa e Riavvia]
   ↓
6. User click bottone
   ↓
7. App chiude → Installer avvia → App riavvia
   ↓
8. Nuova versione attiva! ✅
```

---

## 📁 File Modificati/Creati

### File Creati
- `shared/types/update-types.ts` - TypeScript types
- `renderer/src/store/slices/update-slice.ts` - Redux state
- `renderer/src/components/UpdateModal.tsx` - UI component
- `renderer/src/components/UpdateModal.css` - Styling

### File Modificati
- `package.json` - Dependencies, scripts, publish config
- `main/index.ts` - autoUpdater logic
- `main/ipc-handlers.ts` - Update handlers
- `main/preload.ts` - IPC bridge
- `renderer/src/store/store.ts` - Redux store
- `renderer/src/components/MainWindow.tsx` - Integration
- `renderer/src/global.d.ts` - TypeScript definitions

---

## 🐛 Troubleshooting

### Update Non Rilevato

**Problema**: App non mostra notifica update

**Possibili Cause**:
1. Tag release non inizia con 'v' → Usa `v1.0.1` non `1.0.1`
2. File `latest.yml` non caricato su GitHub
3. Release non marcata come "Latest"
4. Versione app uguale a release (1.0.0 → 1.0.0)
5. Development mode attivo (usa installer, non `npm start`)

### Download Fallisce

**Problema**: Progress bar si blocca

**Soluzioni**:
1. Verifica connessione internet
2. Disabilita VPN/Proxy temporaneamente
3. Controlla firewall/antivirus
4. Verifica che file su GitHub non sia corrotto

### Errore 404

**Problema**: Console mostra errore 404

**Normale!** Significa che non ci sono release pubbliche. Crea la prima release su GitHub.

---

## 🔐 Security Best Practices

✅ **Implementato**:
- Context Isolation abilitato
- Node Integration disabilitato
- Content Security Policy configurato
- IPC Bridge sicuro (solo funzioni specifiche esposte)
- HTTPS per download (automatico con GitHub)
- Checksum verification SHA512 (automatico con electron-updater)

❌ **Non Implementato** (opzionale):
- Code Signing (richiede certificato ~$100-400/anno)
- Se implementato in futuro: nessun warning SmartScreen

---

## 📊 Version Management

Usa **Semantic Versioning** (SemVer):

```
MAJOR.MINOR.PATCH
  1  .  0  .  12

MAJOR: Breaking changes (1.0.0 → 2.0.0)
MINOR: New features (1.0.0 → 1.1.0)
PATCH: Bug fixes (1.0.0 → 1.0.1)
```

**Esempi**:
- Bug fix: `1.0.0` → `1.0.1`
- Nuova feature: `1.0.1` → `1.1.0`
- Breaking change: `1.1.0` → `2.0.0`

---

## 🎨 UI Personalizzata

Il modal di update usa il **dark theme Discord-inspired** dell'app:

- Background: Gradient `#2d3139` → `#36393f`
- Accent color: Blue gradient `#00b0ff` → `#0078d4`
- Font: Inter (modern, clean)
- Animazioni: Fade-in, slide-up
- Progress bar: Animata con glow effect
- Responsive: Si adatta a schermi piccoli

---

## 🔧 Comandi Utili

```bash
# Development
npm start

# Build
npm run build

# Package (senza publish)
npm run package

# Package e Publish su GitHub (richiede GH_TOKEN)
npm run package:publish
```

---

## 📝 Template Release Notes

```markdown
## 🚀 Novità in v1.0.1

### Nuove Funzionalità
- Aggiunta funzione X
- Implementato feature Y

### Miglioramenti
- Performance migliorate del 30%
- UI più responsive

### Bug Fix
- Corretto crash su Windows 11
- Risolto problema con timezone

### Tecnico
- Aggiornato electron a v28.3.3
- Migrato a electron-updater v6.6.2

---

### Installazione
- **Nuovi utenti**: Scarica installer qui sotto
- **Utenti esistenti**: L'app si aggiornerà automaticamente

### File
- **ControlloStatoNSIS-1.0.1-Setup.exe** (XXX MB) - Installer Windows

---

**Full Changelog**: https://github.com/ToseSenpai/ControlloStatoNSIS/compare/v1.0.0...v1.0.1
```

---

## ✅ Checklist Pre-Release

Prima di pubblicare una release, verifica:

- [ ] Version in `package.json` incrementata
- [ ] Codice testato localmente
- [ ] `npm run build` completato senza errori
- [ ] `npm run package` completato
- [ ] Installer testato su macchina pulita
- [ ] Tag release inizia con 'v' (es. `v1.0.1`)
- [ ] File `.exe` e `latest.yml` caricati
- [ ] Release marcata come "Latest"
- [ ] Release notes compilate
- [ ] Code committed e pushed su GitHub

---

## 📞 Supporto

Per problemi o domande:
- GitHub Issues: https://github.com/ToseSenpai/ControlloStatoNSIS/issues
- Documentazione electron-updater: https://www.electron.build/auto-update

---

**Versione Guida**: 1.0
**Data**: 2025-01-15
**Sistema**: electron-updater v6.6.2 + GitHub Releases
