# IaC Guardian - Project Status

**Last Updated:** 2026-02-17
**Phase:** Demo-ready, planning extensibility framework
**Repository:** https://github.com/ananth-vaid/iac-guardian

---

## Executive Summary

✅ **Demo-Ready:** All 3 surfaces working (pre-commit, GitHub Actions, Streamlit UI)
✅ **Live PR Demo:** https://github.com/ananth-vaid/iac-guardian/pull/1
⏳ **Next:** Add extensibility to easily create new incident/optimization scenarios

---

## What Works ✅

### Core Features
- [x] **Pre-commit hook** - Blocks risky changes with Claude analysis
- [x] **GitHub Actions workflow** - Posts concise PR comments (8 lines)
- [x] **Streamlit main UI** - Interactive analysis with 2 demo scenarios
- [x] **Management dashboard** - Metrics, trends, demo data visualization
- [x] **Auto-remediation** - Generates HPA configs and safe alternatives
- [x] **Concise output** - Risk/Why/Action format (15x shorter than before)

### Technical Capabilities
- [x] Generic diff parsing (K8s, Terraform, any IaC)
- [x] Datadog metric integration (with mock fallback)
- [x] Claude Sonnet 4.5 analysis
- [x] Auto-fix generation (HPA, right-sizing)
- [x] Simulated PR creation
- [x] E2E testing framework

### Demo Materials
- [x] PRESENTATION_DEMO.md - 7-minute presentation script
- [x] Example PR comments for both scenarios
- [x] Working GitHub Actions workflow
- [x] E2E_TEST_RESULTS.md - Complete test documentation

---

## Current Architecture

### Pipeline Flow
```
Git Diff → Parse (generic) → Datadog Context → Claude Analysis → Concise Output → Auto-Fix
```

### Hardcoded Elements (Blocking Extensibility)

1. **`app.py` lines 281-330**
   - Hardcoded if/elif dropdown for scenarios
   - Inline diff content (~50 lines per scenario)
   - **Impact:** Adding scenario = edit this file

2. **`analyze_pr.py` lines 148-149**
   - Prompt explicitly mentions "Scenario 1" and "Scenario 2"
   - **Impact:** Not generic for new scenarios

3. **`datadog_api_client.py` line 278**
   - Checks for literal "payment-api" string
   - **Impact:** Can't query metrics for other services

4. **`fix_generator.py` lines 35-39**
   - Only handles 2 fix types (k8s_replica_fix, cost_optimization_fix)
   - **Impact:** New scenarios can't generate fixes

### Generic Elements (Already Extensible)

- ✅ **Diff parsing** - Regex-based, works with any file type
- ✅ **Claude reasoning** - Flexible AI can analyze new patterns
- ✅ **Output formatting** - Consistent across all scenarios
- ✅ **Datadog client** - Has mock fallback, real API ready

---

## Current Scenarios (2)

### Scenario 1: Peak Traffic Risk
- **Change:** K8s replica reduction (20→5)
- **Risk:** CRITICAL - Can't handle peak traffic
- **Datadog metrics:** CPU, replica count, request rate, incidents
- **Auto-fix:** Generate HPA with safe min/max replicas
- **Example:** PR #1 - Reduces payment-api replicas

### Scenario 2: Cost Optimization
- **Change:** Terraform over-provisioning (5x c5.2xlarge → 10x c5.4xlarge)
- **Risk:** WARNING - 13x capacity vs actual usage
- **Datadog metrics:** CPU/memory utilization, instance stats
- **Auto-fix:** Right-size to 3x c5.2xlarge (saves $282k/year)
- **Example:** Demo diff showing cost waste

---

## Known Issues & Fixes

### Fixed (During E2E Testing)
- ✅ .env file not loaded by git hooks → Added loading in install_hooks.sh
- ✅ Verbose PR comments (50+ lines) → Concise format (8 lines)
- ✅ Missing demo_diff.txt for scenario 1 → Created
- ✅ run_ui.sh not loading .env → Added sourcing
- ✅ TEST_SCRIPT.sh not loading .env → Added sourcing

### No Known Blockers
All critical functionality working for demo.

---

## Planned: Extensibility Framework

### Problem
Adding new scenario today requires:
- Edit 4 Python files
- Write ~65 lines of code
- 30+ minutes of work
- Error-prone (manual edits across codebase)

### Solution (Approved Plan)
Hybrid YAML + Python framework:
- **Simple scenarios:** Just edit `scenarios.yaml` (~15 lines, 2 minutes)
- **Complex fixes:** Optional Python plugins for auto-remediation
- **Backwards compatible:** Existing 2 scenarios work unchanged

### Implementation
- **Phase 1:** Create `scenario_engine.py` + `scenarios.yaml` (30 mins)
- **Phase 2:** Update 4 files to use dynamic loading (2 hours)
- **Phase 3:** Validate existing scenarios still work (30 mins)
- **Phase 4:** Add 3 new scenarios to prove extensibility (1 hour)
- **Total:** 3-4 hours

### New Scenarios to Add (Priority)

**P0 - Incident Detection:**
1. Missing health checks (liveness/readiness probes)
2. Missing PodDisruptionBudget (risky rolling updates)
3. Insufficient replicas for HA (<3 replicas in prod)
4. Missing resource limits (memory/CPU unbounded)
5. Single availability zone (no AZ redundancy)
6. Missing monitoring/alerts

**P1 - Optimization & Governance:**
7. Over-provisioned resources (<20% utilization)
8. No auto-scaling configured (static capacity)
9. Expensive instance types (on-demand vs spot/reserved)
10. Missing cost allocation tags
11. Database encryption disabled (compliance risk)
12. Publicly accessible resources (security risk)
13. Security groups too open (0.0.0.0/0)
14. Outdated images/versions (known CVEs)

---

## Key Decisions & Rationale

### Technical Decisions
- **Concise PR comments:** Engineers need to understand in 10 seconds, not scroll through 50 lines
- **Mock Datadog data:** Enables demo without real API keys
- **Simulated PR creation:** Shows auto-fix capability without GitHub token requirements
- **Hybrid extensibility:** Balance simplicity (YAML) with flexibility (Python plugins)

### Architecture Decisions
- **Keep parsing generic:** Works with any IaC file type
- **Claude as smart layer:** AI bridges known and unknown patterns
- **Backwards compatible:** Don't break existing scenarios during refactor

---

## Files Reference

### Critical for Understanding
- `app.py` - UI and scenario definitions (lines 281-330 need refactoring)
- `scripts/analyze_pr.py` - Claude analysis and prompts
- `scripts/datadog_api_client.py` - Metric queries
- `scripts/fix_generator.py` - Auto-remediation
- `scripts/output_formatter.py` - Concise format generation

### Documentation
- `PRESENTATION_DEMO.md` - Hackathon demo script (7-8 minutes)
- `E2E_TEST_RESULTS.md` - Complete testing documentation
- `examples/*/EXAMPLE_PR_COMMENT.md` - Sample PR comments
- `.claude/plans/fancy-leaping-gadget.md` - Extensibility implementation plan

### Configuration
- `.env` - API keys (ANTHROPIC_API_KEY, DATADOG_API_KEY, DATADOG_APP_KEY)
- `requirements.txt` - Python dependencies
- `.github/workflows/iac-review.yml` - GitHub Actions workflow

---

## Environment Setup

```bash
# Quick start
cd /Users/ananth.vaidyanathan/iac-guardian
source venv/bin/activate

# Run UI
./run_ui.sh  # Main UI at :8501
streamlit run dashboard.py --server.port 8502  # Dashboard at :8502

# Test scenarios
python scripts/analyze_pr.py examples/scenario-1-peak-traffic/demo_diff.txt
./TEST_SCRIPT.sh

# Install pre-commit hook
./install_hooks.sh
```

---

## Demo Readiness Checklist

- [x] Pre-commit hook working
- [x] GitHub Actions posting comments
- [x] Streamlit UIs running
- [x] Both scenarios analyze correctly
- [x] Auto-fix generation working
- [x] Live PR demo available
- [x] Presentation script ready
- [x] Example PR comments created
- [x] E2E test results documented
- [ ] New scenarios added (planned)
- [ ] Extensibility framework implemented (planned)

---

## Open Questions

- [ ] Which 3-5 scenarios to demo in presentation?
- [ ] Full extensibility framework (4 hrs) or keep simple for hackathon?
- [ ] Test with real Datadog API keys?
- [ ] Deploy to production after hackathon?

---

## Contact & Resources

- **Repository:** https://github.com/ananth-vaid/iac-guardian
- **Demo PR:** https://github.com/ananth-vaid/iac-guardian/pull/1
- **Plan:** `.claude/plans/fancy-leaping-gadget.md`
