# IaC Guardian - Product Vision
## Beyond Static Analysis: Preventing Real Incidents

---

## The Problem with Current Tools

### What Exists (Terracotta, Checkov, etc.)
**Static Guardrails:**
- ✅ S3 bucket open? → Block
- ✅ Encryption missing? → Block
- ✅ Single-AZ? → Block

**Limitation:** These are **always wrong** configurations.

### What's Missing
**Context-Aware Risk Detection:**
- ❌ Will this replica reduction cause an outage?
- ❌ Can the new instance type handle the load?
- ❌ Will this network change break dependencies?
- ❌ Will this version change cause compatibility issues?

**Challenge:** These require **production context** to determine risk.

---

## IaC Guardian's Approach: Dynamic Risk Detection

### Core Insight (from Overmind)
> "We know that the first question anyone asks when something breaks is 'What changed?'
> So build a product that delivers real value **before** you make changes."

### Your Competitive Advantage

**Static tools answer:** "Is this configuration valid?"
**IaC Guardian answers:** "Will this change cause an incident?"

---

## How to Detect Incident-Causing Changes

### 1. Real Production Metrics (✅ You Have This!)

Query Datadog for:
- **Traffic patterns** - Peak load times, request rates
- **Resource utilization** - CPU, memory, disk over time
- **Performance baselines** - Latency, error rates
- **Capacity metrics** - Current vs max capacity

**Example:**
```python
# Detect: "Reducing replicas below peak traffic needs"
current_replicas = 20
proposed_replicas = 5
peak_traffic = datadog.get_peak_traffic(service="payment-api", days=7)
peak_replicas_needed = calculate_needed_replicas(peak_traffic)

if proposed_replicas < peak_replicas_needed:
    risk = "CRITICAL"
    reason = f"Peak traffic needs {peak_replicas_needed} replicas, proposed only {proposed_replicas}"
```

### 2. Blast Radius Calculation (Need to Build)

Understand **what this change affects**:
- Which services depend on this resource?
- What's the scope of impact?
- Is this in the critical path?

**Inspired by Overmind:**
```
Change: Reduce payment-api replicas
Blast Radius:
  ├─ payment-api service (DIRECT)
  ├─ checkout flow (DEPENDENCY)
  ├─ order-processor (DOWNSTREAM)
  └─ revenue metrics (BUSINESS IMPACT)
```

**Implementation:**
- Parse Terraform/K8s to build dependency graph
- Query Datadog APM for service dependencies
- Use service mesh data (if available)

### 3. Historical Incident Analysis (Need to Build)

Learn from **past incidents**:
- Query Datadog/PagerDuty incidents
- Correlate with infrastructure changes
- Build patterns of what causes outages

**Example:**
```python
# Check: "Similar change caused incident before?"
past_incidents = datadog.get_incidents(service="payment-api", days=90)
similar_changes = find_similar_changes(current_change, past_incidents)

if similar_changes:
    risk = "HIGH"
    reason = f"Similar change caused incident {incident_id} on {date}"
```

### 4. AI-Powered Reasoning (✅ You Have This!)

Claude analyzes:
- Change context
- Production metrics
- Historical patterns
- Service dependencies

**Your secret sauce:** Claude can reason about complex scenarios that rules-based systems miss.

### 5. Continuous Learning (Future)

Feedback loop:
1. Predict risk before deployment
2. Track what actually happens
3. Learn from false positives/negatives
4. Improve detection over time

---

## Product Roadmap: Static → Dynamic

### Phase 1: Hackathon (✅ Current)
**Static + Basic Dynamic**
- Static guardrails (encryption, single-AZ)
- Basic capacity analysis (replicas vs traffic)
- Cost optimization
- Auto-remediation

**Data sources:**
- Datadog metrics (traffic, CPU, memory)
- Git diff parsing
- Claude AI analysis

### Phase 2: Blast Radius (Next 3-6 months)
**Add dependency understanding**
- Parse Terraform state for dependencies
- Query Datadog APM for service relationships
- Build resource dependency graph
- Calculate change impact scope

**New capabilities:**
- "This change affects 12 downstream services"
- "Critical path: Yes - payment flow depends on this"
- "Estimated blast radius: 50k users"

### Phase 3: Incident Correlation (6-12 months)
**Learn from history**
- Ingest incident data (Datadog, PagerDuty)
- Correlate incidents with infrastructure changes
- Build incident pattern library
- Predictive risk scoring

**New capabilities:**
- "Similar change caused incident INC-4521"
- "3 past outages related to replica reductions"
- "Risk score: 85/100 based on historical data"

### Phase 4: Continuous Learning (12+ months)
**Close the loop**
- Track prediction accuracy
- Learn from false positives/negatives
- Auto-tune risk thresholds
- Team-specific risk profiles

**New capabilities:**
- "Predictions 92% accurate for this team"
- "Auto-adjusting thresholds based on your tolerance"
- "This team has higher risk tolerance for off-hours"

---

## Technical Architecture for Dynamic Detection

### Data Flow

```
Infrastructure Change (PR)
         ↓
┌─────────────────────────────────────┐
│  1. Parse Changes                   │
│  - Extract resources changed        │
│  - Identify change type             │
│  - Calculate scope                  │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  2. Gather Context                  │
│  ├─ Production Metrics (Datadog)    │
│  ├─ Blast Radius (Dependencies)     │
│  ├─ Historical Incidents            │
│  └─ Service Relationships           │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  3. AI Risk Analysis (Claude)       │
│  - Analyze all context              │
│  - Reason about impact              │
│  - Generate risk assessment         │
│  - Suggest mitigations              │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  4. Present Results                 │
│  ├─ Risk level (Critical/High/Low)  │
│  ├─ Blast radius visualization      │
│  ├─ Historical precedent            │
│  └─ Auto-fix (if available)         │
└─────────────────────────────────────┘
```

### Key Components

**Blast Radius Calculator:**
```python
class BlastRadiusCalculator:
    def calculate(self, change):
        # Parse Terraform state
        dependencies = self.parse_terraform_graph(change)

        # Query service dependencies
        service_deps = self.datadog.get_service_dependencies(change.service)

        # Combine
        blast_radius = {
            'direct_resources': dependencies,
            'downstream_services': service_deps,
            'estimated_users_affected': self.estimate_user_impact(service_deps),
            'critical_path': self.is_critical_path(change.service)
        }

        return blast_radius
```

**Incident Correlator:**
```python
class IncidentCorrelator:
    def find_similar_incidents(self, change):
        # Get recent incidents
        incidents = self.datadog.get_incidents(days=90)

        # For each incident, check if similar change happened before it
        similar = []
        for incident in incidents:
            change_before_incident = self.get_changes_before(incident, hours=24)
            if self.is_similar_change(change, change_before_incident):
                similar.append({
                    'incident_id': incident.id,
                    'date': incident.date,
                    'impact': incident.severity,
                    'similar_change': change_before_incident
                })

        return similar
```

**AI Risk Reasoner:**
```python
def analyze_with_context(change, metrics, blast_radius, incidents):
    prompt = f"""
    Analyze this infrastructure change:

    CHANGE: {change.description}

    PRODUCTION METRICS:
    {metrics}

    BLAST RADIUS:
    - Affects {len(blast_radius.downstream_services)} services
    - Critical path: {blast_radius.critical_path}
    - Estimated user impact: {blast_radius.estimated_users_affected}

    HISTORICAL INCIDENTS:
    {incidents}

    Questions:
    1. What's the risk level of this change?
    2. What could go wrong?
    3. Have similar changes caused incidents before?
    4. What's the blast radius if it fails?
    5. What mitigations should be in place?
    """

    return claude.analyze(prompt)
```

---

## Example: Detecting Incident-Causing Changes

### Scenario 1: Replica Reduction ✅ (You Have This!)

**Change:** Reduce replicas 20 → 5

**Static analysis:** ✅ Valid YAML

**Dynamic analysis:**
1. **Metrics:** Peak traffic 82k req/min needs 18 replicas
2. **Blast radius:** Payment flow, checkout, revenue tracking
3. **History:** Similar change caused INC-4521 (23min outage)
4. **AI reasoning:** "This will crash during peak traffic"

**Result:** 🚨 CRITICAL - Block deployment

### Scenario 2: Network ACL Change

**Change:** Open security group to 0.0.0.0/0

**Static analysis:** 🚨 Block (always wrong)

**Dynamic analysis:** Not needed (static rule catches it)

**Result:** 🚨 HIGH - Block deployment

### Scenario 3: Version Upgrade

**Change:** Upgrade API version v2.0 → v2.1

**Static analysis:** ✅ Valid (just a version bump)

**Dynamic analysis:**
1. **Metrics:** Current v2.0 performance is good
2. **Blast radius:** 15 downstream services call this API
3. **History:** v2.1 breaking change in beta (removed endpoint)
4. **Dependencies:** 3 services still use removed endpoint
5. **AI reasoning:** "Breaking change will cause 3 services to fail"

**Result:** 🚨 HIGH - Block deployment, list affected services

### Scenario 4: Instance Type Change

**Change:** t3.large → t3.xlarge

**Static analysis:** ✅ Valid

**Dynamic analysis:**
1. **Metrics:** Current t3.large at 45% CPU average
2. **Blast radius:** Single instance, non-critical service
3. **History:** No incidents related to this service
4. **Cost:** +$60/month
5. **AI reasoning:** "Over-provisioning - current instance has capacity"

**Result:** ⚠️ MEDIUM - Allow but warn about cost

---

## Data Sources for Dynamic Detection

### 1. Metrics & Observability
- **Datadog** (✅ You use this)
  - Metrics: CPU, memory, traffic
  - APM: Service dependencies
  - Logs: Error patterns
  - Events: Deployments, config changes

- **Prometheus/Grafana**
- **CloudWatch**

### 2. Incident Management
- **PagerDuty** - Incident history
- **Datadog Incidents** - Incident timeline
- **Jira/ServiceNow** - Postmortem tickets

### 3. Infrastructure State
- **Terraform State** - Resource dependencies
- **CloudTrail** - Who changed what
- **GitHub** - Change history

### 4. Service Mesh/APM
- **Datadog APM** - Service call graph
- **Istio/Linkerd** - Traffic routing
- **AWS App Mesh** - Service dependencies

---

## Positioning: Why This is Hard (Your Moat)

### Why Others Don't Do This

**Static analysis is easy:**
- Rule: "RDS must be multi-AZ"
- Implementation: Parse config, check attribute
- **Anyone can build this**

**Dynamic analysis is hard:**
- Question: "Will this replica reduction cause an outage?"
- Requires:
  1. Real-time production metrics
  2. Traffic pattern understanding
  3. Capacity modeling
  4. Historical incident correlation
  5. Dependency graph
  6. AI reasoning
- **This is your moat**

### Competitive Advantage

**Terracotta/Checkov:**
- ❌ Static rules only
- ❌ No production context
- ❌ Can't predict incidents

**IaC Guardian:**
- ✅ Static + Dynamic
- ✅ Real production metrics
- ✅ AI-powered reasoning
- ✅ Incident prediction
- ✅ Auto-remediation

**Overmind:**
- ✅ Blast radius (good)
- ✅ Change tracking (good)
- ❌ Post-incident focus (reactive)
- ❌ No pre-deployment blocking

**You combine the best of both:**
- Pre-deployment blocking (like Terracotta)
- Blast radius + dependencies (like Overmind)
- Real metrics + AI (unique to you)

---

## Business Model

### Phase 1: Free/OSS (Hackathon)
- Basic static checks
- Simple capacity analysis
- Community-driven rules

### Phase 2: Team ($99/user/month)
- Full static + dynamic analysis
- Datadog integration
- Basic blast radius
- 10k changes/month

### Phase 3: Enterprise ($custom)
- Advanced blast radius
- Incident correlation
- Custom learning models
- Unlimited changes
- SLA + support

### Add-ons
- **Incident Correlation** - $5k/month
- **Custom Rules Engine** - $10k/month
- **Dedicated AI Model** - $20k/month (fine-tuned on your data)

---

## Metrics to Track

### Product Metrics
- Changes analyzed
- Incidents prevented
- False positive rate
- Time to analysis
- Auto-fix acceptance rate

### Business Metrics
- Outages prevented (count)
- $ value of prevented outages
- Cloud cost saved
- Engineering time saved
- MTTR reduction (when incident does happen, faster root cause)

---

## Roadmap Summary

**Today (Hackathon):**
- Static checks + basic capacity analysis
- 2 scenarios (replicas, cost)
- Datadog metrics
- Claude AI

**Month 1-3:**
- Add 10+ scenarios
- Blast radius v1 (Terraform graph)
- Incident API integration
- Production deployment

**Month 4-6:**
- Blast radius v2 (service dependencies via APM)
- Historical incident correlation
- Risk scoring v2
- Multi-cloud support

**Month 7-12:**
- Continuous learning
- Team-specific models
- Post-incident analysis integration
- "What changed?" reverse lookup

**Year 2:**
- Predictive incident prevention
- Auto-remediation v2 (smarter)
- Cost optimization v2 (FinOps integration)
- Compliance dashboards

---

## Answer to Your Question

> "Is there a way to build detection for real-time incident-causing changes?"

**YES - And you're already doing it!** The key is:

1. **Real production metrics** ✅ (Datadog)
2. **AI reasoning** ✅ (Claude)
3. **Blast radius** 🔨 (Need to build)
4. **Incident correlation** 🔨 (Need to build)
5. **Continuous learning** 🔮 (Future)

**Your replicas scenario proves it works:**
- Not a static rule
- Requires production metrics
- Context-dependent
- Prevents real incidents

**Static guardrails (S3 public, single-AZ) are table stakes.**
**Dynamic incident prevention (replicas, capacity) is your moat.**

---

## Next Steps

### For Hackathon:
Focus on the story you have - it's already compelling!

### After Hackathon:
1. Add blast radius calculation
2. Integrate PagerDuty/Datadog incidents
3. Build more dynamic scenarios
4. Start learning from production deployments

---

**Bottom line:** You can absolutely build incident-causing change detection. It's hard, which is why it's valuable. You're already on the right path with Datadog + Claude.
