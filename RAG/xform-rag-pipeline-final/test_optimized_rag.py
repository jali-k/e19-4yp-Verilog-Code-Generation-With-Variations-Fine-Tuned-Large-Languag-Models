#!/usr/bin/env python3
"""
Test script for the optimized RAG pipeline
Tests the improved code generation capabilities
"""

import sys
import os
from pathlib import Path

# Add the xform_rag package to the path
sys.path.insert(0, str(Path(__file__).parent / "xform_rag"))

from xform_rag import RAGConfig, XformRAGPipeline


def test_optimized_generation():
    """Test the optimized RAG pipeline with various transformation requests"""

    print("🚀 Testing Optimized RAG Pipeline")
    print("=" * 50)

    # Initialize the pipeline
    config = RAGConfig.from_dict({"model_type": "ollama", "model_name": "codellama"})

    pipeline = XformRAGPipeline(config)

    # Test connectivity
    if not pipeline.code_generator.test_connection():
        print("❌ Pipeline connectivity test failed")
        return False

    print("✅ Pipeline initialized successfully")

    # Test cases that represent different complexities
    test_cases = [
        {
            "name": "wire_to_reg_conversion",
            "description": "Transform wire declarations to reg declarations in a Verilog module",
            "expected_components": [
                "visitor",
                "transform_function",
                "main",
                "argparse",
            ],
        },
        {
            "name": "add_enable_signal",
            "description": "Add an enable signal to control a counter in a Verilog module",
            "expected_components": [
                "visitor",
                "transform_function",
                "main",
                "argparse",
            ],
        },
        {
            "name": "signal_width_change",
            "description": "Change the width of a signal from 8 bits to 16 bits",
            "expected_components": [
                "visitor",
                "transform_function",
                "main",
                "argparse",
            ],
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases):
        print(f"\n🔧 Test {i+1}: {test_case['name']}")
        print(f"Description: {test_case['description']}")

        try:
            # Generate the xform
            result = pipeline.generate_xform(test_case["description"])

            if "error" in result:
                print(f"❌ Generation failed: {result['error']}")
                results.append(
                    {
                        "test": test_case["name"],
                        "success": False,
                        "error": result["error"],
                    }
                )
                continue

            # Check validation results
            validation = result.get("validation", {})
            completeness_score = validation.get("completeness_score", 0.0)
            is_valid = validation.get("is_valid", False)

            print(f"📊 Completeness Score: {completeness_score:.2f}")
            print(f"✅ Valid Code: {is_valid}")

            if validation.get("missing_components"):
                print(f"⚠️  Missing: {', '.join(validation['missing_components'])}")

            if validation.get("warnings"):
                print(f"⚠️  Warnings: {len(validation['warnings'])} issues")

            # Save the generated code for inspection
            output_dir = Path("test_outputs")
            output_dir.mkdir(exist_ok=True)

            output_file = output_dir / f"{test_case['name']}_generated.py"
            with open(output_file, "w") as f:
                f.write(result["code"])

            print(f"💾 Code saved to: {output_file}")

            results.append(
                {
                    "test": test_case["name"],
                    "success": is_valid and completeness_score >= 0.6,
                    "score": completeness_score,
                    "validation": validation,
                }
            )

        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(
                {"test": test_case["name"], "success": False, "error": str(e)}
            )

    # Summary
    print("\n" + "=" * 50)
    print("📈 TEST SUMMARY")
    print("=" * 50)

    successful_tests = sum(1 for r in results if r.get("success", False))
    total_tests = len(results)
    avg_score = sum(r.get("score", 0) for r in results) / len(results) if results else 0

    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print(f"📊 Average Completeness Score: {avg_score:.2f}")

    for result in results:
        status = "✅" if result.get("success", False) else "❌"
        score = result.get("score", 0)
        print(f"{status} {result['test']}: {score:.2f}")

    return successful_tests / total_tests >= 0.6  # At least 60% success rate


if __name__ == "__main__":
    success = test_optimized_generation()
    if success:
        print("\n🎉 Optimization Test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Optimization Test FAILED!")
        sys.exit(1)
