# Supermarket Management System

> Gestionale per supermercati modernizzato da COBOL legacy a Python 3.11+ con PostgreSQL.  
> Generato automaticamente dal sistema COBOL Modernizer.

---

## Business Rules Implementate

| Regola | Formula | Implementazione |
|--------|---------|-----------------|
| Stipendio dipendente | `SALARY = HOURLY_RATE × HOURS_WORKED` | `EmployeeService.calculate_salary()` |
| Profitto | `PROFIT = SELLING_PRICE - COGS` | `ProfitService.calculate_profit()` |
| Resto acquisto | `CHANGE = MONEY_PAID - TOTAL` | `OrderService.calculate_change()` |

---

## Avvio con Docker 🐳 (consigliato)

Il modo più semplice — senza installare Python o PostgreSQL:

```bash
# Dalla root del repository
make supermarket-db      # avvia PostgreSQL
make supermarket         # avvia la CLI interattiva
```

Per importare i prodotti dal file COBOL originale:
```bash
make supermarket-migrate
```

📖 **[Guida Docker completa → ../DOCKER.md](../DOCKER.md)**

---

## Installazione Manuale

### Prerequisiti

- Python 3.11+
- PostgreSQL 12+
- pip

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

### 6. Avvia l'applicazione

```bash
python3 main.py
```

---

## Migrazione Dati dal COBOL (opzionale)

```bash
# Copia i file COBOL nella cartella output/
cp /path/to/DATABASE.txt .
cp /path/to/products.txt .

# Esegui la migrazione ETL
python3 etl_migration.py
```

---

## Utilizzo

### Login Amministratore

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

---

## Test

```bash
pip install pytest
pytest tests/ -v
```

55 test automatici che verificano le business rules e tutti i servizi.

---

## Struttura del Progetto

```
output/
├── main.py                    # Entry point
├── etl_migration.py           # Script migrazione dati da COBOL
├── config.py                  # Configurazione da variabili d'ambiente
├── requirements.txt           # Dipendenze Python
├── .env.example               # Template .env
├── Dockerfile                 # Immagine Docker
│
├── models/                    # Classi SQLAlchemy ORM
├── repositories/              # Accesso dati (pattern Repository)
├── services/                  # Business logic
├── cli/                       # Interfaccia utente CLI
├── database/                  # Connessione e inizializzazione DB
└── tests/                     # Test automatici (55 test)
```

---

## Miglioramenti rispetto al COBOL Legacy

| Aspetto | COBOL | Python |
|---------|-------|--------|
| Credenziali | Hardcodate in chiaro | Hashate con bcrypt in database |
| Dati | File piatto corrotto (52 record con duplicati) | DB relazionale (26 prodotti unici) |
| Validazione | Nessuna | Robusta a livello service |
| Persistenza ordini | Solo visualizzati | Salvati con timestamp |
| Audit trail | Nessuno | Tabella `activity_logs` |
| Limite prodotti | Max 100 per ordine | Illimitato |
| Portabilità | Solo Windows | Qualsiasi OS via `.env` |
