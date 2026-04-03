# COBOL Modernizer

> Sistema Multi-Agente per la Modernizzazione di Software Legacy  
> **Aitho Academy — Modernizzazione legacy & AI**  
> Autore: Giuseppe Cavone

---

## Avvio Rapido con Docker 🐳

Il modo più semplice per avviare entrambi i sistemi — senza installare Python, Poetry o PostgreSQL:

```bash
git clone https://github.com/gcavone/cobol-modernizer.git
cd cobol-modernizer
cp .env.example .env          # inserisci la tua chiave API nel file .env

make modernizer               # avvia il sistema multi-agente su http://localhost:2718
make supermarket              # avvia il gestionale Python con PostgreSQL
```

📖 **[Guida Docker completa → DOCKER.md](DOCKER.md)**

---

## Panoramica

Questo repository contiene il progetto finale del corso, composto da due parti:

| Parte | Descrizione | Avvio |
|-------|-------------|-------|
| **COBOL Modernizer** | Sistema multi-agente LangGraph che analizza codice COBOL e genera automaticamente un progetto Python moderno | `make modernizer` |
| **Supermarket System** | Il progetto Python generato — gestionale per supermercati modernizzato da COBOL a Python + PostgreSQL | `make supermarket` |

---

## Struttura del Repository

```
cobol-modernizer/
│
├── README.md                        ← Questo file
├── DOCKER.md                        ← Guida Docker completa
├── README_SISTEMA_MULTIAGENTE.md    ← Istruzioni sistema multi-agente
├── Dockerfile                       ← Immagine Docker sistema multi-agente
├── docker-compose.yml               ← Orchestra tutti i servizi
├── Makefile                         ← Comandi rapidi
├── .env.example                     ← Template variabili d'ambiente
├── .dockerignore
│
├── cobol_modernizer2.py             ← Notebook Marimo principale
├── pyproject.toml                   ← Dipendenze Poetry
├── prompts/                         ← Prompt degli agenti (.md)
├── outputs/                         ← Output .md generati dagli agenti
│
├── ACCOUNTING_SYSTEM.COB            ← Codice COBOL originale
├── BUYROUTINE.COB
├── DATABASE.txt
├── products.txt
│
└── output/                          ← Progetto Python generato
    ├── README.md                    ← Istruzioni progetto Python
    ├── Dockerfile                   ← Immagine Docker supermarket
    ├── main.py
    ├── etl_migration.py
    ├── requirements.txt
    ├── .env.example
    ├── models/
    ├── repositories/
    ├── services/
    ├── cli/
    ├── database/
    └── tests/
```

---

## Parte 1 — COBOL Modernizer (Sistema Multi-Agente)

Il sistema multi-agente analizza il codice COBOL di un gestionale per supermercati e genera automaticamente:
- L'analisi delle business rules (Discovery Agent)
- L'architettura Python moderna (Architecture Agent)
- Lo script ETL per la migrazione dati (Migration Agent)
- Il codice Python completo file per file (CodeGen Agent)

📖 **[Istruzioni complete → README_SISTEMA_MULTIAGENTE.md](README_SISTEMA_MULTIAGENTE.md)**

---

## Parte 2 — Supermarket System (Progetto Generato)

Il gestionale per supermercati modernizzato, con:
- Autenticazione admin con bcrypt
- Gestione prodotti, dipendenti, ordini e profitti
- Database PostgreSQL con ORM SQLAlchemy
- CLI interattiva
- Test automatici (55 test)

📖 **[Istruzioni complete → output/README.md](output/README.md)**

---

## Tecnologie Utilizzate

| Componente | Tecnologia |
|------------|-----------|
| Orchestrazione agenti | LangGraph |
| Modelli LLM | Groq / Mistral / Anthropic Claude |
| Interfaccia notebook | Marimo |
| Osservabilità | MLflow |
| Database | PostgreSQL + SQLAlchemy |
| Gestione ambiente | Poetry |
| Containerizzazione | Docker + Docker Compose |
| Test | pytest |

---

## Licenza

Progetto didattico — Aitho Academy 2026
