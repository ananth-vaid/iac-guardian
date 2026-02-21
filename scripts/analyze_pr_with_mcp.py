#!/usr/bin/env python3
"""
Enhanced PR Analysis using Datadog MCP Server
Queries real Datadog metrics via Claude's MCP integration
"""

import os
import sys
import anthropic
from pathlib import Path

def analyze_pr_with_datadog_mcp(diff_file: str, pr_number: str = None):
    """
    Analyze infrastructure PR using Claude + Datadog MCP tools

    This leverages the official Datadog MCP server to query real metrics
    """

    # Load diff content
    with open(diff_file, 'r') as f:
        diff_content = f.read()

    # Extract service name from diff
    service_name = extract_service_name(diff_content)

    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print(f"🔍 Analyzing PR with Datadog MCP integration...")
    print(f"   Service: {service_name}")

    # Create analysis prompt that leverages MCP tools
    messages = [{
        "role": "user",
        "content": f"""You are IaC Guardian, an AI-powered infrastructure reviewer with access to Datadog production metrics.

**Infrastructure Change:**
```diff
{diff_content}
```

**Your Task:**
1. Use the Datadog MCP tools to query REAL production metrics for service: **{service_name}**
2. Query the last 7 days of:
   - CPU usage (average and peak)
   - Memory usage (average and peak)
   - Request rates
   - Any incidents or alerts
3. Analyze if this infrastructure change is risky based on REAL data
4. Provide a concise risk assessment

**Output Format:**
## 🚨 Risk Level: [CRITICAL/HIGH/MEDIUM/LOW]

**Why This is Risky:**
[1-2 sentences based on ACTUAL Datadog metrics you queried]

**Action:**
- [Specific recommendation based on real data]
- [Another recommendation]

**📊 Datadog Metrics Referenced:**
- [List the actual metrics you found]
"""
    }]

    # Call Claude with MCP tools enabled
    print("🤖 Querying Claude with Datadog MCP tools enabled...")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=messages,
    )

    # Process response and handle tool calls
    analysis_text = ""
    tool_uses = []

    for block in response.content:
        if block.type == "text":
            analysis_text += block.text
        elif block.type == "tool_use":
            tool_uses.append({
                "name": block.name,
                "input": block.input
            })
            print(f"   ✓ Used MCP tool: {block.name}")

    # If Claude made tool calls, show what it queried
    if tool_uses:
        print(f"\n📊 Datadog Queries Made:")
        for tool in tool_uses:
            print(f"   - {tool['name']}: {tool['input']}")
    else:
        print("   ⚠️  No Datadog MCP tools were used (check MCP configuration)")

    return analysis_text


def extract_service_name(diff_content: str) -> str:
    """Extract service name from diff content"""

    # Try to find service name in various ways
    import re

    # Look for common patterns
    patterns = [
        r'name:\s*([a-zA-Z0-9\-]+)',  # K8s metadata.name
        r'service[:\s]+([a-zA-Z0-9\-]+)',  # service: payment-api
        r'/([a-zA-Z0-9\-]+)\.yaml',  # filename
        r'/([a-zA-Z0-9\-]+)-deployment',  # deployment name
    ]

    for pattern in patterns:
        match = re.search(pattern, diff_content)
        if match:
            service = match.group(1)
            # Skip generic names
            if service not in ['Deployment', 'Service', 'ConfigMap', 'deployment']:
                return service

    # Default fallback
    return "unknown-service"


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_pr_with_mcp.py <diff_file> [pr_number]")
        sys.exit(1)

    diff_file = sys.argv[1]
    pr_number = sys.argv[2] if len(sys.argv) > 2 else "local"

    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    # Run analysis
    print("=" * 80)
    print("🛡️  IaC GUARDIAN - Enhanced with Datadog MCP")
    print("=" * 80)
    print()

    analysis = analyze_pr_with_datadog_mcp(diff_file, pr_number)

    print()
    print("=" * 80)
    print("📋 ANALYSIS RESULTS")
    print("=" * 80)
    print()
    print(analysis)
    print()


if __name__ == "__main__":
    main()
