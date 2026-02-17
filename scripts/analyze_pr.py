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
from output_formatter import OutputFormatter

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
            if os.getenv('GITHUB_ACTIONS') != 'true':
                print("ℹ️  No automatic fix available for this issue")
            return None

        if os.getenv('GITHUB_ACTIONS') != 'true':
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
        if os.getenv('GITHUB_ACTIONS') != 'true':
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

Analyze this infrastructure change and provide a CRISP, SHORT analysis in exactly this format:

## Risk Level: [CRITICAL/HIGH/MEDIUM/LOW]

## Why This is Risky
[1-2 sentences max. Be specific with numbers from the metrics. What will break?]

## What To Do
[1-2 bullet points max. Clear action items.]

Focus on:
- **Scenario 1**: If replicas reduced → can it handle peak traffic?
- **Scenario 2**: If compute added → is it right-sized?

Keep it SHORT and PUNCHY. Like a busy engineer needs to understand in 10 seconds.
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
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

    # Format and output the analysis
    formatter = OutputFormatter()

    # Check if we're outputting for GitHub (has GITHUB_ACTIONS env) or terminal
    is_github = os.getenv('GITHUB_ACTIONS') == 'true'

    if is_github:
        # Format for GitHub PR comment (concise format)
        formatted_output = formatter.format_for_github_concise(analysis, fix_pr_url)
    else:
        # Format for terminal (clean, no HTML)
        formatted_output = formatter.format_for_terminal(analysis, fix_pr_url)

    print(formatted_output)


if __name__ == "__main__":
    main()
