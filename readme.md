# Controllo Stato Richiesta NSIS (v2.0.0)

## Descrizione

Questa applicazione desktop, sviluppata in Python (versione 3.x) e PyQt6, permette di automatizzare il controllo dello stato di richieste (presumibilmente sul sistema NSIS o un portale simile).

L'applicazione svolge le seguenti funzioni principali:
1.  Permette all'utente di selezionare un file Excel (`.xlsx`).
2.  Legge un elenco di codici di richiesta dalla colonna specificata ("Ricerca") nel file Excel.
3.  Per ciascun codice, utilizza un componente `QWebEngineView` integrato per navigare sulla pagina web pertinente e inserire il codice nel campo di ricerca.
4.  Estrae lo stato della richiesta e altri dati associati (protocollo, provvedimento, data, note, ecc.) dalla tabella dei risultati sulla pagina web.
5.  Aggiorna l'interfaccia utente in tempo reale mostrando lo stato dell'elaborazione, una barra di progresso, messaggi di log e contatori per i diversi stati trovati (Aperta, Chiusa, In Lavorazione, ecc.).
6.  Scrive i risultati ottenuti (Stato, Protocollo, Provvedimento, Data, Note) nelle colonne corrispondenti del file Excel originale, accanto a ciascun codice di ricerca.

L'applicazione è stata refactoring da un singolo script a una struttura multi-file per migliorare l'organizzazione, la leggibilità e la manutenibilità del codice.

## 🧹 Pulizia del Progetto

Il progetto è stato recentemente pulito e ottimizzato:

- ✅ **Rimossi tutti i print di debug** dal codice sorgente
- ✅ **Eliminati file temporanei** (__pycache__, log files)
- ✅ **Organizzata la documentazione** nella cartella `docs/`
- ✅ **Aggiunta configurazione per linting** e formattazione del codice
- ✅ **Creati file di test** per i moduli principali
- ✅ **Configurato logging strutturato** con rotazione automatica
- ✅ **Aggiunto Makefile** per automatizzare le operazioni comuni
- ✅ **Rimossa dipendenza non utilizzata** (qtawesome)

## Struttura del Progetto

Il codice è stato suddiviso nei seguenti file, ognuno con una responsabilità specifica:

* **`README.md`**
    * **Contenuto:** Questo file. Fornisce una panoramica del progetto, la sua struttura e come eseguirlo.
    * **Scopo:** Documentazione principale per chiunque interagisca con il progetto.

* **`main.py`**
    * **Contenuto:** Punto di ingresso principale dell'applicazione. Contiene solo il blocco `if __name__ == '__main__':`.
    * **Scopo:** Inizializza l'oggetto `QtWidgets.QApplication`, importa la classe `App` da `main_window.py`, crea l'istanza della finestra principale, la visualizza (`window.show()`) e avvia il ciclo degli eventi (`app.exec()`). Isola la logica di avvio dell'applicazione.

* **`main_window/`**
    * **Contenuto:** Package modulare contenente tutti i componenti dell'applicazione.
    * **Scopo:** Organizza il codice in moduli specializzati per migliorare la manutenibilità.

* **`config.py`**
    * **Contenuto:** Tutte le costanti globali utilizzate nell'applicazione.
    * **Scopo:** Centralizza valori di configurazione come:
        * Parametri per le operazioni web (es. `MAX_RETRIES`, `FETCH_TIMEOUT_MS`).
        * Selettori CSS/JavaScript per l'estrazione dei dati dalla pagina web.
        * Codici colore per l'interfaccia utente e i badge di stato.
        * Nomi delle colonne Excel target (per lettura e scrittura).
        * Indici di colonna di fallback.
        Questo facilita la modifica di questi valori senza dover cercare nel codice principale e migliora la leggibilità evitando stringhe/numeri "magici".

* **`requirements.txt`**
    * **Contenuto:** Elenco delle dipendenze Python necessarie per eseguire il progetto.
    * **Scopo:** Permette una facile installazione delle librerie richieste tramite `pip install -r requirements.txt`.

* **`docs/`**
    * **Contenuto:** Documentazione del progetto (report di refactoring, guide, etc.).
    * **Scopo:** Organizza tutti i file di documentazione in un'unica cartella.

* **`tests/`**
    * **Contenuto:** Test unitari e di integrazione per i moduli principali.
    * **Scopo:** Garantisce la qualità del codice e facilita il debugging.

* **`logging_config.py`**
    * **Contenuto:** Configurazione centralizzata per il logging dell'applicazione.
    * **Scopo:** Gestisce i log con rotazione automatica e formattazione strutturata.

* **`pyproject.toml`**
    * **Contenuto:** Configurazione del progetto Python con impostazioni per linting e testing.
    * **Scopo:** Standardizza la configurazione per strumenti di sviluppo.

* **`Makefile`**
    * **Contenuto:** Comandi automatizzati per operazioni comuni del progetto.
    * **Scopo:** Semplifica lo sviluppo e il deployment.

## Requisiti

Per eseguire questa applicazione, è necessario avere installato:

* **Windows 10 o superiore** (64-bit)
* Python 3.8 o superiore
* Le seguenti librerie Python:
    * `PyQt6`
    * `PyQt6-WebEngine`
    * `openpyxl`

### Requisiti di Sistema
* **Sistema Operativo**: Windows 10/11 (64-bit)
* **RAM**: Minimo 4GB, Consigliato 8GB
* **Spazio Disco**: Minimo 500MB liberi
* **Risoluzione**: Minimo 1024x768
* **Browser**: Chrome o Edge (per l'automazione web)

È consigliabile installare le dipendenze usando `pip`:
```bash
pip install -r requirements.txt
```

## 🚀 Sviluppo

### Installazione dipendenze di sviluppo
```bash
make install-dev
```

### Esecuzione test
```bash
make test
```

### Formattazione codice
```bash
make format
```

### Controllo qualità codice
```bash
make lint
```

### Pulizia progetto
```bash
make clean
```

### Esecuzione applicazione
```bash
make run
```

### Creazione installer Windows
```bash
make installer
```
**Nota**: Richiede Inno Setup 6 installato.

## 📝 Logging

L'applicazione utilizza un sistema di logging strutturato:
- I log vengono salvati in `%APPDATA%\ControlloStatoNSIS\logs\` con timestamp
- Rotazione automatica dei file di log
- Configurazione centralizzata in `logging_config.py`

## 🪟 Configurazione Windows

L'applicazione è ottimizzata per Windows con:
- **High DPI Awareness** per schermi ad alta risoluzione
- **Integrazione con AppData** per configurazioni e log
- **Supporto per Windows 10/11** con temi nativi
- **Installer professionale** con Inno Setup