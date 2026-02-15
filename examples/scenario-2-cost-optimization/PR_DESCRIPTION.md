# Scale up data processing cluster

## Changes
- Increase `data_processor` instances: 5 → 10
- Upgrade instance type: `c5.2xlarge` → `c5.4xlarge`

## Rationale
Preparing for Q1 data pipeline expansion. Need more processing capacity for new analytics workloads.

## Cost Impact
- Current: 5x c5.2xlarge = ~$1,680/month
- New: 10x c5.4xlarge = ~$6,720/month
- Increase: +$5,040/month

---

**Expected IaC Guardian Analysis:**
This PR should trigger COST OPTIMIZATION warning because:
1. Datadog shows current 5 instances run at 15% CPU utilization
2. Over-provisioning by ~3x for the stated workload
3. Recommendation: Use 4x c5.2xlarge instead (same capacity, saves $3k/month)
