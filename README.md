# 🧠 Mind-Q Agent

> A local-first intelligent knowledge management system that learns and adapts over time.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-120%2B%20passing-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 📁 **File Watching** — Automatically ingests new documents
- 🕸️ **Knowledge Graph** — Builds semantic relationships using KùzuDB
- 🔍 **Vector Search** — Semantic similarity search via ChromaDB
- 🧬 **Hebbian Learning** — Connections strengthen with use
- 🌐 **Web Discovery** — Crawl and ingest web content
- 📊 **Confidence Scoring** — Multi-factor knowledge reliability

---

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ File Watcher│───▶│  Ingestion  │───▶│  Extraction │
└─────────────┘    │  Pipeline   │    │  (NLP)      │
                   └─────────────┘    └──────┬──────┘
                                             │
              ┌──────────────────────────────┼──────────────────────────┐
              ▼                              ▼                          ▼
        ┌──────────┐                  ┌──────────┐               ┌──────────┐
        │ KùzuDB   │◀═══════════════▶│ ChromaDB │               │ SQLite   │
        │ (Graph)  │                  │ (Vector) │               │ (Events) │
        └──────────┘                  └──────────┘               └──────────┘
              │                              │                          │
              └──────────────────────────────┼──────────────────────────┘
                                             ▼
                                    ┌─────────────────┐
                                    │  Search Engine  │
                                    └─────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ Learning System │
                                    │ (Hebbian/Decay) │
                                    └─────────────────┘
```

---

## 📁 Project Structure

```
mind-q-agent/
├── mind_q_agent/               # Main source code
│   ├── config/                 # Configuration manager
│   ├── discovery/              # Web crawling & discovery
│   │   ├── fetcher.py          # Async HTTP client
│   │   ├── parser.py           # HTML content extraction
│   │   └── engine.py           # Discovery loop
│   ├── extraction/             # NLP & entity extraction
│   ├── graph/                  # KùzuDB interface
│   ├── ingestion/              # Document processing pipeline
│   ├── learning/               # Hebbian learning components
│   │   ├── tracker.py          # Interaction logging
│   │   ├── hebbian_math.py     # Weight calculations
│   │   ├── decay_math.py       # Temporal decay
│   │   ├── pruning.py          # Graph pruning
│   │   ├── scheduler.py        # Maintenance jobs
│   │   ├── confidence.py       # Confidence scoring
│   │   ├── hierarchy.py        # Concept classification
│   │   ├── cluster.py          # Community detection
│   │   └── authority.py        # Source authority
│   ├── search/                 # Search engine
│   ├── vector/                 # ChromaDB interface
│   ├── watcher/                # File system monitoring
│   ├── utils/                  # Helpers & logging
│   └── cli.py                  # CLI implementation
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests (20+ files)
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
├── config/
│   └── default.yaml            # Default configuration
├── scripts/
│   ├── init_db.py              # Database initialization
│   └── generate_status_report.py
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/mind-q-agent.git
cd mind-q-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLP model
python -m spacy download en_core_web_sm
```

### 2. Initialize Databases

```bash
python scripts/init_db.py
```

### 3. Run the CLI

```bash
# Show help
python main.py --help

# Search for knowledge
python main.py search "machine learning neural networks"

# Ingest a file
python main.py ingest /path/to/document.pdf
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mind_q_agent --cov-report=html

# Run specific test module
pytest tests/unit/test_hebbian_math.py -v
```

---

## ⚙️ Configuration

Edit `config/default.yaml`:

```yaml
db:
  graph_path: ./data/graph
  vector_path: ./data/vectors
  interactions_path: ./data/interactions.db

learning:
  hebbian_alpha: 0.1
  decay_rate: 0.01
  prune_threshold: 0.1

discovery:
  max_pages: 10
  timeout: 10.0
```

---

## 📊 Development Phases

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 0** | Foundation (DB interfaces, config, logging) | ✅ 100% |
| **Phase 1** | MVP Core (Ingestion, search, CLI) | ✅ 100% |
| **Phase 2** | Learning (Hebbian, decay, pruning) | ✅ 100% |
| **Phase 3** | Enhancements (Discovery, confidence, clustering) | ✅ 100% |

**Total Progress: 40/40 tasks (100%)**

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| Graph DB | KùzuDB |
| Vector DB | ChromaDB |
| NLP | spaCy + sentence-transformers |
| File Watching | watchdog |
| PDF Parsing | PyMuPDF |
| Testing | pytest |

---

## 📚 Key Concepts

### Hebbian Learning
> "Neurons that fire together, wire together"

When you search for concepts and click on results, the connections between those concepts strengthen over time.

### Temporal Decay
Unused connections gradually weaken, ensuring the knowledge graph stays relevant.

### Confidence Scoring
Each fact's confidence is calculated from:
- Edge weight (co-occurrence frequency)
- Source authority (trustworthiness)
- Recency (when last updated)
- Corroboration (multiple sources)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Built with ❤️ for personal knowledge management</b>
</p>
