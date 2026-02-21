#!/usr/bin/env python3
"""
Quick test to verify UI components work
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def test_imports():
    """Test all imports work"""
    print("Testing imports...")
    try:
        from analyze_pr import parse_diff, analyze_with_claude
        from datadog_api_client import get_datadog_context, DatadogAPIClient
        from fix_generator import FixGenerator
        import streamlit as st
        import plotly.graph_objects as go
        import pandas as pd
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_parse_diff():
    """Test diff parsing"""
    print("\nTesting diff parsing...")
    try:
        # Create a test diff
        test_diff = """diff --git a/test.yaml b/test.yaml
index 123..456 100644
--- a/test.yaml
+++ b/test.yaml
@@ -1,1 +1,1 @@
-  replicas: 20
+  replicas: 5
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_diff)
            diff_file = f.name

        from analyze_pr import parse_diff
        changes = parse_diff(diff_file)

        assert 'files' in changes
        assert 'raw_diff' in changes
        print("✅ Diff parsing works")

        import os
        os.unlink(diff_file)
        return True
    except Exception as e:
        print(f"❌ Diff parsing error: {e}")
        return False


def test_datadog_client():
    """Test Datadog client (will use mock data)"""
    print("\nTesting Datadog client...")
    try:
        from datadog_api_client import DatadogAPIClient
        client = DatadogAPIClient()

        # Should fall back to mock data
        metrics = client._mock_k8s_metrics("test-service", "production")
        assert 'service' in metrics
        assert 'current_state' in metrics
        print("✅ Datadog client works (using mock data)")
        return True
    except Exception as e:
        print(f"❌ Datadog client error: {e}")
        return False


def test_fix_generator():
    """Test fix generator"""
    print("\nTesting fix generator...")
    try:
        from fix_generator import FixGenerator
        generator = FixGenerator()

        # Test HPA config generation
        hpa = generator._generate_hpa_config("test-service", 10, 20)
        assert 'HorizontalPodAutoscaler' in hpa
        assert 'minReplicas: 10' in hpa
        print("✅ Fix generator works")
        return True
    except Exception as e:
        print(f"❌ Fix generator error: {e}")
        return False


def main():
    print("🧪 Running IaC Guardian UI Tests\n")
    print("=" * 50)

    tests = [
        test_imports,
        test_parse_diff,
        test_datadog_client,
        test_fix_generator,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 50)
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("\n✅ All tests passed! UI is ready to run.")
        print("\nRun the UI with:")
        print("  ./run_ui.sh")
        print("\nOr manually:")
        print("  streamlit run app.py")
        return 0
    else:
        print("\n❌ Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
