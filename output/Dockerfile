# ── Dockerfile — Supermarket Management System (CLI Python) ───────────────────
FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema necessarie per psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice
COPY . .

# Crea cartella logs
RUN mkdir -p logs

# Variabile d'ambiente per indicare che siamo in Docker
ENV RUNNING_IN_DOCKER=true

# Avvio: aspetta che il DB sia pronto poi lancia main.py
CMD ["python", "main.py"]
