---
title: CodeFlow AI
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

<div align="center">

<img src="https://img.shields.io/badge/CodeFlow_AI-🤖_PR_Security_Analyzer-6366f1?style=for-the-badge" alt="CodeFlow AI"/>

# CodeFlow AI

### AI-Powered GitHub Pull Request Security Analyzer

[![Live on HF Spaces](https://img.shields.io/badge/🤗_Live_Demo-Hugging_Face-FFD21E?style=flat-square)](https://huggingface.co/spaces/vijaykumarbalusa/codeflow-ai)
[![GitHub App](https://img.shields.io/badge/GitHub_App-CodeFlow--AI-181717?style=flat-square&logo=github)](https://github.com/apps/codeflow-ai-vijaykumarbalusa)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=flat-square)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**CodeFlow AI automatically reviews every Pull Request for security vulnerabilities, code quality issues, and best practice violations — posting detailed analysis comments in seconds.**

[Features](#-features) · [Architecture](#-architecture) · [Setup](#-setup) · [How It Works](#-how-it-works) · [Self-Hosting](#-self-hosting)

---

</div>

## 🚀 What It Does

When a developer opens a Pull Request, CodeFlow AI:

1. **Receives** the GitHub webhook instantly
2. **Analyzes** the code diff using Llama 3.3 70B via Groq
3. **Retrieves** similar past patterns from Qdrant vector DB (RAG)
4. **Posts** a detailed security report directly on the PR — in under 2 seconds

**Example output on a vulnerable PR:**

```
🔍 CodeFlow AI Analysis

Overall Risk: 🔴🔴 Critical
Issues Found: 4
  🔴 High: 4  🟡 Medium: 0  🟢 Low: 0

Issues Found:
  ► 🔴 SQL Injection Vulnerability        (Confidence: 100%)
  ► 🔴 Hardcoded Secret Detected          (Confidence: 100%)
  ► 🔴 Hardcoded Password                 (Confidence: 100%)
  ► 🔴 Path Traversal Vulnerability       (Confidence: 100%)

Analysis Time: 1.35s | Model: Llama 3.3 70B | Files: 1
```

---

## ✨ Features

- **🔒 Security Analysis** — SQL injection, path traversal, hardcoded secrets, XSS, command injection, and more
- **🧠 RAG Learning** — Learns from past PRs using Qdrant vector database, improves over time
- **⚡ Fast** — Full analysis in 1–3 seconds using Groq's ultra-fast inference
- **🤖 Smart** — Llama 3.3 70B understands code context, not just pattern matching
- **🔁 Always On** — Deployed on Hugging Face Spaces, responds to every PR automatically
- **📊 Confidence Scores** — Each issue comes with a confidence percentage
- **✅ Safe-to-Merge** — Clear merge recommendation based on risk level

---

## 🏗 Architecture

```
Developer opens PR
        │
        ▼
GitHub sends webhook
        │
        ▼
┌─────────────────────────────────────────┐
│         CodeFlow AI (HF Spaces)         │
│                                         │
│  FastAPI Webhook Handler                │
│        │                                │
│        ▼                                │
│  MultiSignalAnalyzer                    │
│  ├── RAGCodeAnalyzer                    │
│  │   ├── Qdrant Vector DB  ◄──────────┐ │
│  │   └── FastEmbed (ONNX)             │ │
│  └── Groq API (Llama 3.3 70B)         │ │
│        │                              │ │
│        ▼                              │ │
│  Store patterns for learning ─────────┘ │
│        │                                │
│        ▼                                │
│  Comment Formatter (Markdown)           │
└─────────────────┬───────────────────────┘
                  │
                  ▼
        Posts comment on PR
```

### Tech Stack

| Component | Technology |
|-----------|-----------|
| **API Framework** | FastAPI + Uvicorn |
| **AI Model** | Llama 3.3 70B via Groq |
| **Vector Database** | Qdrant Cloud |
| **Embeddings** | FastEmbed (ONNX, BAAI/bge-small-en-v1.5) |
| **GitHub Integration** | GitHub App (JWT auth) |
| **Hosting** | Hugging Face Spaces (Docker) |
| **Language** | Python 3.12 |

---

## 📁 Project Structure

```
codeflow-ai/
├── src/
│   └── codeflow/
│       ├── main.py                  # FastAPI app, webhook endpoint
│       ├── core/
│       │   ├── config.py            # Settings & environment variables
│       │   ├── auth.py              # GitHub App JWT authentication
│       │   ├── github_client.py     # GitHub API client
│       │   ├── webhook_handler.py   # PR event processing
│       │   └── comment_formatter.py # Markdown comment generation
│       ├── agents/
│       │   ├── base.py              # Base agent class
│       │   ├── code_analyzer.py     # Core LLM analysis
│       │   ├── rag_code_analyzer.py # RAG-enhanced analyzer
│       │   └── multi_signal_analyzer.py # Orchestrator
│       └── database/
│           └── vector_store.py      # Qdrant operations + FastEmbed
├── Dockerfile                       # HF Spaces deployment
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

## ⚙️ Setup

### Prerequisites

- Python 3.12+
- [Groq API Key](https://console.groq.com) (free)
- [Qdrant Cloud](https://cloud.qdrant.io) cluster (free tier)
- GitHub Account

### 1. Clone the Repository

```bash
git clone https://github.com/vijaykumarbalusa/Codeflow-AI.git
cd Codeflow-AI
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
# AI
GROQ_API_KEY=gsk_your_key_here

# Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key

# GitHub App
GITHUB_APP_ID=your_app_id
GITHUB_INSTALLATION_ID=your_installation_id
GITHUB_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\n...

# App
ENVIRONMENT=development
```

### 4. Run Locally

```bash
uvicorn src.codeflow.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the API docs.

---

## 🔧 GitHub App Setup

1. Go to **GitHub Settings → Developer Settings → GitHub Apps → New GitHub App**
2. Set:
   - **Webhook URL:** `https://your-deployment-url/webhook/github`
   - **Permissions:** Pull requests (Read & Write), Contents (Read)
   - **Subscribe to:** `pull_request` events
3. Generate a private key and add to `.env` as `GITHUB_PRIVATE_KEY`
4. Install the app on your repository

---

## 🐳 Self-Hosting (Docker)

```bash
docker build -t codeflow-ai .
docker run -p 7860:7860 --env-file .env codeflow-ai
```

### Deploy to Hugging Face Spaces

1. Fork this repository
2. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space) (Docker SDK)
3. Add your environment variables in **Settings → Variables and Secrets**
4. Push your code:

```bash
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/codeflow-ai
git push space main
```

---

## 🔍 How It Works

### 1. Webhook Reception
GitHub sends a `pull_request.opened` or `pull_request.synchronize` event to the `/webhook/github` endpoint. FastAPI responds immediately with `200 OK` and processes the analysis in the background.

### 2. Code Analysis Pipeline

```python
# Simplified flow
diff = await github_client.get_pr_diff(pr_number)
similar_patterns = vector_store.search_similar_code(diff)  # RAG
analysis = await groq_client.analyze(diff, context=similar_patterns)
vector_store.store_for_future_learning(diff, analysis)     # Learn
await github_client.post_comment(pr_number, analysis)
```

### 3. RAG Learning
Every analyzed PR with issues is embedded using FastEmbed and stored in Qdrant. Future PRs with similar code patterns get enhanced context, improving analysis accuracy over time.

### 4. Issue Detection
The LLM is prompted to detect and report:

| Category | Examples |
|----------|----------|
| **Injection** | SQL injection, command injection, LDAP injection |
| **Secrets** | Hardcoded passwords, API keys, tokens |
| **Path Issues** | Path traversal, directory traversal |
| **Crypto** | Weak algorithms, improper TLS |
| **Auth** | Broken auth, insecure sessions |
| **Data Exposure** | Sensitive data in logs, error messages |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service info & status |
| `GET` | `/health` | Health check |
| `POST` | `/webhook/github` | GitHub webhook receiver |
| `GET` | `/docs` | Swagger API docs |

---

## 🛡️ Security

- GitHub webhook signature verification via HMAC
- JWT-based GitHub App authentication (auto-rotated)
- All secrets via environment variables — never hardcoded
- Private key stored securely, never committed to git

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request — CodeFlow AI will review it automatically! 🤖

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ by [Vijay Kumar Balusa](https://github.com/vijaykumarbalusa)

⭐ **Star this repo if CodeFlow AI helped you catch a bug!**

</div>