# IaC Guardian - Streamlit UI

Interactive web interface for demonstrating IaC Guardian's capabilities.

## Quick Start

```bash
# Run the UI (handles venv and dependencies automatically)
./run_ui.sh

# Or manually:
source venv/bin/activate
streamlit run app.py
```

The UI will open at http://localhost:8501

## Features

### 🎯 Demo Scenarios
- **Scenario 1: Peak Traffic Risk** - Analyzes K8s replica reduction that would crash during peak
- **Scenario 2: Cost Optimization** - Identifies over-provisioned infrastructure

### 📊 Visual Analytics
- Real-time Datadog metrics visualization
- CPU utilization charts
- Traffic pattern analysis
- Replica count timeline
- Cost comparison graphs

### 🔧 Auto-Remediation
- Generates safe alternatives to risky changes
- Creates HPA configurations
- Provides cost-optimized recommendations
- Shows PR previews with full descriptions

### 💡 Input Methods
1. **Demo Scenarios** - Pre-loaded examples for quick demos
2. **Upload Diff** - Upload git diff files
3. **Paste Diff** - Manually paste infrastructure changes

## UI Components

### Sidebar
- **API Keys** - Configure Anthropic/Datadog keys
- **Input Method** - Choose how to provide changes
- **Options** - Toggle metrics display and auto-fix

### Main View
- **Changes Detected** - Shows the infrastructure diff
- **Production Metrics** - Live Datadog data with charts
- **AI Analysis** - Claude's risk assessment
- **Auto-Remediation** - Generated fixes and PR preview

## For Demos

### Hackathon Presentation Tips

1. **Start Clean** - Open UI, show welcome screen
2. **Pick Scenario 1** - Select "Peak Traffic Risk"
3. **Show Metrics** - Point out current vs peak traffic
4. **Run Analysis** - Click analyze, show AI reasoning
5. **Show Auto-Fix** - Highlight HPA generation
6. **Switch to Scenario 2** - Show cost optimization
7. **Emphasize Value** - Real metrics + AI = prevented outages

### Key Talking Points

**While metrics load:**
- "Querying real Datadog production data..."
- "Looking at last 7 days of traffic patterns..."

**During analysis:**
- "Claude is analyzing changes against production metrics..."
- "Checking for capacity issues, cost impact..."

**Auto-fix reveal:**
- "It generated a safe alternative with autoscaling..."
- "Saves money AND prevents crashes..."

## Customization

### Add New Scenarios

Edit `app.py` around line 270:

```python
scenario = st.selectbox(
    "Select Demo:",
    [
        "Scenario 1: Peak Traffic Risk",
        "Scenario 2: Cost Optimization",
        "Your New Scenario"  # Add here
    ]
)
```

### Modify Charts

Chart functions are at the top of `app.py`:
- `create_cpu_chart()` - CPU utilization
- `create_replica_chart()` - Replica timeline
- `create_traffic_chart()` - Traffic patterns
- `create_cost_chart()` - Cost comparison

### Change Theme

Edit `.streamlit/config.toml` (create if doesn't exist):

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### API Key Issues
- Set keys in UI sidebar (🔑 API Keys section)
- Or export before running:
  ```bash
  export ANTHROPIC_API_KEY="sk-..."
  export DATADOG_API_KEY="..."
  export DATADOG_APP_KEY="..."
  ```

### Mock Data
If Datadog keys aren't set, app uses mock data automatically.

### Dependencies
If you get import errors:
```bash
pip install -r requirements.txt --upgrade
```

## Architecture

```
app.py (Streamlit UI)
    ↓
scripts/analyze_pr.py (Analysis logic)
    ↓
├── scripts/datadog_api_client.py (Metrics)
├── scripts/fix_generator.py (Auto-remediation)
└── Anthropic API (Claude analysis)
```

## Development

### Run in Dev Mode
```bash
streamlit run app.py --server.runOnSave true
```

### Debug
Add this anywhere in `app.py`:
```python
st.write("Debug:", variable_name)
```

### Hot Reload
Streamlit auto-reloads when you save `app.py`.

---

Built for Datadog AI PM Hackathon 2026
