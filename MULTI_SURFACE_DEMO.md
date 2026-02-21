# IaC Guardian - Multi-Surface Demo Strategy

## The Story: Catching Issues Before Deployment

Show IaC Guardian detecting problems at **3 different stages** - each progressively earlier in the pipeline.

---

## Surface 1: GitHub PR Integration (Like Terracotta)

### What It Shows
"Automated PR checks that block risky changes before merge"

### Demo Flow
1. Show a real GitHub PR with IaC Guardian checks
2. Point to failed check: "IaC Guardian: Risk Detection ❌"
3. Click into check → Shows detailed analysis
4. Point to bot comment with recommendations

### How to Build This

**Option A: Use Your Existing GitHub Action**
Your `.github/workflows/iac-review.yml` already does this!

**Option B: Create Demo PRs**
```bash
# Create demo PRs to show in presentation
cd /Users/ananth.vaidyanathan/iac-guardian

# Scenario 1 PR
git checkout -b demo/peak-traffic-risk
cp examples/scenario-1-peak-traffic/payment-api-deployment.yaml .
git add payment-api-deployment.yaml
git commit -m "Reduce replicas to save costs"
git push origin demo/peak-traffic-risk

# Create PR
gh pr create --title "Reduce payment-api replicas to 5" \
  --body "Scaling down to save $600/month. Should be sufficient for typical load."

# Watch IaC Guardian post analysis as PR comment
```

**Screenshots to Capture:**
- [ ] PR overview with IaC Guardian check (red X)
- [ ] Bot comment with risk analysis
- [ ] Detailed metrics and recommendation
- [ ] Auto-fix PR linked

---

## Surface 2: Datadog UI Dashboard

### What It Shows
"Management visibility into all infrastructure changes and risks"

### Mock Dashboard Sections

**IaC Guardian Overview**
- Total PRs analyzed this week
- Risks blocked (count + estimated $ saved)
- Cost optimizations suggested
- Top risky teams/repos

**Risk Feed**
- Live feed of analyzed PRs
- Risk levels (critical/high/medium/low)
- Time to detection
- Status (blocked/approved/pending)

**Cost Analysis**
- Monthly cost changes detected
- Optimizations applied
- Projected annual savings
- Top cost offenders

**Compliance Status**
- Policy violations caught
- Fix PRs created
- Mean time to remediation

### How to Build This

**Option A: Mock in Streamlit**
Create a separate "Management Dashboard" view in your UI

**Option B: Static Screenshots**
Create mockups showing:
1. Summary metrics at top
2. Risk feed in center
3. Cost trends chart
4. Recent activity table

**Option C: Real Datadog Dashboard** (Best but more work)
Use Datadog Dashboard API to create actual dashboard with mock data

I can help build any of these options.

---

## Surface 3: Claude Code Integration

### What It Shows
"Catch issues locally before even creating a PR"

### Developer Workflow
```bash
# Developer makes a change
vim payment-api-deployment.yaml
# Changes replicas: 20 → 5

# Commits locally
git add payment-api-deployment.yaml
git commit -m "Reduce replicas"

# IaC Guardian pre-commit hook runs
🛡️  Analyzing infrastructure changes...
📊 Querying Datadog metrics...
🤖 Running AI analysis...

❌ CRITICAL: This change will cause outages
   - Peak traffic needs 18 replicas
   - 5 replicas = 306% CPU = crash

🔧 Auto-fix available: Run 'iac-guardian fix'
❌ Commit blocked

# Developer runs fix
iac-guardian fix
✅ Generated HPA with safe scaling
✅ Updated deployment
✅ Ready to commit
```

### How to Build This

**Option A: Git Hook**
```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🛡️  IaC Guardian checking changes..."
git diff --cached | python scripts/analyze_pr.py -
EOF
chmod +x .git/hooks/pre-commit
```

**Option B: Claude Code Skill**
Create a `/iac-check` skill that runs before commits

**Option C: CLI Command**
```bash
iac-guardian check
```

I can help implement any of these.

---

## Demo Presentation Strategy

### Slide: "Shift-Left at Every Stage"

Show 3 screenshots side-by-side:

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Claude Code    │  │  GitHub PR      │  │  Datadog UI     │
│  (Local)        │  │  (Review)       │  │  (Management)   │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ Pre-commit      │  │ Automated       │  │ Executive       │
│ analysis        │  │ checks          │  │ dashboard       │
│                 │  │                 │  │                 │
│ Blocks bad      │→ │ Blocks merge    │→ │ Tracks all      │
│ commits         │  │ if risky        │  │ prevented       │
│                 │  │                 │  │ incidents       │
│ Developer       │  │ Team visibility │  │ Leadership      │
│ feedback        │  │                 │  │ metrics         │
└─────────────────┘  └─────────────────┘  └─────────────────┘
     Seconds              Minutes             Aggregated
```

### Talking Points

**"IaC Guardian works at 3 levels:"**

1. **Local (Claude Code)**
   - "Developer commits a change"
   - "IaC Guardian catches it immediately - before PR"
   - "Offers auto-fix right in terminal"
   - Impact: Saves developer time, prevents bad PRs

2. **PR Review (GitHub)**
   - "If it gets to PR, automated check runs"
   - "Just like Terracotta - blocks merge if risky"
   - "Posts detailed analysis as comment"
   - Impact: Prevents merge to main, team visibility

3. **Management (Datadog UI)**
   - "FinOps and engineering managers see all changes"
   - "Dashboard shows risks blocked, costs saved"
   - "Executive metrics: $2M in outages prevented"
   - Impact: ROI visibility, compliance tracking

**"This is shift-left security, but for infrastructure reliability and cost."**

---

## Quick Build Plan for Hackathon

### Priority 1: GitHub PR (Easiest - Already Have)
- [ ] Create 2 demo PRs in your repo
- [ ] Let GitHub Action run
- [ ] Capture screenshots of:
  - PR with failed check
  - Bot comment
  - Detailed analysis

**Time: 15 minutes**

### Priority 2: Datadog Dashboard (Medium)
- [ ] Create management dashboard mockup
- [ ] Add to Streamlit as new page
- [ ] Show aggregated metrics

**Time: 1 hour**

### Priority 3: Claude Code Integration (Harder)
- [ ] Create git pre-commit hook
- [ ] Or demo with CLI command
- [ ] Record terminal demo

**Time: 30 minutes**

---

## Implementation Help

Want me to:

1. **Create the GitHub demo PRs** - Use your existing Action
2. **Build a Datadog-style dashboard view** in Streamlit
3. **Create a pre-commit hook** for local checks
4. **Make a composite screenshot** showing all 3 surfaces

Which should I start with?

---

## Inspiration from Terracotta

Your screenshots show:
- ✅ Cost Report (monetary impact)
- ✅ Guardrail Report (policy violations)
- ✅ Summary comment (bot posts analysis)
- ✅ Check status (blocks on failure)

You can match/exceed this with:
- **Better AI analysis** (Claude vs rules)
- **Real metrics** (Datadog vs estimates)
- **Auto-fixes** (generates safe alternatives)
- **Multi-surface** (local + PR + dashboard)

---

## Key Demo Moment

Show all 3 surfaces detecting THE SAME issue:

**Scenario: Engineer tries to reduce replicas 20→5**

1. **Claude Code**: Catches during commit
   ```
   ❌ Cannot commit: Peak traffic requires 18+ replicas
   ```

2. **GitHub PR**: If bypassed, catches during PR
   ```
   ❌ Check failed: IaC Guardian Risk Detection
   Bot comment: "This will cause outages..."
   ```

3. **Datadog Dashboard**: Aggregates across all PRs
   ```
   This week: 3 critical risks blocked
   Estimated impact: $2M in prevented outages
   ```

**Message:** "We catch problems at every stage - no way a risky change gets through."
