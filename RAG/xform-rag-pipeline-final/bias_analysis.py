#!/usr/bin/env python3
"""
Bias Removal Comparison Script
Demonstrates the difference between biased and unbiased generation
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from unbiased_rag_pipeline import UnbiasedCodeGenerator, UnbiasedTestFramework
from xform_rag import create_pipeline
from xform_rag.config import RAGConfig


def compare_biased_vs_unbiased():
    """Compare biased current system vs unbiased approach"""

    print("🔬 BIAS ANALYSIS: Current vs Unbiased RAG Pipeline")
    print("=" * 60)

    # Test scenarios that should be treated equally
    test_scenarios = [
        {
            "name": "Wire to Reg Conversion",
            "request": "Convert wire declarations to reg declarations in Verilog",
            "test_verilog": """module test(input clk, output wire [7:0] data);
    wire internal_sig;
    wire enable;
    assign data = internal_sig ? 8'hFF : 8'h00;
endmodule""",
            "test_args": ["--signal", "internal_sig"],
        },
        {
            "name": "Signal Width Modification",
            "request": "Change signal width from 8 bits to 16 bits",
            "test_verilog": """module test(input clk, output reg [7:0] data);
    reg [7:0] buffer;
    always @(posedge clk) buffer <= data + 1;
endmodule""",
            "test_args": ["--signal", "data", "--width", "16"],
        },
        {
            "name": "Port Addition",
            "request": "Add new input port called enable to control operation",
            "test_verilog": """module counter(input clk, input rst, output reg [7:0] count);
    always @(posedge clk) begin
        if (rst) count <= 0;
        else count <= count + 1;
    end
endmodule""",
            "test_args": ["--port-name", "enable", "--port-type", "input"],
        },
        {
            "name": "Module Renaming",
            "request": "Rename module from counter to timer",
            "test_verilog": """module counter(input clk, output reg [7:0] count);
    always @(posedge clk) count <= count + 1;
endmodule""",
            "test_args": ["--old-name", "counter", "--new-name", "timer"],
        },
    ]

    # Setup configurations
    config = RAGConfig(
        data_dir=Path("."),
        vector_store_dir=Path("./vector_store"),
        model_type="ollama",
        model_name="codellama",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        embedding_type="sentence-transformers",
    )

    print("\\n🔧 Testing Current Biased System...")
    try:
        # Test current biased system
        biased_pipeline = create_pipeline(
            data_dir=".",
            model_type="ollama",
            model_name="codellama",
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            embedding_type="sentence-transformers",
        )

        biased_results = []
        for scenario in test_scenarios:
            try:
                result = biased_pipeline.generate_xform(scenario["request"])
                biased_results.append(
                    {
                        "scenario": scenario["name"],
                        "has_code": bool(result.get("code")),
                        "method": "biased_generation",
                        "code_length": len(result.get("code", "")),
                        "likely_template": "wire_to_reg" in scenario["name"].lower()
                        or "module" in scenario["name"].lower(),
                    }
                )
            except Exception as e:
                biased_results.append(
                    {"scenario": scenario["name"], "error": str(e), "method": "failed"}
                )

        print("   Biased Results Summary:")
        for result in biased_results:
            status = "✅ Template" if result.get("likely_template") else "⚠️ Generic"
            print(
                f"     {result['scenario']}: {status} ({result.get('code_length', 0)} chars)"
            )

    except Exception as e:
        print(f"   ❌ Biased system failed: {e}")
        biased_results = []

    print("\\n🎯 Testing Unbiased System...")
    try:
        # Test unbiased system
        unbiased_generator = UnbiasedCodeGenerator(config)
        unbiased_framework = UnbiasedTestFramework(unbiased_generator)

        # Convert test scenarios for unbiased testing
        unbiased_scenarios = []
        for scenario in test_scenarios:
            unbiased_scenarios.append(
                {
                    "name": scenario["name"],
                    "request": scenario["request"],
                    "test_verilog": scenario["test_verilog"],
                    "test_args": scenario["test_args"],
                }
            )

        unbiased_results = unbiased_framework.run_unbiased_test_suite(
            unbiased_scenarios
        )

        print("   Unbiased Results Summary:")
        for result in unbiased_results["test_results"]:
            status = "✅ Generated" if result["generation_success"] else "❌ Failed"
            print(f"     {result['scenario']}: {status} (Pure RAG)")

        print(f"\\n   📊 Unbiased Metrics:")
        summary = unbiased_results["summary"]
        print(f"     Generation Rate: {summary['generation_rate']:.1%}")
        print(f"     Execution Rate: {summary['execution_rate']:.1%}")
        print(f"     Transformation Rate: {summary['transformation_rate']:.1%}")

    except Exception as e:
        print(f"   ❌ Unbiased system failed: {e}")

    print("\\n🎯 BIAS ANALYSIS COMPLETE")
    print("=" * 60)


def show_bias_removal_strategy():
    """Explain the strategy for removing bias"""

    print("\\n📋 BIAS REMOVAL STRATEGY")
    print("=" * 40)

    print("\\n1. 🚫 REMOVE Hardcoded Transformation Logic:")
    print("   - Delete wire-to-reg specific auto-correction")
    print("   - Delete module-rename specific auto-correction")
    print("   - Remove all transformation-specific templates")

    print("\\n2. ✅ IMPROVE Vector Store Knowledge:")
    print("   - Fix embedding dimension mismatch")
    print("   - Ensure all 24 xform files are properly indexed")
    print("   - Add more diverse transformation examples")

    print("\\n3. 🧠 ENHANCE LLM Generation:")
    print("   - Use smaller, faster models (phi3:mini, qwen2.5-coder:1.5b)")
    print("   - Improve prompt engineering for pattern recognition")
    print("   - Add few-shot examples in prompts")

    print("\\n4. 🔬 IMPLEMENT Unbiased Evaluation:")
    print("   - Equal treatment for all transformation types")
    print("   - Real execution testing without favoritism")
    print("   - Comprehensive metrics across all scenarios")

    print("\\n5. 🎯 VALIDATE True Intelligence:")
    print("   - Test on completely new transformation types")
    print("   - Measure generation consistency across runs")
    print("   - Compare performance with and without bias")


if __name__ == "__main__":
    compare_biased_vs_unbiased()
    show_bias_removal_strategy()
