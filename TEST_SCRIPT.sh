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

PASS=0
FAIL=0

run_scenario() {
    local num="$1"
    local name="$2"
    local diff_file="$3"

    echo ""
    echo "🧪 Testing Scenario ${num}: ${name}..."
    echo "---"
    if python3 scripts/analyze_pr.py "$diff_file"; then
        echo ""
        echo "✅ Scenario ${num} complete"
        PASS=$((PASS + 1))
    else
        echo ""
        echo "❌ Scenario ${num} FAILED"
        FAIL=$((FAIL + 1))
    fi
}

run_scenario 1 "Peak Traffic Risk"          examples/scenario-1-peak-traffic/demo_diff.txt
run_scenario 2 "Cost Optimization"          examples/scenario-2-cost-optimization/demo_diff.txt
run_scenario 3 "Missing Health Checks"      examples/scenario-3-health-checks/demo_diff.txt
run_scenario 4 "Missing PodDisruptionBudget" examples/scenario-4-pdb/demo_diff.txt
run_scenario 5 "Insufficient Replicas"      examples/scenario-5-replicas/demo_diff.txt
run_scenario 6 "Security Group Too Open"    examples/scenario-6-security/demo_diff.txt

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results: ${PASS}/6 passed, ${FAIL} failed"
if [ "$FAIL" -eq 0 ]; then
    echo "🎉 All tests passed! Ready for demo."
else
    echo "⚠️  Some scenarios failed. Check output above."
    exit 1
fi
