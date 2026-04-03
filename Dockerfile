# ── Dockerfile — COBOL Modernizer (sistema multi-agente Marimo) ───────────────
FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installa dipendenze Python direttamente con pip
RUN pip install --no-cache-dir \
    marimo \
    langchain==0.3.25 \
    langgraph \
    langchain-groq \
    langchain-mistralai \
    langchain-anthropic \
    mlflow \
    python-dotenv \
    pydantic

# Copia il codice sorgente
COPY cobol_modernizer2.py ./
COPY prompts/ ./prompts/
COPY ACCOUNTING_SYSTEM.COB ./
COPY BUYROUTINE.COB ./
COPY DATABASE.txt ./
COPY products.txt ./

# Crea cartelle per gli output
RUN mkdir -p outputs output

# Esponi la porta Marimo
EXPOSE 2718

# Avvia Marimo
CMD ["marimo", "run", "cobol_modernizer2.py", "--host", "0.0.0.0", "--port", "2718"]
