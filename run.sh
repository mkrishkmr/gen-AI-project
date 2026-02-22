#!/bin/bash
# Manual Testing Launcher (Unix)
# 1. Installs missing dependencies
# 2. Runs all tests
# 3. If tests pass, launches the UI

set -e
echo ">>> Installing dependencies"
pip install -q groq pandas datasets python-dotenv pytest streamlit fastapi uvicorn

echo ""
echo ">>> Running tests"
python -m pytest tests/ -v

echo ""
echo ">>> All tests passed. Launching UI..."
streamlit run src/ui/app.py
