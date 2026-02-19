#!/usr/bin/env python3
"""
seed_demo_metrics.py — Seed 30 days of realistic IaC Guardian metrics into Datadog.

Usage:
    source .env && python scripts/seed_demo_metrics.py

Requires DATADOG_API_KEY to be set. Will print a summary on completion.
"""

import os
import sys
import random
import time
from datetime import datetime, timedelta

# Add scripts dir to path for metrics_emitter import
sys.path.insert(0, os.path.dirname(__file__))
from metrics_emitter import emit_analysis_metrics, _api_key, _submit_series


# ── Seed configuration ────────────────────────────────────────────────────────

DAYS = 30
TOTAL_PRS = 312           # avg ~10/day
FLAGGED_COUNT = 89        # 28% flag rate
CRITICAL_COUNT = 23       # of flagged
INCIDENTS_PREVENTED = 18  # subset of critical
TOTAL_COST_SAVINGS = 2_300_000  # $2.3M annual across all flagged cost issues

REPOS = [
    ("payment-api", 12),
    ("checkout", 8),
    ("data-processor", 6),
    ("user-service", 5),
    ("infra-core", 4),
    ("ml-pipeline", 3),
    ("frontend", 3),
]

SCENARIOS = [
    ("peak-traffic",   "incident",    0.55),
    ("cost-optimization", "cost",     0.30),
    ("security",       "security",    0.08),
    ("health-checks",  "reliability", 0.04),
    ("pdb",            "reliability", 0.02),
    ("replicas",       "incident",    0.01),
]

RISK_LEVELS_FOR_FLAGGED = [
    ("critical", 0.26),   # ~23 critical
    ("high",     0.38),
    ("medium",   0.36),
]


def weighted_choice(choices):
    """Pick from [(value, weight)] list."""
    total = sum(w for _, w in choices)
    r = random.random() * total
    cumulative = 0
    for value, weight in choices:
        cumulative += weight
        if r <= cumulative:
            return value
    return choices[-1][0]


def build_daily_counts(total: int, days: int) -> list[int]:
    """Build realistic daily counts — growing trend with weekday variance."""
    base = total / days
    counts = []
    for d in range(days):
        # Gentle upward trend (adoption grows ~50% over 30 days)
        trend = 1.0 + (d / days) * 0.5
        # Weekday effect: Mon-Fri ~1.2x, weekend ~0.4x
        day_of_week = d % 7
        wday = 1.2 if day_of_week < 5 else 0.4
        jitter = random.gauss(1.0, 0.15)
        counts.append(max(1, int(base * trend * wday * jitter)))

    # Scale to exact total by adjusting random days
    actual = sum(counts)
    diff = total - actual
    step = 1 if diff > 0 else -1
    indices = random.choices(range(days), k=abs(diff))
    for i in indices:
        counts[i] += step
    return counts


def seed():
    if not _api_key():
        print("❌ DATADOG_API_KEY not set. Cannot seed metrics.")
        sys.exit(1)

    print(f"🌱 Seeding {DAYS} days of IaC Guardian metrics into Datadog...")
    print(f"   Target: {TOTAL_PRS} PRs analyzed, {FLAGGED_COUNT} flagged, "
          f"{CRITICAL_COUNT} critical, ${TOTAL_COST_SAVINGS/1e6:.1f}M savings")
    print()

    now = datetime.utcnow()
    # Datadog v1 API rejects timestamps older than ~1 hour.
    # Spread all data points across the last 50 minutes so everything is accepted.
    window_seconds = 50 * 60  # 50 minutes

    daily_pr_counts = build_daily_counts(TOTAL_PRS, DAYS)
    daily_flag_counts = build_daily_counts(FLAGGED_COUNT, DAYS)

    # Repo weight list for sampling
    repo_choices = [(r, w) for r, w in REPOS]

    total_emitted = 0
    all_series = []
    pr_index = 0  # global index across all days for timestamp spreading

    for day_idx in range(DAYS):
        prs_today = daily_pr_counts[day_idx]
        flags_today = min(daily_flag_counts[day_idx], prs_today)

        for pr_i in range(prs_today):
            # Spread evenly across last 50 minutes
            offset = int((pr_index / TOTAL_PRS) * window_seconds)
            ts = int((now - timedelta(seconds=window_seconds - offset)).timestamp())
            pr_index += 1

            is_flagged = pr_i < flags_today
            repo = weighted_choice(repo_choices)

            if is_flagged:
                chosen = weighted_choice(
                    [(s, w) for s, _, w in SCENARIOS]
                )
                scenario_type = chosen
                category = next(c for s, c, _ in SCENARIOS if s == chosen)
                risk_level = weighted_choice(RISK_LEVELS_FOR_FLAGGED)
            else:
                scenario_type = weighted_choice(
                    [(s, w) for s, _, w in SCENARIOS]
                )
                category = next(c for s, c, _ in SCENARIOS if s == scenario_type)
                risk_level = "low"

            cost_savings = 0.0
            if is_flagged and category == "cost":
                # Distribute total savings across cost-flagged issues
                cost_savings = random.gauss(
                    TOTAL_COST_SAVINGS / max(1, int(FLAGGED_COUNT * 0.30)),
                    50_000
                )
                cost_savings = max(10_000, cost_savings)

            duration_ms = random.gauss(3200, 800)

            # Build series directly for batch submit
            risk = risk_level.lower()
            tags_pr = [
                f"risk_level:{risk}",
                f"scenario_type:{scenario_type}",
                f"repo:{repo}",
                "data_source:seeded",
            ]
            all_series.append({
                "metric": "iac_guardian.pr.analyzed",
                "type": "count",
                "points": [[ts, 1]],
                "tags": tags_pr,
            })

            if risk in ("critical", "high", "medium"):
                all_series.append({
                    "metric": "iac_guardian.risk.blocked",
                    "type": "count",
                    "points": [[ts, 1]],
                    "tags": [
                        f"risk_level:{risk}",
                        f"category:{category}",
                        f"repo:{repo}",
                    ],
                })

            if risk in ("critical", "high") and random.random() < 0.78:
                all_series.append({
                    "metric": "iac_guardian.incident.prevented",
                    "type": "count",
                    "points": [[ts, 1]],
                    "tags": [
                        f"scenario_type:{scenario_type}",
                        f"repo:{repo}",
                    ],
                })

            if cost_savings > 0:
                all_series.append({
                    "metric": "iac_guardian.cost.savings_annual",
                    "type": "gauge",
                    "points": [[ts, cost_savings]],
                    "tags": [f"repo:{repo}", f"scenario_type:{scenario_type}"],
                })

            all_series.append({
                "metric": "iac_guardian.analysis.duration_ms",
                "type": "gauge",
                "points": [[ts, max(500, duration_ms)]],
                "tags": ["data_source:seeded"],
            })

            total_emitted += 1

        # Flush every ~500 series to stay under API limits
        if len(all_series) >= 500:
            ok = _submit_series(all_series)
            if not ok:
                print(f"  ⚠️  Batch submit failed around day {day_idx}")
            all_series = []
            time.sleep(0.3)  # be gentle with rate limits

        if (day_idx + 1) % 10 == 0:
            print(f"  Day {day_idx + 1}/{DAYS}: {total_emitted} PRs emitted so far...")

    # Final flush
    if all_series:
        _submit_series(all_series)

    print()
    print(f"✅ Done! Emitted {total_emitted} data points across {DAYS} days.")
    print("   Open Datadog → Dashboards → 'IaC Guardian Impact' to see the data.")
    print("   Note: Metrics may take 1-2 minutes to appear in Datadog.")


if __name__ == "__main__":
    seed()
