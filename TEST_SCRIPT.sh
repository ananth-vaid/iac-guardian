#!/bin/bash
# Quick test script to verify IaC Guardian works locally

set -e

echo "🧪 Testing IaC Guardian locally..."
echo ""

# Load .env file if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "✓ Loaded .env file"
fi

# Check if in venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Not in virtual environment. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
fi

# Check Python dependencies
echo "✓ Checking dependencies..."
python3 -c "import anthropic, yaml, hcl2" 2>/dev/null || {
    echo "❌ Missing dependencies. Run: pip install -r requirements.txt"
    exit 1
}

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not set"
    echo "   Run: export ANTHROPIC_API_KEY='your-key'"
    exit 1
fi
echo "✓ API key configured"

# Test Scenario 1
echo ""
echo "🧪 Testing Scenario 1: Peak Traffic Risk..."
echo "---"
python3 scripts/analyze_pr.py examples/scenario-1-peak-traffic/demo_diff.txt
echo ""
echo "✅ Scenario 1 complete"

# Test Scenario 2
echo ""
echo "🧪 Testing Scenario 2: Cost Optimization..."
echo "---"
python3 scripts/analyze_pr.py examples/scenario-2-cost-optimization/demo_diff.txt
echo ""
echo "✅ Scenario 2 complete"

echo ""
echo "🎉 All tests passed! Ready for demo."
