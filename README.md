# IaC Guardian

AI-powered Infrastructure-as-Code PR reviewer that prevents production incidents before they happen.

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

## Setup

See individual scenario folders in `examples/` for demo PRs.

---

Built for Datadog AI PM Hackathon 2026
