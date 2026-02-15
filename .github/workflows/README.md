# GitHub Action Setup

## Required Secrets

Add these to your repo settings (Settings → Secrets and variables → Actions):

### Required:
- `ANTHROPIC_API_KEY` - Your Claude API key from console.anthropic.com
- `DATADOG_API_KEY` - Datadog API key
- `DATADOG_APP_KEY` - Datadog Application key

### Automatic:
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

## How It Works

1. Triggered on any PR that changes `.yaml`, `.yml`, or `.tf` files
2. Gets diff between base branch and PR branch
3. Runs Python analysis script with Claude + Datadog MCP
4. Posts (or updates) comment on PR with findings

## Testing Locally

```bash
# Get a PR diff
git diff main...your-branch > pr_diff.txt

# Run analysis
export ANTHROPIC_API_KEY="your-key"
export DATADOG_API_KEY="your-key"
export DATADOG_APP_KEY="your-key"
python scripts/analyze_pr.py pr_diff.txt
```
