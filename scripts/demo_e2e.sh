#!/bin/bash
# demo_e2e.sh — Create demo PRs for all 6 scenarios and trigger GitHub Actions
# Usage: ./scripts/demo_e2e.sh [--dry-run]
#
# Prerequisites: gh CLI authenticated, git repo with remote origin set

set -e

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN mode — will not push or create PRs"
fi

# Load .env if present
if [ -f .env ]; then
    set -a; source .env; set +a
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "unknown/repo")
BASE_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "main")

echo "🛡️  IaC Guardian — E2E Demo Flow"
echo "   Repo: $REPO"
echo "   Base: $BASE_BRANCH"
echo ""

declare -a SCENARIO_NAMES=(
    "peak-traffic"
    "cost-optimization"
    "health-checks"
    "pdb"
    "replicas"
    "security"
)
declare -a SCENARIO_TITLES=(
    "chore: reduce payment-api replicas for cost savings"
    "infra: scale data-processing cluster for new workload"
    "deploy: add api-server to production namespace"
    "deploy: frontend scaling update"
    "deploy: optimize checkout service replicas"
    "security: add SSH access rule for ops team"
)
declare -a SCENARIO_BODIES=(
    "Reducing replicas from 20 to 5 to save cost during low-traffic period."
    "Scaling from 5x c5.2xlarge to 10x c5.4xlarge for new ML workload."
    "Moving api-server to production namespace. Container health probes TBD."
    "Updating frontend deployment configuration."
    "Reducing checkout replicas from 3 to 2 to free up cluster capacity."
    "Opening SSH access for ops team debugging. Will lock down after investigation."
)
declare -a SCENARIO_DIFFS=(
    "examples/scenario-1-peak-traffic/demo_diff.txt"
    "examples/scenario-2-cost-optimization/demo_diff.txt"
    "examples/scenario-3-health-checks/demo_diff.txt"
    "examples/scenario-4-pdb/demo_diff.txt"
    "examples/scenario-5-replicas/demo_diff.txt"
    "examples/scenario-6-security/demo_diff.txt"
)

PR_URLS=()

for i in "${!SCENARIO_NAMES[@]}"; do
    NUM=$((i + 1))
    NAME="${SCENARIO_NAMES[$i]}"
    TITLE="${SCENARIO_TITLES[$i]}"
    BODY="${SCENARIO_BODIES[$i]}"
    DIFF_FILE="${SCENARIO_DIFFS[$i]}"
    BRANCH="demo/scenario-${NUM}-${NAME}"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Scenario ${NUM}: ${NAME}"
    echo "   Branch: $BRANCH"

    if $DRY_RUN; then
        echo "   [DRY RUN] Would push branch and create PR: $TITLE"
        continue
    fi

    # Clean up any existing branch
    git branch -D "$BRANCH" 2>/dev/null || true
    git checkout -b "$BRANCH"

    # Copy diff file as an actual file change to trigger the workflow
    DIFF_DEST="iac-changes/scenario-${NUM}-${NAME}.diff"
    mkdir -p iac-changes
    cp "$DIFF_FILE" "$DIFF_DEST"

    git add "$DIFF_DEST"
    git commit -m "$TITLE"

    # Push branch
    git push origin "$BRANCH" --force

    # Create PR using gh CLI
    PR_URL=$(gh pr create \
        --title "$TITLE" \
        --body "$BODY" \
        --base "$BASE_BRANCH" \
        --head "$BRANCH" \
        2>&1 | tail -1)

    PR_URLS+=("Scenario ${NUM}: $PR_URL")
    echo "   ✅ PR created: $PR_URL"

    # Return to base branch
    git checkout "$BASE_BRANCH"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 All demo PRs created!"
echo ""
echo "📎 PR URLs (watch GitHub Actions tab for IaC Guardian comments):"
for url in "${PR_URLS[@]}"; do
    echo "   $url"
done
echo ""
echo "💡 Each PR will receive an IaC Guardian analysis comment within ~60 seconds."
