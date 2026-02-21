#!/bin/bash
# Create demo PRs to show IaC Guardian in action on GitHub

cd "$(dirname "$0")"

echo "🚀 Creating demo PRs for IaC Guardian..."
echo ""

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Check if we have gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Install with: brew install gh"
    exit 1
fi

# Scenario 1: Peak Traffic Risk
echo "📝 Creating Scenario 1: Peak Traffic Risk PR..."
git checkout -b demo/scenario-1-peak-traffic 2>/dev/null || git checkout demo/scenario-1-peak-traffic
cp examples/scenario-1-peak-traffic/payment-api-deployment.yaml ./payment-api-deployment.yaml
git add payment-api-deployment.yaml
git commit -m "Reduce payment-api replicas to 5 for cost savings

- Scale down from 20 → 5 replicas
- Estimated savings: ~$600/month
- Should handle typical load" --allow-empty

git push -u origin demo/scenario-1-peak-traffic -f

gh pr create \
  --title "🔻 Reduce payment-api replicas to 5" \
  --body "## Changes
- Scale down \`payment-api\` from 20 → 5 replicas
- Estimated savings: ~$600/month in compute costs

## Rationale
Current utilization shows we're over-provisioned. Reducing to 5 replicas should be sufficient for typical load.

## Testing
- [ ] Verified in staging environment
- [ ] Load testing pending

---

**Expected:** IaC Guardian should flag this as HIGH RISK due to peak traffic capacity." \
  --base main \
  --head demo/scenario-1-peak-traffic || echo "PR may already exist"

echo "✅ Scenario 1 PR created"
echo ""

# Scenario 2: Cost Optimization
echo "📝 Creating Scenario 2: Cost Optimization PR..."
git checkout -b demo/scenario-2-cost-optimization 2>/dev/null || git checkout demo/scenario-2-cost-optimization
cp examples/scenario-2-cost-optimization/compute.tf ./compute.tf
git add compute.tf
git commit -m "Scale up data processing cluster

- Increase instances: 5 → 10
- Upgrade type: c5.2xlarge → c5.4xlarge
- Preparing for Q1 data pipeline expansion" --allow-empty

git push -u origin demo/scenario-2-cost-optimization -f

gh pr create \
  --title "📈 Scale up data processing cluster" \
  --body "## Changes
- Increase \`data_processor\` instances: 5 → 10
- Upgrade instance type: \`c5.2xlarge\` → \`c5.4xlarge\`

## Rationale
Preparing for Q1 data pipeline expansion. Need more processing capacity for new analytics workloads.

## Cost Impact
- Current: 5x c5.2xlarge = ~$1,680/month
- New: 10x c5.4xlarge = ~$6,720/month
- Increase: +$5,040/month

---

**Expected:** IaC Guardian should suggest cost optimization (currently at 15% CPU utilization)." \
  --base main \
  --head demo/scenario-2-cost-optimization || echo "PR may already exist"

echo "✅ Scenario 2 PR created"
echo ""
git checkout main

echo "🎉 Demo PRs created!"
echo ""
echo "Next steps:"
echo "1. Check PRs at: gh pr list"
echo "2. GitHub Actions will run IaC Guardian automatically"
echo "3. Take screenshots of:"
echo "   - PR checks (should show failures)"
echo "   - Bot comments"
echo "   - Detailed analysis"
echo ""
echo "View PRs:"
gh pr list
