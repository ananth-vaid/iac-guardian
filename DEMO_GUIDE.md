# IaC Guardian - Demo Guide

## Quick Start

### 1. Test Locally (Without GitHub)

```bash
cd /Users/ananth.vaidyanathan/iac-guardian

# Install dependencies (use venv to avoid system package issues)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Test Scenario 1 (Peak Traffic Risk)
python scripts/analyze_pr.py examples/scenario-1-peak-traffic/demo_diff.txt

# Test Scenario 2 (Cost Optimization)
python scripts/analyze_pr.py examples/scenario-2-cost-optimization/demo_diff.txt
```

### 2. Set Up GitHub Demo

1. **Create GitHub repo:**
   ```bash
   gh repo create iac-guardian --public --source=. --remote=origin
   git push -u origin main
   ```

2. **Add secrets** (Settings → Secrets → Actions):
   - `ANTHROPIC_API_KEY` - Your Claude API key
   - `DATADOG_API_KEY` - Datadog API key (optional for demo)
   - `DATADOG_APP_KEY` - Datadog App key (optional for demo)

3. **Push demo branches:**
   ```bash
   git push origin demo/scenario-1-peak-traffic
   git push origin demo/scenario-2-cost-optimization
   ```

4. **Create PRs:**
   ```bash
   gh pr create --base main --head demo/scenario-1-peak-traffic \
     --title "Reduce payment-api replicas for cost savings" \
     --body-file examples/scenario-1-peak-traffic/PR_DESCRIPTION.md

   gh pr create --base main --head demo/scenario-2-cost-optimization \
     --title "Scale up data processing cluster" \
     --body-file examples/scenario-2-cost-optimization/PR_DESCRIPTION.md
   ```

5. **Watch the magic!** GitHub Action will run and post analysis comments

---

## Demo Presentation (5 minutes)

### Slide 1: The Problem (30 sec)
*"Infrastructure changes that look safe can cause production outages and waste millions. We need AI to catch these before they hit prod."*

**Examples:**
- Scaling down to save $500/month → causes $2M outage
- Adding 10 servers "just in case" → wastes $40k/month

### Slide 2: The Solution (30 sec)
*"IaC Guardian: AI-powered PR review that uses real Datadog metrics to predict issues."*

**How it works:**
1. GitHub Action triggers on IaC PR
2. Queries Datadog for real production metrics
3. Claude analyzes: "Will this crash? Is it over-provisioned?"
4. Posts actionable comment on PR

### Slide 3: Demo - Scenario 1 (2 min)
*Show GitHub PR for replica reduction*

**The PR:** Engineer wants to scale down from 20 → 5 replicas to save money

**IaC Guardian catches it:**
```
🚨 HIGH RISK - Will crash during peak traffic

Last Tuesday at 2pm:
- Traffic: 82k requests/min
- Needed: 18 replicas at 85% CPU
- With 5 replicas: 306% CPU = CRASH

Recent incident: INC-4521 (same issue, 23min outage)

❌ BLOCK this PR
```

**Impact:** Prevented production outage worth $2M in lost transactions

### Slide 4: Demo - Scenario 2 (1.5 min)
*Show GitHub PR for adding compute*

**The PR:** Adding 10x c5.4xlarge instances ($6,720/month)

**IaC Guardian optimizes it:**
```
💰 COST OPTIMIZATION - You're over-provisioning by 3x

Current similar instances:
- CPU: 15% average
- Memory: 22%
- Barely utilized

Recommendation:
- Use 4x c5.2xlarge instead
- Same performance
- Save $3,600/month = $43k/year

✅ Approve with changes
```

**Impact:** Saved $43k/year by right-sizing

### Slide 5: Value & Next Steps (30 sec)

**Value:**
- Prevents production outages (save millions)
- Optimizes cloud costs (save hundreds of thousands)
- Uses real Datadog data (not just static analysis)
- Powered by Claude AI (learns from incidents)

**Next Steps:**
- Integrate with Datadog Security (policy compliance)
- Add more scenarios (database changes, network configs)
- Deploy to Datadog engineering teams

---

## Tips for Demo

1. **Keep it visual** - Show actual GitHub PRs with bot comments
2. **Use real numbers** - "$2M outage" resonates more than "high risk"
3. **Show Datadog data** - Mention "This uses real metrics from your production"
4. **Make it personal** - "How many of you have seen this happen?"

## Common Questions

**Q: Does this work with Helm?**
A: Not yet - currently raw K8s YAML and Terraform. Easy to add.

**Q: How accurate is the cost estimation?**
A: Uses AWS pricing + your actual Datadog utilization metrics. Within 10%.

**Q: Can it auto-fix issues?**
A: Not yet - for demo, it just warns. Could add auto-fix PRs later.

**Q: Does it support other clouds (Azure, GCP)?**
A: Architecture supports it - just need to add provider-specific parsers.
