# Example GitHub PR Comment - Scenario 2: Cost Optimization

---

## 🛡️ IaC Guardian Analysis

### ⚠️ Risk Level: WARNING (Over-Provisioning)

---

## Why This is Wasteful

This PR scales `data-processor` infrastructure from **5x c5.2xlarge** to **10x c5.4xlarge** - that's **13x your current capacity needs**. Here's what production metrics show:

**Current Production Utilization:**
- 5x c5.2xlarge instances (8 vCPU, 16GB each)
- **Average CPU: 15%** (should target 50-70%)
- **Average Memory: 22%** (significantly underutilized)
- **Current cost: $4,032/month**

**Proposed Change:**
- 10x c5.4xlarge instances (16 vCPU, 32GB each)
- Total capacity: **13x current actual usage**
- **Projected cost: $34,272/month** (8.5x increase!)
- **Annual waste: $362,880** vs current setup

**Even Current Setup is Over-Provisioned:**
- You're using <20% of what you already have
- Could run same workload on 3x c5.2xlarge safely

---

## What To Do

### ❌ Do NOT merge this PR as-is

This change is **massively over-provisioned** for your actual workload.

### ✅ Recommended Alternative #1: Right-Size Current Setup

**Scale down to actual needs:**

```hcl
resource "aws_instance" "data_processor" {
  count         = 3          # Down from 5 (still 50% headroom)
  instance_type = "c5.2xlarge"  # Keep current instance type

  # ... rest of config
}
```

**Benefits:**
- ✅ Handles current workload at 40-50% utilization (healthy)
- ✅ 50% headroom for growth
- ✅ Saves **$1,612/month** vs current ($19k/year)
- ✅ Saves **$30,660/month** vs proposed ($368k/year!)

---

### ✅ Recommended Alternative #2: Use Auto-Scaling

**Better approach for variable workloads:**

```hcl
resource "aws_autoscaling_group" "data_processor" {
  min_size = 3
  max_size = 6
  desired_capacity = 3

  # Scale up when CPU > 70%
  target_tracking_configuration {
    predefined_metric_type = "ASGAverageCPUUtilization"
    target_value = 70.0
  }
}
```

**Benefits:**
- ✅ Scales automatically based on actual load
- ✅ Runs 3 instances during normal traffic (saves money)
- ✅ Scales to 6 during spikes (still handles growth)
- ✅ Estimated cost: **$10,000/month** (right-sized with growth headroom)

---

## 💰 Cost Comparison

| Configuration | Monthly Cost | Annual Cost | vs Current | vs Proposed |
|--------------|-------------|-------------|------------|-------------|
| **Current (5x c5.2xlarge)** | $4,032 | $48,384 | baseline | **-$362k** |
| **Proposed (10x c5.4xlarge)** | $34,272 | $411,264 | +$363k | baseline |
| **Recommended (3x c5.2xlarge)** | $2,419 | $29,030 | **-$19k** | **-$382k** |
| **With Auto-Scaling (3-6x)** | ~$10,000 | ~$120,000 | -$28k | **-$291k** |

---

## 🔧 Auto-Fix Available

I've generated two alternatives:
1. **[Static Right-Sizing PR #125](https://github.com/your-org/your-repo/pull/125)** - 3x c5.2xlarge
2. **[Auto-Scaling PR #126](https://github.com/your-org/your-repo/pull/126)** - ASG with 3-6 instances

---

## 📊 Datadog Metrics Referenced

- `system.cpu.usage` for data-processor instances (last 30 days)
- `system.mem.used` for data-processor instances (last 30 days)
- `aws.ec2.cpuutilization` from CloudWatch integration
- Job processing queue depth and throughput

**[View full utilization dashboard →](https://app.datadoghq.com/dashboard/xyz-data-processor)**

---

## 💡 Impact

**If merged as-is:**
- 💸 **Waste $362k/year** on unused capacity
- 📊 Run at ~6% CPU utilization (severely over-provisioned)
- 🎯 Miss FinOps efficiency targets

**With recommended fix:**
- ✅ Save **$282k/year** vs proposed change
- ✅ Save **$19k/year** vs even current setup
- ✅ Still have 50% headroom for growth
- ✅ Meet FinOps target of 50-70% utilization

---

## 🤔 Questions Answered

**Q: "What if we have a traffic spike?"**
A: Auto-scaling option scales to 6 instances = 2x your peak workload. Or static 3 instances still handles 5x your current average.

**Q: "We're planning for growth."**
A: At 15% current utilization, you have room to **6x your workload** before needing more instances.

**Q: "What about redundancy?"**
A: 3 instances across availability zones provides N+1 redundancy. Current 5 is already over-redundant.

---

<sub>🤖 Powered by **Datadog metrics** + **Claude AI** + **AWS Cost Calculator**</sub>
<sub>💬 Questions? Override needed? Comment `/iac-guardian override <reason>`</sub>
