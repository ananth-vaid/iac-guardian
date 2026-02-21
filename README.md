# IaC Guardian

AI-powered Infrastructure-as-Code PR reviewer that prevents production incidents before they happen.

**Status:** ✅ Demo-ready | **Live Demo:** [PR #1](https://github.com/ananth-vaid/iac-guardian/pull/1)

## What It Does

Analyzes Terraform and Kubernetes PRs for:
- 🚨 **Risk Detection**: Catches changes that will cause outages based on real production metrics
- 💰 **Cost Optimization**: Identifies over-provisioned resources and suggests right-sizing
- 📋 **Policy Compliance**: Enforces infrastructure best practices

## How It Works

1. GitHub Action triggers on PR
2. Analyzes infrastructure changes (K8s manifests, Terraform)
3. Queries Datadog via MCP for real production metrics
4. Uses Claude AI to assess risk and provide recommendations
5. Posts analysis as PR comment

## Demo Scenarios

### Scenario 1: Prevent Peak Traffic Crash
PR reduces K8s replicas → Analysis shows it can't handle peak load → Blocks merge

### Scenario 2: Cost Optimization
PR adds over-provisioned instances → Suggests right-sizing → Saves $30k/month

## Quick Start

### 🚀 Full Demo (All 3 Surfaces)
```bash
# See DEMO_QUICKSTART.md for complete setup
./install_hooks.sh        # Local pre-commit
./create_demo_prs.sh      # GitHub PRs
streamlit run dashboard.py --server.port 8502 &  # Management dashboard
./run_ui.sh &             # Main UI
```

### Option 1: Web UI
```bash
./run_ui.sh  # http://localhost:8501
```

### Option 2: Management Dashboard
```bash
streamlit run dashboard.py --server.port 8502
```

### Option 3: Local CLI
```bash
./install_hooks.sh  # Installs pre-commit hook
git add <iac-file>
git commit  # IaC Guardian runs automatically
```

### Option 4: Command Line
```bash
source venv/bin/activate
export ANTHROPIC_API_KEY="your-key"
python scripts/analyze_pr.py examples/scenario-1-peak-traffic/demo_diff.txt
```

## Demo Strategy: 3 Surfaces

IaC Guardian catches issues at **3 different stages**:

1. **Local (Pre-Commit)** - Blocks bad commits before PR creation
2. **GitHub (PR Review)** - Automated checks that block merges
3. **Dashboard (Management)** - Executive visibility and ROI tracking

**See [3_SURFACE_DEMO.md](3_SURFACE_DEMO.md) for complete 5-minute demo script**

## Documentation

- **[DEMO_QUICKSTART.md](DEMO_QUICKSTART.md)** - 2-minute setup, 5-minute demo
- **[3_SURFACE_DEMO.md](3_SURFACE_DEMO.md)** - Complete multi-surface demo guide
- **[MULTI_SURFACE_DEMO.md](MULTI_SURFACE_DEMO.md)** - Strategy and implementation
- **[UI_README.md](UI_README.md)** - Streamlit UI guide
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Original presentation guide
- **[HACKATHON_DEMO.md](HACKATHON_DEMO.md)** - Hackathon-specific tips
- `examples/` - Demo scenario files

---

Built for Datadog AI PM Hackathon 2026
