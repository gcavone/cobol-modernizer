# Output: output
*Generato il 2026-04-02 09:51:26*

**Richiesta utente:** Analizza il codice COBOL ed estrai le business rules

---

# ANALISI DISCOVERY AGENT — SISTEMA SUPERMARKET LEGACY COBOL

---

## PARTE 1 — SPIEGAZIONE NARRATIVA

### Cosa fa il sistema

Questo è un gestionale per supermercati scritto in COBOL che gestisce tre funzioni principali: amministrazione dei prodotti (aggiunta/eliminazione), calcolo stipendi dipendenti e profitti, e un modulo di acquisto per i clienti. Il sistema utilizza autenticazione hardcodata per l'accesso admin e memorizza i dati su file di testo piatto (DATABASE.txt e products.txt).

### Come funziona — flusso principale

1. **Menu principale**: L'utente sceglie tra Amministratore, Buyer o Esci
2. **Accesso Amministratore**: Richiede email (robby@gmail.com) e password (robby@123) hardcodate
3. **Menu Admin**: Offre quattro opzioni:
   - Calcolo stipendi dipendenti (nome, ID, ore lavorate)
   - Modifica prodotti (aggiunta/eliminazione)
   - Calcolo profitti (COGS vs prezzo di vendita)
   - Ritorno al menu principale
4. **Flusso Buyer**: Visualizza lista prodotti da file, consente di ordinare più articoli, calcola totale e resto
5. **Gestione file**: Legge da DATABASE.txt (record 60 caratteri), scrive modifiche sullo stesso file

### Le logiche di business principali

- **Calcolo stipendio**: `SALARY = HOURLY_RATE (500 PHP fisso) × HOURS_WORKED`
- **Calcolo profitto**: `PROFIT = SELLING_PRICE − COGS`
- **Calcolo resto**: `CHANGE = MONEY_PAID − TOTAL_AMOUNT`
- **Struttura prodotto**: Codice 8 cifre + Nome 37 caratteri + Unità 7 caratteri + Prezzo 8 cifre (totale 60 char)
- **Ordine multiplo**: Consente di ordinare fino a 100 prodotti per transazione
- **Conteggio prodotti**: Conta i record letti dal file per visualizzare il catalogo

### I problemi principali del codice legacy

1. **Credenziali hardcodate**: Email e password admin sono scritte direttamente nel codice sorgente (ADMIN-INFO section). Chiunque acceda al codice può leggere le credenziali.

2. **Duplicazione massiccia di codice**: Le routine di continuazione (SALARY-CONTINUE-ROUTINE, PROFIT-CONTINUE-ROUTINE) sono identiche e ripetute. Stessa cosa per RECEIPT-ROUTINE che appare in due moduli diversi.

3. **Gestione file difettosa**: La routine MAIN-ROUTINE legge il file e lo riscrive senza logica chiara. La condizione `IF DELETE-PRODUCT-CODE NOT EQUAL TO PCODE-IN` è sempre vera all'inizio (DELETE-PRODUCT-CODE non è inizializzato), causando duplicazione di tutti i record.

4. **Incoerenza nei percorsi file**: ACCOUNTING_SYSTEM.COB usa `G:\Cobol\DATABASE.TXT` mentre BUYROUTINE.COB usa `C:\Cobol\products.TXT`. I due moduli non condividono la stessa fonte dati.

5. **Dati corrotti nel DATABASE.txt**: Ci sono record duplicati (ogni prodotto appare 2 volte), record incompleti (Luncheon Meat manca il prezzo), e record malformati (Ketchup e Pepper hanno prezzi in formato errato: 00007000 invece di 70.00).

6. **Variabili non inizializzate**: EOFSW non è sempre resettato tra le operazioni, causando comportamenti imprevisti quando si eseguono più operazioni consecutive.

7. **Mancanza di validazione input**: Non ci sono controlli su input utente (es. ore negative, prezzi negativi, codici prodotto duplicati).

8. **Logica di eliminazione prodotto incompleta**: REMOVE-ROUTINE legge il file ma non lo chiude correttamente, e non resetta EOFSW prima di leggere.

9. **Typo nel codice**: "ADMISNISTRATOR-ROUTINE" è scritto male (manca una 'I'), creando confusione nei nomi delle routine.

10. **Nessuna persistenza dati per ordini**: Gli ordini inseriti nel RECEIPT-ROUTINE non vengono salvati su file; vengono solo visualizzati a schermo.

### Cosa si guadagna con la modernizzazione

- **Sicurezza**: Spostare credenziali in file di configurazione esterni o database con hashing
- **Manutenibilità**: Eliminare duplicazione di codice con funzioni riutilizzabili e librerie comuni
- **Integrità dati**: Usare un database relazionale (SQL) invece di file piatti, con vincoli di integrità
- **Coerenza**: Unificare i due moduli in un'unica applicazione con una sola fonte di dati
- **Validazione**: Aggiungere controlli su input (range, formato, unicità)
- **Audit trail**: Registrare tutte le operazioni (login, modifiche prodotti, ordini) per tracciabilità
- **Scalabilità**: Passare da COBOL a un linguaggio moderno (Java, Python, C#) con framework web
- **User experience**: Interfaccia grafica moderna invece di schermate testuali posizionate

---

## PARTE 2 — ANALISI TECNICA

### Business Rules Estratte

| # | Regola | Formula/Logica | Modulo | Stato |
|---|--------|---|--------|-------|
| 1 | Calcolo Stipendio Dipendente | `SALARY = HOURLY_RATE × HOURS_WORKED` | ACCOUNTING_SYSTEM.COB | ✓ Implementato |
| 2 | Tariffa Oraria Fissa | `HOURLY_RATE = 500 PHP` | ACCOUNTING_SYSTEM.COB | ⚠ Hardcodata |
| 3 | Calcolo Profitto | `PROFIT = SELLING_PRICE − COGS` | ACCOUNTING_SYSTEM.COB | ✓ Implementato |
| 4 | Calcolo Resto Transazione | `CHANGE = MONEY_PAID − TOTAL_AMOUNT` | ACCOUNTING_SYSTEM.COB, BUYROUTINE.COB | ✓ Implementato |
| 5 | Somma Totale Ordine | `TOTAL = Σ(PPRICE[i])` per i=1 a ORD | ACCOUNTING_SYSTEM.COB, BUYROUTINE.COB | ✓ Implementato |
| 6 | Autenticazione Admin | Email = "robby@gmail.com" AND Password = "robby@123" | ACCOUNTING_SYSTEM.COB | ⚠ Hardcodata |
| 7 | Eliminazione Prodotto | Se `DELETE-PRODUCT-CODE = PCODE-IN`, non scrivere record | ACCOUNTING_SYSTEM.COB | ❌ Difettosa |
| 8 | Limite Ordini | Max 100 prodotti per transazione (OCCURS 100 TIMES) | ACCOUNTING_SYSTEM.COB, BUYROUTINE.COB | ✓ Implementato |
| 9 | Formato Record Prodotto | 60 caratteri: PCODE(8) + PNAME(37) + UNIT(7) + PRICE(8) | ACCOUNTING_SYSTEM.COB | ✓ Definito |
| 10 | Conteggio Prodotti Catalogo | Incrementa REC-COUNTER per ogni record letto | ACCOUNTING_SYSTEM.COB, BUYROUTINE.COB | ✓ Implementato |

---

### Strutture Dati

#### Tabella 1: Record Prodotto (File)

| Campo COBOL | Tipo | Dimensione | Descrizione | Valore Esempio |
|---|---|---|---|---|
| PCODE-IN / PROD-CODE | PIC 9(8) | 8 cifre | Codice prodotto univoco | 00000001 |
| PNAME-IN / PROD-NAME | PIC X(37) | 37 caratteri | Nome prodotto | "Canned Sardines" |
| UNIT-IN / PROD-UNIT | PIC X(7) | 7 caratteri | Unità di misura | "155g" |
| PRICE-IN / PROD-PRICE | PIC 9(8) o S9(4)V9(2) | 8 cifre o 6+2 decimali | Prezzo unitario | 18.75 |

#### Tabella 2: Strutture Working Storage — Amministrazione

| Variabile COBOL | Tipo | Dimensione | Scopo | Valore Iniziale |
|---|---|---|---|---|
| EMAIL (ADMIN-INFO) | PIC X(15) | 15 char | Email admin | "robby@gmail.com" |
| ADMIN-PASSWORD | PIC X(9) | 9 char | Password admin | "robby@123" |
| EMPLOYEE-NAME | PIC X(50) | 50 char | Nome dipendente | (input) |
| EMPLOYEE-ID | PIC X(10) | 10 char | ID dipendente | (input) |
| HOURLY-RATE | PIC 9(5) | 5 cifre | Tariffa oraria PHP | 500 |
| HOURS-WORKED | PIC 99 | 2 cifre | Ore lavorate | (input) |
| SALARY | PIC 9(6) | 6 cifre | Stipendio calcolato | (calcolato) |
| COGS | PIC 9(6)V99 | 6+2 decimali | Costo merce venduta | (input) |
| SELLING-PRICE | PIC 9(6)V99 | 6+2 decimali | Prezzo di vendita | (input) |
| PROFIT | PIC 9(6)V99 | 6+2 decimali | Profitto calcolato | (calcolato) |

#### Tabella 3: Strutture Working Storage — Ordini

| Variabile COBOL | Tipo | Dimensione | Scopo | Valore Iniziale |
|---|---|---|---|---|
| ORD | PIC 9(2) | 2 cifre | Numero di prodotti ordinati | (input) |
| PPCODE(I) | PIC X(9) OCCURS 100 | 9 char × 100 | Array codici prodotto | (input) |
| PPNAME(I) | PIC X(37) OCCURS 100 | 37 char × 100 | Array nomi prodotto | (input) |
| PPUNIT(I) | PIC X(7) OCCURS 100 | 7 char × 100 | Array unità | (input) |
| PPRICE(I) | PIC 9(4)V9(2) OCCURS 100 | 6+2 decimali × 100 | Array prezzi | (input) |
| TOTAL | PIC 9(4)V9(2) | 6+2 decimali | Totale ordine | 0 |
| MONEY | PIC 9(4)V9(2) | 6+2 decimali | Importo pagato | (input) |
| CHANGE | PIC 9(4)V9(2) | 6+2 decimali | Resto calcolato | (calcolato) |
| I | PIC 9(2) | 2 cifre | Contatore loop | 0 |

#### Tabella 4: Variabili di Controllo

| Variabile COBOL | Tipo | Scopo | Valore Iniziale |
|---|---|---|---|
| EOFSW | PIC X | Flag fine file | 'N' |
| REC-COUNTER | PIC 9(3) | Contatore record letti | 0 |
| CHOICE | PIC 9 | Scelta menu utente | (input) |
| ANSWER | PIC X | Risposta Y/N | (input) |
| DELETE-PRODUCT-CODE | PIC 9(8) | Codice prodotto da eliminare | (input) |
| TOKEN | PIC 9 | Variabile temporanea | (non usata) |

---

### Flussi Utente

#### Flusso 1: Accesso Amministratore

```
START
  ↓
[MAIN-ROUTINE] Apri file DATABASE.txt
  ↓
[INIT-ROUTINE] Mostra menu principale
  ↓
Utente sceglie opzione 1 (ADMINISTRATOR)
  ↓
[LOG-ROUTINE] Richiedi email e password
  ↓
Email = "robby@gmail.com" AND Password = "robby@123"?
  ├─ SÌ → [ADMINISTRATOR-ROUTINE] Mostra menu admin
  │         ├─ Opzione 1 → [SALARY-ROUTINE] Calcolo stipendi
  │         ├─ Opzione 2 → [MODIFY-ROUTINE] Gestione prodotti
  │         │              ├─ Opzione 1 → [ADD-ROUTINE] Aggiungi prodotto
  │         │              └─ Opzione 2 → [REMOVE-ROUTINE] Elimina prodotto
  │         ├─ Opzione 3 → [PROFIT-ROUTINE] Calcolo profitti
  │         └─ Opzione 4 → Ritorna a INIT-ROUTINE
  │
  └─ NO → [INVALID-ROUTINE] Mostra errore
           ├─ Opzione 0 → Ritorna a LOG-ROUTINE
           └─ Opzione 1 → Ritorna a INIT-ROUTINE
```

#### Flusso 2: Acquisto Prodotti (Buyer)

```
START
  ↓
[INIT-ROUTINE] Mostra menu principale
  ↓
Utente sceglie opzione 2 (BUYER)
  ↓
[BUYER-ROUTINE] Mostra menu buyer
  ↓
Utente sceglie opzione 1 (BUY PRODUCT)
  ↓
[LIST-ROUTINE]
  ├─ [INITIALIZE-ROUTINE] Leggi primo record da DATABASE.txt
  ├─ [PROCESS-RECORD-ROUTINE] Visualizza ogni prodotto (loop fino EOF)
  ├─ [TERMINATE-ROUTINE] Mostra conteggio totale prodotti
  └─ [RECEIPT-ROUTINE]
      ├─ Richiedi numero prodotti da ordinare (ORD)
      ├─ Loop i=1 a ORD:
      │   ├─ Richiedi codice prodotto
      │   ├─ Richiedi nome prodotto
      │   ├─ Richiedi unità
      │   └─ Richiedi prezzo
      ├─ Visualizza ricevuta con tutti i prodotti
      ├─ Calcola TOTAL = Σ(PPRICE[i])
      ├─ Richiedi importo pagato (MONEY)
      ├─ Calcola CHANGE = MONEY - TOTAL
      └─ Visualizza ricevuta finale con resto
```

#### Flusso 3: Calcolo Stipendio

```
[SALARY-ROUTINE]
  ├─ Richiedi nome dipendente
  ├─ Richiedi ID dipendente
  ├─ Richiedi ore lavorate
  ├─ CALCOLA: SALARY = 500 × HOURS-WORKED
  ├─ Visualizza risultati
  └─ [SALARY-CONTINUE-ROUTINE]
      ├─ Opzione Y → Ritorna a SALARY-ROUTINE
      └─ Opzione N → Ritorna a ADMINISTRATOR-ROUTINE
```

#### Flusso 4: Calcolo Profitto

```
[PROFIT-ROUTINE]
  ├─ Richiedi COGS (Cost of Goods Sold)
  ├─ Richiedi SELLING-PRICE
  ├─ CALCOLA: PROFIT = SELLING-PRICE - COGS
  ├─ Visualizza profitto
  └─ [PROFIT-CONTINUE-ROUTINE]
      ├─ Opzione Y → Ritorna a PROFIT-ROUTINE
      └─ Opzione N → Ritorna a ADMINISTRATOR-ROUTINE
```

---

### Anomalie Rilevate

#### Anomalia 1: Credenziali Hardcodate (CRITICA)
**Ubicazione**: ACCOUNTING_SYSTEM.COB, ADMIN-INFO section
```cobol
05 EMAIL PIC X(15) VALUE "robby@gmail.com".
05 ADMIN-PASSWORD PIC X(9) VALUE "robby@123".
```
**Impatto**: Chiunque legga il codice sorgente conosce le credenziali. Nessuna protezione.
**Severità**: 🔴 CRITICA

---

#### Anomalia 2: Logica di Eliminazione Prodotto Difettosa
**Ubicazione**: ACCOUNTING_SYSTEM.COB, MAIN-ROUTINE e REMOVE-ROUTINE
```cobol
IF DELETE-PRODUCT-CODE NOT EQUAL TO PCODE-IN
    WRITE OUTREC FROM REC-OUT
END-IF
```
**Problema**: 
- DELETE-PRODUCT-CODE non è inizializzato all'inizio, quindi è sempre 0
- La condizione `NOT EQUAL TO PCODE-IN` è sempre vera per i prodotti reali
- Risultato: **tutti i record vengono riscritti, nessuno viene eliminato**
- Inoltre, il file viene aperto in OUTPUT (sovrascrittura), non in EXTEND

**Severità**: 🔴 CRITICA

---

#### Anomalia 3: Variabile EOFSW Non Resettata
**Ubicazione**: ACCOUNTING_SYSTEM.COB, multiple routine
```cobol
01   EOFSW PIC X VALUE 'N'.
```
**Problema**: 
- EOFSW è inizializzato a 'N' una sola volta all'inizio del programma
- Quando si esegue REMOVE-ROUTINE dopo aver letto il file in MAIN-ROUTINE, EOFSW è già 'Y'
- Il loop `PERFORM UNTIL EOFSW = 'Y'` non esegue nemmeno un'iterazione
- Nessun record viene letto o scritto

**Severità**: 🔴 CRITICA

---

#### Anomalia 4: Incoerenza Percorsi File
**Ubicazione**: ACCOUNTING_SYSTEM.COB vs BUYROUTINE.COB
```cobol
ACCOUNTING_SYSTEM.COB:
    SELECT INFILE ASSIGN TO "G:\Cobol\DATABASE.TXT".

BUYROUTINE.COB:
    SELECT IN-FILE ASSIGN TO "C:\Cobol\products.TXT".
```
**Problema**: 
- Due moduli leggono da file diversi
- DATABASE.txt contiene dati corrotti e duplicati
- products.txt contiene dati puliti
- Nessuna sincronizzazione tra i due file

**Severità**: 🟠 ALTA

---

#### Anomalia 5: Dati Corrotti in DATABASE.txt
**Ubicazione**: DATABASE.txt
```
00000001 Canned Sardines		     155g   18.75
00000001 Canned Sardines		     155g   18.75    ← DUPLICATO
...
00000017 Luncheon Meat			     165              ← MANCA PREZZO
00000027Ketchup 			     155g   00007000  ← PREZZO MALFORMATO (70.00?)
00000032Pepper				     155g   00008000  ← PREZZO MALFORMATO (80.00?)
2                                                    ← RECORD INCOMPLETO
```
**Impatto**: 
- Ogni prodotto appare 2 volte (duplicazione)
- Alcuni record sono incompleti
- Prezzi in formato errato (8 cifre senza decimali)
- Record finale "2" è corrotto

**Severità**: 🟠 ALTA

---

#### Anomalia 6: Duplicazione Massiccia di Codice
**Ubicazione**: ACCOUNTING_SYSTEM.COB
```cobol
SALARY-CONTINUE-ROUTINE:
    DISPLAY (17, 25) "ENTER ANOTHER? [Y/N]".
    ACCEPT (17, 47) ANSWER.
    IF ANSWER = 'Y' OR ANSWER = 'y' THEN
      PERFORM SALARY-ROUTINE THROUGH SALARY-END
    ELSE IF ANSWER = 'N' OR ANSWER = 'n' THEN
      PERFORM ADMISNISTRATOR-ROUTINE THROUGH ADMINISTRATOR-END
    ...

PROFIT-CONTINUE-ROUTINE:
    DISPLAY (12, 25) "ENTER ANOTHER? [Y/N]".
    ACCEPT (12, 47) ANSWER.
    IF ANSWER = 'Y' OR ANSWER = 'y' THEN
      PERFORM PROFIT-ROUTINE THROUGH PROFIT-END
    ELSE IF ANSWER = 'N' OR ANSWER = 'n' THEN
      PERFORM ADMISNISTRATOR-ROUTINE THROUGH ADMINISTRATOR-END
    ...
```
**Problema**: Codice identico ripetuto 3 volte (SALARY, PROFIT, CONTINUE). Difficile da mantenere.

**Severità**: 🟡 MEDIA

---

#### Anomalia 7: RECEIPT-ROUTINE Duplicata
**Ubicazione**: ACCOUNTING_SYSTEM.COB e BUYROUTINE.COB
```cobol
Entrambi i moduli contengono la stessa routine RECEIPT-ROUTINE
con codice identico (circa 40 righe).
```
**Problema**: Manutenzione difficile, bug fix deve essere applicato in due posti.

**Severità**: 🟡 MEDIA

---

#### Anomalia 8: Typo nei Nomi Routine
**Ubicazione**: ACCOUNTING_SYSTEM.COB
```cobol
ADMISNISTRATOR-ROUTINE  ← Manca una 'I' (dovrebbe essere ADMINISTRATOR)
ADMINISTRATOR-END       ← Scritto correttamente qui
```
**Problema**: Incoerenza nei nomi, confusione durante la lettura del codice.

**Severità**: 🟡 MEDIA

---

#### Anomalia 9: Nessuna Validazione Input
**Ubicazione**: Tutte le routine di input
```cobol
DISPLAY (10, 25)"ENTER HOURS WORKED: ".
ACCEPT HOURS-WORKED.
COMPUTE SALARY = HOURLY-RATE * HOURS-WORKED.
```
**Problema**: 
- Nessun controllo su valori negativi
- Nessun controllo su range (es. ore > 24)
- Nessun controllo su formato (es. input non numerico)
- Nessun controllo su duplicati di codice prodotto

**Severità**: 🟡 MEDIA

---

#### Anomalia 10: Nessuna Persistenza Ordini
**Ubicazione**: RECEIPT-ROUTINE
```cobol
PERFORM UNTIL I > ORD
    DISPLAY PCODE(I), PNAME(I), PUNIT(I), PPRICE(I)
    ADD 1 TO I
END-PERFORM.
```
**Problema**: 
- Gli ordini vengono visualizzati ma non salvati su file
- Nessuna traccia storica delle transazioni
- Nessun audit trail

**Severità**: 🟡 MEDIA

---

#### Anomalia 11: File Aperto in OUTPUT Anziché EXTEND
**Ubicazione**: ACCOUNTING_SYSTEM.COB, MAIN-ROUTINE
```cobol
SELECT OUTFILE ASSIGN TO "G:\Cobol\DATABASE.TXT".
...
OPEN INPUT INFILE OUTPUT OUTFILE.
```
**Problema**: 
- OUTFILE è aperto in OUTPUT (sovrascrittura)
- Se il programma fallisce durante la scrittura, il file viene perso
- Non c'è backup

**Severità**: 🔴 CRITICA

---

#### Anomalia 12: Variabile TOKEN Non Usata
**Ubicazione**: ACCOUNTING_SYSTEM.COB, TEMP-VARIBLES
```cobol
05 TOKEN PIC 9.
```
**Problema**: Variabile dichiarata ma mai usata. Codice morto.

**Severità**: 🟢 BASSA

---

#### Anomalia 13: Mancanza di Chiusura File in REMOVE-ROUTINE
**Ubicazione**: ACCOUNTING_SYSTEM.COB, REMOVE-ROUTINE
```cobol
REMOVE-ROUTINE.
    DISPLAY CLEARSCREEN.
    DISPLAY "ENTER PRODUCT CODE TO DELETE: ".
    ACCEPT DELETE-PRODUCT-CODE.
    PERFORM UNTIL EOFSW = 'Y'
    READ INFILE
    ...
    END-PERFORM.
REMOVE-END.
```
**Problema**: 
- Il file INFILE non viene chiuso dopo la lettura
- EOFSW non viene resettato
- La prossima operazione di lettura fallirà

**Severità**: 🔴 CRITICA

---

#### Anomalia 14: Formato Prezzo Incoerente
**Ubicazione**: Definizioni di PRICE in vari moduli
```cobol
ACCOUNTING_SYSTEM.COB:
    PRICE-IN PIC 9(8).           ← 8 cifre intere
    PRICE-OUT PIC 9(6)V99.       ← 6 cifre + 2 decimali
    PPRICE PIC 9(4)V99.          ← 4 cifre + 2 decimali

BUYROUTINE.COB:
    PROD-PRICE PIC S9(4)V9(2).   ← Signed, 4 cifre + 2 decimali
```
**Problema**: 
- Nessuna coerenza nel formato prezzo
- Conversioni implicite possono causare perdita di dati
- Prezzo massimo in PPRICE è 9999.99 (insufficiente per alcuni prodotti)

**Severità**: 🟠 ALTA

---

### Dipendenze

#### Tabella: Dipendenze tra Moduli

| Modulo | Dipende Da | Tipo Dipendenza | Descrizione |
|--------|-----------|---|---|
| ACCOUNTING_SYSTEM.COB | DATABASE.txt | File Input/Output | Legge e scrive prodotti |
| ACCOUNTING_SYSTEM.COB | products.txt | Nessuna (non usato) | File non referenziato |
| BUYROUTINE.COB | products.txt | File Input | Legge catalogo prodotti |
| BUYROUTINE.COB | DATABASE.txt | Nessuna (non usato) | File non referenziato |
| ACCOUNTING_SYSTEM.COB | BUYROUTINE.COB | Nessuna (moduli separati) | Codice duplicato, nessuna chiamata |

#### Tabella: Dipendenze da File Dati

| File | Modulo | Operazione | Formato | Stato |
|------|--------|-----------|--------|-------|
| DATABASE.txt | ACCOUNTING_SYSTEM.COB | READ, WRITE | 60 char record | ⚠ Corrotto |
| products.txt | BUYROUTINE.COB | READ | 60 char record | ✓ Pulito |
| DATABASE.txt | BUYROUTINE.COB | Nessuna | — | ❌ Non usato |

#### Tabella: Dipendenze Logiche (Business Rules)

| Regola | Dipende Da | Modulo | Note |
|--------|-----------|--------|-------|
| SALARY = HOURLY_RATE × HOURS_WORKED | HOURLY_RATE (500 hardcoded) | ACCOUNTING_SYSTEM.COB | Tariffa non configurabile |
| PROFIT = SELLING_PRICE − COGS | Input utente | ACCOUNTING_SYSTEM.COB | Nessuna validazione |
| CHANGE = MONEY − TOTAL | TOTAL (somma prezzi) | ACCOUNTING_SYSTEM.COB, BUYROUTINE.COB | Duplicato in due moduli |
| Autenticazione Admin | EMAIL, ADMIN-PASSWORD (hardcoded) | ACCOUNTING_SYSTEM.COB | Credenziali non sicure |
| Eliminazione Prodotto | DELETE-PRODUCT-CODE, EOFSW | ACCOUNTING_SYSTEM.COB | Logica difettosa |

#### Grafo Dipendenze (Testo)

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERMARKET SYSTEM                        │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
        ┌───────▼────────┐   │   ┌─────────▼────────┐
        │ ACCOUNTING_    │   │   │  BUYROUTINE.COB  │
        │ SYSTEM.COB     │   │   │                  │
        └───────┬────────┘   │   └─────────┬────────┘
                │            │             │
        ┌───────▼────────┐   │   ┌─────────▼────────┐
        │ DATABASE.txt   │   │   │  products.txt    │
        │ (CORROTTO)     │   │   │  (PULITO)        │
        └────────────────┘   │   └──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  HARDCODED      │
                    │  CREDENTIALS    │
                    │ robby@gmail.com │
                    │  robby@123      │
                    └─────────────────┘

DUPLICAZIONE DI CODICE:
  ACCOUNTING_SYSTEM.COB ──┐
                          ├─→ RECEIPT-ROUTINE (identica)
  BUYROUTINE.COB ─────────┘

  ACCOUNTING_SYSTEM.COB ──┐
                          ├─→ SALARY-CONTINUE-ROUTINE (simile)
                          ├─→ PROFIT-CONTINUE-ROUTINE (simile)
                          └─→ CONTINUE-ROUTINE (simile)
```

---

## RIEPILOGO ESECUTIVO

| Aspetto | Valutazione | Note |
|--------|------------|-------|
| **Sicurezza** | 🔴 CRITICA | Credenziali hardcodate, nessuna crittografia |
| **Integrità Dati** | 🔴 CRITICA | Logica eliminazione difettosa, file corrotto |
| **Manutenibilità** | 🔴 CRITICA | Duplicazione massiccia, typo nei nomi |
| **Affidabilità** | 🔴 CRITICA | EOFSW non resettato, file non chiuso |
| **Validazione** | 🟠 ALTA | Nessun controllo input |
| **Coerenza** | 🟠 ALTA | Due moduli, due file, formati incoerenti |
| **Scalabilità** | 🟠 ALTA | Limite 100 prodotti, file piatto |
| **Audit Trail** | 🟠 ALTA | Nessuna traccia transazioni |

**Conclusione**: Il sistema è in uno stato critico e richiede una riscrittura completa. Non è sicuro per l'uso in produzione.