#!/bin/bash
echo "=== Step 1: fastapi ==="
python -c "import fastapi; print('OK')"
echo "=== Step 2: config ==="
python -c "from src.codeflow.core.config import get_settings; print('OK')"
echo "=== Step 3: multi_signal_analyzer ==="
python -c "from src.codeflow.agents.multi_signal_analyzer import MultiSignalAnalyzer; print('OK')"
echo "=== Step 4: webhook_handler ==="
python -c "from src.codeflow.core.webhook_handler import WebhookHandler; print('OK')"
echo "=== Step 5: full app ==="
python -c "from src.codeflow.main import app; print('OK')"
echo "=== Starting uvicorn ==="
exec uvicorn src.codeflow.main:app --host 0.0.0.0 --port $PORT
