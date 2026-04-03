# ── Dockerfile — COBOL Modernizer (sistema multi-agente Marimo) ───────────────
FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Aggiorna pip
RUN pip install --no-cache-dir --upgrade pip

# Installa dipendenze con versioni fisse per evitare conflitti
RUN pip install --no-cache-dir \
    "marimo==0.10.19" \
    "langchain==0.3.25" \
    "langchain-core==0.3.58" \
    "langgraph==0.2.74" \
    "langgraph-checkpoint==2.0.26" \
    "langchain-groq==0.3.2" \
    "langchain-mistralai==0.2.4" \
    "langchain-anthropic==0.3.10" \
    "mlflow==2.21.3" \
    "python-dotenv==1.0.0" \
    "pydantic==2.10.6"

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