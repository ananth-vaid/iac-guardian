#!/bin/bash
# demo_e2e.sh — Create demo PRs for scenarios 3-6 and trigger GitHub Actions
# Usage: ./scripts/demo_e2e.sh [--dry-run] [--all]
#
# Scenarios 1 & 2 already have live PRs. This script creates PRs for 3-6.
# Each PR commits a real .yaml/.tf file so the workflow triggers and analyzes it.
#
# Prerequisites: gh CLI authenticated, run from repo root on main branch

set -e

DRY_RUN=false
SCENARIOS="3 4 5 6"

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --all)     SCENARIOS="1 2 3 4 5 6" ;;
    esac
done

if [ -f .env ]; then
    set -a; source .env; set +a
fi

BASE_BRANCH="main"
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "unknown/repo")

echo "🛡️  IaC Guardian — E2E Demo PR Creator"
echo "   Repo: $REPO"
echo "   Creating PRs for scenarios: $SCENARIOS"
echo ""

PR_URLS=()

create_scenario_pr() {
    local NUM="$1"
    local BRANCH="demo/scenario-${NUM}-$(scenario_name $NUM)"
    local TITLE="$(scenario_title $NUM)"
    local BODY="$(scenario_body $NUM)"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Scenario ${NUM}: $(scenario_name $NUM)"
    echo "   Branch: $BRANCH"

    if $DRY_RUN; then
        echo "   [DRY RUN] Would create: $TITLE"
        return
    fi

    git checkout "$BASE_BRANCH" 2>/dev/null
    git branch -D "$BRANCH" 2>/dev/null || true
    git checkout -b "$BRANCH"

    # Write the real infrastructure file for this scenario
    write_scenario_file "$NUM"

    git add -A
    # --no-verify: these are intentionally risky demo files; GitHub Actions will still catch them
    git commit --no-verify -m "$TITLE"
    git push origin "$BRANCH" --force

    EXISTING=$(gh pr list --head "$BRANCH" --json number -q '.[0].number' 2>/dev/null || echo "")
    if [ -n "$EXISTING" ]; then
        PR_URL=$(gh pr view "$EXISTING" --json url -q .url)
        echo "   ♻️  PR already exists: $PR_URL"
    else
        PR_URL=$(gh pr create \
            --title "$TITLE" \
            --body "$BODY" \
            --base "$BASE_BRANCH" \
            --head "$BRANCH" \
            2>&1 | tail -1)
        echo "   ✅ PR created: $PR_URL"
    fi

    PR_URLS+=("Scenario ${NUM} [$(scenario_name $NUM)]: $PR_URL")
    git checkout "$BASE_BRANCH"
}

scenario_name() {
    case "$1" in
        1) echo "peak-traffic" ;;
        2) echo "cost-optimization" ;;
        3) echo "health-checks" ;;
        4) echo "pdb" ;;
        5) echo "replicas" ;;
        6) echo "security" ;;
    esac
}

scenario_title() {
    case "$1" in
        1) echo "chore: reduce payment-api replicas for cost savings" ;;
        2) echo "infra: scale data-processing cluster for new workload" ;;
        3) echo "deploy: add api-server to production namespace" ;;
        4) echo "deploy: frontend HA configuration update" ;;
        5) echo "deploy: optimize checkout service replicas" ;;
        6) echo "security: add SSH access rule for ops team" ;;
    esac
}

scenario_body() {
    case "$1" in
        1) echo "Reducing replicas from 20 to 5 to save cost during low-traffic period." ;;
        2) echo "Scaling from 5x c5.2xlarge to 10x c5.4xlarge for new ML workload." ;;
        3) echo "Moving api-server to production namespace. Health probes to be added in follow-up." ;;
        4) echo "Updating frontend deployment. PodDisruptionBudget configuration TBD." ;;
        5) echo "Reducing checkout replicas from 3 to 2 to free up cluster capacity." ;;
        6) echo "Opening SSH port for ops team debugging session. Will restrict CIDR after investigation." ;;
    esac
}

write_scenario_file() {
    case "$1" in
        1)
            mkdir -p k8s
            cat > k8s/payment-api-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-api
  namespace: production
  labels:
    app: payment-api
    team: payments
spec:
  replicas: 5
  selector:
    matchLabels:
      app: payment-api
  template:
    metadata:
      labels:
        app: payment-api
    spec:
      containers:
      - name: payment-api
        image: payment-api:v3.2.1
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
EOF
            ;;
        2)
            mkdir -p terraform
            cat > terraform/compute.tf << 'EOF'
provider "aws" {
  region = "us-east-1"
}

# Data processing cluster - scaling up for new workload
resource "aws_instance" "data_processor" {
  count         = 10
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "c5.4xlarge"

  tags = {
    Name        = "data-processor-${count.index}"
    Environment = "production"
    Team        = "data-platform"
  }
}
EOF
            ;;
        3)
            mkdir -p k8s
            cat > k8s/api-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  namespace: production
spec:
  replicas: 10
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: api
        image: api-server:v2.0
        ports:
        - containerPort: 8080
        # NOTE: No liveness or readiness probes configured
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
EOF
            ;;
        4)
            mkdir -p k8s
            cat > k8s/frontend-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: production
  # NOTE: No PodDisruptionBudget defined for this service
spec:
  replicas: 5
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: frontend:v1.8.3
        ports:
        - containerPort: 3000
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
EOF
            ;;
        5)
            mkdir -p k8s
            cat > k8s/checkout-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
  namespace: production
  labels:
    app: checkout
    team: payments
spec:
  replicas: 2
  selector:
    matchLabels:
      app: checkout
  template:
    metadata:
      labels:
        app: checkout
    spec:
      containers:
      - name: checkout
        image: checkout:v4.1.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
EOF
            ;;
        6)
            mkdir -p terraform
            cat > terraform/security-groups.tf << 'EOF'
resource "aws_security_group" "app_servers" {
  name        = "app-servers"
  description = "Security group for application servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH access for ops team"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # WARNING: Open to internet!
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
EOF
            ;;
    esac
}

# Run selected scenarios
for NUM in $SCENARIOS; do
    create_scenario_pr "$NUM"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Done!"
echo ""
echo "📎 PR URLs (GitHub Actions will post IaC Guardian comments within ~60s):"
for url in "${PR_URLS[@]}"; do
    echo "   $url"
done
echo ""
echo "💡 Open the Actions tab to watch each scenario get analyzed live."
