# Datadog Dashboard Setup for IaC Guardian

## Quick Import

### Option 1: Import via Datadog UI (Recommended)
1. Open Datadog: https://app.datadoghq.com/dashboard/lists
2. Click **New Dashboard** → **Import Dashboard JSON**
3. Upload `datadog-dashboard.json`
4. Click **Import**

### Option 2: Import via API
```bash
curl -X POST "https://api.datadoghq.com/api/v1/dashboard" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DATADOG_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DATADOG_APP_KEY}" \
  -d @datadog-dashboard.json
```

---

## Dashboard Overview

The dashboard visualizes 12 key metrics across 4 categories:

### 1. Overview Metrics (Top Row)
- **PRs Analyzed**: Total pull requests reviewed in last 7 days
- **Critical Risks Blocked**: Count of critical-severity issues caught
- **Cost Savings**: Annual cost savings from optimization recommendations
- **Avg Response Time**: Mean analysis duration in seconds

### 2. Trends & Distribution
- **PRs Analyzed Over Time**: Daily PR analysis volume
- **Risk Distribution**: Breakdown by severity (Critical/High/Medium/Low)

### 3. Service & Scenario Insights
- **Top Services with Issues**: Which services have most infrastructure risks
- **Scenario Detection Breakdown**: Most common risk patterns detected
- **Auto-Fix Generation Rate**: % of risks with automated fixes

### 4. Cost & Performance
- **Cost Savings by Type**: Right-sizing, spot instances, auto-scaling savings
- **Analysis Performance**: p50/p95/p99 latency percentiles
- **Recent Events**: Real-time stream of PR analysis events

---

## Emitting Metrics from IaC Guardian

### Step 1: Install Datadog Python Client

```bash
pip install datadog-api-client
```

### Step 2: Create Metrics Emitter Module

Create `scripts/datadog_metrics_emitter.py`:

```python
#!/usr/bin/env python3
"""
Datadog Metrics Emitter for IaC Guardian
Sends custom metrics to Datadog for dashboard visualization
"""

import os
import time
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries

class IaCGuardianMetrics:
    def __init__(self):
        configuration = Configuration()
        configuration.api_key["apiKeyAuth"] = os.getenv("DATADOG_API_KEY")
        configuration.api_key["appKeyAuth"] = os.getenv("DATADOG_APP_KEY")
        self.api_client = ApiClient(configuration)
        self.metrics_api = MetricsApi(self.api_client)

    def emit_pr_analyzed(self, pr_number: str, service: str):
        """Emit metric when PR is analyzed"""
        self._submit_count_metric(
            metric_name="iac_guardian.pr.analyzed",
            value=1,
            tags=[f"pr:{pr_number}", f"service:{service}", "tool:iac_guardian"]
        )

    def emit_risk_detected(self, risk_level: str, service: str, scenario: str):
        """Emit metric when risk is detected"""
        self._submit_count_metric(
            metric_name="iac_guardian.risk.detected",
            value=1,
            tags=[
                f"risk_level:{risk_level.lower()}",
                f"service:{service}",
                f"scenario_name:{scenario}",
                "tool:iac_guardian"
            ]
        )

    def emit_scenario_detected(self, scenario_name: str, service: str):
        """Emit metric when scenario is detected"""
        self._submit_count_metric(
            metric_name="iac_guardian.scenario.detected",
            value=1,
            tags=[f"scenario_name:{scenario_name}", f"service:{service}", "tool:iac_guardian"]
        )

    def emit_fix_generated(self, fix_type: str, service: str):
        """Emit metric when auto-fix is generated"""
        self._submit_count_metric(
            metric_name="iac_guardian.fix.generated",
            value=1,
            tags=[f"fix_type:{fix_type}", f"service:{service}", "tool:iac_guardian"]
        )

    def emit_cost_savings(self, amount: float, optimization_type: str, service: str):
        """Emit cost savings metric"""
        self._submit_gauge_metric(
            metric_name="iac_guardian.cost.savings",
            value=amount,
            tags=[
                f"optimization_type:{optimization_type}",
                f"service:{service}",
                "tool:iac_guardian"
            ]
        )

    def emit_analysis_duration(self, duration_seconds: float, service: str):
        """Emit analysis duration metric"""
        self._submit_gauge_metric(
            metric_name="iac_guardian.analysis.duration",
            value=duration_seconds,
            tags=[f"service:{service}", "tool:iac_guardian"]
        )

    def _submit_count_metric(self, metric_name: str, value: int, tags: list):
        """Submit a count metric to Datadog"""
        try:
            body = MetricPayload(
                series=[
                    MetricSeries(
                        metric=metric_name,
                        type=MetricIntakeType.COUNT,
                        points=[
                            MetricPoint(
                                timestamp=int(time.time()),
                                value=float(value),
                            ),
                        ],
                        tags=tags,
                    ),
                ],
            )
            self.metrics_api.submit_metrics(body=body)
        except Exception as e:
            # Don't fail analysis if metrics fail
            print(f"Warning: Failed to emit metric {metric_name}: {e}")

    def _submit_gauge_metric(self, metric_name: str, value: float, tags: list):
        """Submit a gauge metric to Datadog"""
        try:
            body = MetricPayload(
                series=[
                    MetricSeries(
                        metric=metric_name,
                        type=MetricIntakeType.GAUGE,
                        points=[
                            MetricPoint(
                                timestamp=int(time.time()),
                                value=value,
                            ),
                        ],
                        tags=tags,
                    ),
                ],
            )
            self.metrics_api.submit_metrics(body=body)
        except Exception as e:
            print(f"Warning: Failed to emit metric {metric_name}: {e}")

    def emit_event(self, title: str, text: str, alert_type: str, service: str, pr_url: str = None):
        """Emit event to Datadog event stream"""
        # Using DogStatsD for events (simpler)
        from datadog import initialize, api

        initialize(
            api_key=os.getenv("DATADOG_API_KEY"),
            app_key=os.getenv("DATADOG_APP_KEY")
        )

        tags = [f"service:{service}", "tool:iac_guardian"]
        if pr_url:
            tags.append(f"pr_url:{pr_url}")

        api.Event.create(
            title=title,
            text=text,
            alert_type=alert_type,  # "error", "warning", "info", "success"
            tags=tags
        )
```

### Step 3: Integrate into analyze_pr.py

Add to `scripts/analyze_pr.py`:

```python
from datadog_metrics_emitter import IaCGuardianMetrics
import time

def analyze_pr(diff_file, pr_number=None, service=None):
    start_time = time.time()
    metrics = IaCGuardianMetrics()

    # Extract service name if not provided
    if not service:
        service = extract_service_from_diff(diff_content)

    # Emit PR analyzed metric
    metrics.emit_pr_analyzed(pr_number or "local", service)

    # ... existing analysis code ...

    # After risk detection
    risk_level = extract_risk_level(analysis)
    metrics.emit_risk_detected(risk_level, service, scenario_name)

    # After scenario detection
    metrics.emit_scenario_detected(scenario_name, service)

    # After fix generation
    if fix_generated:
        metrics.emit_fix_generated(fix_type, service)

    # Emit cost savings if applicable
    if cost_savings > 0:
        metrics.emit_cost_savings(cost_savings, "rightsizing", service)

    # Emit analysis duration
    duration = time.time() - start_time
    metrics.emit_analysis_duration(duration, service)

    # Emit event for critical risks
    if risk_level == "CRITICAL":
        metrics.emit_event(
            title=f"🚨 Critical Risk Detected in {service}",
            text=f"IaC Guardian detected critical infrastructure risk in PR #{pr_number}",
            alert_type="error",
            service=service,
            pr_url=f"https://github.com/ananth-vaid/iac-guardian/pull/{pr_number}"
        )
```

### Step 4: Add to GitHub Actions Workflow

Update `.github/workflows/iac-review.yml`:

```yaml
- name: Analyze PR
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    DATADOG_API_KEY: ${{ secrets.DATADOG_API_KEY }}
    DATADOG_APP_KEY: ${{ secrets.DATADOG_APP_KEY }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python scripts/analyze_pr.py \
      --pr-number ${{ github.event.pull_request.number }} \
      --service $(basename $(dirname ${{ github.event.pull_request.head.ref }}))
```

---

## Demo Mode: Generate Sample Metrics

For hackathon demo without real metrics, use this script:

```bash
#!/bin/bash
# scripts/generate_demo_metrics.py

from datadog_metrics_emitter import IaCGuardianMetrics
import random
import time

metrics = IaCGuardianMetrics()

# Simulate 30 days of data
for day in range(30):
    # Random PRs per day (5-15)
    prs_today = random.randint(5, 15)

    for pr in range(prs_today):
        service = random.choice(["payment-api", "user-service", "auth-service", "billing-api"])
        scenario = random.choice([
            "peak_traffic_risk",
            "cost_optimization",
            "missing_health_checks",
            "missing_pdb",
            "insufficient_replicas",
            "security_group_open"
        ])
        risk = random.choice(["critical", "high", "medium", "low"])

        # Emit metrics
        metrics.emit_pr_analyzed(f"pr-{day}-{pr}", service)
        metrics.emit_risk_detected(risk, service, scenario)
        metrics.emit_scenario_detected(scenario, service)

        # Some get fixes
        if random.random() > 0.3:
            metrics.emit_fix_generated("auto_fix", service)

        # Cost savings
        if scenario == "cost_optimization":
            savings = random.randint(50000, 300000)
            metrics.emit_cost_savings(savings, "rightsizing", service)

        # Duration
        duration = random.uniform(8, 25)
        metrics.emit_analysis_duration(duration, service)

    print(f"Generated metrics for day {day+1}/30")
    time.sleep(0.1)  # Avoid rate limiting

print("✅ Demo metrics generated! Check your dashboard.")
```

Run it:
```bash
python scripts/generate_demo_metrics.py
```

---

## Customization

### Add Custom Widgets

Edit `datadog-dashboard.json` to add:

**SLO Widget** (% of PRs reviewed within 30s):
```json
{
  "definition": {
    "title": "Analysis SLO",
    "type": "slo",
    "slo_id": "iac_guardian_slo_id"
  }
}
```

**APM Trace Widget** (if integrated with APM):
```json
{
  "definition": {
    "title": "Analysis Traces",
    "type": "trace_service",
    "service": "iac-guardian"
  }
}
```

### Template Variables

Use dashboard filters:
- Filter by `$service` to see metrics for specific microservice
- Filter by `$risk_level` to focus on critical/high risks only

---

## Alerting

### Create Monitors

**Critical Risk Alert:**
```bash
curl -X POST "https://api.datadoghq.com/api/v1/monitor" \
-H "DD-API-KEY: ${DATADOG_API_KEY}" \
-H "DD-APPLICATION-KEY: ${DATADOG_APP_KEY}" \
-d '{
  "type": "metric alert",
  "query": "sum(last_5m):sum:iac_guardian.risk.detected{risk_level:critical}.as_count() > 5",
  "name": "IaC Guardian: High volume of critical risks",
  "message": "{{#is_alert}}More than 5 critical infrastructure risks detected in 5 minutes!{{/is_alert}}",
  "tags": ["team:sre", "tool:iac_guardian"]
}'
```

**Slow Analysis Alert:**
```bash
curl -X POST "https://api.datadoghq.com/api/v1/monitor" \
-H "DD-API-KEY: ${DATADOG_API_KEY}" \
-H "DD-APPLICATION-KEY: ${DATADOG_APP_KEY}" \
-d '{
  "type": "metric alert",
  "query": "avg(last_5m):avg:iac_guardian.analysis.duration{*} > 30",
  "name": "IaC Guardian: Slow analysis performance",
  "message": "Analysis taking longer than 30 seconds on average",
  "tags": ["team:sre", "tool:iac_guardian"]
}'
```

---

## Next Steps

1. ✅ Import dashboard JSON to Datadog
2. ✅ Install `datadog-api-client` package
3. ✅ Create `datadog_metrics_emitter.py`
4. ✅ Integrate into `analyze_pr.py`
5. ✅ Add secrets to GitHub Actions
6. ✅ Run demo metrics generator
7. ✅ Create monitors for critical alerts
8. ✅ Share dashboard link with stakeholders

---

## Troubleshooting

**Dashboard shows no data:**
- Check API keys are set: `echo $DATADOG_API_KEY`
- Verify metrics emitter is being called
- Check Datadog Metrics Explorer for `iac_guardian.*` metrics

**Metrics delayed:**
- Custom metrics can take 2-3 minutes to appear
- Use `datadog-agent status` to check local agent

**Import fails:**
- Ensure JSON is valid: `jq . datadog-dashboard.json`
- Check API permissions include dashboard creation

---

## Resources

- [Datadog Custom Metrics Guide](https://docs.datadoghq.com/metrics/custom_metrics/)
- [Dashboard API Reference](https://docs.datadoghq.com/api/latest/dashboards/)
- [Python Client Documentation](https://github.com/DataDog/datadog-api-client-python)
