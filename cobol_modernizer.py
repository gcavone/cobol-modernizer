import marimo

__generated_with = "0.13.11"
app = marimo.App(width="medium")


# ═══════════════════════════════════════════════════════════════════════════════
# CELLA 1 — Import e configurazione
# ═══════════════════════════════════════════════════════════════════════════════
@app.cell
def _():
    import marimo as mo
    import os
    import time
    import uuid
    import socket
    import subprocess
    from pydantic import BaseModel, Field
    from typing import TypedDict, Annotated, Optional
    from dotenv import load_dotenv
    from langchain_mistralai import ChatMistralAI
    from langchain_core.messages import SystemMessage, HumanMessage
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import StateGraph, START, END
    from langgraph.graph.message import add_messages
    import mlflow
    import mlflow.langchain

    load_dotenv()

    mlflow.set_experiment("COBOL-Modernizer")
    mlflow.langchain.autolog(log_traces=False)

    return (
        Annotated, BaseModel, ChatMistralAI, END, Field,
        HumanMessage, MemorySaver, Optional, START, StateGraph,
        SystemMessage, TypedDict, add_messages, mlflow, mo,
        os, socket, subprocess, time, uuid,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CELLA 2 — Lettura file COBOL e prompt
# ═══════════════════════════════════════════════════════════════════════════════
@app.cell
def _(os):
    import os as _os

    def read_file(path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except FileNotFoundError:
            return f"[FILE NON TROVATO: {path}]"

    def get_prompt(filename: str) -> str:
        base = _os.path.dirname(_os.path.abspath(__file__))
        return read_file(_os.path.join(base, "prompts", filename))

    # ── Lettura file COBOL ────────────────────────────────────────────────────
    base_dir = _os.path.dirname(_os.path.abspath(__file__))

    COBOL_ACCOUNTING = read_file(_os.path.join(base_dir, "ACCOUNTING_SYSTEM.COB"))
    COBOL_BUYROUTINE = read_file(_os.path.join(base_dir, "BUYROUTINE.COB"))
    DATABASE_TXT     = read_file(_os.path.join(base_dir, "DATABASE.txt"))
    PRODUCTS_TXT     = read_file(_os.path.join(base_dir, "products.txt"))

    COBOL_CONTEXT = f"""
=== ACCOUNTING_SYSTEM.COB ===
{COBOL_ACCOUNTING}

=== BUYROUTINE.COB ===
{COBOL_BUYROUTINE}

=== DATABASE.txt ===
{DATABASE_TXT}

=== products.txt ===
{PRODUCTS_TXT}
"""

    # ── Lettura prompt ────────────────────────────────────────────────────────
    PROMPT_ORCHESTRATOR = get_prompt("01_orchestrator.md")
    PROMPT_DISCOVERY    = get_prompt("02_discovery.md")
    PROMPT_ARCHITECTURE = get_prompt("03_architecture.md")
    PROMPT_MIGRATION    = get_prompt("04_migration.md")
    PROMPT_CODEGEN      = get_prompt("05_codegen.md")
    PROMPT_REVIEWER     = get_prompt("06_reviewer.md")

    print(f"File COBOL caricati: {len(COBOL_ACCOUNTING)} + {len(COBOL_BUYROUTINE)} char")
    print(f"Prompt caricati: {len(PROMPT_ORCHESTRATOR)} + {len(PROMPT_DISCOVERY)} + ...")

    return (
        COBOL_CONTEXT, PROMPT_ARCHITECTURE, PROMPT_CODEGEN,
        PROMPT_DISCOVERY, PROMPT_MIGRATION, PROMPT_ORCHESTRATOR,
        PROMPT_REVIEWER,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CELLA 3 — Stato del grafo e LLM
# ═══════════════════════════════════════════════════════════════════════════════
@app.cell
def _(
    Annotated, BaseModel, COBOL_CONTEXT, ChatMistralAI, END, Field,
    HumanMessage, MemorySaver, Optional, PROMPT_ARCHITECTURE,
    PROMPT_CODEGEN, PROMPT_DISCOVERY, PROMPT_MIGRATION,
    PROMPT_ORCHESTRATOR, PROMPT_REVIEWER, START, StateGraph,
    SystemMessage, TypedDict, add_messages, mlflow, os, time, uuid,
):
    # ── LLM ───────────────────────────────────────────────────────────────────
    llm = ChatMistralAI(
        model="mistral-small-latest",
        temperature=0,
        api_key=os.getenv("MISTRAL_API_KEY"),
    )

    # ── Stato globale del grafo ───────────────────────────────────────────────
    class ModernizerState(TypedDict):
        messages:             Annotated[list, add_messages]
        user_request:         str
        next_agent:           str

        # Flags di completamento step
        discovery_done:       bool
        architecture_done:    bool
        migration_done:       bool

        # Output accumulati dagli agenti
        discovery_output:     str
        architecture_output:  str
        migration_output:     str
        codegen_output:       str
        reviewer_output:      str

        # Output finale mostrato all utente
        final_response:       str

    # ── Schema output strutturato orchestratore ───────────────────────────────
    class OrchestratorDecision(BaseModel):
        ragionamento: str = Field(
            description="Spiega perche hai scelto questo agente e quale step e necessario prima."
        )
        next_agent: str = Field(
            description="L agente da attivare: discovery, architecture, migration, codegen, reviewer"
        )
        missing_steps: str = Field(
            description="Lista degli step precedenti non ancora completati, o 'nessuno' se tutti ok."
        )

    orchestrator_llm = llm.with_structured_output(OrchestratorDecision)

    # ═══════════════════════════════════════════════════════════════════════════
    # NODI DEL GRAFO
    # ═══════════════════════════════════════════════════════════════════════════

    @mlflow.trace(name="[1] Orchestrator Node")
    def orchestrator_node(state: ModernizerState):
        print("\n🎯 ORCHESTRATOR: Analisi richiesta utente...")

        contesto_stato = (
            f"STATO ATTUALE DEL PROGETTO:\n"
            f"- Discovery completato: {state.get('discovery_done', False)}\n"
            f"- Architecture completata: {state.get('architecture_done', False)}\n"
            f"- Migration completata: {state.get('migration_done', False)}\n\n"
            f"RICHIESTA UTENTE: {state['user_request']}"
        )

        res = orchestrator_llm.invoke([
            SystemMessage(content=PROMPT_ORCHESTRATOR),
            HumanMessage(content=contesto_stato),
        ])

        # Opzione B: forza i passi precedenti se mancanti
        agent_richiesto = res.next_agent.strip().lower()

        if agent_richiesto in ("codegen", "reviewer"):
            if not state.get("discovery_done", False):
                agent_richiesto = "discovery"
                print("   ⚠️  Forzo DISCOVERY — step obbligatorio mancante")
            elif not state.get("architecture_done", False):
                agent_richiesto = "architecture"
                print("   ⚠️  Forzo ARCHITECTURE — step obbligatorio mancante")

        if agent_richiesto == "migration" and not state.get("discovery_done", False):
            agent_richiesto = "discovery"
            print("   ⚠️  Forzo DISCOVERY — richiesto prima di migration")

        print(f"   Ragionamento: {res.ragionamento[:100]}...")
        print(f"   Agente selezionato: {agent_richiesto}")
        print(f"   Step mancanti: {res.missing_steps}")

        span = mlflow.get_current_active_span()
        if span:
            span.set_attribute("ragionamento", res.ragionamento)
            span.set_attribute("next_agent", agent_richiesto)
            span.set_attribute("missing_steps", res.missing_steps)

        return {"next_agent": agent_richiesto}


    @mlflow.trace(name="[2] Discovery Agent")
    def discovery_node(state: ModernizerState):
        print("\n🔍 DISCOVERY: Analisi codice COBOL in corso...")

        res = llm.invoke([
            SystemMessage(content=PROMPT_DISCOVERY),
            HumanMessage(content=(
                f"Analizza il seguente codice COBOL ed estrai tutte le business rules:\n\n"
                f"{COBOL_CONTEXT}"
            )),
        ])

        output = res.content
        print(f"   Output: {len(output)} caratteri generati")

        span = mlflow.get_current_active_span()
        if span:
            span.set_attribute("output_length", len(output))
            span.set_attribute("preview", output[:200])

        return {
            "discovery_output": output,
            "discovery_done":   True,
            "final_response":   output,
        }


    @mlflow.trace(name="[3] Architecture Agent")
    def architecture_node(state: ModernizerState):
        print("\n🏗️  ARCHITECTURE: Progettazione struttura Python...")

        res = llm.invoke([
            SystemMessage(content=PROMPT_ARCHITECTURE),
            HumanMessage(content=(
                f"CODICE COBOL ORIGINALE:\n{COBOL_CONTEXT}\n\n"
                f"ANALISI BUSINESS RULES:\n{state.get('discovery_output', 'Non disponibile')}"
            )),
        ])

        output = res.content
        print(f"   Output: {len(output)} caratteri generati")

        span = mlflow.get_current_active_span()
        if span:
            span.set_attribute("output_length", len(output))
            span.set_attribute("preview", output[:200])

        return {
            "architecture_output": output,
            "architecture_done":   True,
            "final_response":      output,
        }


    @mlflow.trace(name="[4] Migration Agent")
    def migration_node(state: ModernizerState):
        print("\n🗃️  MIGRATION: Generazione script ETL PostgreSQL...")

        res = llm.invoke([
            SystemMessage(content=PROMPT_MIGRATION),
            HumanMessage(content=(
                f"CODICE COBOL ORIGINALE:\n{COBOL_CONTEXT}\n\n"
                f"ANALISI BUSINESS RULES:\n{state.get('discovery_output', 'Non disponibile')}\n\n"
                f"ARCHITETTURA PROPOSTA:\n{state.get('architecture_output', 'Non disponibile')}"
            )),
        ])

        output = res.content
        print(f"   Output: {len(output)} caratteri generati")

        span = mlflow.get_current_active_span()
        if span:
            span.set_attribute("output_length", len(output))
            span.set_attribute("preview", output[:200])

        return {
            "migration_output": output,
            "migration_done":   True,
            "final_response":   output,
        }


    @mlflow.trace(name="[5] CodeGen Agent")
    def codegen_node(state: ModernizerState):
        print("\n💻 CODEGEN: Generazione codice Python modernizzato...")

        res = llm.invoke([
            SystemMessage(content=PROMPT_CODEGEN),
            HumanMessage(content=(
                f"CODICE COBOL ORIGINALE:\n{COBOL_CONTEXT}\n\n"
                f"BUSINESS RULES ESTRATTE:\n{state.get('discovery_output', 'Non disponibile')}\n\n"
                f"ARCHITETTURA PROPOSTA:\n{state.get('architecture_output', 'Non disponibile')}\n\n"
                f"SCRIPT MIGRAZIONE DATI:\n{state.get('migration_output', 'Non disponibile')}\n\n"
                f"RICHIESTA SPECIFICA: {state.get('user_request', '')}"
            )),
        ])

        output = res.content
        print(f"   Output: {len(output)} caratteri generati")

        span = mlflow.get_current_active_span()
        if span:
            span.set_attribute("output_length", len(output))
            span.set_attribute("preview", output[:200])

        # Salva output su file
        import os as _os
        base = _os.path.dirname(_os.path.abspath(__file__))
        out_path = _os.path.join(base, "output", f"codegen_{int(time.time())}.py")
        _os.makedirs(_os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"   Salvato in: {out_path}")

        return {
            "codegen_output": output,
            "final_response": output,
        }


    @mlflow.trace(name="[6] Reviewer Agent")
    def reviewer_node(state: ModernizerState):
        print("\n✅ REVIEWER: Verifica qualita del codice generato...")

        res = llm.invoke([
            SystemMessage(content=PROMPT_REVIEWER),
            HumanMessage(content=(
                f"CODICE COBOL ORIGINALE:\n{COBOL_CONTEXT}\n\n"
                f"CODICE PYTHON GENERATO:\n{state.get('codegen_output', 'Non disponibile')}"
            )),
        ])

        output = res.content
        print(f"   Output: {len(output)} caratteri generati")

        span = mlflow.get_current_active_span()
        if span:
            span.set_attribute("output_length", len(output))
            span.set_attribute("preview", output[:200])

        return {
            "reviewer_output": output,
            "final_response":  output,
        }


    # ═══════════════════════════════════════════════════════════════════════════
    # ROUTING
    # ═══════════════════════════════════════════════════════════════════════════

    def route_after_orchestrator(state: ModernizerState):
        agent = state.get("next_agent", "discovery")
        valid = {"discovery", "architecture", "migration", "codegen", "reviewer"}
        return agent if agent in valid else "discovery"


    # ═══════════════════════════════════════════════════════════════════════════
    # COSTRUZIONE GRAFO
    # ═══════════════════════════════════════════════════════════════════════════

    builder = StateGraph(ModernizerState)

    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("discovery",    discovery_node)
    builder.add_node("architecture", architecture_node)
    builder.add_node("migration",    migration_node)
    builder.add_node("codegen",      codegen_node)
    builder.add_node("reviewer",     reviewer_node)

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {
            "discovery":    "discovery",
            "architecture": "architecture",
            "migration":    "migration",
            "codegen":      "codegen",
            "reviewer":     "reviewer",
        }
    )

    # Tutti i nodi terminano dopo l esecuzione
    for node in ["discovery", "architecture", "migration", "codegen", "reviewer"]:
        builder.add_edge(node, END)

    memory  = MemorySaver()
    graph   = builder.compile(checkpointer=memory)


    # ═══════════════════════════════════════════════════════════════════════════
    # CHATBOT HANDLER
    # ═══════════════════════════════════════════════════════════════════════════

    def resetChatbot():
        thread_id = str(uuid.uuid4())

        # Stato persistente tra i messaggi
        project_state = {
            "discovery_done":     False,
            "architecture_done":  False,
            "migration_done":     False,
            "discovery_output":   "",
            "architecture_output": "",
            "migration_output":   "",
            "codegen_output":     "",
        }

        def chatbot_handler(messages, config):
            user_message = getattr(messages, "content", messages)[-1].content

            if mlflow.active_run():
                mlflow.end_run()

            with mlflow.start_run(run_name=f"modernizer-{thread_id[:8]}"):
                mlflow.log_param("model",        "mistral-small-latest")
                mlflow.log_param("thread_id",    thread_id)
                mlflow.log_param("user_request", user_message[:100])
                mlflow.log_text(user_message, "user_request.txt")

                for attempt in range(3):
                    try:
                        # Costruisce lo stato di input con il contesto accumulato
                        input_state = {
                            "messages":     [HumanMessage(content=user_message)],
                            "user_request": user_message,
                            **project_state,
                        }

                        response = graph.invoke(
                            input_state,
                            config={"configurable": {
                                "thread_id":       thread_id,
                                "recursion_limit": 10,
                            }},
                            debug=True,
                        )

                        # Aggiorna lo stato persistente con i nuovi output
                        for key in ["discovery_done", "architecture_done",
                                    "migration_done", "discovery_output",
                                    "architecture_output", "migration_output",
                                    "codegen_output"]:
                            if response.get(key) is not None:
                                project_state[key] = response[key]

                        # Log MLflow
                        mlflow.log_metric("discovery_done",    int(project_state["discovery_done"]))
                        mlflow.log_metric("architecture_done", int(project_state["architecture_done"]))
                        mlflow.log_metric("migration_done",    int(project_state["migration_done"]))

                        output = response.get("final_response", "")
                        if output:
                            mlflow.log_text(output, "agent_output.txt")
                            return output

                        return "Errore: nessun output generato."

                    except Exception as e:
                        mlflow.log_param("error", str(e))
                        if "503" in str(e) or "overflow" in str(e):
                            if attempt < 2:
                                time.sleep(2)
                                continue
                        return f"Errore: {e}"

        return chatbot_handler

    return graph, resetChatbot


# ═══════════════════════════════════════════════════════════════════════════════
# CELLA 4 — Visualizzazione grafo
# ═══════════════════════════════════════════════════════════════════════════════
@app.cell
def _(graph, mo):
    mo.mermaid(graph.get_graph().draw_mermaid())
    return


# ═══════════════════════════════════════════════════════════════════════════════
# CELLA 5 — Chat UI
# ═══════════════════════════════════════════════════════════════════════════════
@app.cell
def _(mo, resetChatbot):
    chatbot_handler = resetChatbot()
    chat_interface  = mo.ui.chat(
        chatbot_handler,
        prompts=[
            "Analizza il codice COBOL ed estrai le business rules",
            "Progetta l architettura Python moderna per questo sistema",
            "Genera lo script di migrazione dati in PostgreSQL",
            "Genera il codice Python per il modulo Employee con calcolo stipendi",
            "Genera il codice Python per il modulo acquisti con ricevuta",
            "Verifica la qualita del codice generato",
        ],
    )
    mo.vstack([
        mo.md("## 🏭 COBOL Modernizer — Supermarket System"),
        mo.md("Trasforma il sistema gestionale COBOL in Python moderno con PostgreSQL."),
        chat_interface,
    ])
    return


# ═══════════════════════════════════════════════════════════════════════════════
# CELLA 6 — MLflow Control Panel
# ═══════════════════════════════════════════════════════════════════════════════
@app.cell
def _(mo, socket, subprocess, time):
    get_state, set_state = mo.state({"running": False, "port": 8080})

    def is_port_open(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(("127.0.0.1", port)) == 0

    def start_mlflow():
        port = get_state()["port"]
        if not is_port_open(port):
            subprocess.Popen(
                ["mlflow", "ui", "--port", str(port), "--host", "127.0.0.1"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(2)
        set_state({"running": True, "port": port})

    attivo = is_port_open(get_state()["port"])

    bottone = mo.ui.button(
        label="🚀 Avvia MLflow",
        on_click=lambda _: start_mlflow(),
        disabled=attivo,
        kind="neutral",
    )
    status = (
        mo.md(f"🟢 **MLflow attivo** sulla porta {get_state()['port']}")
        if attivo else mo.md("🔴 **MLflow spento**")
    )
    link = (
        mo.Html(
            f'<a href="http://127.0.0.1:{get_state()["port"]}" target="_blank" '
            f'style="padding:10px 20px;background:#0194E3;color:white;'
            f'border-radius:8px;text-decoration:none;font-weight:bold;">'
            f'🔗 Apri Dashboard MLflow</a>'
        ) if attivo else mo.md("_Avvia il server per vedere il link_")
    )

    mo.vstack([
        mo.md("### 📊 MLflow Control Panel"),
        mo.hstack([bottone, status], align="center", justify="start"),
        mo.md("---"),
        link,
    ])
    return


if __name__ == "__main__":
    app.run()
