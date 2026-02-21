#!/bin/bash
# Create a PR for a specific IaC Guardian scenario
# Usage: ./scripts/create_scenario_pr.sh <scenario_number>

set -e

SCENARIO=$1

if [ -z "$SCENARIO" ]; then
    echo "Usage: $0 <scenario_number>"
    echo ""
    echo "Available scenarios:"
    echo "  3 - Missing Health Checks"
    echo "  4 - Missing PodDisruptionBudget"
    echo "  5 - Insufficient Replicas"
    echo "  6 - Security Group Too Open"
    exit 1
fi

# Load environment
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Define scenario details
case $SCENARIO in
    3)
        BRANCH="demo/missing-health-checks"
        TITLE="Deploy API without health checks"
        FILE="k8s/api-deployment.yaml"
        DIFF_CONTENT='apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: myapp/api:v2.1.0
        ports:
        - containerPort: 8080
        # NOTE: No liveness or readiness probes configured!'
        ;;
    4)
        BRANCH="demo/missing-pdb"
        TITLE="Update deployment without PodDisruptionBudget"
        FILE="k8s/web-deployment.yaml"
        DIFF_CONTENT='apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-frontend
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: web
        image: myapp/web:latest
# NOTE: No PodDisruptionBudget defined!'
        ;;
    5)
        BRANCH="demo/insufficient-replicas"
        TITLE="Reduce replicas below HA threshold"
        FILE="k8s/critical-service.yaml"
        DIFF_CONTENT='apiVersion: apps/v1
kind: Deployment
metadata:
  name: critical-service
spec:
  replicas: 1  # Changed from 3 to 1 - NOT HA!'
        ;;
    6)
        BRANCH="demo/open-security-group"
        TITLE="Update security group with overly permissive rules"
        FILE="terraform/security-groups.tf"
        DIFF_CONTENT='resource "aws_security_group" "web_server" {
  name        = "web-server-sg"
  description = "Security group for web servers"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # OPEN TO THE WORLD!
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}'
        ;;
    *)
        echo "❌ Invalid scenario number. Choose 3-6."
        exit 1
        ;;
esac

echo "🚀 Creating PR for Scenario $SCENARIO"
echo "Branch: $BRANCH"
echo "Title: $TITLE"
echo ""

# Store current branch
ORIGINAL_BRANCH=$(git branch --show-current)

# Check if branch already exists
if git show-ref --quiet refs/heads/$BRANCH; then
    echo "⚠️  Branch $BRANCH already exists."
    read -p "Delete and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        git branch -D $BRANCH
    else
        echo "❌ Aborted."
        exit 1
    fi
fi

# Create and switch to new branch
git checkout -b $BRANCH

# Create directory if needed
mkdir -p $(dirname $FILE)

# Create the file
echo "$DIFF_CONTENT" > $FILE

# Commit
git add $FILE
git commit -m "$TITLE

This change introduces infrastructure risk that IaC Guardian should detect.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to remote
echo ""
echo "📤 Pushing to remote..."
git push -u origin $BRANCH

# Create PR using gh CLI
echo ""
echo "🔧 Creating pull request..."
gh pr create \
    --title "$TITLE" \
    --body "$(cat <<EOF
## What Changed
This PR introduces Scenario $SCENARIO from the IaC Guardian demo.

## Expected IaC Guardian Analysis
The GitHub Action should automatically comment on this PR with:
- Risk assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Explanation of why this change is risky
- Recommended remediation actions

## Testing
This is a demo PR to test IaC Guardian's automated review capabilities.

---
🤖 Generated for IaC Guardian demo
EOF
)" \
    --base main

# Return to original branch
git checkout $ORIGINAL_BRANCH

echo ""
echo "✅ PR created successfully!"
echo ""
echo "Next steps:"
echo "1. Check GitHub Actions tab for workflow run"
echo "2. Review the IaC Guardian comment (appears in ~30 seconds)"
echo "3. Optional: Close PR when done testing"
echo ""
echo "To recreate this PR:"
echo "  ./scripts/create_scenario_pr.sh $SCENARIO"
