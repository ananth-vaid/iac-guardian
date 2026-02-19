"""
metrics_emitter.py — Emit IaC Guardian custom metrics to Datadog.

Submits iac_guardian.* series via POST /api/v1/series.
Silent no-op if DATADOG_API_KEY is not set.
"""

import os
import time
import requests


def _api_key() -> str | None:
    return os.getenv("DATADOG_API_KEY")


def _site() -> str:
    return os.getenv("DATADOG_SITE", "datadoghq.com")


def _submit_series(series: list[dict]) -> bool:
    """POST a list of metric series to Datadog. Returns True on success."""
    api_key = _api_key()
    if not api_key:
        return False

    url = f"https://api.{_site()}/api/v1/series"
    headers = {
        "Content-Type": "application/json",
        "DD-API-KEY": api_key,
    }

    try:
        resp = requests.post(url, json={"series": series}, headers=headers, timeout=5)
        return resp.status_code == 202
    except Exception:
        return False


def emit_analysis_metrics(
    *,
    risk_level: str,
    scenario_type: str,
    repo: str = "unknown",
    data_source: str = "mock",
    category: str = "incident",
    cost_savings_annual: float = 0.0,
    duration_ms: float = 0.0,
    timestamp: int | None = None,
) -> None:
    """
    Emit one analysis run's worth of metrics to Datadog.

    Args:
        risk_level:          CRITICAL / HIGH / MEDIUM / LOW
        scenario_type:       e.g. "peak-traffic", "cost-optimization"
        repo:                GitHub repo name
        data_source:         "mcp" | "mock"
        category:            "incident" | "cost" | "security" | "reliability"
        cost_savings_annual: Estimated annual USD savings (for cost scenarios)
        duration_ms:         Analysis wall-clock time in milliseconds
        timestamp:           Unix epoch; defaults to now
    """
    if not _api_key():
        return

    ts = timestamp or int(time.time())
    risk = risk_level.lower()

    series: list[dict] = [
        {
            "metric": "iac_guardian.pr.analyzed",
            "type": "count",
            "points": [[ts, 1]],
            "tags": [
                f"risk_level:{risk}",
                f"scenario_type:{scenario_type}",
                f"repo:{repo}",
                f"data_source:{data_source}",
            ],
        },
    ]

    # Flagged = anything above LOW
    if risk in ("critical", "high", "medium"):
        series.append({
            "metric": "iac_guardian.risk.blocked",
            "type": "count",
            "points": [[ts, 1]],
            "tags": [
                f"risk_level:{risk}",
                f"category:{category}",
                f"repo:{repo}",
            ],
        })

    # Incident prevented = CRITICAL or HIGH
    if risk in ("critical", "high"):
        series.append({
            "metric": "iac_guardian.incident.prevented",
            "type": "count",
            "points": [[ts, 1]],
            "tags": [
                f"scenario_type:{scenario_type}",
                f"repo:{repo}",
            ],
        })

    # Cost savings gauge (only emit if non-zero)
    if cost_savings_annual > 0:
        series.append({
            "metric": "iac_guardian.cost.savings_annual",
            "type": "gauge",
            "points": [[ts, cost_savings_annual]],
            "tags": [
                f"repo:{repo}",
                f"scenario_type:{scenario_type}",
            ],
        })

    # Analysis duration
    if duration_ms > 0:
        series.append({
            "metric": "iac_guardian.analysis.duration_ms",
            "type": "gauge",
            "points": [[ts, duration_ms]],
            "tags": [f"data_source:{data_source}"],
        })

    _submit_series(series)


def infer_category(scenario_type: str, analysis_text: str = "") -> str:
    """Guess category tag from scenario type or analysis text."""
    s = scenario_type.lower()
    a = analysis_text.lower()
    if "security" in s or "ssh" in a or "cidr" in a:
        return "security"
    if "cost" in s or "over-provision" in a or "savings" in a:
        return "cost"
    if "pdb" in s or "health" in s or "probe" in s or "reliability" in a:
        return "reliability"
    return "incident"


def infer_cost_savings(analysis_text: str) -> float:
    """Extract annual cost savings estimate from analysis text (USD)."""
    import re
    # Look for patterns like "$1.2M", "$450K", "$120,000"
    m = re.search(r'\$([0-9,]+(?:\.[0-9]+)?)\s*([MmKk]?)', analysis_text)
    if not m:
        return 0.0
    value = float(m.group(1).replace(",", ""))
    suffix = m.group(2).upper()
    if suffix == "M":
        value *= 1_000_000
    elif suffix == "K":
        value *= 1_000
    return value
