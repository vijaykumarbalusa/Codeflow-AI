# Contributing to CodeFlow AI

Thank you for your interest in contributing!

## How to Contribute
- 🐛 Report bugs via GitHub Issues
- 💡 Suggest features via GitHub Issues  
- 🔧 Fix bugs by submitting a Pull Request
- 📚 Improve documentation
- 🧪 Add tests to improve coverage

## Development Setup

1. Fork and clone the repo
2. Create virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy env file: `cp .env.example .env` and fill in your API keys
5. Run locally: `uvicorn src.codeflow.main:app --reload --port 8000`

## Submitting a Pull Request

1. Create a branch from main: `git checkout -b feature/your-feature`
2. Make your changes and test locally
3. Push and open a PR — CodeFlow AI will automatically review it 🤖
4. Link related issues using `Fixes #123`

## Questions?

Open a [GitHub Discussion](https://github.com/vijaykumarbalusa/Codeflow-AI/discussions)
