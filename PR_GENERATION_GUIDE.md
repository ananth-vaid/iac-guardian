# PR Generation Guide for IaC Guardian Demo

## Quick Start

### Generate All 4 Demo PRs at Once
```bash
cd /Users/ananth.vaidyanathan/iac-guardian
./scripts/create_all_demo_prs.sh
```

This creates PRs for all 4 new scenarios:
- Scenario 3: Missing Health Checks
- Scenario 4: Missing PodDisruptionBudget
- Scenario 5: Insufficient Replicas
- Scenario 6: Security Group Too Open

### Generate Individual PRs
```bash
# Scenario 3 - Missing Health Checks
./scripts/create_scenario_pr.sh 3

# Scenario 4 - Missing PodDisruptionBudget
./scripts/create_scenario_pr.sh 4

# Scenario 5 - Insufficient Replicas
./scripts/create_scenario_pr.sh 5

# Scenario 6 - Open Security Group
./scripts/create_scenario_pr.sh 6
```

---

## What Happens When You Run the Script

1. **Creates a new branch** (e.g., `demo/missing-health-checks`)
2. **Adds infrastructure file** with the risky change
3. **Commits the change** with descriptive message
4. **Pushes to GitHub**
5. **Creates PR** with template description
6. **GitHub Action triggers** automatically
7. **IaC Guardian analyzes** the PR in ~30 seconds
8. **Comment posted** with risk assessment

---

## Testing & Iteration

### View Your PRs
```bash
# List all open PRs
gh pr list

# View specific PR in browser
gh pr view 2 --web
```

### Check GitHub Actions Status
```bash
# See workflow runs
gh run list

# View specific run logs
gh run view <run-id> --log
```

### Recreate a PR

If you want to test again:

```bash
# Close the existing PR
gh pr close 2

# Delete the remote branch
git push origin --delete demo/missing-health-checks

# Recreate the PR
./scripts/create_scenario_pr.sh 3
```

Or let the script do it:
```bash
./scripts/create_scenario_pr.sh 3
# When prompted "Branch already exists. Delete and recreate? (y/n)", press 'y'
```

---

## Manual PR Creation (Step-by-Step)

If you prefer manual control:

### Step 1: Create Branch
```bash
git checkout -b demo/my-scenario
```

### Step 2: Make Risky Change
Edit or create an infrastructure file:

**Example: k8s/risky-deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  replicas: 1  # Too few for HA!
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        # Missing health checks!
```

### Step 3: Commit
```bash
git add k8s/risky-deployment.yaml
git commit -m "Deploy service with insufficient replicas"
```

### Step 4: Push
```bash
git push -u origin demo/my-scenario
```

### Step 5: Create PR
```bash
gh pr create \
  --title "Deploy service with insufficient replicas" \
  --body "Testing IaC Guardian risk detection"
```

---

## Expected Results by Scenario

### Scenario 3: Missing Health Checks
- **Risk Level:** HIGH or CRITICAL
- **Detection:** Deployment without liveness/readiness probes
- **Recommendation:** Add health check configuration
- **Auto-fix:** Sample probe YAML

### Scenario 4: Missing PodDisruptionBudget
- **Risk Level:** HIGH
- **Detection:** No PDB for production deployment
- **Recommendation:** Create PodDisruptionBudget
- **Auto-fix:** PDB YAML with safe settings

### Scenario 5: Insufficient Replicas
- **Risk Level:** CRITICAL
- **Detection:** Single replica in production
- **Recommendation:** Increase to 3+ for HA
- **Auto-fix:** HPA configuration

### Scenario 6: Open Security Group
- **Risk Level:** CRITICAL
- **Detection:** Security group allows 0.0.0.0/0 on SSH
- **Recommendation:** Restrict to specific CIDR blocks
- **Auto-fix:** Updated security group rules

---

## Troubleshooting

### "gh: command not found"
Install GitHub CLI:
```bash
brew install gh
gh auth login
```

### "Error: ANTHROPIC_API_KEY not set"
Ensure .env file exists:
```bash
cat .env
# Should contain: ANTHROPIC_API_KEY=sk-ant-...
```

### GitHub Action doesn't trigger
Check workflow file exists:
```bash
cat .github/workflows/iac-review.yml
```

Ensure workflow is enabled in GitHub:
1. Go to repository → Actions tab
2. Check if "IaC Guardian Review" workflow is listed
3. Click on workflow → Enable if disabled

### Comment doesn't appear
Check workflow run:
```bash
gh run list --limit 5
gh run view <run-id> --log
```

Common issues:
- API key not set in GitHub Secrets
- Workflow syntax error
- Permission issue (needs write access to PR comments)

---

## Demo Flow

### Recommended Demo Order

1. **Start with Scenario 3 (Missing Health Checks)**
   - Clear visual diff
   - Obvious risk
   - Good conversation starter

2. **Show Scenario 6 (Open Security Group)**
   - Security-focused
   - Critical severity
   - Shows Terraform support

3. **Demo Scenario 5 (Insufficient Replicas)**
   - Ties to observability data
   - Shows Datadog integration potential
   - Demonstrates auto-fix (HPA)

4. **End with Scenario 4 (Missing PDB)**
   - Subtle but important
   - Shows depth of analysis
   - Production-readiness theme

### Presentation Tips

- **Have PRs pre-created** before demo
- **Show GitHub Actions tab** (live workflow running)
- **Point out concise comment format** (8 lines vs 50+)
- **Highlight auto-fix PRs** if generated
- **Show Datadog dashboard** with metrics

---

## Cleanup After Demo

### Close all demo PRs
```bash
gh pr list --json number --jq '.[].number' | xargs -I {} gh pr close {}
```

### Delete demo branches
```bash
git branch | grep demo/ | xargs git branch -D
git push origin --delete demo/missing-health-checks
git push origin --delete demo/missing-pdb
git push origin --delete demo/insufficient-replicas
git push origin --delete demo/open-security-group
```

### Quick cleanup script
```bash
#!/bin/bash
for scenario in 3 4 5 6; do
    case $scenario in
        3) BRANCH="demo/missing-health-checks" ;;
        4) BRANCH="demo/missing-pdb" ;;
        5) BRANCH="demo/insufficient-replicas" ;;
        6) BRANCH="demo/open-security-group" ;;
    esac
    gh pr close $(gh pr list --head $BRANCH --json number --jq '.[0].number') 2>/dev/null || true
    git push origin --delete $BRANCH 2>/dev/null || true
done
echo "✅ Cleanup complete"
```

---

## Next Steps

1. Generate PRs: `./scripts/create_all_demo_prs.sh`
2. Watch GitHub Actions run
3. Review IaC Guardian comments
4. Test Datadog dashboard with metrics
5. Practice demo flow
6. Prepare for hackathon presentation

---

## Resources

- **Repository:** https://github.com/ananth-vaid/iac-guardian
- **GitHub CLI Docs:** https://cli.github.com/manual/
- **GitHub Actions Logs:** https://github.com/ananth-vaid/iac-guardian/actions
