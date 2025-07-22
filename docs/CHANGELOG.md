# Changelog

Tutte le modifiche notevoli a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-XX

### Added
- 🆕 **Refactoring architetturale completo** - Suddivisione del codice in moduli specializzati
- 🆕 **Sistema di logging strutturato** con rotazione automatica
- 🆕 **Test unitari** per i moduli principali
- 🆕 **Configurazione per linting e formattazione** del codice
- 🆕 **Makefile** per automatizzare le operazioni comuni
- 🆕 **Script di deployment** automatizzato
- 🆕 **CI/CD pipeline** con GitHub Actions
- 🆕 **Gestione versioni** centralizzata
- 🆕 **Documentazione organizzata** nella cartella `docs/`

### Changed
- 🔄 **Migliorata la struttura del progetto** con package modulare
- 🔄 **Ottimizzato il sistema di gestione stati** con State Machine
- 🔄 **Migliorata la gestione degli errori** e logging
- 🔄 **Aggiornata l'interfaccia utente** con design system Luma

### Removed
- 🗑️ **Rimossi tutti i print di debug** dal codice sorgente
- 🗑️ **Eliminati file temporanei** (__pycache__, log files)
- 🗑️ **Rimossa dipendenza non utilizzata** (qtawesome)

### Fixed
- 🐛 **Corretti problemi di memoria** con la gestione dei thread
- 🐛 **Migliorata la stabilità** dell'automazione web
- 🐛 **Risolti problemi di compatibilità** con PyQt6

## [1.0.0] - 2023-XX-XX

### Added
- 🆕 **Prima versione dell'applicazione**
- 🆕 **Interfaccia grafica** con PyQt6
- 🆕 **Automazione web** per controllo stati NSIS
- 🆕 **Gestione file Excel** per input/output
- 🆕 **Barra di progresso** e contatori di stato
- 🆕 **Logging in tempo reale** dell'elaborazione

---

## Note di Sviluppo

### Convenzioni di Versioning
- **MAJOR.MINOR.PATCH** (es. 2.0.0)
- **MAJOR**: Cambiamenti incompatibili con le versioni precedenti
- **MINOR**: Nuove funzionalità compatibili con le versioni precedenti
- **PATCH**: Correzioni di bug compatibili con le versioni precedenti

### Emoji utilizzate
- 🆕 Added (nuove funzionalità)
- 🔄 Changed (modifiche a funzionalità esistenti)
- 🗑️ Removed (funzionalità rimosse)
- 🐛 Fixed (correzioni di bug)
- 🔧 Maintenance (manutenzione e miglioramenti) 