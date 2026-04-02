# COBOL Modernizer

> Sistema Multi-Agente per la Modernizzazione di Software Legacy  
> **Aitho Academy — Modernizzazione legacy & AI**  
> Autore: Giuseppe Cavone

---

## Panoramica

Questo repository contiene il progetto finale del corso, composto da due parti:

| Parte | Descrizione | Cartella |
|-------|-------------|----------|
| **COBOL Modernizer** | Sistema multi-agente LangGraph che analizza codice COBOL e genera automaticamente un progetto Python moderno | `CobolModernizer2/` |
| **Supermarket System** | Il progetto Python generato dal sistema — gestionale per supermercati modernizzato da COBOL a Python + PostgreSQL | `output/` |

---

## Struttura del Repository

```
cobol-modernizer/
│
├── README.md                        ← Questo file
│
├── CobolModernizer2/                ← Sistema multi-agente (LangGraph)
│   ├── cobol_modernizer2.py         ← Notebook Marimo principale
│   ├── prompts/                     ← Prompt degli agenti (.md)
│   │   ├── 01_orchestrator.md
│   │   ├── 02_discovery.md
│   │   ├── 03_architecture.md
│   │   ├── 04_migration.md
│   │   ├── 05_codegen.md
│   │   ├── 05b_filelist.md
│   │   └── 06_reviewer.md
│   └── outputs/                     ← Output .md generati dagli agenti
│
└── output/                          ← Progetto Python generato
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

📖 **[Istruzioni complete → CobolModernizer2/README.md](CobolModernizer2/README.md)**

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
| Test | pytest |

---

## Relazione e Presentazione

- 📄 Relazione finale: `Relazione_COBOL_Modernizer_FINALE.pdf`
- 📊 Presentazione: `CobolModernizer_Presentazione.pptx`

---

## Licenza

Progetto didattico — Aitho Academy 2026
