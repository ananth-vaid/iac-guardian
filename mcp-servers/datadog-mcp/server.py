#!/usr/bin/env python3
"""
Simple Datadog MCP Server for IaC Guardian
Provides Claude with tools to query Datadog metrics and incidents
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

# MCP SDK imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Datadog imports
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v2.api.incidents_api import IncidentsApi

# Initialize Datadog client
DD_API_KEY = os.getenv("DATADOG_API_KEY")
DD_APP_KEY = os.getenv("DATADOG_APP_KEY")

if not DD_API_KEY or not DD_APP_KEY:
    print("Warning: DATADOG_API_KEY or DATADOG_APP_KEY not set", file=sys.stderr)

configuration = Configuration()
configuration.api_key["apiKeyAuth"] = DD_API_KEY
configuration.api_key["appKeyAuth"] = DD_APP_KEY

# Create server instance
server = Server("datadog-mcp-server")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Datadog tools"""
    return [
        Tool(
            name="query_datadog_metrics",
            description="""Query Datadog metrics for a specific service.

Examples:
- K8s replicas: query='avg:kubernetes_state.deployment.replicas_available{kube_deployment:payment-api}'
- CPU usage: query='avg:kubernetes.cpu.usage.total{kube_deployment:payment-api}'
- Restarts: query='sum:kubernetes.containers.restarts{kube_deployment:payment-api}'
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Datadog metric query string",
                    },
                    "hours_back": {
                        "type": "integer",
                        "description": "How many hours of data to fetch",
                        "default": 24,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_deployment_replicas",
            description="""Get current and historical replica counts for a Kubernetes deployment.

Queries kubernetes_state.deployment.replicas_available to understand current scale
and whether reducing replicas would be safe.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {
                        "type": "string",
                        "description": "Kubernetes deployment name (e.g., 'payment-api')",
                    },
                    "hours_back": {
                        "type": "integer",
                        "description": "How many hours of data to analyze",
                        "default": 168,
                    },
                },
                "required": ["deployment_name"],
            },
        ),
        Tool(
            name="get_deployment_health",
            description="""Get health signals for a Kubernetes deployment.

Returns liveness probe failures, container restarts, and CPU usage.
Use this to assess if a deployment has existing issues or instability.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {
                        "type": "string",
                        "description": "Kubernetes deployment name (e.g., 'api-server')",
                    },
                    "hours_back": {
                        "type": "integer",
                        "description": "How many hours of data to analyze",
                        "default": 24,
                    },
                },
                "required": ["deployment_name"],
            },
        ),
        Tool(
            name="get_pdb_status",
            description="""Get PodDisruptionBudget status for a Kubernetes deployment.

Returns disruptions_allowed and pods_desired to assess HA readiness.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {
                        "type": "string",
                        "description": "Kubernetes deployment name",
                    },
                },
                "required": ["deployment_name"],
            },
        ),
        Tool(
            name="get_hpa_status",
            description="""Get HorizontalPodAutoscaler status for a Kubernetes deployment.

Returns current vs desired replicas to understand autoscaling behavior.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_name": {
                        "type": "string",
                        "description": "Kubernetes deployment name",
                    },
                },
                "required": ["deployment_name"],
            },
        ),
        Tool(
            name="get_service_health",
            description="""Get comprehensive health metrics for a service.

Returns K8s CPU, container restarts, and request errors.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service (e.g., 'payment-api')",
                    },
                    "hours_back": {
                        "type": "integer",
                        "description": "How many hours of data to analyze",
                        "default": 24,
                    },
                },
                "required": ["service_name"],
            },
        ),
        Tool(
            name="search_datadog_incidents",
            description="""Search for Datadog incidents related to a service or query.

Returns list of incidents with severity, status, and timestamps.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'service:payment-api' or 'env:production')",
                    },
                    "days_back": {
                        "type": "integer",
                        "description": "How many days back to search",
                        "default": 30,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="analyze_capacity_risk",
            description="""Analyze if a replica/capacity change is safe based on historical metrics.

Queries peak CPU and replica counts to determine if reducing capacity would cause issues.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Service name",
                    },
                    "current_replicas": {
                        "type": "integer",
                        "description": "Current number of replicas",
                    },
                    "proposed_replicas": {
                        "type": "integer",
                        "description": "Proposed number of replicas",
                    },
                },
                "required": ["service_name", "current_replicas", "proposed_replicas"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool execution"""

    try:
        if name == "query_datadog_metrics":
            result = await query_metrics(
                arguments["query"],
                arguments.get("hours_back", 24)
            )
            return [TextContent(type="text", text=result)]

        elif name == "get_deployment_replicas":
            result = await get_deployment_replicas(
                arguments["deployment_name"],
                arguments.get("hours_back", 168)
            )
            return [TextContent(type="text", text=result)]

        elif name == "get_deployment_health":
            result = await get_deployment_health(
                arguments["deployment_name"],
                arguments.get("hours_back", 24)
            )
            return [TextContent(type="text", text=result)]

        elif name == "get_pdb_status":
            result = await get_pdb_status(arguments["deployment_name"])
            return [TextContent(type="text", text=result)]

        elif name == "get_hpa_status":
            result = await get_hpa_status(arguments["deployment_name"])
            return [TextContent(type="text", text=result)]

        elif name == "get_service_health":
            result = await get_service_health(
                arguments["service_name"],
                arguments.get("hours_back", 24)
            )
            return [TextContent(type="text", text=result)]

        elif name == "search_datadog_incidents":
            result = await search_incidents(
                arguments["query"],
                arguments.get("days_back", 30)
            )
            return [TextContent(type="text", text=result)]

        elif name == "analyze_capacity_risk":
            result = await analyze_capacity_risk(
                arguments["service_name"],
                arguments["current_replicas"],
                arguments["proposed_replicas"]
            )
            return [TextContent(type="text", text=result)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def query_metrics(query: str, hours_back: int) -> str:
    """Query Datadog metrics"""
    try:
        with ApiClient(configuration) as api_client:
            api_instance = MetricsApi(api_client)

            now = int(datetime.now().timestamp())
            from_time = now - (hours_back * 3600)

            response = api_instance.query_metrics(
                _from=from_time,
                to=now,
                query=query
            )

            # Format response
            if response.series:
                series = response.series[0]
                points = series.pointlist

                # Calculate stats
                values = [p[1] for p in points if p[1] is not None]
                if values:
                    avg = sum(values) / len(values)
                    max_val = max(values)
                    min_val = min(values)

                    return f"""Metric Query Results:
Query: {query}
Time Range: Last {hours_back} hours
Points: {len(points)}

Statistics:
- Average: {avg:.2f}
- Maximum: {max_val:.2f}
- Minimum: {min_val:.2f}

Recent Values (last 5):
{chr(10).join([f"  {datetime.fromtimestamp(p[0]/1000).strftime('%Y-%m-%d %H:%M')}: {p[1]:.2f}" for p in points[-5:]])}
"""
                else:
                    return f"No data points found for query: {query}"
            else:
                return f"No series data returned for query: {query}"

    except Exception as e:
        # Fallback to mock data for demo
        return f"""⚠️  Using mock data (API error: {str(e)})

Metric Query Results (MOCK):
Query: {query}
Time Range: Last {hours_back} hours

Statistics:
- Average: 65.3
- Maximum: 92.1
- Minimum: 42.8

Note: Configure DATADOG_API_KEY for real data
"""


async def get_deployment_replicas(deployment_name: str, hours_back: int) -> str:
    """Get current and historical replica counts for a K8s deployment"""
    replicas_result = await query_metrics(
        f"avg:kubernetes_state.deployment.replicas_available{{kube_deployment:{deployment_name}}}",
        hours_back
    )
    unavailable_result = await query_metrics(
        f"avg:kubernetes_state.deployment.replicas_unavailable{{kube_deployment:{deployment_name}}}",
        min(hours_back, 24)
    )

    output = f"Deployment Replicas: {deployment_name}\n"
    output += "=" * 60 + "\n\n"
    output += f"### Available Replicas (last {hours_back}h)\n{replicas_result}\n"
    output += f"### Unavailable Replicas (last 24h)\n{unavailable_result}\n"
    return output


async def get_deployment_health(deployment_name: str, hours_back: int) -> str:
    """Get health signals for a K8s deployment"""
    queries = {
        "CPU Usage": f"avg:kubernetes.cpu.usage.total{{kube_deployment:{deployment_name}}}",
        "Container Restarts": f"sum:kubernetes.containers.restarts{{kube_deployment:{deployment_name}}}",
        "Liveness Probe Failures": f"sum:kubernetes.liveness_probe.failure.total{{kube_deployment:{deployment_name}}}",
    }

    results = {}
    for metric_name, query in queries.items():
        results[metric_name] = await query_metrics(query, hours_back)

    output = f"Deployment Health: {deployment_name}\n"
    output += f"Time Range: Last {hours_back} hours\n"
    output += "=" * 60 + "\n\n"
    for metric_name, result in results.items():
        output += f"### {metric_name}\n{result}\n\n"
    return output


async def get_pdb_status(deployment_name: str) -> str:
    """Get PodDisruptionBudget status for a K8s deployment"""
    disruptions = await query_metrics(
        f"avg:kubernetes_state.pdb.disruptions_allowed{{kube_deployment:{deployment_name}}}",
        hours_back=1
    )
    pods_desired = await query_metrics(
        f"avg:kubernetes_state.pdb.pods_desired{{kube_deployment:{deployment_name}}}",
        hours_back=1
    )

    output = f"PodDisruptionBudget Status: {deployment_name}\n"
    output += "=" * 60 + "\n\n"
    output += f"### Disruptions Allowed\n{disruptions}\n"
    output += f"### Pods Desired\n{pods_desired}\n"
    return output


async def get_hpa_status(deployment_name: str) -> str:
    """Get HorizontalPodAutoscaler status for a K8s deployment"""
    current = await query_metrics(
        f"avg:kubernetes_state.hpa.current_replicas{{kube_deployment:{deployment_name}}}",
        hours_back=24
    )
    desired = await query_metrics(
        f"avg:kubernetes_state.hpa.desired_replicas{{kube_deployment:{deployment_name}}}",
        hours_back=24
    )

    output = f"HPA Status: {deployment_name}\n"
    output += "=" * 60 + "\n\n"
    output += f"### Current Replicas\n{current}\n"
    output += f"### Desired Replicas\n{desired}\n"
    return output


async def get_service_health(service_name: str, hours_back: int) -> str:
    """Get comprehensive service health metrics"""

    queries = {
        "CPU Usage": f"avg:kubernetes.cpu.usage.total{{kube_deployment:{service_name}}}",
        "Container Restarts": f"sum:kubernetes.containers.restarts{{kube_deployment:{service_name}}}",
        "Requests": f"sum:trace.http.request.hits{{service:{service_name}}}.as_count()",
        "Errors": f"sum:trace.http.errors{{service:{service_name}}}.as_count()",
    }

    results = {}
    for metric_name, query in queries.items():
        result = await query_metrics(query, hours_back)
        results[metric_name] = result

    # Combine results
    output = f"Service Health Report: {service_name}\n"
    output += f"Time Range: Last {hours_back} hours\n"
    output += "=" * 60 + "\n\n"

    for metric_name, result in results.items():
        output += f"### {metric_name}\n{result}\n\n"

    return output


async def search_incidents(query: str, days_back: int) -> str:
    """Search for incidents"""
    try:
        with ApiClient(configuration) as api_client:
            api_instance = IncidentsApi(api_client)

            # Calculate time range
            now = datetime.now()
            from_time = now - timedelta(days=days_back)

            # Search incidents
            response = api_instance.list_incidents(
                include="incident_severity,incident_commander",
                filter_query=query,
                filter_start_date=from_time.isoformat(),
                filter_end_date=now.isoformat(),
            )

            if response.data:
                output = f"Found {len(response.data)} incidents for query: {query}\n\n"
                for incident in response.data[:10]:  # Limit to 10
                    output += f"""
Incident: {incident.attributes.title}
Severity: {incident.attributes.severity or 'Unknown'}
Status: {incident.attributes.status}
Created: {incident.attributes.created}
"""
                return output
            else:
                return f"No incidents found for query: {query}"

    except Exception as e:
        return f"""⚠️  Using mock data (API error: {str(e)})

Incident Search Results (MOCK):
Query: {query}
Found: 2 incidents

1. Peak Traffic Overload - payment-api
   Severity: SEV-2
   Status: Resolved
   Created: 2026-02-15

2. Memory Leak Detected
   Severity: SEV-3
   Status: Resolved
   Created: 2026-02-10

Note: Configure DATADOG_API_KEY for real data
"""


async def analyze_capacity_risk(
    service_name: str,
    current_replicas: int,
    proposed_replicas: int
) -> str:
    """Analyze if capacity change is safe"""

    # Query last 7 days of peak metrics
    cpu_result = await query_metrics(
        f"max:kubernetes.cpu.usage.total{{kube_deployment:{service_name}}}",
        hours_back=168  # 7 days
    )

    requests_result = await query_metrics(
        f"sum:trace.http.request.hits{{service:{service_name}}}.as_count()",
        hours_back=168
    )

    # Simple risk assessment
    risk_level = "UNKNOWN"
    reason = "Unable to determine from available metrics"

    if "Maximum: " in cpu_result:
        # Parse max CPU
        max_cpu_line = [line for line in cpu_result.split('\n') if 'Maximum:' in line][0]
        max_cpu = float(max_cpu_line.split(':')[1].strip())

        # Calculate per-replica CPU
        cpu_per_replica = max_cpu / current_replicas

        # Project new CPU usage
        projected_cpu = cpu_per_replica * proposed_replicas

        if proposed_replicas < current_replicas:
            # Reducing capacity
            capacity_ratio = current_replicas / proposed_replicas

            if projected_cpu > 90:
                risk_level = "CRITICAL"
                reason = f"Projected CPU would reach {projected_cpu:.0f}% (dangerous!)"
            elif projected_cpu > 75:
                risk_level = "HIGH"
                reason = f"Projected CPU: {projected_cpu:.0f}% (risky during peaks)"
            elif capacity_ratio > 2:
                risk_level = "MEDIUM"
                reason = f"Reducing by {capacity_ratio:.1f}x may impact performance"
            else:
                risk_level = "LOW"
                reason = f"Projected CPU: {projected_cpu:.0f}% (acceptable)"

    return f"""Capacity Risk Analysis: {service_name}

Change: {current_replicas} → {proposed_replicas} replicas

Risk Assessment: {risk_level}
Reason: {reason}

Metrics Analyzed:
{cpu_result}

Recommendation:
{"⛔ DO NOT MERGE - Capacity too low" if risk_level == "CRITICAL" else "✓ Safe to proceed" if risk_level == "LOW" else "⚠️ Proceed with caution"}
"""


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="datadog-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
