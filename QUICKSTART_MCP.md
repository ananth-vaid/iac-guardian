# Quick Start: Datadog MCP Integration

## 3-Minute Setup

### Step 1: Install the Datadog MCP Server
```bash
cd /Users/ananth.vaidyanathan/iac-guardian/mcp-servers/datadog-mcp
./setup.sh
```

### Step 2: Configure Claude Code

Add to your Claude Code configuration:

**macOS:** `~/.config/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "datadog": {
      "command": "/Users/ananth.vaidyanathan/iac-guardian/mcp-servers/datadog-mcp/venv/bin/python",
      "args": [
        "/Users/ananth.vaidyanathan/iac-guardian/mcp-servers/datadog-mcp/server.py"
      ],
      "env": {
        "DATADOG_API_KEY": "your-datadog-api-key",
        "DATADOG_APP_KEY": "your-datadog-app-key"
      }
    }
  }
}
```

Or use your existing `.env` file values:
```bash
# Get your keys
source /Users/ananth.vaidyanathan/iac-guardian/.env
echo "DATADOG_API_KEY: $DATADOG_API_KEY"
echo "DATADOG_APP_KEY: $DATADOG_APP_KEY"
```

### Step 3: Restart Claude Code

Close and reopen your Claude Code terminal/app.

### Step 4: Test the Integration

Ask Claude:
```
Query Datadog metrics for payment-api service - show me CPU usage for the last 24 hours
```

You should see Claude use the `query_datadog_metrics` tool!

---

## Using MCP Tools in IaC Guardian

### Test 1: Query Metrics via Claude

In Claude Code, try:
```
Use the Datadog MCP tools to:
1. Get service health for payment-api
2. Search for incidents in the last 30 days
3. Analyze if reducing replicas from 20 to 5 is safe
```

### Test 2: Update analyze_pr.py to Use MCP

Add this to `scripts/analyze_pr.py`:

```python
def analyze_pr_with_mcp(diff_file):
    """Enhanced analysis using Datadog MCP"""

    with open(diff_file, 'r') as f:
        diff_content = f.read()

    # Use Claude with MCP tools enabled
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""Analyze this infrastructure change using Datadog MCP tools:

```diff
{diff_content}
```

Steps:
1. Extract service name from the diff
2. Use get_service_health to fetch real metrics
3. Use analyze_capacity_risk if replicas are changing
4. Provide risk assessment based on REAL production data

Format your response:
## Risk Level: [CRITICAL/HIGH/MEDIUM/LOW]
## Why This is Risky:
[Based on actual Datadog metrics]
## What To Do:
- [Specific recommendations]
"""
        }],
        # This enables MCP tool use
        betas=["tools-2024-04-04"],
    )

    # Extract analysis from response
    analysis = ""
    for block in response.content:
        if block.type == "text":
            analysis += block.text

    return analysis
```

### Test 3: Create PR with MCP-Enhanced Analysis

```bash
# Create a demo PR
./scripts/create_scenario_pr.sh 3

# The GitHub Action will use the MCP-enhanced analysis
# Check the PR comment - it should reference REAL Datadog metrics!
```

---

## Available MCP Tools

Once configured, Claude can use these tools:

### 1. `query_datadog_metrics`
Query any Datadog metric:
```
query_datadog_metrics(
  query="avg:system.cpu.user{service:payment-api}",
  hours_back=24
)
```

### 2. `get_service_health`
Get comprehensive health report:
```
get_service_health(
  service_name="payment-api",
  hours_back=24
)
```

Returns: CPU, Memory, Requests, Errors

### 3. `search_datadog_incidents`
Search incidents:
```
search_datadog_incidents(
  query="service:payment-api",
  days_back=30
)
```

### 4. `analyze_capacity_risk`
Assess if capacity change is safe:
```
analyze_capacity_risk(
  service_name="payment-api",
  current_replicas=20,
  proposed_replicas=5
)
```

Returns: Risk level, projected metrics, recommendation

---

## Example: Full MCP-Powered Analysis

```python
#!/usr/bin/env python3
"""
Example: Analyze PR using Datadog MCP tools
"""

import anthropic
import os

def main():
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    diff = """
--- a/k8s/payment-api.yaml
+++ b/k8s/payment-api.yaml
@@ -5,7 +5,7 @@
   name: payment-api
 spec:
-  replicas: 20
+  replicas: 5
"""

    messages = [{
        "role": "user",
        "content": f"""You are IaC Guardian. Analyze this change using Datadog MCP:

{diff}

Use these MCP tools:
1. get_service_health("payment-api", 168)  # Last 7 days
2. analyze_capacity_risk("payment-api", 20, 5)
3. search_datadog_incidents("service:payment-api", 30)

Provide a risk assessment.
"""
    }]

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=messages,
        betas=["tools-2024-04-04"],
    )

    # Claude will automatically use MCP tools!
    print("Claude's Analysis:")
    for block in response.content:
        if block.type == "text":
            print(block.text)

if __name__ == "__main__":
    main()
```

Run it:
```bash
cd /Users/ananth.vaidyanathan/iac-guardian
python example_mcp_analysis.py
```

---

## Troubleshooting

### "MCP tools not available"

Check Claude config:
```bash
cat ~/.config/Claude/claude_desktop_config.json
```

Ensure the `mcpServers` section exists with `datadog` configured.

### "Connection refused" or "Server not starting"

Test the server directly:
```bash
cd /Users/ananth.vaidyanathan/iac-guardian/mcp-servers/datadog-mcp
source venv/bin/activate
python server.py
```

Should output: No errors, waits for input

### "API key errors"

Check your keys are loaded:
```bash
echo $DATADOG_API_KEY
echo $DATADOG_APP_KEY
```

Update the config JSON with correct values.

### Claude not using the tools

Make sure to:
1. Restart Claude Code after config changes
2. Use `betas=["tools-2024-04-04"]` in API calls
3. Explicitly ask Claude to "use Datadog MCP tools"

---

## Next Steps

1. ✅ Setup complete? Test with: `python -c "import mcp; print('OK')"`
2. ✅ Config added? Check: `cat ~/.config/Claude/claude_desktop_config.json`
3. ✅ Claude restarted? Ask Claude: "List available MCP tools"
4. ✅ Integration working? Create PR and check for real metrics in comments

---

## Benefits You'll See

### Before (Mock Data):
```
⚠️ Using mock data for demo
CPU: 65% (mock)
Recommendation: Based on typical patterns...
```

### After (Real MCP Data):
```
✅ Queried Datadog via MCP
CPU peaks at 92% during business hours
Last incident: Feb 15 - Peak Traffic Overload
⛔ CRITICAL: Reducing to 5 replicas will cause outage
```

**Real metrics = Real confidence in recommendations!**

---

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Datadog API Docs](https://docs.datadoghq.com/api/latest/)
- [Claude Tool Use](https://docs.anthropic.com/claude/docs/tool-use)
- [IaC Guardian + MCP Guide](DATADOG_MCP_INTEGRATION.md)
