# Testing Datadog MCP Integration

## Quick Test Checklist

### ✅ Step 1: Add Datadog MCP Server

```bash
claude mcp add --transport http datadog-mcp https://mcp.datadoghq.com/api/unstable/mcp-server/mcp
```

### ✅ Step 2: Configure Keys

Edit: `~/.config/Claude/claude_desktop_config.json`

Add your keys:
```json
{
  "mcpServers": {
    "datadog-mcp": {
      "transport": "http",
      "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp",
      "headers": {
        "DD-API-KEY": "your-api-key",
        "DD-APPLICATION-KEY": "your-app-key"
      }
    }
  }
}
```

**Get your keys:**
- API Key: https://app.datadoghq.com/organization-settings/api-keys
- App Key: https://app.datadoghq.com/organization-settings/application-keys

### ✅ Step 3: Restart Claude Code

Close and reopen your Claude Code session.

### ✅ Step 4: Test MCP Tools

In this Claude Code session, ask:

```
List all available Datadog MCP tools
```

You should see tools like:
- `mcp__datadog__query_metrics`
- `mcp__datadog__search_logs`
- `mcp__datadog__list_incidents`
- etc.

### ✅ Step 5: Test a Query

Ask Claude:

```
Use the Datadog MCP tools to query CPU metrics for any service in my account. Show me what services have data available.
```

Claude should use the MCP tools to query your actual Datadog account!

---

## Test with IaC Guardian

### Test 1: Basic Analysis

```bash
cd /Users/ananth.vaidyanathan/iac-guardian

# Test with existing scenario
python scripts/analyze_pr_with_mcp.py examples/scenario-1-peak-traffic/demo_diff.txt
```

Expected output:
```
🔍 Analyzing PR with Datadog MCP integration...
   Service: payment-api
🤖 Querying Claude with Datadog MCP tools enabled...
   ✓ Used MCP tool: query_metrics
   ✓ Used MCP tool: search_incidents

📊 Datadog Queries Made:
   - query_metrics: {...}
   - search_incidents: {...}

📋 ANALYSIS RESULTS
==================
## 🚨 Risk Level: CRITICAL
...based on REAL metrics...
```

### Test 2: Create PR with MCP Analysis

Update GitHub Actions to use MCP:

```bash
# Edit .github/workflows/iac-review.yml
# Change: python scripts/analyze_pr.py
# To:     python scripts/analyze_pr_with_mcp.py
```

Then create a PR:
```bash
./scripts/create_scenario_pr.sh 5
```

The PR comment should reference REAL Datadog metrics! 🎉

---

## Troubleshooting

### "MCP tools not found"

Check your config file exists and has the right structure:
```bash
cat ~/.config/Claude/claude_desktop_config.json
```

Should have `mcpServers` → `datadog-mcp` section.

### "Authentication failed"

Verify your keys work:
```bash
# Test keys directly
curl -X GET "https://api.datadoghq.com/api/v1/validate" \
  -H "DD-API-KEY: your-key" \
  -H "DD-APPLICATION-KEY: your-app-key"

# Should return: {"valid": true}
```

### "No data for service"

The service name needs to match what's in your Datadog account:
```bash
# List services in your account
curl -X GET "https://api.datadoghq.com/api/v2/services" \
  -H "DD-API-KEY: $DATADOG_API_KEY" \
  -H "DD-APPLICATION-KEY: $DATADOG_APP_KEY"
```

Update the demo diffs to use actual service names from your account.

### Claude not using MCP tools

Make sure to:
1. Restart Claude Code after config changes
2. Ask Claude explicitly: "Use Datadog MCP tools to..."
3. Check the MCP server is listed: Ask "What MCP servers are available?"

---

## Comparison: Before vs After

### Before (Mock Data):
```bash
$ python scripts/analyze_pr.py demo_diff.txt

⚠️  Using mock data for demo
CPU: 65% (mock)
Incidents: None (mock)

Risk: HIGH (estimated)
```

### After (Real MCP Data):
```bash
$ python scripts/analyze_pr_with_mcp.py demo_diff.txt

🤖 Querying Claude with Datadog MCP tools enabled...
   ✓ Used MCP tool: query_metrics
   ✓ Used MCP tool: search_incidents

📊 Real Datadog data:
CPU peaks at 92.3% during business hours
3 incidents in last 30 days
Current replica count: 18

Risk: CRITICAL (based on production metrics)
⛔ DO NOT MERGE - Will cause outage
```

---

## Next Steps

Once MCP is working:

1. **Update all scenarios** - Use real service names from your Datadog account
2. **Update GitHub Actions** - Switch to `analyze_pr_with_mcp.py`
3. **Demo with confidence** - Show REAL metrics in your hackathon presentation!

---

## Benefits

✅ **Real metrics** instead of mock data
✅ **No custom server** to maintain
✅ **Official Datadog integration**
✅ **Automatic tool discovery** by Claude
✅ **Production-ready** for post-hackathon use

Your IaC Guardian is now powered by real observability data! 🚀
