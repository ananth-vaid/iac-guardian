# IaC Guardian - 3-Surface Demo Guide

## The Story: Shift-Left at Every Stage

**Core Message:** "IaC Guardian catches infrastructure risks at 3 different stages - each progressively earlier in the pipeline."

---

## Setup (Before Demo)

### 1. Local Pre-Commit (10 seconds)
```bash
cd /Users/ananth.vaidyanathan/iac-guardian
./install_hooks.sh
export ANTHROPIC_API_KEY="your-key"
```

### 2. GitHub PRs (2 minutes)
```bash
# Only if PRs don't exist yet
./create_demo_prs.sh
```

### 3. Management Dashboard (5 seconds)
```bash
streamlit run dashboard.py --server.port 8502 &
```

### 4. Main UI (5 seconds)
```bash
./run_ui.sh &
```

Now you have:
- http://localhost:8501 - Main UI (for audience)
- http://localhost:8502 - Dashboard (for management view)
- Terminal ready for local demo
- GitHub PRs ready

---

## Demo Flow (5 minutes)

### Opening: The Problem (30 seconds)

**Script:**
"Infrastructure changes slip through code review all the time. A change that looks fine to engineers can cause a $2M outage or waste $300k a year. Why? Because engineers don't see production metrics during code review."

**Slide:** Show stats
- 67% of outages from infrastructure changes
- Average incident cost: $2M
- Average cloud waste: 35%

---

### Surface 1: Local Development (1 minute)

**Script:**
"Let me show you a real example. An engineer is about to commit a change to reduce replicas from 20 to 5 to save money."

**Demo:**
```bash
# Terminal visible to audience

# Show the file
cat examples/scenario-1-peak-traffic/payment-api-deployment.yaml

# Stage the change
git add payment-api-deployment.yaml

# Try to commit - IaC Guardian blocks it!
git commit -m "Reduce replicas to save costs"
```

**What Happens:**
```
🛡️  IaC Guardian - Pre-Commit Analysis
==================================================================
📄 Infrastructure files changed: 1
   - payment-api-deployment.yaml

🔍 Analyzing changes...
📊 Querying Datadog metrics...
🤖 Running AI analysis...

==================================================================
🛡️  IaC GUARDIAN ANALYSIS
==================================================================

Risk Level: CRITICAL

🚨 HIGH RISK - Will crash during peak traffic

Analysis:
- Current: 20 replicas at 65% CPU
- Peak (last Tuesday): 82k req/min needed 18 replicas at 85% CPU
- Proposed: 5 replicas = 306% CPU = CRASH
- Recent incident: INC-4521 (same issue, 23min outage)

Recommendation: Use HPA with min 15 replicas

==================================================================

❌ COMMIT BLOCKED: Critical issues detected

💡 Options:
   1. Fix the issues manually
   2. Run 'python iac-guardian-cli.py fix' for auto-fix
   3. Override with: git commit --no-verify
```

**Key Points:**
- ✅ Caught BEFORE commit
- ✅ Uses real production metrics
- ✅ Suggests fix (HPA)
- ✅ Developer gets instant feedback

**Impact:** "Saved developer from even creating a bad PR. Prevented wasted time in code review."

---

### Surface 2: GitHub PR Review (1.5 minutes)

**Script:**
"But what if someone bypasses the local check? Maybe they used --no-verify, or didn't have the hook installed. That's where GitHub integration comes in."

**Demo:**
1. Open GitHub PR (have it open in browser tab)
2. Show PR title: "Reduce payment-api replicas to 5"
3. Point to **failed checks** (red X):
   ```
   ❌ IaC Guardian: Risk Detection
   ❌ Terracotta: Cost Check
   ❌ Terracotta: Guardrail Violation Check
   ```

4. Click into IaC Guardian check
5. Show bot comment with full analysis

**What They See:**
- Summary report (like your Terracotta screenshots)
- Cost impact: "Would save $600/mo but cause $2M outage"
- Datadog metrics embedded
- Recommendation: "Use HPA instead"
- Link to auto-fix PR

**Key Points:**
- ✅ Blocks merge automatically
- ✅ Visible to whole team
- ✅ Links to fix PR
- ✅ Integrates with existing workflow

**Impact:** "Even if local check is bypassed, we catch it at PR review. No risky change can merge."

---

### Surface 3: Management Dashboard (1.5 minutes)

**Script:**
"Now imagine you're an engineering manager or on the FinOps team. You need visibility across ALL infrastructure changes, not just one PR. That's where the management dashboard comes in."

**Demo:**
1. Switch to http://localhost:8502
2. Show **Key Metrics** at top:
   - 47 PRs analyzed this week
   - 8 risks blocked
   - $428k cost impact detected
   - 3 outages prevented

3. Point to **Daily Activity** chart:
   - "We're analyzing 5-9 PRs per day"
   - "Finding 1-2 risks per day on average"

4. Point to **Cost Impact Timeline**:
   - "This week we detected $428k in potential waste"
   - "Actually saved $285k through fixes"

5. Point to **Risk Feed**:
   - Show the same payment-api PR from earlier
   - Status: "Blocked" with "CRITICAL" badge
   - Impact: "$2M outage prevented"

6. Point to **Top Repositories**:
   - "payments-infra has the most risks"
   - "Suggests where to focus engineering training"

7. Show **ROI Calculation**:
   - 3 outages prevented = $6M value
   - $428k cost waste avoided
   - 48 engineering hours saved

**Key Points:**
- ✅ Executive visibility
- ✅ Tracks ROI
- ✅ Identifies problem areas
- ✅ Shows business impact

**Impact:** "Leadership can track the value: millions in prevented outages, hundreds of thousands in cost savings."

---

### The Full Picture (30 seconds)

**Script:**
"So to summarize - IaC Guardian works at 3 levels:"

**Show diagram:**
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  1. LOCAL       │→ │  2. GITHUB PR   │→ │  3. DASHBOARD   │
│  (Developer)    │  │  (Team)         │  │  (Management)   │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ Pre-commit hook │  │ Automated check │  │ Executive view  │
│ Instant feedback│  │ Blocks merge    │  │ ROI tracking    │
│ 8 seconds       │  │ Team visible    │  │ Aggregated      │
│                 │  │                 │  │                 │
│ ✅ Prevents     │  │ ✅ Catches      │  │ ✅ Measures     │
│    bad commits  │  │    bad merges   │  │    total impact │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Key Message:**
"We catch problems at EVERY stage. No way a risky change makes it to production."

---

## Q&A Prep

### "How is this different from Terracotta?"

**Good answer:**
"Great question! We saw Terracotta's approach and built on it:
1. **AI-powered analysis** - We use Claude, not just rules
2. **Real metrics** - We query Datadog for production data
3. **Multi-surface** - We catch issues locally too, not just in PRs
4. **Auto-remediation** - We generate safe alternatives automatically

Think of it as: Terracotta + AI + Real metrics + Local checks"

### "Does this slow down deployments?"

**Good answer:**
"No - it speeds them up!
- Local check: 8 seconds
- PR check: 10 seconds
- But prevents hours/days of incident response
- And prevents broken deploys that would be rolled back anyway

Net result: Faster AND safer"

### "What if developers bypass the hooks?"

**Good answer:**
"That's why we have 3 layers:
1. Local check - convenience for devs
2. GitHub check - enforced, can't bypass
3. Dashboard - leadership sees everything

Even if layer 1 is bypassed, layers 2 and 3 catch it."

### "How accurate is the AI?"

**Good answer:**
"Very accurate because it uses real data:
- Queries actual Datadog production metrics
- Sees historical traffic patterns
- Knows about past incidents
- Not guessing - analyzing real numbers

Plus Claude Sonnet 4.5 is trained on infrastructure patterns."

---

## Demo Tips

### Do's ✅
- **Go slow** - Let people read the terminal output
- **Point at specific numbers** - "See this? 85% CPU at peak"
- **Tell a story** - Follow one change through all 3 surfaces
- **Show the same PR** in all 3 views for continuity

### Don'ts ❌
- Don't rush through the terminal - it's impressive!
- Don't skip the dashboard - that's your executive buy-in
- Don't forget to emphasize "real production metrics"
- Don't use jargon without explaining

### Recovery Plan

**If terminal demo fails:**
- Fall back to showing screenshots
- Or show the Streamlit UI with the same scenario

**If GitHub is slow:**
- Have screenshots ready
- Or skip to dashboard

**If dashboard doesn't load:**
- Show main UI instead
- Just explain "this is what management would see"

---

## Screenshot Checklist

Before demo, capture:
- [ ] Terminal showing blocked commit
- [ ] GitHub PR with failed checks (like Terracotta)
- [ ] GitHub bot comment with analysis
- [ ] Dashboard overview
- [ ] Main UI analysis

Save these as backup if live demo fails.

---

## Time Allocation

- Opening: 30 sec
- Local demo: 1 min
- GitHub PR: 1.5 min
- Dashboard: 1.5 min
- Wrap-up: 30 sec
- **Total: 5 minutes**

---

## Strongest Moment

**The "Same Issue, 3 Surfaces" reveal:**

Show the payment-api replica reduction appearing in:
1. Terminal (blocked locally)
2. GitHub PR (blocked in review)
3. Dashboard (tracked in metrics)

**Script:**
"Notice something? It's the SAME issue caught at EVERY level. That's the power of multi-surface detection. No way this risky change makes it to production."

---

## Closing Statement

**Script:**
"IaC Guardian combines real Datadog production metrics with Claude AI to catch infrastructure risks before they happen. We prevent million-dollar outages, save hundreds of thousands in cloud waste, and we do it at every stage of development - from commit to merge to production.

This isn't just a tool. It's shift-left security, but for infrastructure reliability and cost.

Ready for questions!"

---

**Good luck! 🚀**
