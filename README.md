# Mind-Q Agent

An intelligent local knowledge management system that combines graph databases, vector embeddings, and NLP to build a personal knowledge graph from your files.

## 🎯 Overview

Mind-Q Agent is a production-quality knowledge management system that:
- Monitors local files and extracts knowledge automatically
- Builds a semantic knowledge graph using KùzuDB
- Creates vector embeddings for intelligent search using ChromaDB
- Uses NLP (spaCy) for entity extraction and relationship detection
- Implements Hebbian learning for strengthening connections

## 🏗️ Architecture

```
File Watcher → Text Extraction → Entity Extraction → Graph + Vector Storage → Search
```

### Technology Stack

- **Python 3.10+** - Core language
- **KùzuDB** - High-performance embedded graph database
- **ChromaDB** - Vector database for semantic search
- **spaCy** - NLP and entity extraction
- **sentence-transformers** - Text embeddings
- **watchdog** - File system monitoring

## 📁 Project Structure

```
mind-q-agent/
├── src/
│   ├── graph/         # KùzuDB interface
│   ├── vector/        # ChromaDB interface
│   ├── extraction/    # Entity extraction
│   ├── watcher/       # File system monitoring
│   ├── learning/      # Hebbian learning
│   ├── query/         # Search engine
│   └── utils/         # Utilities
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── data/
│   ├── graph/         # Graph database storage
│   ├── vectors/       # Vector storage
│   ├── uploads/       # Input files
│   └── outputs/       # Generated outputs
├── config/            # Configuration files
└── docs/              # Documentation
```

## 🚀 Setup

### 1. Clone and Navigate
```bash
cd /Users/haitham/development/mind-q-agent
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

## 🧪 Development

### Run Tests
```bash
pytest tests/ -v --cov=src
```

### Code Formatting
```bash
black src/ tests/
ruff check src/ tests/
```

### Using Aider (AI Pair Programming)
```bash
aider --model gemini/gemini-2.0-flash-exp
```

## 📝 Development Phases

Development follows a phase-by-phase approach with testing after each task:

1. **Phase 1**: Core Infrastructure (Graph + Vector DB interfaces)
2. **Phase 2**: File Watching & Text Extraction
3. **Phase 3**: Entity Extraction & NLP
4. **Phase 4**: Hebbian Learning
5. **Phase 5**: Query & Search Engine
6. **Phase 6**: Discovery & Insights

## 🤝 Contributing

This is a personal project, but contributions and suggestions are welcome!

## 📄 License

MIT License

---

**Status**: 🚧 In Development
