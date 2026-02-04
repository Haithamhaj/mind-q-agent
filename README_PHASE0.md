# 🏗️ Phase 0: Foundation Layer Documentation

## Overview
The Foundation Layer provides the core infrastructure for the Mind-Q Agent, handling data storage, configuration, error management, and file system monitoring.

## 📂 Architecture Components

### 1. Database Layer
*   **Graph Database:** KùzuDB (`src/graph/kuzu_graph.py`)
    *   Embedded, high-performance graph store.
    *   Handles Nodes (`Document`, `Concept`) and Edges (`DISCUSSES`, `RELATED_TO`, `IS_CHILD_OF`).
*   **Vector Database:** ChromaDB (`src/vector/chroma_store.py`)
    *   Local vector storage for semantic search.
    *   Stores document embeddings and metadata.

### 2. Infrastructure
*   **File Watcher:** `FileWatcher` (`src/watcher/file_watcher.py`)
    *   Monitors `./data/docs` for changes.
    *   Debounces events (1.0s window).
    *   Queues events for the Ingestion Pipeline.
*   **Config Manager:** `ConfigManager` (`src/config/manager.py`)
    *   Singleton loading from `config/default.yaml`.
    *   Supports Environment Variable overrides (e.g., `MINDQ_DB_GRAPH_PATH`).
*   **Logging:** `src/utils/logger.py`
    *   Structured logging to console (colorized) and file (`logs/mindq.log`).
    *   Rotating file handler (10MB limit).

### 3. Utilities
*   **Error Handling:** `src/utils/errors.py`
    *   `MindQError`: Base exception.
    *   `DatabaseError`, `IngestionError`: Specific domains.
    *   `log_error`: Standardized error logging helper.
*   **Scripts:**
    *   `scripts/init_db.py`: Initializes or resets the KùzuDB schema.

## 🚀 Usage

### Initialization
```bash
# Initialize databases
python scripts/init_db.py

# Reset (Delete existing data and re-init)
python scripts/init_db.py --reset
```

### Configuration
Edit `config/default.yaml` or use Environment Variables:
```bash
export MINDQ_LOGGING_LEVEL=DEBUG
export MINDQ_DB_GRAPH_PATH=/path/to/graph
```

## 🧪 Testing
Run Phase 0 Integration Test:
```bash
pytest tests/integration/test_phase0.py -v
```
