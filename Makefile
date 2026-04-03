# ── Makefile — COBOL Modernizer ───────────────────────────────────────────────
# Comandi rapidi per gestire i due sistemi Docker.
# Requisiti: Docker Desktop installato e in esecuzione.
#
# Uso:
#   make help             → mostra tutti i comandi disponibili
#   make modernizer       → avvia il sistema multi-agente
#   make supermarket      → avvia il gestionale Python
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help modernizer modernizer-stop supermarket-db supermarket supermarket-stop \
        supermarket-migrate logs-modernizer logs-supermarket stop clean

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║              COBOL Modernizer — Comandi Docker               ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  SISTEMA MULTI-AGENTE (Marimo)"
	@echo "  ─────────────────────────────"
	@echo "  make modernizer          Avvia il notebook Marimo su http://localhost:2718"
	@echo "  make modernizer-stop     Ferma il sistema multi-agente"
	@echo "  make logs-modernizer     Mostra i log del sistema multi-agente"
	@echo ""
	@echo "  SUPERMARKET SYSTEM (CLI Python + PostgreSQL)"
	@echo "  ─────────────────────────────────────────────"
	@echo "  make supermarket-db      Avvia solo il database PostgreSQL"
	@echo "  make supermarket-migrate Esegui la migrazione ETL dai file COBOL"
	@echo "  make supermarket         Avvia la CLI interattiva del gestionale"
	@echo "  make supermarket-stop    Ferma database e applicazione"
	@echo "  make logs-supermarket    Mostra i log del gestionale"
	@echo ""
	@echo "  GENERALE"
	@echo "  ─────────"
	@echo "  make stop                Ferma tutti i container"
	@echo "  make clean               Rimuove container, immagini e volumi"
	@echo ""

# ── Sistema Multi-Agente ──────────────────────────────────────────────────────
modernizer:
	@echo "🤖 Avvio COBOL Modernizer (Marimo)..."
	@echo "   Assicurati di aver configurato .env con la tua chiave API"
	docker compose --profile modernizer up --build -d
	@echo ""
	@echo "✅ Sistema avviato!"
	@echo "   Apri il browser su: http://localhost:2718"
	@echo ""

modernizer-stop:
	@echo "🛑 Arresto COBOL Modernizer..."
	docker compose --profile modernizer down

logs-modernizer:
	docker compose logs -f modernizer

# ── Supermarket System ────────────────────────────────────────────────────────
supermarket-db:
	@echo "🗄️  Avvio database PostgreSQL..."
	docker compose --profile supermarket up -d db
	@echo "   Attendo che il database sia pronto..."
	@docker compose exec db pg_isready -U supermarket_user -d supermarket_db \
		|| (sleep 5 && docker compose exec db pg_isready -U supermarket_user -d supermarket_db)
	@echo "✅ Database pronto su localhost:5432"
	@echo ""

supermarket-migrate:
	@echo "📦 Esecuzione migrazione ETL COBOL → PostgreSQL..."
	docker compose --profile supermarket run --rm \
		-v $(PWD)/DATABASE.txt:/app/DATABASE.txt \
		-v $(PWD)/products.txt:/app/products.txt \
		supermarket python etl_migration.py
	@echo "✅ Migrazione completata!"

supermarket:
	@echo "🛒 Avvio Supermarket Management System..."
	@echo "   Avvio database se non e in esecuzione..."
	docker compose --profile supermarket up -d db
	@echo "   Attendo che il database sia pronto..."
	@sleep 5
	@echo "   Avvio interfaccia CLI..."
	@echo ""
	docker compose --profile supermarket run --rm supermarket

supermarket-stop:
	@echo "🛑 Arresto Supermarket System..."
	docker compose --profile supermarket down

logs-supermarket:
	docker compose logs -f supermarket

# ── Generale ─────────────────────────────────────────────────────────────────
stop:
	@echo "🛑 Arresto di tutti i container..."
	docker compose --profile modernizer --profile supermarket down
	@echo "✅ Tutti i container arrestati"

clean:
	@echo "🧹 Pulizia container, immagini e volumi..."
	docker compose --profile modernizer --profile supermarket down --rmi all --volumes
	@echo "✅ Pulizia completata"
