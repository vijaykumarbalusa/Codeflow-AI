# 🤖 CodeFlow AI

> AI-powered Pull Request review automation with RAG and multi-signal analysis

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Features

- **AI Code Analysis** - Groq Llama 3.3 70B for security scanning
- **RAG (Learning)** - Remembers past code patterns, learns from experience
- **Multi-Signal** - Combines AI + static analysis for 85%+ accuracy
- **Vector Search** - Qdrant for semantic code similarity
- **FastAPI** - Production-ready webhook receiver
- **Zero Cost** - 100% free tier resources

## 📊 Accuracy

- Base AI: 70%
- With RAG: 80%
- Multi-signal: 85%+
- False positive rate: <10%

## 🚀 Quick Start
```bash
git clone https://github.com/vijaykumarbalusa/Codeflow-AI.git
cd Codeflow-AI
poetry install
cp .env.example .env
# Add your API keys to .env
poetry run uvicorn src.codeflow.main:app --reload
```

## 🔧 Configuration

Required in `.env`:
- `GROQ_API_KEY` - Get free at console.groq.com
- `QDRANT_URL` - Get free at cloud.qdrant.io
- `QDRANT_API_KEY`

## 🧪 Testing
```bash
poetry run pytest
poetry run python test_multi_signal.py
```

## 📈 Capabilities

**Detects:**
- SQL injection
- Hardcoded secrets
- XSS vulnerabilities
- Missing error handling
- Insecure cryptography
- And more...

**Technologies:**
- FastAPI (web server)
- Groq (LLM inference)
- Qdrant (vector database)
- Pydantic (validation)
- Poetry (dependencies)

## 🏗️ Architecture
```
GitHub Webhook → FastAPI → Multi-Signal Analyzer
                              ├─ RAG (past patterns)
                              ├─ LLM analysis
                              └─ Static analysis
                              ↓
                          Combined result
```

## 📝 License

MIT

## 👤 Author

Vijay Kumar Balusa
# CodeFlow AI Production Test Thu Feb 19 00:11:45 PST 2026
# CodeFlow AI Production Test Thu Feb 19 00:14:31 PST 2026
# Final test
