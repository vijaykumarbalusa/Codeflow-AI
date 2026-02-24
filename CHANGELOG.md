# Changelog

All notable changes to CodeFlow AI are documented here.

---

## [v1.0.0] — 2026-02-24

### First Production Release

#### Added
- AI-powered PR security analysis using Llama 3.3 70B via Groq
- RAG learning system with Qdrant vector database
- FastEmbed (ONNX) for memory-efficient embeddings (~80MB)
- GitHub App integration with JWT authentication
- Detects: SQL injection, hardcoded secrets, path traversal, command injection, weak crypto, broken auth
- Confidence scores (0-100%) per issue
- Risk level: None / Low / Medium / High / Critical
- Background task processing — responds to GitHub in <1s
- Deployed on Hugging Face Spaces (Docker, free tier)
- Keep-alive cron job via cron-job.org

#### Tech Stack
- Python 3.12, FastAPI, Uvicorn
- Groq API (llama-3.3-70b-versatile)
- Qdrant Cloud, FastEmbed BAAI/bge-small-en-v1.5
- Docker on Hugging Face Spaces

---

## [Unreleased]

### Planned
- Support for more languages (Go, Rust, Java)
- Update existing PR comment instead of posting new one
- Webhook signature verification
- GitLab and Bitbucket support
