#!/bin/bash
# Create all demo PRs for IaC Guardian scenarios 3-6
# Usage: ./scripts/create_all_demo_prs.sh

set -e

echo "🚀 Creating all IaC Guardian demo PRs"
echo "======================================"
echo ""

for scenario in 3 4 5 6; do
    echo "Creating PR for Scenario $scenario..."
    ./scripts/create_scenario_pr.sh $scenario
    echo ""
    echo "Waiting 5 seconds before next PR..."
    sleep 5
done

echo ""
echo "✅ All 4 demo PRs created!"
echo ""
echo "View your PRs:"
echo "  gh pr list"
echo ""
echo "Or visit:"
echo "  https://github.com/ananth-vaid/iac-guardian/pulls"
