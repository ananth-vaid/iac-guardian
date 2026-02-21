# IaC Guardian - Demo Quick Start

## 🚀 Launch All 3 Surfaces (2 minutes)

```bash
cd /Users/ananth.vaidyanathan/iac-guardian

# 1. Install local hooks
./install_hooks.sh

# 2. Create GitHub PRs (if needed)
./create_demo_prs.sh

# 3. Start management dashboard
streamlit run dashboard.py --server.port 8502 &

# 4. Start main UI
./run_ui.sh &

# 5. Set API key
export ANTHROPIC_API_KEY="your-key-here"
```

**URLs:**
- Main UI: http://localhost:8501
- Dashboard: http://localhost:8502
- GitHub PRs: `gh pr list`

---

## 📝 5-Minute Demo Script

### 1. Local Check (1 min)
```bash
# Terminal visible
git add examples/scenario-1-peak-traffic/payment-api-deployment.yaml
git commit -m "Reduce replicas"
# → Shows IaC Guardian blocking commit with analysis
```

**Say:** "Caught locally before even creating a PR"

### 2. GitHub PR (1.5 min)
- Open PR in browser (created by script)
- Point to failed checks
- Show bot comment
- Point to auto-fix link

**Say:** "If local check is bypassed, GitHub catches it"

### 3. Dashboard (1.5 min)
- Open http://localhost:8502
- Point to metrics: "47 PRs, 8 risks blocked, $428k saved"
- Point to risk feed
- Point to ROI calculation

**Say:** "Management sees total impact across all changes"

### 4. Wrap-up (30 sec)
**Say:** "3 surfaces, same issue caught at every stage. No risky change makes it to production."

---

## 🎯 Key Talking Points

### Why 3 Surfaces?

**Local (Claude Code/Terminal):**
- Fastest feedback (8 seconds)
- Prevents wasted PR review time
- Developer-friendly

**GitHub PR:**
- Team visibility
- Enforced (can't bypass)
- Integrates with workflow

**Dashboard (Datadog-style):**
- Executive metrics
- ROI tracking
- Identifies problem areas

### Differentiation from Terracotta

✅ **AI-powered** (Claude vs rules)
✅ **Real metrics** (Datadog production data)
✅ **Multi-surface** (local + PR + dashboard)
✅ **Auto-remediation** (generates safe alternatives)

---

## 🆘 Emergency Backup

**If demo fails:**

### Plan B: Screenshots only
- Have terminal output screenshot
- Have GitHub PR screenshot
- Have dashboard screenshot
- Walk through them

### Plan C: Main UI only
- Skip local/GitHub
- Focus on Streamlit UI
- Show both scenarios there

### Plan D: Slides + Screenshots
- Explain architecture
- Show value prop
- Use Terracotta screenshots as inspiration

---

## ✅ Pre-Demo Checklist

- [ ] Both Streamlit apps running (8501, 8502)
- [ ] GitHub PRs created and checks failed
- [ ] ANTHROPIC_API_KEY exported
- [ ] Terminal window sized for audience
- [ ] Browser tabs open (GitHub PRs, both UIs)
- [ ] Backup screenshots saved
- [ ] Terracotta screenshots ready for comparison

---

## 🎬 Opening Line

"Infrastructure changes that look safe can cause million-dollar outages. I'm going to show you how IaC Guardian catches these issues at 3 different stages - before commit, during PR review, and in management dashboards - using real production metrics and AI."

---

## 🎤 Closing Line

"IaC Guardian prevents outages, saves costs, and works everywhere your engineers work - from their terminals to GitHub to executive dashboards. This is shift-left for infrastructure reliability."

---

## 📊 Key Numbers to Memorize

- **8 seconds** - Local analysis time
- **$2M** - Typical outage cost prevented
- **$428k** - Cost waste detected (this week)
- **3 surfaces** - Local, PR, Dashboard
- **47 PRs** - Analyzed this week
- **8 risks** - Blocked this week

---

## 🔥 Strongest Demo Moment

**"The Same Issue, 3 Times" reveal:**

1. Show terminal blocking the commit
2. Show GitHub blocking the PR
3. Show dashboard tracking it

**Say:** "See how it's the SAME change caught at EVERY level? That's multi-surface detection. No escape."

---

Need help? Everything is in `/3_SURFACE_DEMO.md`
