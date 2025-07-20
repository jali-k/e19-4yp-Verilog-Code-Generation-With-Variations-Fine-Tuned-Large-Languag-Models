#!/usr/bin/env python3
"""
Quick runner for comprehensive xform testing
Run this to test multiple scenarios with the current pipeline
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_xform_test import XformScenarioTester


def main():
    """Quick runner function"""
    print("🚀 Starting Comprehensive Xform Test Suite")
    print("=" * 60)

    tester = XformScenarioTester()
    results_dir, evaluations = tester.run_comprehensive_test()

    print(f"\n✨ Test completed!")
    print(f"📁 Results: {results_dir}")
    print(f"📊 Evaluated: {len(evaluations)} scenarios")


if __name__ == "__main__":
    main()
