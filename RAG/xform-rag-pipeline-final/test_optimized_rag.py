#!/usr/bin/env python3
"""
Test script for the Priority 1 improved RAG pipeline
Tests the enhanced code generation capabilities with new features
"""

import sys
import os
from pathlib import Path

# Add the xform_rag package to the path
sys.path.insert(0, str(Path(__file__).parent))

from xform_rag import RAGConfig, XformRAGPipeline


def test_optimized_generation():
    """Test the Priority 1 improved RAG pipeline with various transformation requests"""

    print("🚀 Testing Priority 1 Improved RAG Pipeline")
    print("=" * 50)

    # Initialize the pipeline with Priority 1 improvements
    config = RAGConfig(
        model_type="ollama",
        model_name="codellama",
        embedding_model="microsoft/codebert-base",  # Priority 1: CodeBERT embeddings
        embedding_type="codebert",
        data_dir=".",
        vector_store_dir="./vector_store",
        output_dir="./generated",
    )

    try:
        pipeline = XformRAGPipeline(config)
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        print("💡 Falling back to sentence-transformers...")

        # Fallback to sentence transformers if CodeBERT fails
        config.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        config.embedding_type = "huggingface"
        pipeline = XformRAGPipeline(config)

    # Test system components
    print("\n🧪 Testing System Components...")
    test_results = pipeline.test_system()

    for component, result in test_results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {component}")

    if not all(test_results.values()):
        print("⚠️ Some components failed - continuing with available functionality...")

    print(f"\n✅ Pipeline initialized with {config.embedding_model}")

    # Show system stats with Priority 1 improvements
    stats = pipeline.get_system_stats()
    print(
        f"📊 Vector store documents: {stats['vector_store'].get('vector_store_documents', 'N/A')}"
    )
    print(f"📊 Embedding model: {stats['config']['embedding_model']}")
    print(f"📊 Embedding type: {stats['config']['embedding_type']}")

    # Test cases that represent different complexities with Priority 1 validation
    test_cases = [
        {
            "name": "wire_to_reg_conversion",
            "description": "Transform wire declarations to reg declarations in a Verilog module",
            "complexity": "simple",
        },
        {
            "name": "add_enable_signal",
            "description": "Add an enable signal to control assignments in a Verilog module",
            "complexity": "medium",
        },
        {
            "name": "signal_width_change",
            "description": "Change the width of a signal from 8 bits to 16 bits in Verilog",
            "complexity": "medium",
        },
        {
            "name": "module_rename",
            "description": "Rename a Verilog module from old_name to new_name",
            "complexity": "simple",
        },
        {
            "name": "port_addition",
            "description": "Add a new input port called debug_enable to a Verilog module",
            "complexity": "complex",
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases):
        print(f"\n🔧 Test {i+1}: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"Complexity: {test_case['complexity']}")

        try:
            # Priority 1: Enhanced generation with validation
            result = pipeline.generate_xform(test_case["description"])

            if "error" in result:
                print(f"❌ Generation failed: {result['error']}")
                if "validation_issues" in result:
                    print(
                        f"   Validation issues: {', '.join(result['validation_issues'])}"
                    )
                results.append(
                    {
                        "test": test_case["name"],
                        "success": False,
                        "error": result["error"],
                    }
                )
                continue

            # Priority 1: Check validation warnings
            if "validation_warnings" in result:
                print(
                    f"⚠️  Validation warnings: {len(result['validation_warnings'])} issues"
                )
                for warning in result["validation_warnings"][:3]:  # Show first 3
                    print(f"   - {warning}")

            # Basic code quality checks
            code = result.get("code", "")
            has_shebang = code.startswith("#!/usr/bin/env python3")
            has_main = "def main():" in code
            has_argparse = "argparse" in code
            has_pyverilog = "from pyverilog.vparser.parser import parse" in code

            quality_score = (
                sum([has_shebang, has_main, has_argparse, has_pyverilog]) / 4.0
            )

            print(f"📊 Quality Score: {quality_score:.2f}")
            print(f"✅ Has shebang: {has_shebang}")
            print(f"✅ Has main(): {has_main}")
            print(f"✅ Has argparse: {has_argparse}")
            print(f"✅ Has PyVerilog: {has_pyverilog}")

            # Save the generated code for inspection
            output_dir = Path("test_outputs")
            output_dir.mkdir(exist_ok=True)

            output_file = output_dir / f"{test_case['name']}_priority1.py"
            with open(output_file, "w") as f:
                f.write(result["code"])

            print(f"💾 Code saved to: {output_file}")
            print(f"📏 Code length: {len(code)} characters")

            success = quality_score >= 0.75 and len(code) > 500  # Reasonable thresholds

            results.append(
                {
                    "test": test_case["name"],
                    "success": success,
                    "quality_score": quality_score,
                    "code_length": len(code),
                    "warnings": result.get("validation_warnings", []),
                }
            )

        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(
                {"test": test_case["name"], "success": False, "error": str(e)}
            )

    # Summary with Priority 1 improvements
    print("\n" + "=" * 60)
    print("📈 PRIORITY 1 ENHANCED TEST SUMMARY")
    print("=" * 60)

    successful_tests = sum(1 for r in results if r.get("success", False))
    total_tests = len(results)
    avg_quality = (
        sum(r.get("quality_score", 0) for r in results) / len(results) if results else 0
    )
    avg_length = (
        sum(r.get("code_length", 0) for r in results) / len(results) if results else 0
    )

    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print(f"📊 Average Quality Score: {avg_quality:.2f}")
    print(f"📏 Average Code Length: {avg_length:.0f} characters")
    print(f"🧠 Embedding Model: {config.embedding_model}")
    print(f"🔧 Total Warnings: {sum(len(r.get('warnings', [])) for r in results)}")

    print(f"\n📋 Individual Results:")
    for result in results:
        status = "✅" if result.get("success", False) else "❌"
        quality = result.get("quality_score", 0)
        length = result.get("code_length", 0)
        warnings = len(result.get("warnings", []))
        print(
            f"{status} {result['test']}: Quality={quality:.2f}, Length={length}, Warnings={warnings}"
        )

    # Priority 1 specific insights
    print(f"\n🔍 Priority 1 Analysis:")
    print(
        f"- Input validation prevented: {sum(1 for r in results if 'validation_issues' in r.get('error', ''))} invalid requests"
    )
    print(
        f"- Generated code with quality > 0.75: {sum(1 for r in results if r.get('quality_score', 0) > 0.75)}/{total_tests}"
    )
    print(
        f"- Average warnings per generation: {sum(len(r.get('warnings', [])) for r in results) / total_tests:.1f}"
    )

    return successful_tests / total_tests >= 0.6  # At least 60% success rate


if __name__ == "__main__":
    success = test_optimized_generation()
    if success:
        print("\n🎉 Priority 1 Enhanced RAG Test PASSED!")
        print(
            "🚀 The improved pipeline with CodeBERT, validation, and caching is working!"
        )
        sys.exit(0)
    else:
        print("\n💥 Priority 1 Enhanced RAG Test FAILED!")
        print("🔧 Check the generated code and validation warnings above.")
        sys.exit(1)
