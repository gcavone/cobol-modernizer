# Supermarket Management System

> Gestionale per supermercati modernizzato da COBOL legacy a Python 3.11+ con PostgreSQL.  
> Generato automaticamente dal sistema COBOL Modernizer.

---

## Business Rules Implementate

Le tre formule originali del sistema COBOL sono state preservate e modernizzate:

| Regola | Formula | Implementazione |
|--------|---------|-----------------|
| Stipendio dipendente | `SALARY = HOURLY_RATE × HOURS_WORKED` | `EmployeeService.calculate_salary()` |
| Profitto | `PROFIT = SELLING_PRICE - COGS` | `ProfitService.calculate_profit()` |
| Resto acquisto | `CHANGE = MONEY_PAID - TOTAL` | `OrderService.calculate_change()` |

---

## Prerequisiti

- Python 3.11+
- PostgreSQL 12+
- pip

---

## Installazione

### 1. Clona il repository

```bash
git clone https://github.com/gcavone/cobol-modernizer.git
cd cobol-modernizer/output
```

### 2. Crea il virtualenv

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

> **Nota**: Su Python 3.14 `psycopg2-binary` potrebbe non compilare.
> In quel caso usa: `pip install psycopg[binary]`

### 4. Configura il database PostgreSQL

Crea l'utente e il database:

```bash
psql postgres -c "CREATE USER supermarket_user WITH PASSWORD 'supermarket_pass';"
psql postgres -c "CREATE DATABASE supermarket_db OWNER supermarket_user;"
psql postgres -c "ALTER DATABASE supermarket_db OWNER TO supermarket_user;"
psql supermarket_db -c "ALTER SCHEMA public OWNER TO supermarket_user;"
```

### 5. Configura le variabili d'ambiente

```bash
cp .env.example .env
```

Il file `.env` deve contenere:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=supermarket_db
DB_USER=supermarket_user
DB_PASSWORD=supermarket_pass
LOG_LEVEL=INFO
ADMIN_EMAIL=robby@gmail.com
ADMIN_PASSWORD_HASH=$2b$12$lbQ7.nODQxFqx4gDdW7st.jOq3LpeBWzvPy8FwKXo2Yl.sl7BNcSa
DATABASE_URL=postgresql://supermarket_user:supermarket_pass@localhost:5432/supermarket_db
```

### 6. Avvia l'applicazione

```bash
python3 main.py
```

Al primo avvio il sistema crea automaticamente tutte le tabelle e popola il database con:
- 1 admin di default
- 8 prodotti di esempio
- 4 dipendenti di esempio

---

## Migrazione Dati dal COBOL (opzionale)

Se hai i file originali `DATABASE.txt` e `products.txt` del sistema COBOL, puoi importarli:

```bash
# Copia i file COBOL nella cartella output/
cp /path/to/DATABASE.txt .
cp /path/to/products.txt .

# Esegui la migrazione ETL
python3 etl_migration.py
```

Lo script gestisce automaticamente:
- Deduplica dei record (ogni prodotto appare 2 volte nel file originale)
- Parsing dei prezzi in formato COBOL (00001875 → 18.75)
- Scarto dei record incompleti con log
- Transazione atomica con rollback in caso di errore

---

## Utilizzo

### Login Amministratore

Dal menu principale seleziona `1) Administrator`:

```
Email:    robby@gmail.com
Password: robby@123
```

### Menu Amministratore

| Opzione | Funzione |
|---------|----------|
| 1) Manage Products | Aggiunta, modifica, eliminazione prodotti |
| 2) Manage Employees | Gestione dipendenti e calcolo stipendi |
| 3) Calculate Profit | Calcolo profitto (SELLING_PRICE - COGS) |
| 4) View Orders | Storico ordini clienti |
| 5) Logout | Esci |

### Flusso Buyer

Dal menu principale seleziona `2) Buyer`:
1. Visualizza il catalogo prodotti
2. Inserisci il numero di articoli da ordinare
3. Per ogni articolo inserisci il codice prodotto e la quantità
4. Visualizza il totale
5. Inserisci l'importo pagato
6. Il sistema calcola e mostra il resto

---

## Test

Il progetto include 55 test automatici che verificano le business rules e tutti i servizi:

```bash
pip install pytest
pytest tests/ -v
```

### Cosa viene testato

| Classe di test | N. test | Descrizione |
|----------------|---------|-------------|
| `TestBusinessRules` | 9 | Le 3 formule COBOL con tutti i casi limite |
| `TestAuthService` | 11 | Login, password, creazione admin |
| `TestProductService` | 10 | CRUD prodotti, validazione codice e prezzo |
| `TestEmployeeService` | 8 | Calcolo stipendi, validazione ore |
| `TestProfitService` | 5 | Calcolo profitti, COGS negativo |
| `TestOrderService` | 7 | Creazione ordini, calcolo resto, pagamento insufficiente |
| `TestIntegration` | 4 | Flusso completo buyer end-to-end |

---

## Struttura del Progetto

```
output/
├── main.py                    # Entry point
├── etl_migration.py           # Script migrazione dati da COBOL
├── config.py                  # Configurazione da variabili d'ambiente
├── requirements.txt           # Dipendenze Python
├── .env                       # Variabili d'ambiente (non committare!)
├── .env.example               # Template .env
│
├── models/                    # Classi SQLAlchemy ORM
│   ├── product.py             # Prodotto (Base condiviso)
│   ├── admin.py               # Amministratore
│   ├── employee.py            # Dipendente
│   ├── order.py               # Ordine cliente
│   ├── order_item.py          # Riga ordine
│   ├── salary_record.py       # Registro stipendio
│   ├── profit_record.py       # Registro profitto
│   └── activity_log.py        # Log attività
│
├── repositories/              # Accesso dati (pattern Repository)
│   ├── base_repository.py     # CRUD generico
│   ├── product_repository.py
│   ├── admin_repository.py
│   ├── employee_repository.py
│   ├── order_repository.py
│   ├── order_item_repository.py
│   ├── salary_repository.py
│   ├── profit_repository.py
│   └── activity_log_repository.py
│
├── services/                  # Business logic
│   ├── auth_service.py        # Autenticazione con bcrypt
│   ├── product_service.py     # Gestione prodotti
│   ├── employee_service.py    # Stipendi: SALARY = RATE × HOURS
│   ├── order_service.py       # Ordini: CHANGE = PAYMENT - TOTAL
│   ├── profit_service.py      # Profitti: PROFIT = PRICE - COGS
│   └── activity_service.py    # Logging attività
│
├── cli/                       # Interfaccia utente CLI
│   ├── main_menu.py
│   ├── admin_menu.py
│   ├── buyer_menu.py
│   ├── product_menu.py
│   ├── employee_menu.py
│   ├── profit_menu.py
│   ├── order_menu.py
│   └── ui_helpers.py
│
├── database/                  # Connessione e inizializzazione DB
│   ├── connection.py
│   └── init_db.py
│
├── tests/                     # Test automatici (55 test)
│   └── test_supermarket.py
│
└── logs/                      # Log applicazione (creata automaticamente)
    └── app.log
```

---

## Schema Database

| Tabella | Descrizione |
|---------|-------------|
| `admins` | Amministratori con password hashata (bcrypt) |
| `products` | Catalogo prodotti (codice 8 cifre UNIQUE) |
| `employees` | Dipendenti con tariffa oraria |
| `orders` | Ordini clienti con totale, pagamento e resto |
| `order_items` | Righe ordine (FK → orders, products) |
| `salary_records` | Storico calcoli stipendio |
| `profit_records` | Storico calcoli profitto |
| `activity_logs` | Audit trail di tutte le operazioni |

---

## Miglioramenti rispetto al COBOL Legacy

| Aspetto | COBOL | Python |
|---------|-------|--------|
| Credenziali | Hardcodate in chiaro | Hashate con bcrypt in database |
| Dati | File piatto corrotto (52 record con duplicati) | DB relazionale (26 prodotti unici) |
| Validazione | Nessuna | Robusta a livello service |
| Persistenza ordini | Solo visualizzati | Salvati con timestamp |
| Audit trail | Nessuno | Tabella `activity_logs` |
| Limite prodotti | Max 100 per ordine (array COBOL) | Illimitato |
| Portabilità | Solo Windows (percorsi fissi) | Qualsiasi OS via `.env` |

---

## Credenziali di Default

**Admin**
- Email: `robby@gmail.com`
- Password: `robby@123`

**Prodotti di esempio** (creati all'avvio)
- `00000001` Canned Sardines 155g — ₱18.75
- `00000002` Canned Sardines Spicy 155g — ₱18.75
- `00000003` Condensed Milk 300mL — ₱53.00
- `00000004` Evaporated Milk 410mL — ₱44.00
- `00000005` Powdered Milk 300g — ₱96.25
- `00000006` Cooking Oil 1L — ₱125.50
- `00000007` Rice 2kg — ₱85.00
- `00000008` Sugar 1kg — ₱45.00

**Dipendenti di esempio**
- `EMP001` Juan Dela Cruz — ₱500.00/ora
- `EMP002` Maria Santos — ₱500.00/ora
- `EMP003` Pedro Reyes — ₱550.00/ora
- `EMP004` Ana Garcia — ₱500.00/ora
