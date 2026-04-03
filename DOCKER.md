# 🐳 Guida Docker — COBOL Modernizer

Avvia entrambi i sistemi con Docker in pochi comandi, senza installare nulla sul tuo computer (eccetto Docker Desktop).

---

## Prerequisiti

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installato e in esecuzione
- `make` disponibile nel terminale (preinstallato su Mac e Linux; su Windows usa Git Bash)

---

## Setup iniziale (solo la prima volta)

```bash
# 1. Clona il repository
git clone https://github.com/gcavone/cobol-modernizer.git
cd cobol-modernizer

# 2. Configura le variabili d'ambiente per il sistema multi-agente
cp .env.example .env
# Apri .env e inserisci la tua chiave API (Groq, Mistral o Anthropic)
```

---

## Sistema Multi-Agente (COBOL Modernizer)

```bash
# Avvia il notebook Marimo
make modernizer

# Apri il browser su http://localhost:2718
# Ferma il sistema
make modernizer-stop
```

Gli output generati dagli agenti (file `.md`) vengono salvati in `outputs/`.  
Il codice Python generato viene salvato in `output/`.

---

## Supermarket System (Gestionale Python)

```bash
# Avvia il database PostgreSQL
make supermarket-db

# (opzionale) Importa i prodotti dai file COBOL originali
make supermarket-migrate

# Avvia la CLI interattiva
make supermarket
```

Credenziali admin: `robby@gmail.com` / `robby@123`

---

## Comandi disponibili

```bash
make help               # Mostra tutti i comandi disponibili
make modernizer         # Avvia sistema multi-agente su :2718
make modernizer-stop    # Ferma sistema multi-agente
make supermarket-db     # Avvia solo PostgreSQL
make supermarket-migrate # Esegui migrazione ETL COBOL → PostgreSQL
make supermarket        # Avvia la CLI del gestionale
make supermarket-stop   # Ferma database e app
make stop               # Ferma tutti i container
make clean              # Rimuove container, immagini e volumi
```

---

## Senza Makefile (comandi Docker diretti)

```bash
# Sistema multi-agente
docker compose --profile modernizer up --build -d
docker compose --profile modernizer down

# Database PostgreSQL
docker compose --profile supermarket up -d db

# CLI Supermarket
docker compose --profile supermarket run --rm supermarket

# Ferma tutto
docker compose --profile modernizer --profile supermarket down
```

---

## Struttura file Docker

```
cobol-modernizer/
├── Dockerfile              ← immagine sistema multi-agente
├── docker-compose.yml      ← orchestra tutti i servizi
├── .dockerignore           ← esclude file non necessari
├── Makefile                ← comandi rapidi
├── DOCKER.md               ← questa guida
└── output/
    ├── Dockerfile          ← immagine supermarket CLI
    └── .dockerignore
```

---

## Risoluzione problemi

**Porta 2718 già in uso**
```bash
# Cambia la porta in docker-compose.yml: "2719:2718"
```

**Porta 5432 già in uso** (PostgreSQL locale)
```bash
# Cambia la porta in docker-compose.yml: "5433:5432"
```

**Il container supermarket non si connette al DB**
```bash
# Verifica che il database sia healthy
docker compose ps
# Aspetta qualche secondo e riprova
make supermarket
```

**Pulisci tutto e ricomincia da capo**
```bash
make clean
make supermarket-db
make supermarket
```
