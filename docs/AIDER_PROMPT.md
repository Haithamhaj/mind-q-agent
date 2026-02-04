## Aider Prompt for Mind-Q Agent Development

Copy this exact prompt when starting Aider:

```
أنا أبني Mind-Q Agent - نظام knowledge management محلي.

السياق:
- Technology Stack: Python 3.10+, KùzuDB (graph database), ChromaDB (vector database), spaCy (NLP)
- الهندسة: File watcher → Text extraction → Entity extraction → Graph + Vector storage → Search
- الهدف: بناء phase بـ phase مع اختبارات بعد كل task

هيكل المشروع:
```
mind-q-agent/
├── src/
│   ├── graph/         # KùzuDB interface
│   ├── vector/        # ChromaDB interface  
│   ├── extraction/    # استخراج entities
│   ├── watcher/       # مراقبة الملفات
│   ├── learning/      # Hebbian learning
│   └── query/         # Search engine
├── tests/
│   ├── unit/
│   └── integration/
└── data/
```

راح أعطيك tasks واحد واحد. لكل task:
1. اكتب الكود مع type hints كاملة و docstrings
2. error handling محكم
3. unit tests شاملة  
4. production-quality code

جاهز؟
```

## How to Start

```bash
cd /Users/haitham/development/mind-q-agent
source venv/bin/activate
aider --model gemini/gemini-2.0-flash-exp
```

Then paste the prompt above and start developing!
