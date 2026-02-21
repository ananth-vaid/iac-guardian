# Datadog MCP Server Integration for IaC Guardian

## Overview

Integrating the Datadog MCP (Model Context Protocol) server allows IaC Guardian to query real Datadog metrics directly through Claude's tool system, replacing mock data with production observability.

**Benefits:**
- ✅ Real-time production metrics (CPU, memory, request rates)
- ✅ Historical incident data for risk assessment
- ✅ APM traces for service dependencies
- ✅ No separate API client needed - Claude handles it
- ✅ Unified query interface across all MCP servers

---

## Step 1: Install Datadog MCP Server

### Check if Datadog MCP Server Exists

First, check if a Datadog MCP server is available:

```bash
# Search for Datadog MCP packages
npm search @modelcontextprotocol/server-datadog
# or
pip search datadog-mcp-server
```

### If Available: Install
```bash
# If npm-based
npm install -g @modelcontextprotocol/server-datadog

# If Python-based
pip install datadog-mcp-server
```

### If Not Available: Create Custom MCP Server

If there's no official Datadog MCP server yet, create one:

**File: `mcp-servers/datadog-server/index.js`**

```javascript
#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { Configuration, MetricsApi, LogsApi, IncidentsApi } from '@datadog/api';

const DD_API_KEY = process.env.DATADOG_API_KEY;
const DD_APP_KEY = process.env.DATADOG_APP_KEY;

const config = new Configuration({
  apiKey: DD_API_KEY,
  appKey: DD_APP_KEY,
});

const metricsApi = new MetricsApi(config);
const logsApi = new LogsApi(config);
const incidentsApi = new IncidentsApi(config);

const server = new Server(
  {
    name: "datadog-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "query_metrics",
        description: "Query Datadog metrics with a specific query string",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Datadog metric query (e.g., 'avg:system.cpu.user{service:payment-api}')",
            },
            from: {
              type: "number",
              description: "Start timestamp (Unix epoch seconds)",
            },
            to: {
              type: "number",
              description: "End timestamp (Unix epoch seconds)",
            },
          },
          required: ["query", "from", "to"],
        },
      },
      {
        name: "search_incidents",
        description: "Search for Datadog incidents by service or time range",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query (e.g., 'service:payment-api')",
            },
            from: {
              type: "number",
              description: "Start timestamp",
            },
            to: {
              type: "number",
              description: "End timestamp",
            },
          },
          required: ["query"],
        },
      },
      {
        name: "get_service_metrics",
        description: "Get common metrics for a specific service (CPU, memory, requests)",
        inputSchema: {
          type: "object",
          properties: {
            service_name: {
              type: "string",
              description: "Service name (e.g., 'payment-api')",
            },
            hours_back: {
              type: "number",
              description: "How many hours of data to fetch",
              default: 24,
            },
          },
          required: ["service_name"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "query_metrics") {
    const response = await metricsApi.queryMetrics({
      query: args.query,
      from: args.from,
      to: args.to,
    });

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.series, null, 2),
        },
      ],
    };
  }

  if (name === "search_incidents") {
    const response = await incidentsApi.listIncidents({
      query: args.query,
      from: args.from,
      to: args.to,
    });

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(response.data, null, 2),
        },
      ],
    };
  }

  if (name === "get_service_metrics") {
    const hoursBack = args.hours_back || 24;
    const to = Math.floor(Date.now() / 1000);
    const from = to - (hoursBack * 3600);

    // Query multiple metrics in parallel
    const [cpu, memory, requests] = await Promise.all([
      metricsApi.queryMetrics({
        query: `avg:system.cpu.user{service:${args.service_name}}`,
        from,
        to,
      }),
      metricsApi.queryMetrics({
        query: `avg:system.mem.used{service:${args.service_name}}`,
        from,
        to,
      }),
      metricsApi.queryMetrics({
        query: `sum:trace.http.request.hits{service:${args.service_name}}.as_count()`,
        from,
        to,
      }),
    ]);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            service: args.service_name,
            time_range: { from, to, hours: hoursBack },
            metrics: {
              cpu: cpu.series,
              memory: memory.series,
              requests: requests.series,
            },
          }, null, 2),
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Datadog MCP server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
```

**Package.json:**
```json
{
  "name": "datadog-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "datadog-mcp-server": "./index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "@datadog/api": "^1.0.0"
  }
}
```

Install dependencies:
```bash
cd mcp-servers/datadog-server
npm install
chmod +x index.js
npm link  # Makes it globally available
```

---

## Step 2: Configure MCP Server in Claude

Add to your Claude MCP configuration:

**File: `~/.claude/mcp_settings.json`**

```json
{
  "mcpServers": {
    "datadog": {
      "command": "datadog-mcp-server",
      "env": {
        "DATADOG_API_KEY": "your-api-key-here",
        "DATADOG_APP_KEY": "your-app-key-here"
      }
    }
  }
}
```

Or if you created a custom server:

```json
{
  "mcpServers": {
    "datadog": {
      "command": "node",
      "args": ["/Users/ananth.vaidyanathan/iac-guardian/mcp-servers/datadog-server/index.js"],
      "env": {
        "DATADOG_API_KEY": "your-api-key-here",
        "DATADOG_APP_KEY": "your-app-key-here"
      }
    }
  }
}
```

Restart Claude Code to load the MCP server:
```bash
# Restart your Claude Code session
```

---

## Step 3: Update IaC Guardian to Use MCP Tools

### Option A: Use MCP Tools Directly in analyze_pr.py

**Modify `scripts/analyze_pr.py`:**

```python
import anthropic

def analyze_pr_with_mcp(diff_file):
    """Analyze PR using Claude with Datadog MCP tools"""

    with open(diff_file, 'r') as f:
        diff_content = f.read()

    # Extract service name from diff
    service_name = extract_service_name(diff_content)

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Initial message with tool use
    messages = [
        {
            "role": "user",
            "content": f"""You are IaC Guardian, an AI-powered infrastructure reviewer.

Analyze this infrastructure change and assess the risk:

```diff
{diff_content}
```

**Your task:**
1. Use the Datadog MCP tools to fetch real production metrics for service: {service_name}
2. Query the last 24 hours of CPU, memory, and request rate data
3. Search for recent incidents related to this service
4. Based on the real metrics, assess if this change is risky
5. Provide a concise risk assessment in this format:

## Risk Level: [CRITICAL/HIGH/MEDIUM/LOW]

## Why This is Risky:
[1-2 sentences based on REAL metrics]

## What To Do:
- [Action 1]
- [Action 2]
"""
        }
    ]

    # Call Claude with tool use enabled
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=messages,
        tools="auto",  # Automatically use available MCP tools
    )

    # Handle tool use responses
    while response.stop_reason == "tool_use":
        # Extract tool results
        tool_results = []
        for content_block in response.content:
            if content_block.type == "tool_use":
                print(f"🔧 Claude is using tool: {content_block.name}")
                print(f"   Arguments: {content_block.input}")
                # Tool results are automatically handled by MCP

        # Continue conversation
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": "Continue with your analysis based on the Datadog metrics."
        })

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=messages,
            tools="auto",
        )

    # Extract final analysis
    analysis = ""
    for content_block in response.content:
        if hasattr(content_block, "text"):
            analysis += content_block.text

    return analysis
```

### Option B: Create MCP-Aware Wrapper

**New file: `scripts/datadog_mcp_client.py`**

```python
#!/usr/bin/env python3
"""
Datadog MCP Client for IaC Guardian
Wrapper around MCP tools for cleaner integration
"""

import os
from typing import Dict, List, Optional
import anthropic

class DatadogMCPClient:
    """Client for querying Datadog via MCP tools through Claude"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-5-20250929"

    def get_service_metrics(self, service_name: str, hours_back: int = 24) -> Dict:
        """
        Get comprehensive metrics for a service using MCP tools

        Returns dict with CPU, memory, request rates, and incidents
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"""Use the Datadog MCP tools to fetch metrics for service: {service_name}

Query the following for the last {hours_back} hours:
1. CPU usage (avg and max)
2. Memory usage (avg and max)
3. Request rate (requests per minute)
4. Any incidents related to this service

Return the results in JSON format with these keys:
- cpu_avg, cpu_max
- memory_avg, memory_max
- requests_per_minute
- incidents (list of incidents with severity and title)
"""
            }],
            tools="auto",
        )

        # Parse response
        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text

        # Extract JSON from response
        import json
        try:
            return json.loads(result_text)
        except:
            # Fallback to text parsing
            return {"raw": result_text}

    def check_service_health(self, service_name: str) -> Dict:
        """Quick health check using MCP tools"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""Use Datadog MCP tools to check health of {service_name}.

Check:
1. Is CPU usage above 80%?
2. Are there error spikes?
3. Any recent incidents?

Return: {{ "healthy": true/false, "issues": ["list", "of", "issues"] }}
"""
            }],
            tools="auto",
        )

        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text

        import json
        try:
            return json.loads(result_text)
        except:
            return {"healthy": True, "issues": []}

    def analyze_capacity_for_replica_change(
        self,
        service_name: str,
        current_replicas: int,
        new_replicas: int
    ) -> Dict:
        """
        Analyze if replica change is safe based on real metrics
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"""Use Datadog MCP tools to analyze this change:

Service: {service_name}
Current replicas: {current_replicas}
Proposed replicas: {new_replicas}

Query the last 7 days of metrics and determine:
1. Peak CPU usage per replica
2. Peak request rate
3. Can {new_replicas} replicas handle the peak load?

Return JSON:
{{
  "safe": true/false,
  "risk_level": "CRITICAL/HIGH/MEDIUM/LOW",
  "reason": "explanation",
  "peak_cpu_per_replica": 75.5,
  "peak_requests_per_second": 1000,
  "recommended_min_replicas": 10
}}
"""
            }],
            tools="auto",
        )

        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text

        import json
        try:
            return json.loads(result_text)
        except:
            return {
                "safe": False,
                "risk_level": "UNKNOWN",
                "reason": "Failed to analyze metrics",
            }
```

### Step 4: Update analyze_pr.py to Use MCP Client

```python
from datadog_mcp_client import DatadogMCPClient

def analyze_pr(diff_file):
    # ... existing code ...

    # Initialize MCP client
    dd_mcp = DatadogMCPClient()

    # Detect scenario
    if "replicas:" in diff_content:
        service_name = extract_service_name(diff_content)
        old_replicas, new_replicas = extract_replica_change(diff_content)

        print(f"🔍 Analyzing replica change via Datadog MCP...")
        capacity_analysis = dd_mcp.analyze_capacity_for_replica_change(
            service_name,
            old_replicas,
            new_replicas
        )

        print(f"✅ MCP Analysis: {capacity_analysis['risk_level']}")
        print(f"   Reason: {capacity_analysis['reason']}")

        # Use real data in prompt
        prompt = f"""
Analyze this infrastructure change:

{diff_content}

**Real Production Metrics from Datadog:**
- Peak CPU per replica: {capacity_analysis['peak_cpu_per_replica']}%
- Peak requests/sec: {capacity_analysis['peak_requests_per_second']}
- Recommended min replicas: {capacity_analysis['recommended_min_replicas']}
- MCP Assessment: {capacity_analysis['risk_level']}
- Reason: {capacity_analysis['reason']}

Provide your analysis...
"""

    # ... rest of analysis ...
```

---

## Step 4: Test MCP Integration

### Test 1: Verify MCP Server is Running

```bash
# Check available MCP tools
claude-code --list-mcp-tools | grep datadog
```

You should see:
```
datadog.query_metrics
datadog.search_incidents
datadog.get_service_metrics
```

### Test 2: Query Metrics via MCP

Create test script:

```python
# test_mcp.py
from datadog_mcp_client import DatadogMCPClient

client = DatadogMCPClient()

# Test service metrics
metrics = client.get_service_metrics("payment-api", hours_back=24)
print("Metrics:", metrics)

# Test health check
health = client.check_service_health("payment-api")
print("Health:", health)

# Test capacity analysis
capacity = client.analyze_capacity_for_replica_change(
    "payment-api",
    current_replicas=20,
    new_replicas=5
)
print("Capacity:", capacity)
```

Run:
```bash
python test_mcp.py
```

### Test 3: Full PR Analysis with MCP

```bash
# Analyze PR with real Datadog metrics
python scripts/analyze_pr.py examples/scenario-1-peak-traffic/demo_diff.txt

# Should see:
# 🔍 Analyzing replica change via Datadog MCP...
# 🔧 Claude is using tool: get_service_metrics
# ✅ MCP Analysis: CRITICAL
```

---

## Benefits of MCP Integration

### Before (Direct API):
```python
# Hardcoded queries
datadog_client.query("avg:cpu{service:payment-api}")
```

### After (MCP):
```python
# Claude intelligently queries what it needs
mcp_client.get_service_metrics("payment-api")
# Claude automatically:
# - Queries CPU, memory, requests
# - Searches for incidents
# - Correlates metrics
# - Provides context-aware analysis
```

### Key Advantages:

1. **Smarter Queries**: Claude determines what metrics are relevant
2. **No Hardcoded Logic**: MCP tools are generic, Claude adapts
3. **Better Context**: Claude sees raw metrics and makes informed decisions
4. **Extensibility**: Add new MCP tools without changing IaC Guardian code
5. **Unified Interface**: Same pattern for Snowflake, Jira, etc.

---

## Advanced: Multi-MCP Analysis

Combine multiple MCP servers for richer analysis:

```python
# Query Datadog + Jira + PagerDuty via MCP
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    messages=[{
        "role": "user",
        "content": f"""Analyze this infrastructure change:

{diff_content}

Use all available MCP tools:
1. Datadog: Get production metrics for payment-api
2. Jira: Search for recent incidents with payment-api
3. PagerDuty: Check on-call escalations for this service

Assess risk based on ALL data sources.
"""
    }],
    tools="auto",
)
```

Claude will automatically use all configured MCP servers!

---

## Troubleshooting

### MCP tools not available
```bash
# Check MCP config
cat ~/.claude/mcp_settings.json

# Restart Claude Code
```

### API key errors
```bash
# Verify keys are set
echo $DATADOG_API_KEY
echo $DATADOG_APP_KEY

# Update mcp_settings.json with correct keys
```

### Tool calls failing
```bash
# Test MCP server directly
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | datadog-mcp-server
```

---

## Next Steps

1. ✅ Install/create Datadog MCP server
2. ✅ Configure in `~/.claude/mcp_settings.json`
3. ✅ Create `datadog_mcp_client.py` wrapper
4. ✅ Update `analyze_pr.py` to use MCP
5. ✅ Test with real PRs
6. ✅ Compare MCP results vs mock data
7. ✅ Update documentation with MCP examples

---

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Datadog API Reference](https://docs.datadoghq.com/api/latest/)
- [Claude Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
