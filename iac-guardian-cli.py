#!/usr/bin/env python3
"""
IaC Guardian CLI
Local pre-commit analysis for developers
"""

import sys
import os
import subprocess
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def get_staged_iac_files():
    """Get staged IaC files (K8s, Terraform)"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )

        files = result.stdout.strip().split('\n')
        iac_files = [
            f for f in files
            if f.endswith(('.yaml', '.yml', '.tf', '.tfvars'))
        ]

        return iac_files
    except subprocess.CalledProcessError as e:
        print(f"Warning: git command failed - {e}", file=sys.stderr)
        return []


def get_staged_diff():
    """Get the full staged diff"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Warning: git diff command failed - {e}", file=sys.stderr)
        return ""


def analyze_changes(diff_content):
    """Analyze changes using IaC Guardian backend"""
    import tempfile
    from analyze_pr import parse_diff, analyze_with_claude
    from datadog_api_client import get_datadog_context

    # Save diff to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.diff', delete=False) as f:
        f.write(diff_content)
        diff_file = f.name

    try:
        # Parse changes
        changes = parse_diff(diff_file)

        if not changes['files']:
            return None, None

        # Get Datadog context
        datadog_context = get_datadog_context(changes)

        # Analyze
        analysis = analyze_with_claude(changes, datadog_context)

        return analysis, changes

    finally:
        os.unlink(diff_file)


def format_terminal_output(analysis):
    """Format analysis for terminal"""
    output = []

    output.append("\n" + "=" * 70)
    output.append("🛡️  IaC GUARDIAN ANALYSIS")
    output.append("=" * 70)
    output.append("")

    # Color codes
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Detect risk level
    analysis_upper = analysis.upper()

    if any(word in analysis_upper for word in ['CRITICAL', 'DO NOT MERGE', 'BLOCK']):
        risk_color = RED
        risk_level = "CRITICAL"
    elif 'HIGH RISK' in analysis_upper:
        risk_color = RED
        risk_level = "HIGH RISK"
    elif any(word in analysis_upper for word in ['WARNING', 'CAUTION', 'COST']):
        risk_color = YELLOW
        risk_level = "WARNING"
    else:
        risk_color = GREEN
        risk_level = "LOW RISK"

    output.append(f"{BOLD}{risk_color}Risk Level: {risk_level}{RESET}")
    output.append("")

    # Analysis content
    output.append(analysis)
    output.append("")

    output.append("=" * 70)

    return "\n".join(output)


def main():
    """Main CLI entry point"""

    print("\n🛡️  IaC Guardian - Pre-Commit Analysis")
    print("=" * 70)

    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not set")
        print("   Export your API key: export ANTHROPIC_API_KEY='your-key'")
        sys.exit(1)

    # Get staged files
    iac_files = get_staged_iac_files()

    if not iac_files:
        print("✅ No infrastructure changes detected")
        sys.exit(0)

    print(f"\n📄 Infrastructure files changed: {len(iac_files)}")
    for f in iac_files:
        print(f"   - {f}")

    # Get diff
    print("\n🔍 Analyzing changes...")
    diff = get_staged_diff()

    if not diff:
        print("✅ No changes to analyze")
        sys.exit(0)

    # Analyze
    try:
        print("📊 Querying Datadog metrics...")
        print("🤖 Running AI analysis...")

        analysis, changes = analyze_changes(diff)

        if not analysis:
            print("✅ No issues detected")
            sys.exit(0)

        # Format and display
        formatted = format_terminal_output(analysis)
        print(formatted)

        # Check risk level
        analysis_upper = analysis.upper()

        if any(word in analysis_upper for word in ['CRITICAL', 'DO NOT MERGE', 'HIGH RISK']):
            print("\n❌ COMMIT BLOCKED: Critical issues detected")
            print("\n💡 Options:")
            print("   1. Fix the issues manually")
            print("   2. Run 'python iac-guardian-cli.py fix' for auto-fix")
            print("   3. Override with: git commit --no-verify")
            sys.exit(1)

        elif any(word in analysis_upper for word in ['WARNING', 'COST']):
            print("\n⚠️  WARNING: Issues detected but not blocking")
            print("   Review carefully before pushing")

        else:
            print("\n✅ Looks good!")

        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        # Check if strict mode is disabled (for emergencies)
        strict_mode = os.getenv('IAC_GUARDIAN_STRICT_MODE', 'true').lower() != 'false'
        if strict_mode:
            print("   Blocking commit due to analysis failure")
            print("   To bypass, use: IAC_GUARDIAN_STRICT_MODE=false git commit ...")
            sys.exit(1)  # Block on errors by default
        else:
            print("   Proceeding with commit (strict mode disabled)")
            sys.exit(0)


if __name__ == "__main__":
    main()
