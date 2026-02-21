# Adding New Scenarios - Quick Guide

## TL;DR: 3 Minutes Per Scenario

1. Create example folder with files
2. Add scenario to dropdown in `app.py`
3. Done!

The backend automatically handles ANY infrastructure change.

---

## 🎯 Current Scenarios

You have 2:
1. **Peak Traffic Risk** - K8s replicas reduction
2. **Cost Optimization** - Over-provisioned EC2

---

## ➕ How to Add More (Step-by-Step)

### Option 1: Just Add to UI (Fastest - 2 minutes)

Edit `app.py` around **line 294**:

```python
scenario = st.selectbox(
    "Select Demo:",
    [
        "Scenario 1: Peak Traffic Risk",
        "Scenario 2: Cost Optimization",
        "Scenario 3: Database Encryption Missing",  # ← ADD HERE
        "Scenario 4: Network Security Hole",        # ← ADD HERE
    ]
)
```

Then add the diff content around **line 310**:

```python
elif scenario == "Scenario 3: Database Encryption Missing":
    st.info("🔒 RDS instance created without encryption")
    diff_content = """diff --git a/database.tf b/database.tf
--- a/database.tf
+++ b/database.tf
@@ -1,5 +1,6 @@
 resource "aws_db_instance" "main" {
   identifier     = "production-db"
   engine         = "postgres"
   instance_class = "db.t3.large"
+  storage_encrypted = false
 }"""
```

**That's it!** The backend will automatically:
- Parse the changes
- Query relevant Datadog metrics
- Analyze with Claude
- Generate fixes if applicable

---

## 🚀 Suggested New Scenarios

### 1. Database Encryption Missing
**Risk:** Compliance violation, data breach
**Fix:** Enable encryption, add KMS key

```python
"Scenario 3: Database Encryption"
diff_content = """diff --git a/database.tf b/database.tf
+  storage_encrypted = false
+  # ⚠️ Production DB without encryption!"""
```

---

### 2. Network Security Hole
**Risk:** Open to internet, vulnerable
**Fix:** Restrict to VPN/bastion

```python
"Scenario 4: Security Group Too Open"
diff_content = """diff --git a/security.tf b/security.tf
+  ingress {
+    from_port   = 22
+    to_port     = 22
+    protocol    = "tcp"
+    cidr_blocks = ["0.0.0.0/0"]  # ⚠️ Open to world!
+  }"""
```

---

### 3. No Resource Limits
**Risk:** Can consume all cluster resources
**Fix:** Add resource limits

```python
"Scenario 5: No Resource Limits"
diff_content = """diff --git a/deployment.yaml b/deployment.yaml
+  containers:
+  - name: app
+    image: myapp:latest
+    # ⚠️ No resource limits!"""
```

---

### 4. Single AZ Deployment
**Risk:** No high availability, single point of failure
**Fix:** Multi-AZ deployment

```python
"Scenario 6: Single AZ Risk"
diff_content = """diff --git a/compute.tf b/compute.tf
+  resource "aws_instance" "web" {
+    availability_zone = "us-east-1a"  # Only one AZ!
+    count = 10
+  }"""
```

---

### 5. Log Retention Too Short
**Risk:** Can't investigate incidents
**Fix:** Extend retention

```python
"Scenario 7: Short Log Retention"
diff_content = """diff --git a/logging.tf b/logging.tf
+  resource "aws_cloudwatch_log_group" "app" {
+    retention_in_days = 1  # ⚠️ Only 1 day!
+  }"""
```

---

### 6. Missing Health Checks
**Risk:** Traffic to unhealthy instances
**Fix:** Add liveness/readiness probes

```python
"Scenario 8: No Health Checks"
diff_content = """diff --git a/service.yaml b/service.yaml
+  containers:
+  - name: api
+    # ⚠️ No livenessProbe or readinessProbe"""
```

---

### 7. Downgrade Critical Service
**Risk:** Performance degradation
**Fix:** Keep current or upgrade

```python
"Scenario 9: Version Downgrade"
diff_content = """diff --git a/deployment.yaml b/deployment.yaml
-    image: api:v2.1.0
+    image: api:v1.9.0  # ⚠️ Downgrade!"""
```

---

### 8. Removing Backups
**Risk:** Data loss
**Fix:** Keep backup enabled

```python
"Scenario 10: Backup Disabled"
diff_content = """diff --git a/database.tf b/database.tf
-  backup_retention_period = 7
+  backup_retention_period = 0  # ⚠️ No backups!"""
```

---

## 💡 Full Example: Adding Scenario 3

### Step 1: Edit app.py

Find the scenario dropdown (~line 294):

```python
scenario = st.selectbox(
    "Select Demo:",
    [
        "Scenario 1: Peak Traffic Risk",
        "Scenario 2: Cost Optimization",
        "Scenario 3: Database Encryption Missing",  # NEW
    ]
)
```

### Step 2: Add the diff content (~line 310)

```python
if scenario == "Scenario 1: Peak Traffic Risk":
    st.info("🚨 Reduces K8s replicas 20→5. Will it crash?")
    diff_path = "examples/scenario-1-peak-traffic/payment-api-deployment.yaml"
    diff_content = """..."""

elif scenario == "Scenario 2: Cost Optimization":
    st.info("💰 Adds 10x c5.4xlarge. Is it over-provisioned?")
    diff_path = "examples/scenario-2-cost-optimization/compute.tf"
    diff_content = """..."""

# NEW SCENARIO
elif scenario == "Scenario 3: Database Encryption Missing":
    st.info("🔒 Creates RDS without encryption. Compliance risk?")
    diff_content = """diff --git a/database.tf b/database.tf
index abc123..def456 100644
--- a/database.tf
+++ b/database.tf
@@ -5,6 +5,7 @@ resource "aws_db_instance" "main" {
   engine         = "postgres"
   instance_class = "db.t3.large"
   username       = "admin"
+  storage_encrypted = false

   tags = {
     Name = "production-database"
@@ -12,3 +13,4 @@ resource "aws_db_instance" "main" {
   }
 }"""
```

### Step 3: Test it!

```bash
./run_ui.sh
# Select "Scenario 3: Database Encryption Missing"
# Click Analyze
```

Claude will automatically:
- Detect it's a Terraform change
- See encryption is disabled
- Warn about compliance/security risk
- Potentially suggest enabling encryption

**That's it! 3 minutes total.**

---

## 🎨 Optional: Add Real Files

If you want proper file structure:

```bash
mkdir -p examples/scenario-3-database-encryption

# Create the Terraform file
cat > examples/scenario-3-database-encryption/database.tf << 'EOF'
resource "aws_db_instance" "main" {
  identifier          = "production-db"
  engine              = "postgres"
  engine_version      = "14.7"
  instance_class      = "db.t3.large"
  allocated_storage   = 100
  storage_encrypted   = false  # ⚠️ Security risk!

  username = "admin"

  tags = {
    Name        = "production-database"
    Environment = "production"
  }
}
EOF

# Create description
cat > examples/scenario-3-database-encryption/PR_DESCRIPTION.md << 'EOF'
# Add production database

## Changes
- Create RDS Postgres instance
- 100GB storage
- db.t3.large instance

## Expected IaC Guardian Analysis
Should detect missing encryption and flag as HIGH RISK
EOF
```

---

## 🤖 What the Backend Handles Automatically

The backend is **smart**:

### For Any Change:
1. **Parses** - Extracts file types, changes
2. **Queries** - Gets relevant Datadog metrics
3. **Analyzes** - Claude understands the context
4. **Recommends** - Suggests fixes

### Specific Detections:
- **K8s YAML** → Checks replicas, resources, health checks
- **Terraform** → Checks instances, costs, security
- **Security** → Encryption, network rules, access
- **Cost** → Instance types, counts, utilization

**You don't need to configure anything!** Just add the scenario.

---

## 📊 How Auto-Fix Works for New Scenarios

Current auto-fix supports:
1. K8s replica issues → Generates HPA
2. Cost issues → Right-sizes instances

To add auto-fix for new scenarios, edit `fix_generator.py`:

```python
def generate_fix(self, changes: Dict, datadog_context: Dict, analysis: str):
    # Existing checks...

    # NEW: Database encryption fix
    if 'storage_encrypted = false' in changes.get('raw_diff', ''):
        return self._generate_encryption_fix(changes, datadog_context)

    # NEW: Security group fix
    if '0.0.0.0/0' in changes.get('raw_diff', '') and 'security' in analysis.lower():
        return self._generate_security_fix(changes, datadog_context)
```

Then implement the fix generator:

```python
def _generate_encryption_fix(self, changes, datadog_context):
    return {
        'fix_type': 'encryption_fix',
        'files': [{
            'path': 'database.tf',
            'content': '# Fixed version with encryption...'
        }],
        'pr_title': '🔒 Enable database encryption',
        'pr_body': 'Adds KMS encryption to production RDS...'
    }
```

---

## 🎯 Priority Scenarios to Add

Based on common issues:

### High Value (Add These First)
1. **Database encryption** - Common compliance issue
2. **Security groups** - Common security hole
3. **Missing health checks** - Common reliability issue

### Medium Value
4. **Single AZ** - High availability
5. **Short log retention** - Observability
6. **No resource limits** - Cluster stability

### Demo Value
7. **Version downgrade** - Dramatic "before you break prod"
8. **Backup disabled** - Clear data loss risk

---

## ⚡ Quick Add Command

Want to add a scenario in one command?

```bash
# Create scenario files
cat > add_scenario.sh << 'EOF'
#!/bin/bash
SCENARIO_NUM=$1
SCENARIO_NAME=$2

mkdir -p examples/scenario-$SCENARIO_NUM-$SCENARIO_NAME

echo "Scenario $SCENARIO_NUM created!"
echo "Now:"
echo "1. Add files to examples/scenario-$SCENARIO_NUM-$SCENARIO_NAME/"
echo "2. Add to app.py scenario dropdown"
EOF

chmod +x add_scenario.sh

# Usage:
./add_scenario.sh 3 database-encryption
```

---

## 🎬 Demo with Multiple Scenarios

**For Hackathon:**
1. Show 2-3 scenarios max
2. Pick ones that tell different stories:
   - **Scenario 1:** Outage prevention (replicas)
   - **Scenario 2:** Cost savings (over-provisioning)
   - **Scenario 3:** Security/compliance (encryption)

**Why 2-3 is enough:**
- Shows breadth of detection
- Doesn't drag on
- Each has different impact (outage vs cost vs security)

---

## ✅ Summary

### To add a scenario:
1. **Edit** `app.py` (~5 lines)
2. **Add** diff content (~10 lines)
3. **Test** - Run UI

**Time:** 2-3 minutes per scenario

### The backend automatically:
- ✅ Parses any IaC change
- ✅ Queries relevant metrics
- ✅ Analyzes with Claude
- ✅ Suggests fixes

### To add auto-fix:
- Edit `fix_generator.py`
- Add detection logic
- Implement fix generator
- **Time:** 15-30 minutes per fix type

---

## 🚀 Quick Test

Add a simple scenario right now:

```bash
# Edit app.py, add to dropdown:
"Scenario 3: Database Risk"

# Add diff content:
diff_content = """diff --git a/db.tf b/db.tf
+  storage_encrypted = false"""

# Run and test
./run_ui.sh
```

---

**Bottom line:** Adding scenarios is **trivial**. The hard work (parsing, analyzing, fixing) is already done!

Want me to add 2-3 more scenarios for your demo? 🚀
