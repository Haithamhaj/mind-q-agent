# Contributing to Mind-Q Agent

Thank you for your interest in contributing to Mind-Q Agent! 🎉

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mind-q-agent.git
   cd mind-q-agent
   ```
3. **Set up** the development environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

## 📝 Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow existing code style
- Add docstrings to functions and classes
- Keep functions small and focused

### 3. Write Tests
All new features should have tests:
```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mind_q_agent
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `test:` — Tests
- `refactor:` — Code refactoring

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```
Then create a Pull Request on GitHub.

## 🏗️ Project Structure

```
mind_q_agent/
├── config/       # Configuration management
├── discovery/    # Web crawling
├── extraction/   # NLP & entities
├── graph/        # KùzuDB interface
├── ingestion/    # Document processing
├── learning/     # Hebbian learning
├── search/       # Search engine
├── vector/       # ChromaDB interface
├── watcher/      # File monitoring
└── utils/        # Helpers
```

## ✅ Code Quality

- All tests must pass
- No linting errors
- Docstrings required for public APIs
- Type hints encouraged

## 📋 Areas for Contribution

- 📄 More file format parsers
- 🌐 Web UI dashboard
- 📊 Visualization tools
- 🔧 Performance optimizations
- 📖 Documentation improvements

## ❓ Questions?

Open an issue or discussion on GitHub!
