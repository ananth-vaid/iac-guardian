#!/usr/bin/env python3
"""
IaC Guardian - PR Analysis Script
Analyzes infrastructure changes and provides risk assessment
"""

import os
import sys
import json
import re
from typing import Dict, List, Optional
import anthropic
from datadog_api_client import get_datadog_context
from fix_generator import FixGenerator
from github_pr_creator import GitHubPRCreator

def parse_diff(diff_file: str) -> Dict[str, any]:
    """Parse git diff to extract changed files and their changes"""
    with open(diff_file, 'r') as f:
        diff_content = f.read()

    changes = {
        'files': [],
        'k8s_changes': [],
        'terraform_changes': [],
        'raw_diff': diff_content
    }

    # Extract changed files
    file_pattern = r'diff --git a/(.*?) b/(.*?)(?:\n|$)'
    files = re.findall(file_pattern, diff_content)

    for old_file, new_file in files:
        file_info = {'path': new_file, 'type': None}

        # Determine file type
        if new_file.endswith(('.yaml', '.yml')):
            file_info['type'] = 'kubernetes'
            changes['k8s_changes'].append(file_info)
        elif new_file.endswith('.tf'):
            file_info['type'] = 'terraform'
            changes['terraform_changes'].append(file_info)

        changes['files'].append(file_info)

    # Extract specific K8s changes (replica counts, resource limits)
    replica_changes = re.findall(r'[-+]\s*replicas:\s*(\d+)', diff_content)
    if replica_changes:
        changes['replica_changes'] = replica_changes

    # Extract Terraform instance changes
    instance_changes = re.findall(r'[-+]\s*instance_type\s*=\s*"([^"]+)"', diff_content)
    if instance_changes:
        changes['instance_type_changes'] = instance_changes

    count_changes = re.findall(r'[-+]\s*count\s*=\s*(\d+)', diff_content)
    if count_changes:
        changes['count_changes'] = count_changes

    return changes


def try_create_fix(changes: Dict, datadog_context: Dict, analysis: str) -> Optional[str]:
    """
    Try to generate and create a fix PR

    Returns:
        PR URL if successful, None otherwise
    """
    try:
        # Generate fix
        generator = FixGenerator()
        fix = generator.generate_fix(changes, datadog_context, analysis)

        if not fix:
            print("ℹ️  No automatic fix available for this issue")
            return None

        print(f"\n🔧 Generated fix: {fix['description']}")

        # Create PR
        pr_creator = GitHubPRCreator()
        pr_number = os.getenv('PR_NUMBER')  # From GitHub Actions
        pr_url = pr_creator.create_fix_pr(
            fix=fix,
            original_pr_number=int(pr_number) if pr_number else None
        )

        return pr_url

    except Exception as e:
        print(f"⚠️  Could not create auto-fix: {e}")
        return None


def analyze_with_claude(changes: Dict, datadog_context: Optional[Dict] = None) -> str:
    """Send changes to Claude for analysis"""

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return "❌ Error: ANTHROPIC_API_KEY not set"

    client = anthropic.Anthropic(api_key=api_key)

    # Build context for Claude
    context = f"""You are an infrastructure expert reviewing a pull request for potential issues.

## Changes Detected:
- Files changed: {len(changes['files'])}
- Kubernetes changes: {len(changes['k8s_changes'])} files
- Terraform changes: {len(changes['terraform_changes'])} files

## Specific Changes:
"""

    if changes.get('replica_changes'):
        context += f"- Replica count changes: {changes['replica_changes']}\n"

    if changes.get('instance_type_changes'):
        context += f"- Instance type changes: {changes['instance_type_changes']}\n"

    if changes.get('count_changes'):
        context += f"- Resource count changes: {changes['count_changes']}\n"

    if datadog_context:
        context += f"\n## Real-time Datadog Metrics:\n{json.dumps(datadog_context, indent=2)}\n"

    context += f"\n## Full Diff:\n```diff\n{changes['raw_diff'][:3000]}\n```\n"

    # Prompt for analysis
    prompt = f"""{context}

Analyze this infrastructure change for:

1. **Risk Assessment** 🚨
   - Will this cause outages or performance degradation?
   - Based on the metrics, can the infrastructure handle the load?
   - Are there any dangerous configuration changes?

2. **Cost Impact** 💰
   - Are resources over-provisioned or under-utilized?
   - What's the estimated cost change?
   - Any optimization opportunities?

3. **Recommendations** ✅
   - What should be done before merging?
   - Any safer alternatives?

Focus on these two demo scenarios:
- **Scenario 1**: If replicas are being reduced, check if it can handle peak traffic
- **Scenario 2**: If compute resources are being added, check if they're right-sized

Format your response in clear markdown with emojis, bullet points, and specific numbers from the metrics.
Be direct and actionable - like you're talking to a busy engineer.
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return response.content[0].text

    except Exception as e:
        return f"❌ Error calling Claude API: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_pr.py <diff_file>")
        sys.exit(1)

    diff_file = sys.argv[1]

    if not os.path.exists(diff_file):
        print(f"❌ Error: Diff file not found: {diff_file}")
        sys.exit(1)

    # Parse the diff
    changes = parse_diff(diff_file)

    if not changes['files']:
        print("ℹ️ No infrastructure changes detected in this PR.")
        sys.exit(0)

    # Get Datadog context via API
    datadog_context = get_datadog_context(changes)

    # Analyze with Claude
    analysis = analyze_with_claude(changes, datadog_context)

    # Check if auto-fix is enabled and issue is detected
    auto_fix_enabled = os.getenv('IAC_GUARDIAN_AUTO_FIX', 'true').lower() == 'true'

    fix_pr_url = None
    if auto_fix_enabled and datadog_context:
        # Try to generate and create fix
        fix_pr_url = try_create_fix(changes, datadog_context, analysis)

    # Output the analysis (with fix PR link if created)
    if fix_pr_url:
        print(analysis)
        print(f"\n\n---\n\n## 🔧 Auto-Generated Fix Available\n")
        print(f"✅ **We've created a safe alternative PR for you!**\n")
        print(f"**Fix PR:** {fix_pr_url}\n")
        print(f"This PR includes:")
        print(f"- Safe configuration based on your production metrics")
        print(f"- Detailed explanation of changes")
        print(f"- Cost and performance comparison\n")
        print(f"👉 **Review the fix PR and merge that instead of this risky change.**")
    else:
        print(analysis)


if __name__ == "__main__":
    main()
