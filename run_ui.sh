#!/bin/bash
# Launch IaC Guardian Streamlit UI

cd "$(dirname "$0")"

echo "🛡️  Starting IaC Guardian UI..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Load .env file if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "✓ Loaded environment from .env"
fi

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set"
    echo "   You can set it in the UI or export it:"
    echo "   export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
fi

# Launch Streamlit
echo "🚀 Launching UI at http://localhost:8501"
echo ""
streamlit run app.py
