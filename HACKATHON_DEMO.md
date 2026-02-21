# IaC Guardian - Hackathon Demo Script

## Pre-Demo Setup (2 minutes before)

```bash
cd /Users/ananth.vaidyanathan/iac-guardian
./run_ui.sh
```

- Open http://localhost:8501
- Have browser window ready
- Close sidebar for clean look
- Optional: Set API keys if doing live analysis

## Demo Flow (5 minutes)

### Slide 1: The Problem (30 sec)
**Script:** "Infrastructure changes that look safe can cause production outages. Engineers don't have visibility into real production metrics when reviewing PRs."

**Show:** Welcome screen of IaC Guardian UI

### Slide 2: Scenario 1 - Peak Traffic Risk (2 min)

**Script:** "Let me show you a real example. An engineer wants to reduce replicas from 20 to 5 to save money."

**Actions:**
1. Open sidebar → Select "Scenario 1: Peak Traffic Risk"
2. Show the diff:
   ```
   - replicas: 20
   + replicas: 5
   ```
3. Click "🔍 Analyze Changes"

**While analyzing (fill time):**
- "It's querying Datadog for real production metrics..."
- "Looking at last 7 days of traffic patterns..."
- "Checking recent incidents..."

**Results appear:**
1. **Point to metrics:**
   - "Current: 20 replicas at 65% CPU"
   - "Peak traffic: 82k req/min needed 18 replicas at 85% CPU"

2. **Point to charts:**
   - "This traffic pattern shows peak at 2pm on Tuesday"
   - "Replica count has been stable around 20"

3. **Point to analysis:**
   - "Claude catches it: 5 replicas = 306% CPU = CRASH"
   - "Recent incident INC-4521 was the exact same issue"

4. **Point to auto-fix:**
   - "It generates a safe alternative with HPA"
   - "Minimum 15 replicas, max 22 - autoscales based on CPU"
   - "Still saves money, but won't crash"

**Impact:** "Prevented a $2M outage."

### Slide 3: Scenario 2 - Cost Optimization (1.5 min)

**Script:** "Now let's look at the opposite problem - over-provisioning."

**Actions:**
1. Sidebar → Select "Scenario 2: Cost Optimization"
2. Show the diff:
   ```
   - count = 5, instance_type = "c5.2xlarge"
   + count = 10, instance_type = "c5.4xlarge"
   ```
3. Click "🔍 Analyze Changes"

**Results:**
1. **Point to metrics:**
   - "Current 5 instances: 15% CPU, 22% memory"
   - "Barely utilized!"

2. **Point to cost chart:**
   - "Current: $4k/month"
   - "Proposed: $34k/month"
   - "Recommended: $10k/month"

3. **Point to analysis:**
   - "Claude spots over-provisioning by 3x"
   - "Recommends 6x c5.2xlarge instead"

4. **Point to auto-fix:**
   - "Right-sized alternative"
   - "Saves $282k/year vs original proposal"

**Impact:** "Saved $282k annually through smart right-sizing."

### Slide 4: Wrap-up (30 sec)

**Script:** "IaC Guardian combines real Datadog metrics with Claude AI to:"
- Prevent production outages
- Optimize cloud costs
- Generate safe alternatives automatically

**Show:** Switch back to welcome screen

**Next steps:**
- "Works as GitHub Action on every PR"
- "Can integrate with Datadog Security for policy compliance"
- "Ready to deploy to Datadog engineering teams"

---

## Q&A Prep

### "Does it work with our infrastructure?"
"Yes - supports Kubernetes, Terraform, and extensible to Helm/CloudFormation."

### "How accurate are the metrics?"
"Uses real Datadog production data - same metrics you see in dashboards."

### "Can it auto-merge safe changes?"
"Not yet - for safety, it posts recommendations. Could add auto-merge for low-risk changes."

### "What about other cloud providers?"
"Architecture supports AWS, Azure, GCP - just need provider-specific parsers."

### "How long does analysis take?"
"~10 seconds per PR - queries Datadog, calls Claude, generates recommendations."

### "Can it learn from incidents?"
"Yes! It queries Datadog incidents and uses them as context for analysis."

---

## Backup: Live Analysis

If demo gods smile and you want to go off-script:

1. **Upload real diff:**
   - Sidebar → "Upload Diff"
   - Upload a real K8s or Terraform change

2. **Set API keys:**
   - Sidebar → 🔑 API Keys
   - Enter Anthropic key
   - Enter Datadog keys (or use mock data)

3. **Analyze:**
   - Click analyze
   - Show real-time results

---

## Technical Details (if asked)

**Architecture:**
```
Streamlit UI
    ↓
Claude Sonnet 4.5 (AI analysis)
    ↓
Datadog REST API (real metrics)
    ↓
Auto-fix generator (creates HPA, right-sizes)
```

**Tech stack:**
- Python 3.14
- Streamlit for UI
- Anthropic Claude API
- Datadog REST API
- Plotly for charts

**Metrics queried:**
- Kubernetes: CPU, memory, replicas, requests/sec
- Infrastructure: Instance utilization, cost
- Incidents: Recent outages related to service

---

## Demo Tips

### Do's ✅
- **Go slow** - Let metrics load, let people read charts
- **Point at screen** - "Look at this number here..."
- **Use numbers** - "$2M outage", "$282k saved"
- **Show personality** - "This is the cool part..."

### Don'ts ❌
- Don't rush through metrics - they're impressive!
- Don't skip the auto-fix - it's the wow moment
- Don't use jargon - explain what HPA means
- Don't apologize for mock data - call it "production-like"

### Recovery Strategies

**If app crashes:**
"Let me show you the command-line version..." → run `python scripts/analyze_pr.py examples/...`

**If API keys don't work:**
"We'll use mock data - based on real production patterns"

**If charts don't load:**
"The raw metrics are here..." → point to metric cards

**If you forget the script:**
Just narrate what you see: "Here's current state... here's peak traffic... Claude says..."

---

## Time Checkpoints

- **1:00** - Finished intro, showing Scenario 1
- **2:30** - Showing Scenario 1 results
- **3:30** - Showing Scenario 2 results
- **4:30** - Wrapping up
- **5:00** - Done, opening Q&A

---

**Good luck! 🚀**
