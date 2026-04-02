import marimo

__generated_with = "0.22.0"
app = marimo.App(width="medium")


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

    # LangChain aggiornato — nessun conflitto di dipendenze
    from langchain_mistralai import ChatMistralAI
    from langchain_groq import ChatGroq
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import SystemMessage, HumanMessage
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import StateGraph, START, END
    from langgraph.graph.message import add_messages
    import mlflow
    import mlflow.langchain

    load_dotenv()
    mlflow.set_experiment("COBOL-Modernizer-v2")
    mlflow.langchain.autolog(log_traces=False)
    return (
        Annotated,
        BaseModel,
        ChatAnthropic,
        END,
        Field,
        HumanMessage,
        MemorySaver,
        START,
        StateGraph,
        SystemMessage,
        TypedDict,
        add_messages,
        mlflow,
        mo,
        os,
        socket,
        subprocess,
        time,
        uuid,
    )


@app.cell
def _(os):
    _base_dir = os.path.dirname(os.path.abspath(__file__))

    def _read(path):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except FileNotFoundError:
            return f"[FILE NON TROVATO: {path}]"

    def _prompt(name):
        return _read(os.path.join(_base_dir, "prompts", name))

    COBOL_ACCOUNTING = _read(os.path.join(_base_dir, "ACCOUNTING_SYSTEM.COB"))
    COBOL_BUYROUTINE = _read(os.path.join(_base_dir, "BUYROUTINE.COB"))
    DATABASE_TXT     = _read(os.path.join(_base_dir, "DATABASE.txt"))
    PRODUCTS_TXT     = _read(os.path.join(_base_dir, "products.txt"))

    COBOL_CONTEXT = (
        "=== ACCOUNTING_SYSTEM.COB ===\n" + COBOL_ACCOUNTING +
        "\n=== BUYROUTINE.COB ===\n" + COBOL_BUYROUTINE +
        "\n=== DATABASE.txt ===\n" + DATABASE_TXT +
        "\n=== products.txt ===\n" + PRODUCTS_TXT
    )

    PROMPT_ORCHESTRATOR = _prompt("01_orchestrator.md")
    PROMPT_DISCOVERY    = _prompt("02_discovery.md")
    PROMPT_ARCHITECTURE = _prompt("03_architecture.md")
    PROMPT_MIGRATION    = _prompt("04_migration.md")
    PROMPT_CODEGEN      = _prompt("05_codegen.md")
    PROMPT_FILELIST     = _prompt("05b_filelist.md")
    PROMPT_REVIEWER     = _prompt("06_reviewer.md")

    print(f"COBOL caricato: {len(COBOL_ACCOUNTING) + len(COBOL_BUYROUTINE)} char")
    return (
        COBOL_CONTEXT,
        PROMPT_ARCHITECTURE,
        PROMPT_CODEGEN,
        PROMPT_DISCOVERY,
        PROMPT_FILELIST,
        PROMPT_MIGRATION,
        PROMPT_ORCHESTRATOR,
        PROMPT_REVIEWER,
    )


@app.cell
def _(
    Annotated,
    BaseModel,
    COBOL_CONTEXT,
    ChatAnthropic,
    END,
    Field,
    HumanMessage,
    MemorySaver,
    PROMPT_ARCHITECTURE,
    PROMPT_CODEGEN,
    PROMPT_DISCOVERY,
    PROMPT_FILELIST,
    PROMPT_MIGRATION,
    PROMPT_ORCHESTRATOR,
    PROMPT_REVIEWER,
    START,
    StateGraph,
    SystemMessage,
    TypedDict,
    add_messages,
    mlflow,
    os,
    time,
    uuid,
):
    # ── Scegli il modello LLM ─────────────────────────────────────────────────
    # Cambia questa riga per usare un modello diverso:
    # llm = ChatMistralAI(model="mistral-large-latest", temperature=0, api_key=os.getenv("MISTRAL_API_KEY"), timeout=120)
    # llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=os.getenv("GROQ_API_KEY"))
    llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0, api_key=os.getenv("ANTHROPIC_API_KEY"))

    class ModernizerState(TypedDict):
        messages:             Annotated[list, add_messages]
        user_request:         str
        next_agent:           str
        modalita:             str
        last_completed:       str   # nodo appena completato — usato dall orchestratore per decidere END
        full_generation:      bool  # True = genera tutti i file, False = risposta singola
        discovery_done:       bool
        architecture_done:    bool
        migration_done:       bool
        discovery_output:     str
        architecture_output:  str
        migration_output:     str
        files_da_generare:    str   # JSON con lista file prodotta dall architecture agent
        codegen_output:       str
        reviewer_output:      str
        final_response:       str

    TRIGGER_FULL_GEN = [
        "genera il progetto completo",
        "genera tutto il codice",
        "genera tutti i file",
        "voglio i file python",
        "crea il progetto",
        "full generation",
        "genera il progetto",
    ]

    AUTO_SEQUENCE = ["discovery", "architecture", "migration", "codegen"]

    class OrchestratorDecision(BaseModel):
        ragionamento:  str = Field(description="Perche hai scelto questo agente.")
        next_agent:    str = Field(description="Agente: discovery, architecture, migration, codegen, reviewer")
        missing_steps: str = Field(description="Step precedenti mancanti, o nessuno.")

    orchestrator_llm = llm.with_structured_output(OrchestratorDecision)

    @mlflow.trace(name="[1] Orchestrator")
    def orchestrator_node(state: ModernizerState):
        print("\n[ORCHESTRATOR] Analisi richiesta...")
        req = state["user_request"].lower()
        is_full_gen = any(t in req for t in TRIGGER_FULL_GEN)
        modalita = "auto" if is_full_gen else "step"

        if state.get("modalita") == "auto":
            modalita = "auto"

            # Se codegen e appena completato -> fine sequenza
            if state.get("last_completed") == "codegen":
                print("   -> [AUTO] Completato -> END")
                return {"next_agent": "end", "modalita": modalita}

            for step in AUTO_SEQUENCE:
                if step == "codegen":
                    if (state.get("discovery_done", False) and
                        state.get("architecture_done", False) and
                        state.get("migration_done", False)):
                        print("   -> [AUTO] codegen (full generation)")
                        return {"next_agent": "codegen", "full_generation": True, "modalita": modalita}
                else:
                    if not state.get(step + "_done", False):
                        print(f"   -> [AUTO] {step}")
                        return {"next_agent": step, "modalita": modalita}
            print("   -> [AUTO] Completato -> END")
            return {"next_agent": "end", "modalita": modalita}

        # In step-by-step: se un nodo ha appena completato il suo lavoro, fermati
        if state.get("last_completed"):
            print(f"   -> [STEP] {state['last_completed']} completato -> END")
            return {"next_agent": "end", "last_completed": ""}

        ctx = (
            f"STATO: discovery={state.get('discovery_done',False)}, "
            f"architecture={state.get('architecture_done',False)}, "
            f"migration={state.get('migration_done',False)}\n"
            f"RICHIESTA: {state['user_request']}"
        )
        res = orchestrator_llm.invoke([
            SystemMessage(content=PROMPT_ORCHESTRATOR),
            HumanMessage(content=ctx),
        ])
        agent = "codegen" if is_full_gen else res.next_agent.strip().lower()

        if agent in ("codegen", "reviewer"):
            if not state.get("discovery_done", False):
                agent = "discovery"
                print("   -> Forzo DISCOVERY")
            elif not state.get("architecture_done", False):
                agent = "architecture"
                print("   -> Forzo ARCHITECTURE")
        if agent == "migration" and not state.get("discovery_done", False):
            agent = "discovery"

        print(f"   -> [STEP] {agent}")
        span = mlflow.get_current_active_span()
        if span:
            span.set_attribute("ragionamento", res.ragionamento)
            span.set_attribute("next_agent", agent)
        return {"next_agent": agent, "modalita": modalita, "full_generation": is_full_gen}

    @mlflow.trace(name="[2] Discovery")
    def discovery_node(state: ModernizerState):
        print("\n[DISCOVERY] Analisi COBOL...")
        res = llm.invoke([
            SystemMessage(content=PROMPT_DISCOVERY),
            HumanMessage(content="Analizza il COBOL seguente:\n\n" + COBOL_CONTEXT),
        ])
        out = res.content
        print(f"   -> {len(out)} char")
        return {"discovery_output": out, "discovery_done": True, "final_response": out, "last_completed": "discovery"}

    @mlflow.trace(name="[3] Architecture")
    def architecture_node(state: ModernizerState):
        print("\n[ARCHITECTURE] Progettazione...")

        # Step 1: genera architettura testuale
        res = llm.invoke([
            SystemMessage(content=PROMPT_ARCHITECTURE),
            HumanMessage(content=(
                "COBOL:\n" + COBOL_CONTEXT +
                "\n\nBUSINESS RULES:\n" + state.get("discovery_output", "")
            )),
        ])
        out = res.content
        print(f"   -> {len(out)} char (architettura)")

        # Step 2: genera lista file basata sull architettura appena prodotta
        print("   -> Generazione lista file dall architettura...")

        class FileSpec(BaseModel):
            path:       str = Field(description="Path relativo del file, es. app/models/product.py")
            istruzione: str = Field(description="Istruzione specifica per generare questo file")

        class FileList(BaseModel):
            files: list[FileSpec] = Field(description="Lista ordinata dei file da generare, max 20 file")

        file_list_llm = llm.with_structured_output(FileList)

        try:
            file_list_result = file_list_llm.invoke([
                SystemMessage(content=PROMPT_FILELIST),
                HumanMessage(content=(
                    "ARCHITETTURA PROGETTATA:\n\n" + out +
                    "\n\nBUSINESS RULES:\n" + state.get("discovery_output", "")[:1000]
                )),
            ])
            files = [{"path": f.path, "istruzione": f.istruzione} for f in file_list_result.files]
            import json as _json
            files_json = _json.dumps(files, ensure_ascii=False)
            print(f"   -> Lista: {len(files)} file")
        except Exception as e:
            print(f"   -> Errore lista file: {e} — lista vuota")
            files_json = "[]"

        return {
            "architecture_output":  out,
            "architecture_done":    True,
            "files_da_generare":    files_json,
            "final_response":       out,
            "last_completed":       "architecture",
        }

    @mlflow.trace(name="[4] Migration")
    def migration_node(state: ModernizerState):
        print("\n[MIGRATION] Script ETL...")
        res = llm.invoke([
            SystemMessage(content=PROMPT_MIGRATION),
            HumanMessage(content=(
                "COBOL:\n" + COBOL_CONTEXT +
                "\n\nBUSINESS RULES:\n" + state.get("discovery_output", "") +
                "\n\nARCHITETTURA:\n" + state.get("architecture_output", "")
            )),
        ])
        out = res.content
        print(f"   -> {len(out)} char")
        return {"migration_output": out, "migration_done": True, "final_response": out, "last_completed": "migration"}

    @mlflow.trace(name="[5] CodeGen")
    def codegen_node(state: ModernizerState):
        if state.get("full_generation"):
            print("\n[CODEGEN] Modalita full generation...")
        else:
            print("\n[CODEGEN] Risposta singola...")
            res = llm.invoke([
                SystemMessage(content=PROMPT_CODEGEN),
                HumanMessage(content=(
                    "COBOL:\n" + COBOL_CONTEXT +
                    "\n\nBUSINESS RULES:\n" + state.get("discovery_output", "") +
                    "\n\nARCHITETTURA:\n" + state.get("architecture_output", "") +
                    "\n\nMIGRAZIONE:\n" + state.get("migration_output", "") +
                    "\n\nRICHIESTA: " + state.get("user_request", "")
                )),
            ])
            out = res.content
            print(f"   -> {len(out)} char (nessun file salvato)")
            return {"codegen_output": out, "final_response": out, "last_completed": "codegen"}

        print("\n[FULL CODEGEN] Avvio generazione completa...")

        base    = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(base, "output")

        architecture = state.get("architecture_output", "")
        discovery    = state.get("discovery_output", "")

        # Usa la lista file prodotta dall architecture agent
        import json as _json
        try:
            files_raw = _json.loads(state.get("files_da_generare", "[]"))
            files_da_generare = [(f["path"], f["istruzione"]) for f in files_raw]
            print(f"   [1/1] Lista file dall architettura: {len(files_da_generare)} file")
        except Exception as e:
            print(f"   -> Errore lettura lista: {e} - fallback")
            files_da_generare = [
                ("requirements.txt", "Genera requirements.txt con sqlalchemy, psycopg2-binary, bcrypt, python-dotenv"),
                (".env.example",     "Genera .env.example con DATABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD_HASH"),
                ("README.md",        "Genera README.md con istruzioni setup e avvio"),
            ]

        # Genera ogni file
        print(f"   Generazione {len(files_da_generare)} file...")

        contesto_base = (
            "=== ARCHITETTURA ===\n" + architecture +
            "\n\n=== BUSINESS RULES ===\n" + discovery[:800] +
            "\n\n=== REGOLE CHIAVE ===\n"
            "- SALARY = HOURLY_RATE * HOURS_WORKED (default 500)\n"
            "- PROFIT = SELLING_PRICE - COGS\n"
            "- CHANGE = PAYMENT - TOTAL\n"
            "- Admin: robby@gmail.com, password bcrypt\n"
            "- DB: PostgreSQL via SQLAlchemy, config da .env\n"
        )

        file_generati = []
        file_falliti  = []
        contesto_codice = ""
        totale = len(files_da_generare)
        span = mlflow.get_current_active_span()

        for idx, (filepath, istruzione) in enumerate(files_da_generare, 1):
            print(f"   [{idx}/{totale}] {filepath}...")
            successo = False
            for attempt in range(3):
                try:
                    prompt_file = (
                        contesto_base +
                        "\n\nCODICE GIA GENERATO:\n" + contesto_codice +
                        "\n\nFILE: " + filepath +
                        "\nISTRUZIONE: " + istruzione +
                        "\n\nRestituisci SOLO il codice, senza spiegazioni o markdown."
                    )
                    res = llm.invoke([
                        SystemMessage(content=PROMPT_CODEGEN),
                        HumanMessage(content=prompt_file),
                    ])
                    codice = res.content

                    if codice.strip().startswith("```"):
                        lines = codice.strip().split("\n")
                        lines = lines[1:]
                        if lines and lines[-1].strip() == "```":
                            lines = lines[:-1]
                        codice = "\n".join(lines)

                    full_path = os.path.join(out_dir, filepath)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(codice)

                    contesto_codice += f"\n# === {filepath} ===\n{codice}\n"

                    file_generati.append(filepath)
                    print(f"      -> OK ({len(codice)} char)")
                    successo = True
                    time.sleep(2)
                    break

                except Exception as e:
                    print(f"      -> Tentativo {attempt+1}/3: {e}")
                    if attempt < 10:
                        time.sleep(120)

            if not successo:
                file_falliti.append(filepath)
                print(f"      -> Saltato")

        import zipfile
        zip_path = os.path.join(base, "supermarket_modernizzato.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(out_dir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    zf.write(fpath, os.path.relpath(fpath, out_dir))

        if span:
            span.set_attribute("file_generati", len(file_generati))
            span.set_attribute("file_falliti",  len(file_falliti))

        riepilogo = (
            f"Generazione completata!\n\n"
            f"File generati ({len(file_generati)}/{totale}):\n" +
            "\n".join(f"  - {f}" for f in file_generati) +
            (f"\n\nFile falliti:\n" + "\n".join(f"  - {f}" for f in file_falliti) if file_falliti else "") +
            f"\n\nProgetto in: output/\nZIP: supermarket_modernizzato.zip"
        )
        print(f"\n[FULL CODEGEN] {len(file_generati)}/{totale} file generati")
        return {"codegen_output": riepilogo, "final_response": riepilogo, "last_completed": "codegen"}

    @mlflow.trace(name="[6] Reviewer")
    def reviewer_node(state: ModernizerState):
        print("\n[REVIEWER] Verifica qualita...")
        res = llm.invoke([
            SystemMessage(content=PROMPT_REVIEWER),
            HumanMessage(content=(
                "COBOL:\n" + COBOL_CONTEXT +
                "\n\nCODICE PYTHON:\n" + state.get("codegen_output", "Non disponibile")
            )),
        ])
        out = res.content
        print(f"   -> {len(out)} char")
        return {"reviewer_output": out, "final_response": out, "last_completed": "reviewer"}

    def route_after_orchestrator(state: ModernizerState):
        agent = state.get("next_agent", "discovery")
        if agent == "end":
            return END
        valid = {"discovery", "architecture", "migration", "codegen", "reviewer"}
        return agent if agent in valid else "discovery"

    def route_after_node(state: ModernizerState):
        # Tutti i nodi tornano sempre all orchestratore.
        # E l orchestratore a decidere se continuare o andare a END.
        return "orchestrator"

    builder = StateGraph(ModernizerState)
    builder.add_node("orchestrator",  orchestrator_node)
    builder.add_node("discovery",     discovery_node)
    builder.add_node("architecture",  architecture_node)
    builder.add_node("migration",     migration_node)
    builder.add_node("codegen",       codegen_node)
    builder.add_node("reviewer",      reviewer_node)

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges(
        "orchestrator", route_after_orchestrator,
        {"discovery": "discovery", "architecture": "architecture",
         "migration": "migration", "codegen": "codegen",
         "reviewer": "reviewer", END: END}
    )
    for _n in ["discovery", "architecture", "migration", "codegen", "reviewer"]:
        builder.add_edge(_n, "orchestrator")

    memory = MemorySaver()
    graph  = builder.compile(checkpointer=memory)

    def resetChatbot():
        thread_id = str(uuid.uuid4())
        project_state = {
            "modalita": "step",
            "last_completed": "",
            "full_generation": False,
            "discovery_done": False, "architecture_done": False, "migration_done": False,
            "discovery_output": "", "architecture_output": "",
            "files_da_generare": "[]",
            "migration_output": "", "codegen_output": "",
        }

        def chatbot_handler(messages, config):
            user_message = getattr(messages, "content", messages)[-1].content
            if mlflow.active_run():
                mlflow.end_run()
            with mlflow.start_run(run_name=f"modernizer-v2-{thread_id[:8]}"):
                mlflow.log_param("model", "claude-haiku")
                mlflow.log_param("user_request", user_message[:100])
                mlflow.log_text(user_message, "user_request.txt")
                for attempt in range(3):
                    try:
                        response = graph.invoke(
                            {"messages": [HumanMessage(content=user_message)],
                             "user_request": user_message, **project_state},
                            config={"configurable": {"thread_id": thread_id, "recursion_limit": 10}},
                            debug=True,
                        )
                        for key in ["discovery_done", "architecture_done", "migration_done",
                                    "discovery_output", "architecture_output",
                                    "files_da_generare", "migration_output", "codegen_output",
                                    "last_completed", "full_generation"]:
                            if response.get(key) is not None:
                                project_state[key] = response[key]
                        mlflow.log_metric("discovery_done",    int(project_state["discovery_done"]))
                        mlflow.log_metric("architecture_done", int(project_state["architecture_done"]))
                        mlflow.log_metric("migration_done",    int(project_state["migration_done"]))
                        output = response.get("final_response", "")
                        if output:
                            mlflow.log_text(output, "agent_output.txt")

                            # Salva l output in un file .md nella cartella outputs/
                            last = project_state.get("last_completed", "output")
                            if not last:
                                last = "output"
                            import datetime as _dt
                            timestamp = _dt.datetime.now().strftime("%H%M%S")
                            outputs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
                            os.makedirs(outputs_dir, exist_ok=True)
                            md_path = os.path.join(outputs_dir, f"{last}_{timestamp}.md")
                            with open(md_path, "w", encoding="utf-8") as _f:
                                _f.write(f"# Output: {last}\n")
                                _f.write(f"*Generato il {_dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                                _f.write(f"**Richiesta utente:** {user_message}\n\n")
                                _f.write("---\n\n")
                                _f.write(output)
                            print(f"   -> Output salvato in: outputs/{last}_{timestamp}.md")

                            return output
                        return "Errore: nessun output generato."
                    except Exception as e:
                        mlflow.log_param("error", str(e))
                        if "503" in str(e) or "overflow" in str(e):
                            if attempt < 2:
                                import time as _t
                                _t.sleep(2)
                                continue
                        return f"Errore: {e}"
        return chatbot_handler

    return (resetChatbot,)


@app.cell
def _(mo):
    mo.mermaid("""
    graph LR
    S([start]) --> ORC[orchestrator]

    ORC -->|step| DIS[discovery]
    ORC -->|step| ARC[architecture]
    ORC -->|step| MIG[migration]
    ORC -->|step/full| COD[codegen]
    ORC -->|step| REV[reviewer]
    ORC -->|fine| E([end])

    DIS --> ORC
    ARC --> ORC
    MIG --> ORC
    COD --> ORC
    REV --> ORC
    """)
    return


@app.cell
def _(mo, resetChatbot):
    chatbot_handler = resetChatbot()
    chat_interface  = mo.ui.chat(
        chatbot_handler,
        prompts=[
            "Analizza il codice COBOL ed estrai le business rules",
            "Progetta l architettura Python moderna",
            "Genera lo script di migrazione dati in PostgreSQL",
            "Genera il progetto completo",
        ],
    )
    mo.vstack([
        mo.md("## COBOL Modernizer v2 — LangChain aggiornato"),
        mo.md("Modello attivo: **Claude Haiku** — cambia nella cella 3 per usare Groq o Mistral."),
        chat_interface,
    ])
    return


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
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            time.sleep(2)
        set_state({"running": True, "port": port})

    attivo  = is_port_open(get_state()["port"])
    bottone = mo.ui.button(label="Avvia MLflow", on_click=lambda _: start_mlflow(), disabled=attivo, kind="neutral")
    status  = mo.md(f"MLflow attivo sulla porta {get_state()['port']}") if attivo else mo.md("MLflow spento")
    link    = mo.Html(f'<a href="http://127.0.0.1:{get_state()["port"]}" target="_blank" style="padding:10px 20px;background:#0194E3;color:white;border-radius:8px;text-decoration:none;">Apri MLflow</a>') if attivo else mo.md("_Avvia il server_")
    mo.vstack([mo.md("### MLflow Control Panel"), mo.hstack([bottone, status]), mo.md("---"), link])
    return


if __name__ == "__main__":
    app.run()
