# Controllo Stato Richiesta NSIS (v1.0)

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

## Struttura del Progetto

Il codice è stato suddiviso nei seguenti file, ognuno con una responsabilità specifica:

* **`README.md`**
    * **Contenuto:** Questo file. Fornisce una panoramica del progetto, la sua struttura e come eseguirlo.
    * **Scopo:** Documentazione principale per chiunque interagisca con il progetto.

* **`main.py`**
    * **Contenuto:** Punto di ingresso principale dell'applicazione. Contiene solo il blocco `if __name__ == '__main__':`.
    * **Scopo:** Inizializza l'oggetto `QtWidgets.QApplication`, importa la classe `App` da `main_window.py`, crea l'istanza della finestra principale, la visualizza (`window.show()`) e avvia il ciclo degli eventi (`app.exec()`). Isola la logica di avvio dell'applicazione.

* **`main_window.py`**
    * **Contenuto:** Definisce la classe principale `App(QtWidgets.QWidget)`, che rappresenta la finestra principale dell'applicazione.
    * **Scopo:** È il cuore logico e visivo dell'applicazione. Contiene:
        * La definizione della struttura dell'interfaccia utente (layout, pulsanti, area log, progress bar, badge, vista web).
        * La gestione degli eventi dell'interfaccia utente (es. click sui pulsanti "Avvia", "Interrompi", "Apri NSIS").
        * La logica per selezionare e leggere il file Excel (`pandas`).
        * Il coordinamento del ciclo di controllo dei codici, invocando i metodi per l'interazione web (`Workspace_state`).
        * L'aggiornamento in tempo reale dei widget della UI (log, progress bar, etichette di stato, contatori badge).
        * La gestione del salvataggio dei risultati sul file Excel (`openpyxl`).
        * L'inizializzazione e l'uso dei componenti definiti in `web_engine.py` e `ui_components.py`.

* **`config.py`**
    * **Contenuto:** Tutte le costanti globali utilizzate nell'applicazione.
    * **Scopo:** Centralizza valori di configurazione come:
        * Parametri per le operazioni web (es. `MAX_RETRIES`, `Workspace_TIMEOUT_MS`).
        * Selettori CSS/JavaScript per l'estrazione dei dati dalla pagina web.
        * Codici colore per l'interfaccia utente e i badge di stato.
        * Nomi delle colonne Excel target (per lettura e scrittura).
        * Indici di colonna di fallback.
        Questo facilita la modifica di questi valori senza dover cercare nel codice principale e migliora la leggibilità evitando stringhe/numeri "magici".

* **`web_engine.py`**
    * **Contenuto:** Classi `WebEnginePage(QtWebEngineCore.QWebEnginePage)` e `JSBridge(QtCore.QObject)`.
    * **Scopo:** Raggruppa le classi specificamente legate all'interazione avanzata con il componente `QtWebEngine`:
        * `WebEnginePage`: Personalizza il comportamento della pagina web caricata (es. gestione apertura nuove finestre).
        * `JSBridge`: Facilita la comunicazione bidirezionale tra il codice Python e il JavaScript eseguito nella pagina web, utilizzando `QWebChannel` per ricevere dati da JavaScript (come i risultati dell'estrazione).

* **`ui_components.py`**
    * **Contenuto:** Classi per widget GUI personalizzati, come `CustomProgressBar(QtWidgets.QProgressBar)`.
    * **Scopo:** Isola la definizione di componenti dell'interfaccia utente riutilizzabili o con logica di disegno complessa. Mantiene la definizione della UI principale (`main_window.py`) più pulita.

* **(Opzionale) `requirements.txt`**
    * **Contenuto:** Elenco delle dipendenze Python necessarie per eseguire il progetto.
    * **Scopo:** Permette una facile installazione delle librerie richieste tramite `pip install -r requirements.txt`.

## Requisiti

Per eseguire questa applicazione, è necessario avere installato:

* Python 3.x
* Le seguenti librerie Python:
    * `PyQt6`
    * `PyQt6-WebEngine`
    * `pandas`
    * `openpyxl`

È consigliabile installare le dipendenze usando `pip`:
```bash
pip install PyQt6 PyQt6-WebEngine pandas openpyxl