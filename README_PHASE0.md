# Mind-Q Agent - Phase 0: Foundation

This document describes the foundational components implemented in Phase 0.

## 🎯 Goals Achieved

Phase 0 establishes the core infrastructure required for the Mind-Q Agent:

- ✅ Database interfaces (Graph + Vector)
- ✅ Entity extraction pipeline
- ✅ File system monitoring
- ✅ Configuration management
- ✅ Error handling & logging

---

## 📦 Components

### 1. KùzuDB Graph Interface
**File:** `mind_q_agent/graph/kuzu_graph.py`

Manages the knowledge graph with:
- `Document` and `Concept` node tables
- `DISCUSSES` (Document→Concept) edges
- `RELATED_TO` (Concept↔Concept) edges with weights

```python
from mind_q_agent.graph.kuzu_graph import KuzuGraphDB

graph = KuzuGraphDB(db_path="./data/graph_db")
graph.add_document("doc_123", "My Document", "source.md")
graph.add_concept("Machine Learning", "AI technique")
```

---

### 2. ChromaDB Vector Interface
**File:** `mind_q_agent/vector/chroma_vector.py`

Provides semantic search via embeddings:
- Uses `sentence-transformers` for embedding generation
- Supports similarity search with metadata filtering

```python
from mind_q_agent.vector.chroma_vector import ChromaVectorDB

vector_db = ChromaVectorDB(db_path="./data/vector_db")
vector_db.add_documents(["Text content"], [{"source": "file.md"}], ["doc_1"])
results = vector_db.query_similar("search query", k=5)
```

---

### 3. Entity Extractor
**File:** `mind_q_agent/extraction/entity_extractor.py`

Extracts named entities using spaCy:
- Supports multiple entity types (PERSON, ORG, GPE, etc.)
- Configurable confidence threshold

---

### 4. File Watcher
**File:** `mind_q_agent/watcher/file_watcher.py`

Monitors directories for file changes:
- Uses `watchdog` for real-time monitoring
- Triggers callbacks on create/modify/delete events

---

### 5. Configuration Manager
**File:** `mind_q_agent/config/manager.py`

Singleton pattern for centralized config:
- Loads from `config/default.yaml`
- Supports environment variable overrides

---

### 6. Error Handling
**File:** `mind_q_agent/utils/errors.py`

Custom exception hierarchy:
- `MindQError` (base)
- `DatabaseError`, `ConfigError`, `ExtractionError`, etc.

---

### 7. Logging System
**File:** `mind_q_agent/utils/logger.py`

Standardized logging with:
- Console and file handlers
- Configurable log levels

---

## 🧪 Tests

Run Phase 0 tests:
```bash
pytest tests/unit/test_kuzu_graph.py
pytest tests/unit/test_chroma_vector.py
pytest tests/unit/test_entity_extractor.py
pytest tests/unit/test_file_watcher.py
pytest tests/unit/test_config.py
pytest tests/unit/test_errors.py
pytest tests/integration/test_phase0.py
```

---

## 🚀 Quick Start

```bash
# Initialize databases
python scripts/init_db.py

# Run all Phase 0 tests
pytest tests/ -k "phase0 or kuzu or chroma or config or errors"
```

---

## 📊 Status

| Task | Component | Status |
|------|-----------|--------|
| 1 | KùzuDB Graph | ✅ Complete |
| 2 | ChromaDB Vector | ✅ Complete |
| 3 | Entity Extraction | ✅ Complete |
| 4 | File Watcher | ✅ Complete |
| 5 | Integration Test | ✅ Complete |
| 6 | Error Handling | ✅ Complete |
| 7 | Config Manager | ✅ Complete |
| 8 | Logging System | ✅ Complete |
| 9 | Schema Migration | ✅ Complete |
| 10 | Documentation | ✅ Complete |

**Phase 0: 10/10 tasks (100%)** ✅
