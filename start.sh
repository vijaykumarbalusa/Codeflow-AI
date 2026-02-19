#!/bin/bash
echo "=== Testing Python import ==="
python -c "
import traceback
try:
    from src.codeflow.main import app
    print('Import OK')
except Exception as e:
    print('IMPORT FAILED:')
    traceback.print_exc()
" 2>&1

echo "=== Starting uvicorn ==="
exec uvicorn src.codeflow.main:app --host 0.0.0.0 --port $PORT
