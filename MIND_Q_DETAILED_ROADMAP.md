# 🗺️ Mind-Q Agent: The Unified Master Roadmap (The "40-Task" Complete Edition)

**Document Version:** 4.0 (Final Complete Edition)
**Last Updated:** February 4, 2026
**Status:** Active Implementation Guide

---

## 🛑 HOW TO USE THIS MAP

This is the **Single Source of Truth** for Mind-Q. It contains **40 Fully Detailed Tasks**, each with its own specific AI Prompt and Verification Command.

### ⚡ The Workflow
For **EACH** task:
1.  **COPY** the "🤖 AI PROMPT" block.
2.  **PASTE** into your AI agent.
3.  **VERIFY** with the "🧪 COMMAND".
4.  **COMMIT** when green.

---

## 📚 SECTION 1: TECHNICAL CONTEXT (Paste once at start of chat)

**Architecture:**
- **Graph:** KùzuDB (Embedded, C++)
- **Vector:** ChromaDB (Local, Persistent)
- **Concurrency:** Python Multiprocessing for CPU tasks
- **Orchestration:** `queue.Queue`

**Core Formulas:**
1.  **Edge Weight:** $w_{new} = w_{old} + 0.1 \cdot (1 - w_{old}) \cdot I$
2.  **Uncertainty:** $C = 1 - \frac{1}{\sqrt{N + 1}}$
3.  **Decay:** $w_{t} = w_{0} \cdot e^{-0.01 t}$

---

## 🏗️ PHASE 0: FOUNDATION (Tasks 1-10)

### ✅ Task 1: KùzuDB Graph Interface (Complete)
*Status: Done* | *Tests: 17/17 Passed*

### ✅ Task 2: ChromaDB Vector Interface (Complete)
*Status: Done* | *Tests: 8/8 Passed*

### ⏳ Task 3: Entity Extraction (Core Logic)
**Description:** Implement `EntityExtractor` to pull Persons, Orgs, and Dates from text.
**🧪 Command:** `pytest tests/unit/test_entity_extractor.py -v`
**🤖 AI PROMPT:**
```python
Task: Implement Entity Extractor

Create file: src/extraction/entity_extractor.py

Class: EntityExtractor
Dependencies: spaCy (en_core_web_sm), re

Method: extract_all(text: str) -> dict
- entities: List[dict] (Person, Org, GPE from spaCy)
- dates: List[dict] (Regex for "YYYY-MM-DD", "DD Month YYYY")
- emails: List[str] (Regex)
- concepts: List[str] (Noun phrases, lowercase, deduplicated)

Requirements:
- Deterministic output
- Normalize dates to ISO-8601 if possible
- Ignore entities < 3 chars

Create tests in: tests/unit/test_entity_extractor.py
```

### ✅ Task 4: File Watcher (Complete)
*Status: Done* | *Tests: 6/6 Passed*

### ⏳ Task 5: Integration Test (Phase 0)
**Description:** Integration test verifying Watcher -> Queue -> Mock Processor.
**🧪 Command:** `pytest tests/integration/test_phase0.py -v`
**🤖 AI PROMPT:**
```python
Task: Phase 0 Integration Test

Create file: tests/integration/test_phase0.py

Goal: Verify that file events are correctly queued and can be consumed.

Steps to Test:
1. Setup FileWatcher monitoring a temp directory.
2. Create a file in that directory.
3. Assert that an event appears in the `event_queue`.
4. Assert event contains correct path and type.

Use `pytest` with `tmp_path` fixture.
```

### ⏳ Task 6: Error Handling Layer
**Description:** Custom exception taxonomy for the project.
**🧪 Command:** `pytest tests/unit/test_errors.py -v`
**🤖 AI PROMPT:**
```python
Task: Create Error Handling Module

Create file: src/utils/errors.py

Classes:
- MindQError (Base exception)
- DatabaseError (Inherits MindQError)
- IngestionError (Inherits MindQError)
- ExtractionError (Inherits MindQError)

Properties:
- All errors should accept `message` and optional `original_exception`.
- Add a `log_error(e: Exception)` utility function that formats the error for logging.

Create tests in: tests/unit/test_errors.py
```

### ⏳ Task 7: Config Manager
**Description:** Central configuration loader.
**🧪 Command:** `pytest tests/unit/test_config.py -v`
**🤖 AI PROMPT:**
```python
Task: Create Configuration Manager

Create file: src/config/manager.py
Create file: config/default.yaml

Class: ConfigManager

Functionality:
1. Load `config/default.yaml`.
2. Override with environment variables (e.g., `MINDQ_DB_PATH` overrides `db.path`).
3. Provide singleton access `get_config()`.

Default Config Content:
db:
  graph_path: "./data/graph"
  vector_path: "./data/vector"
watcher:
  watch_dir: "./data/docs"

Create tests in: tests/unit/test_config.py
```

### ⏳ Task 8: Logging System
**Description:** Structured logging setup.
**🧪 Command:** Run `python src/utils/logger.py` to see output.
**🤖 AI PROMPT:**
```python
Task: Setup Logging System

Create file: src/utils/logger.py

Function: setup_logging(level="INFO")

Requirements:
- Use standard `logging` library.
- Format: `%(asctime)s | %(levelname)s | %(name)s | %(message)s`
- Handler 1: Console (StreamHandler) with color (use `colorlog` if available, else standard).
- Handler 2: File (RotatingFileHandler) -> `logs/mindq.log`, max 10MB, keep 5 backups.
- Ensure all project loggers use this config.
```

### ⏳ Task 9: Schema Migration Script
**Description:** Utility to initialize or reset KùzuDB.
**🧪 Command:** `python scripts/init_db.py --dry-run`
**🤖 AI PROMPT:**
```python
Task: Database Initialization Script

Create file: scripts/init_db.py

Functionality:
1. Import `KuzuGraphDB`.
2. Call `initialize_schema()`.
3. Add `--reset` flag: If true, delete existing DB folder before initializing.
4. Add `--dry-run` flag: Print what would happen without doing it.

Use `argparse` for CLI arguments.
```

### ⏳ Task 10: Phase 0 Documentation
**Description:** Add docstrings and generate README.
**🧪 Command:** Check `README_PHASE0.md` existence.
**🤖 AI PROMPT:**
```python
Task: Phase 0 Documentation

1. Iterate through `src/watcher`, `src/graph`, `src/vector`.
2. Ensure every class and public method has a Google-style docstring.
3. Create `README_PHASE0.md` summarizing the architecture of the Foundation Layer.
```

---

## 🚀 PHASE 1: MVP CORE (Tasks 11-20)

### ⏳ Task 11: Ingestion Pipeline Logic
**Description:** Core logic to process a single file.
**🧪 Command:** `pytest tests/unit/test_ingestion_logic.py -v`
**🤖 AI PROMPT:**
```python
Task: Ingestion Pipeline Core Logic

Create file: src/ingestion/pipeline.py

Class: IngestionPipeline
Dependencies: GraphDB, VectorDB, Extractor

Method: process_document(file_path: Path, text: str)
1. Generate file hash (SHA256).
2. Check Graph for existing Document node (deduplication). Return if exists.
3. Extract entities/concepts using Extractor.
4. Store in VectorDB (Text + Embedding + Metadata).
5. Store in GraphDB:
   - Node: Document
   - Nodes: Concepts
   - Edges: DISCUSSES (Doc -> Concept)
```

### ⏳ Task 12: Ingestion Queue Worker
**Description:** Background worker to process the queue.
**🧪 Command:** `pytest tests/unit/test_worker.py -v`
**🤖 AI PROMPT:**
```python
Task: Ingestion Queue Worker

Create file: src/ingestion/worker.py

Class: IngestionWorker(threading.Thread)

Logic:
1. Initialize with `event_queue` and `pipeline`.
2. Run loop: `item = queue.get()`.
3. If item is "STOP", break.
4. Call `pipeline.process_document()`.
5. Log success/failure.
6. Call `queue.task_done()`.

Handle exceptions within the loop so the thread doesn't die.
```

### ⏳ Task 13: Co-occurrence Edge Logic
**Description:** Algorithm to link concepts.
**🧪 Command:** `pytest tests/unit/test_cooccurrence.py -v`
**🤖 AI PROMPT:**
```python
Task: Implement Co-occurrence Logic

Update file: src/ingestion/pipeline.py

Method: _create_concept_edges(concepts: List[str], text: str)

Logic:
1. Find all index positions of each concept in text.
2. For each pair of concepts (A, B):
   - Check minimum distance between any instance of A and B.
   - If distance < 100 characters:
     - Create/Update RELATED_TO edge in Graph.
     - Weight increase = 0.5 (initial observation).
```

### ⏳ Task 14: Pipeline Unit Tests
**Description:** Test the pipeline in isolation.
**🧪 Command:** `pytest tests/unit/test_ingestion_pipeline.py -v`
**🤖 AI PROMPT:**
```python
Task: Ingestion Pipeline Tests

Create file: tests/unit/test_ingestion_pipeline.py

Tests:
1. test_process_new_document: Verifies full flow calls (Graph, Vector, Extractor).
2. test_duplicate_document: Verifies it returns early if hash exists.
3. test_error_handling: Verifies exceptions are caught and logged.

Use `unittest.mock` to mock the DBs and Extractor.
```

### ⏳ Task 15: Search Engine (Vector)
**Description:** Clean API for searching.
**🧪 Command:** `pytest tests/unit/test_search.py -v`
**🤖 AI PROMPT:**
```python
Task: Search Engine Core

Create file: src/search/engine.py

Class: SearchEngine
Dependencies: VectorStore

Method: search(query: str, limit: int = 10) -> List[Result]
1. query_vector = vector_store.embed(query)
2. results = vector_store.search(query_vector, k=limit)
3. Return list of dictionaries: {id, text, score, source_file}.
```

### ⏳ Task 16: Search Result Formatting
**Description:** Pretty print results.
**🧪 Command:** Test visually via python script.
**🤖 AI PROMPT:**
```python
Task: Search Result Formatter

Create file: src/search/formatter.py

Function: format_results_table(results: List[dict]) -> str

Logic:
- Use `rich.table.Table` to create a CLI-friendly table.
- Columns: Score (Green), Source (Blue), Excerpt (White).
- Truncate excerpt to 100 chars.
- Return the rendered string or print to console.
```

### ⏳ Task 17: Search Engine Tests
**Description:** Unit tests for search.
**🧪 Command:** `pytest tests/unit/test_search_engine.py -v`
**🤖 AI PROMPT:**
```python
Task: Search Engine Tests

Create file: tests/unit/test_search_engine.py

Tests:
1. test_search_returns_results: Mock vector store returning 3 items.
2. test_search_empty: Mock returning empty list.
3. test_result_structure: key fields (id, score, text) are present.
```

### ⏳ Task 18: CLI Structure
**Description:** Argument parsing skeleton.
**🧪 Command:** `python mindq_cli.py --help`
**🤖 AI PROMPT:**
```python
Task: CLI Skeleton

Create file: mindq_cli.py

Design:
- Use `argparse`.
- Top-level commands: `init`, `ingest`, `search`, `watch`, `stats`.
- Function `main()` that dispatches to handler functions (e.g., `handle_init`).
- Just print "Not implemented" for handlers for now.
```

### ⏳ Task 19: CLI Implementation
**Description:** Connect CLI to actual code.
**🧪 Command:** `python mindq_cli.py stats`
**🤖 AI PROMPT:**
```python
Task: CLI Implementation

Update file: mindq_cli.py

Implement handlers:
- handle_init: Call `scripts.init_db`.
- handle_ingest: Instantiate Pipeline and process file.
- handle_search: Instantiate Engine and print formatted results.
- handle_stats: Call GraphDB.get_counts().

Use `rich.console` for output.
```

### ⏳ Task 20: Phase 1 E2E Test
**Description:** Full System Test.
**🧪 Command:** `pytest tests/e2e/test_system.py -v`
**🤖 AI PROMPT:**
```python
Task: End-to-End System Test

Create file: tests/e2e/test_system.py

Test: test_full_workflow
1. Init fresh DBs (tmp_path).
2. Write "Hello World" to `test_doc.txt`.
3. Run IngestionPipeline on file.
4. Assert Graph has Document node.
5. Search for "Hello".
6. Assert "test_doc.txt" is in results.
```

---

## 🧠 PHASE 2: LEARNING (Tasks 21-30)

### ⏳ Task 21: Interaction Tracker DB
**Description:** Store user events.
**🧪 Command:** `pytest tests/unit/test_tracker.py -v`
**🤖 AI PROMPT:**
```python
Task: Interaction Tracker Database

Create file: src/learning/tracker.py

Class: InteractionTracker
Storage: SQLite (interactions.db)

Method: __init__
- Create table `interactions` if not exists.
- Columns: id, type (search/view/click), content_id, timestamp.
```

### ⏳ Task 22: Interaction Logger API
**Description:** Public methods to log events.
**🧪 Command:** `pytest tests/unit/test_tracker.py -v`
**🤖 AI PROMPT:**
```python
Task: Logger API

Update file: src/learning/tracker.py

Methods:
1. log_search(query: str)
2. log_view(doc_id: str, duration_sec: float)
3. get_recent_interactions(limit=50)

Implement using SQLite INSERTs.
```

### ⏳ Task 23: Hebbian Formula
**Description:** The math of learning.
**🧪 Command:** `pytest tests/unit/test_hebbian_math.py -v`
**🤖 AI PROMPT:**
```python
Task: Hebbian Math Function

Create file: src/learning/hebbian_math.py

Function: calculate_new_weight(current_weight: float, interaction_score: float, learning_rate=0.1) -> float

Formula: w_new = w_old + alpha * (1 - w_old) * I

Tests:
- assert calculate_new_weight(0.5, 1.0) == 0.55
- assert result never exceeds 1.0
```

### ⏳ Task 24: Hebbian Update Job
**Description:** Apply learning to graph.
**🧪 Command:** `pytest tests/unit/test_hebbian_job.py -v`
**🤖 AI PROMPT:**
```python
Task: Hebbian Update Job

Create file: src/learning/hebbian_engine.py

Class: HebbianEngine
Dependencies: GraphDB, InteractionTracker

Method: run_learning_cycle()
1. Fetch recent interactions.
2. For each interaction (e.g., View Doc X):
   - Get concepts linked to Doc X.
   - For each pair of concepts:
     - Get edge.
     - New Weight = calculate_new_weight(old, 0.5).
     - Update edge in Graph.
```

### ⏳ Task 25: Temporal Decay Math
**Description:** The math of forgetting.
**🧪 Command:** `pytest tests/unit/test_decay.py -v`
**🤖 AI PROMPT:**
```python
Task: Decay Math Function

Create file: src/learning/decay.py

Function: apply_decay(weight: float, time_delta_days: float, lambda_val=0.01) -> float

Formula: w_new = w * exp(-lambda * t)

Tests:
- assert apply_decay(1.0, 0) == 1.0
- assert apply_decay(1.0, 100) < 1.0
```

### ⏳ Task 26: Decay Batch Job
**Description:** Apply decay to graph.
**🧪 Command:** `pytest tests/unit/test_decay_job.py -v`
**🤖 AI PROMPT:**
```python
Task: Decay Batch Job

Update file: src/learning/hebbian_engine.py

Method: apply_global_decay()
1. Iterate all RELATED_TO edges in Graph.
2. Calculate time since `last_accessed`.
3. New Weight = apply_decay(current, days_diff).
4. Update edge.

Optimize: Use a Cypher query in KuzuDB if possible for batch update.
```

### ⏳ Task 27: Graph Pruning Logic
**Description:** Identify what to remove.
**🧪 Command:** `pytest tests/unit/test_pruning.py -v`
**🤖 AI PROMPT:**
```python
Task: Pruning Logic

Create file: src/maintenance/pruner.py

Method: identify_weak_edges(threshold=0.1) -> List[EdgeID]
- Query Graph for RELATED_TO edges where weight < threshold.

Method: identify_orphaned_nodes() -> List[NodeID]
- Query for Concept nodes with degree 0.
```

### ⏳ Task 28: Pruning Execution Job
**Description:** Delete the garbage.
**🧪 Command:** `pytest tests/unit/test_pruning.py -v`
**🤖 AI PROMPT:**
```python
Task: Pruning Job

Update file: src/maintenance/pruner.py

Method: execute_prune(dry_run=False)
1. ids = identify_weak_edges()
2. If not dry_run: Delete edges from Graph.
3. ids = identify_orphaned_nodes()
4. If not dry_run: Delete nodes.
5. Return count of deleted items.
```

### ⏳ Task 29: Maintenance Scheduler
**Description:** Run jobs periodically.
**🧪 Command:** `python src/maintenance/scheduler.py`
**🤖 AI PROMPT:**
```python
Task: Maintenance Scheduler

Create file: src/maintenance/scheduler.py

Class: MaintenanceScheduler
Dependencies: HebbianEngine, Pruner

Method: start()
- Use `schedule` library or simple loop.
- Every 1 hour: run_learning_cycle()
- Every 24 hours: apply_global_decay()
- Every 24 hours: execute_prune()
```

### ⏳ Task 30: Phase 2 Integration Test
**Description:** Verify learning loop.
**🧪 Command:** `pytest tests/integration/test_phase2.py -v`
**🤖 AI PROMPT:**
```python
Task: Phase 2 Integration Test

Create file: tests/integration/test_phase2.py

Test:
1. Create Graph with Edge A-B (weight 0.5).
2. Log Interaction (View) relevant to A and B.
3. Run Hebbian Engine cycle.
4. Assert Edge A-B weight > 0.5.
5. Run Decay cycle (mocking time passing).
6. Assert Edge A-B weight < previous.
```

---

## 🔮 PHASE 3: ENHANCEMENTS (Tasks 31-40)

### ⏳ Task 31: Web Scanner Fetcher
**Description:** Fetch HTTP content.
**🧪 Command:** `pytest tests/unit/test_web.py -v`
**🤖 AI PROMPT:**
```python
Task: Web Fetcher

Create file: src/discovery/fetcher.py

Function: fetch_url(url: str, timeout=10) -> str
- Use `requests` with valid User-Agent.
- Handle timeouts/404s.
- Return raw HTML.
```

### ⏳ Task 32: Web Content Parser
**Description:** HTML to clean text.
**🧪 Command:** `pytest tests/unit/test_parser.py -v`
**🤖 AI PROMPT:**
```python
Task: HTML Parser

Create file: src/discovery/parser.py

Function: parse_html(html: str) -> str
- Use `BeautifulSoup`.
- Remove scripts, styles, nav, footer.
- Extract main text content.
- Return clean string.
```

### ⏳ Task 33: Discovery Loop
**Description:** Find new stuff.
**🧪 Command:** `pytest tests/unit/test_discovery.py -v`
**🤖 AI PROMPT:**
```python
Task: Discovery Loop

Create file: src/discovery/engine.py

Method: run_discovery()
1. Query Graph for top 5 concepts (highest weight).
2. Generate search query (e.g., "latest news on [Concept]").
3. Call `search_web` (mock for now).
4. For each URL found:
   - fetch_url()
   - parse_html()
   - IngestionPipeline.process_text()
```

### ⏳ Task 34: Uncertainty Schema Update
**Description:** Add confidence fields.
**🧪 Command:** `python scripts/update_schema.py`
**🤖 AI PROMPT:**
```python
Task: Schema Update for Uncertainty

Update file: src/graph/schema.py (or init script)

Add properties to RELATED_TO edge:
- confidence: float (default 0.0)
- sample_size: int (default 1)
```

### ⏳ Task 35: Confidence Score Logic
**Description:** Calculate confidence.
**🧪 Command:** `pytest tests/unit/test_uncertainty.py -v`
**🤖 AI PROMPT:**
```python
Task: Confidence Logic

Update file: src/learning/hebbian_math.py

Function: calculate_confidence(sample_size: int) -> float
Formula: 1 - (1 / sqrt(sample_size + 1))

Update HebbianEngine:
- When updating edge, increment `sample_size`.
- Update `confidence` using formula.
```

### ⏳ Task 36: Hierarchy Classifier
**Description:** Tag broad concepts.
**🧪 Command:** `pytest tests/unit/test_hierarchy.py -v`
**🤖 AI PROMPT:**
```python
Task: Hierarchy Classifier

Create file: src/learning/hierarchy.py

Method: classify_broad_concepts(threshold=50)
1. Query all Concepts.
2. If `frequency` (or degree) > threshold:
   - Set `is_broad = True`
   - Else `is_broad = False`
```

### ⏳ Task 37: Cluster Detection
**Description:** Group concepts.
**🧪 Command:** `pytest tests/unit/test_clustering.py -v`
**🤖 AI PROMPT:**
```python
Task: Simple Clustering

Update file: src/learning/hierarchy.py

Method: link_to_parents()
1. For each specific concept (is_broad=False):
2. Find connected broad concepts.
3. Link to the one with highest edge weight:
   - Create IS_CHILD_OF edge.
```

### ⏳ Task 38: Source Authority Config
**Description:** Trusted domains list.
**🧪 Command:** `cat config/sources.yaml`
**🤖 AI PROMPT:**
```python
Task: Authority Config

Create file: config/sources.yaml

Content:
trusted:
  - ".gov"
  - ".edu"
  - "wikipedia.org"
  - "arxiv.org"

weights:
  gov: 1.0
  edu: 0.9
  default: 0.5
```

### ⏳ Task 39: Authority Scorer
**Description:** Score content.
**🧪 Command:** `pytest tests/unit/test_authority.py -v`
**🤖 AI PROMPT:**
```python
Task: Authority Scorer

Create file: src/learning/authority.py

Method: get_score(url: str) -> float
1. Load config.
2. Check if URL matches trusted domains.
3. Return corresponding weight.
4. Default to 0.5.
```

### ⏳ Task 40: Final System Polish
**Description:** Clean up code quality.
**🧪 Command:** `flake8 src`
**🤖 AI PROMPT:**
```python
Task: Final Polish

1. Run `flake8` or `ruff` on `src/`.
2. Fix linting errors.
3. Ensure type hints (`mypy`) are consistent.
4. Create final `README.md` describing how to run the full system.
```

---

**End of Granular Roadmap (40 Tasks)** 🚀
