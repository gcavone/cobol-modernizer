# COBOL Modernizer v2 — Sistema Multi-Agente

Sistema di modernizzazione automatica di codice COBOL legacy basato su LangGraph, con agenti specializzati e osservabilità tramite MLflow.

---

## Architettura del Sistema

Il sistema è un grafo LangGraph con 6 nodi che cooperano attraverso uno stato condiviso:

```
START → Orchestrator → Discovery / Architecture / Migration / CodeGen / Reviewer → Orchestrator → END
```

| Agente | Ruolo |
|--------|-------|
| **Orchestrator** | Coordina il flusso, decide quale agente attivare, gestisce le modalità step/auto |
| **Discovery Agent** | Analizza il COBOL ed estrae business rules, strutture dati, anomalie |
| **Architecture Agent** | Progetta la struttura Python moderna e genera la lista dei file da creare |
| **Migration Agent** | Produce lo script ETL Python per migrare i dati in PostgreSQL |
| **CodeGen Agent** | Genera il codice Python file per file con contesto progressivo |
| **Reviewer Agent** | Verifica qualità e coerenza del codice generato |

### Modalità Operative

- **Step-by-step** — Un agente alla volta, l'utente controlla il ritmo
- **One-click** — Digita `"genera il progetto completo"` per eseguire tutta la pipeline in automatico

---

## Avvio con Docker 🐳 (consigliato)

Il modo più semplice — senza installare Python o Poetry:

```bash
cp .env.example .env   # inserisci la tua chiave API
make modernizer        # avvia Marimo su http://localhost:2718
```

📖 **[Guida Docker completa → DOCKER.md](DOCKER.md)**

---

## Installazione Manuale

### Prerequisiti

- Python 3.11+
- [Poetry](https://python-poetry.org/) per la gestione delle dipendenze
- [Marimo](https://marimo.io/) per eseguire il notebook
- Una chiave API per almeno uno di questi modelli:
  - [Groq](https://console.groq.com/) (gratuito, consigliato)
  - [Mistral](https://console.mistral.ai/) (gratuito)
  - [Anthropic](https://console.anthropic.com/) (a pagamento)

### 1. Clona il repository

```bash
git clone https://github.com/gcavone/cobol-modernizer.git
cd cobol-modernizer
```

### 2. Installa le dipendenze con Poetry

```bash
poetry install
poetry shell
```

Se non hai Poetry:
```bash
pip install marimo langchain langgraph langchain-groq langchain-mistralai langchain-anthropic mlflow python-dotenv
```

### 3. Configura le chiavi API

```bash
cp .env.example .env
```

Modifica `.env` inserendo la tua chiave API:

```env
# Scegli il modello che vuoi usare (decommentane solo uno)
GROQ_API_KEY=la_tua_chiave_groq
# MISTRAL_API_KEY=la_tua_chiave_mistral
# ANTHROPIC_API_KEY=la_tua_chiave_anthropic
```

### 4. Avvia il notebook Marimo

```bash
marimo run cobol_modernizer2.py
```

Oppure in modalità edit:
```bash
marimo edit cobol_modernizer2.py
```

---

## Struttura del Notebook

Il notebook `cobol_modernizer2.py` è organizzato in sezioni con titoli visibili nell'interfaccia Marimo:

| Cella | Titolo | Contenuto |
|-------|--------|-----------|
| Titolo | 🤖 COBOL Modernizer v2 | Intestazione del notebook |
| 1 | Import | Tutte le librerie (LangChain, MLflow, Pydantic, ecc.) |
| 2 | 📂 Caricamento file COBOL e prompt | File sorgente COBOL e prompt degli agenti |
| 3 | ⚙️ Configurazione LLM e costanti | **Punto di configurazione principale** — modello LLM e costanti |
| 4 | 🧠 Stato condiviso e Orchestrator | `ModernizerState` e nodo Orchestrator |
| 5 | 🤖 Nodi agenti | Discovery, Architecture, Migration, CodeGen, Reviewer |
| 6 | 🕸️ Grafo LangGraph e chatbot handler | Costruzione grafo, chatbot handler, MLflow tracking |
| 7 | Grafo Mermaid | Visualizzazione del flusso del grafo |
| 8 | Interfaccia chat | Chat con prompt rapidi |
| 9 | 📊 Pannello MLflow | Avvio e accesso alla UI MLflow |

---

## Configurazione del Modello LLM

Il notebook evidenzia in giallo la cella di configurazione con l'avviso **"Modifica qui per cambiare modello"**. Cambia **una sola riga** per usare un modello diverso:

```python
# Groq (gratuito, consigliato per test)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=os.getenv("GROQ_API_KEY"))

# Mistral
llm = ChatMistralAI(model="mistral-large-latest", temperature=0, api_key=os.getenv("MISTRAL_API_KEY"), timeout=120)

# Anthropic Claude
llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0, api_key=os.getenv("ANTHROPIC_API_KEY"))
```

---

## Utilizzo

### Comandi disponibili nella chat

| Comando | Effetto |
|---------|---------|
| `Analizza il codice COBOL ed estrai le business rules` | Attiva il Discovery Agent |
| `Progetta l'architettura Python moderna` | Attiva l'Architecture Agent |
| `Genera lo script di migrazione dati in PostgreSQL` | Attiva il Migration Agent |
| `Genera il progetto completo` | Attiva la pipeline completa in automatico |
| `Fai la review del codice generato` | Attiva il Reviewer Agent |

### Flusso consigliato (step-by-step)

1. Invia: `Analizza il codice COBOL ed estrai le business rules`
2. Leggi l'output del Discovery Agent
3. Invia: `Progetta l'architettura Python moderna`
4. Leggi l'architettura progettata
5. Invia: `Genera lo script di migrazione dati in PostgreSQL`
6. Invia: `Genera il progetto completo`
7. Attendi la generazione (circa 20-40 minuti con Groq gratuito)
8. Il progetto Python generato è disponibile nella cartella `output/`

---

## Output Generati

Dopo l'esecuzione troverai nella cartella `outputs/`:

```
outputs/
├── discovery_HHMMSS.md      ← Analisi COBOL completa
├── architecture_HHMMSS.md   ← Architettura Python progettata
├── migration_HHMMSS.md      ← Script ETL + schema PostgreSQL
└── codegen_HHMMSS.md        ← Riepilogo file generati
```

Il progetto Python completo viene salvato in `output/`.

---

## Osservabilità con MLflow

Il sistema traccia ogni esecuzione con MLflow. Per visualizzare la UI:

```bash
mlflow ui
```

Apri il browser su `http://localhost:5000` per vedere:
- Ogni run con parametri e metriche
- Gli output degli agenti come artifact
- Il ragionamento dell'Orchestrator per ogni decisione

> Con Docker, il pannello MLflow è accessibile direttamente dall'interfaccia Marimo.

---

## Struttura Prompt

I prompt degli agenti sono in `prompts/`:

| File | Agente | Struttura |
|------|--------|-----------|
| `01_orchestrator.md` | Orchestrator | Regole di routing |
| `02_discovery.md` | Discovery | PARTE 1 (tecnica) + PARTE 2 (narrativa) |
| `03_architecture.md` | Architecture | PARTE 1 (tecnica) + PARTE 2 (narrativa) |
| `04_migration.md` | Migration | PARTE 1 (tecnica) + PARTE 2 (narrativa) |
| `05_codegen.md` | CodeGen | Istruzioni generazione singolo file |
| `05b_filelist.md` | FileList | Schema Pydantic lista file |
| `06_reviewer.md` | Reviewer | PARTE 1 (tecnica) + PARTE 2 (narrativa) |

---

## Note sui Rate Limit

Con modelli gratuiti (Groq, Mistral) la generazione completa richiede:
- **Sleep**: 65 secondi tra un file e l'altro
- **Retry**: 3 tentativi per file in caso di errore 429
- **Tempo totale**: circa 20-40 minuti per 20-40 file

Per ridurre i tempi usa un piano a pagamento o Anthropic Claude.

---

## Requisiti Poetry (pyproject.toml)

```toml
[tool.poetry.dependencies]
python = "^3.11"
marimo = "^0.9"
langchain = "^0.3"
langgraph = "^0.2"
langchain-groq = "^0.2"
langchain-mistralai = "^0.2"
langchain-anthropic = "^0.3"
mlflow = "^2.17"
python-dotenv = "^1.0"
pydantic = "^2.0"
```
