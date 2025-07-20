#!/usr/bin/env python3
"""
Unbiased System Validation Script
Tests the bias removal implementation and validates equal treatment
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from xform_rag import create_pipeline
from comprehensive_xform_test import XformScenarioTester


def test_unbiased_generation():
    """Test unbiased generation across multiple transformation types"""
    
    print("🎯 TESTING UNBIASED RAG GENERATION")
    print("=" * 50)
    
    # Create optimized pipeline
    try:
        pipeline = create_pipeline(
            data_dir=".",
            model_type="ollama",
            model_name="qwen2.5-coder:1.5b",  # Smaller model
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            embedding_type="sentence-transformers"
        )
        print("✅ Pipeline created successfully")
    except Exception as e:
        print(f"❌ Pipeline creation failed: {e}")
        return None
    
    # Test scenarios with equal treatment expectation
    test_scenarios = [
        {
            "name": "Wire to Reg Conversion",
            "request": "Convert wire declarations to reg declarations in Verilog",
            "expected_bias": "PREVIOUSLY_BIASED"
        },
        {
            "name": "Signal Width Modification", 
            "request": "Change signal width from 8 bits to 16 bits",
            "expected_bias": "PREVIOUSLY_PARTIAL"
        },
        {
            "name": "Module Renaming",
            "request": "Rename module from counter to timer",
            "expected_bias": "PREVIOUSLY_BIASED"
        },
        {
            "name": "Port Addition",
            "request": "Add new input port called enable to control operation",
            "expected_bias": "PREVIOUSLY_GENERIC"
        },
        {
            "name": "Reset Condition Change",
            "request": "Change reset condition from synchronous to asynchronous",
            "expected_bias": "PREVIOUSLY_GENERIC"
        },
        {
            "name": "Clock Domain Modification",
            "request": "Add clock domain crossing logic with synchronizers",
            "expected_bias": "PREVIOUSLY_GENERIC"
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        print(f"\\n🧪 Testing: {scenario['name']}")
        print(f"   Request: {scenario['request']}")
        print(f"   Previous bias: {scenario['expected_bias']}")
        
        start_time = time.time()
        
        try:
            result = pipeline.generate_xform(scenario["request"])
            
            generation_time = time.time() - start_time
            
            # Analyze the result
            analysis = analyze_generation_result(result, scenario)
            analysis["generation_time"] = generation_time
            
            results.append({
                "scenario": scenario["name"],
                "request": scenario["request"],
                "previous_bias": scenario["expected_bias"],
                "analysis": analysis
            })
            
            # Show analysis
            print(f"   ✅ Generated: {analysis['has_code']}")
            print(f"   📊 Code length: {analysis['code_length']} chars")
            print(f"   ⏱️  Time: {generation_time:.1f}s")
            print(f"   🎯 Quality: {analysis['quality_score']:.2f}")
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            results.append({
                "scenario": scenario["name"],
                "request": scenario["request"],
                "previous_bias": scenario["expected_bias"],
                "analysis": {"error": str(e), "has_code": False}
            })
    
    return results


def analyze_generation_result(result, scenario):
    """Analyze generation result for bias indicators"""
    
    analysis = {
        "has_code": bool(result.get("code")),
        "code_length": len(result.get("code", "")),
        "has_validation": "validation" in result,
        "quality_score": 0.0,
        "bias_indicators": []
    }
    
    code = result.get("code", "")
    
    # Check for bias indicators (should be ABSENT in unbiased system)
    bias_patterns = [
        ("hardcoded_wire_logic", "wire_signals.append" in code),
        ("specific_argument_injection", "--signal" in code and "--width" not in code),
        ("transformation_specific_fixes", "Convert specific signal" in code),
        ("template_favoritism", len(code) > 2000 and "wire" in scenario["request"].lower())
    ]
    
    for pattern_name, condition in bias_patterns:
        if condition:
            analysis["bias_indicators"].append(pattern_name)
    
    # Calculate quality score based on completeness
    if analysis["has_code"]:
        score = 0.3  # Base score for having code
        
        if "class" in code and "def" in code:
            score += 0.3  # Has structure
        
        if "argparse" in code:
            score += 0.2  # Has argument parsing
        
        if "pyverilog" in code:
            score += 0.2  # Uses PyVerilog
        
        # Bonus for reasonable length (not too short or excessively long)
        if 500 <= len(code) <= 2000:
            score += 0.1
        
        # Penalty for bias indicators
        score -= len(analysis["bias_indicators"]) * 0.1
        
        analysis["quality_score"] = max(0.0, min(1.0, score))
    
    return analysis


def compare_with_previous_bias():
    """Compare current unbiased results with previous biased behavior"""
    
    print("\\n📊 BIAS COMPARISON ANALYSIS")
    print("=" * 40)
    
    # Expected behavior based on our bias analysis
    previous_bias_patterns = {
        "Wire to Reg Conversion": {
            "success": True,
            "reason": "Complete hand-crafted logic injection",
            "code_length": 2000
        },
        "Module Renaming": {
            "success": True,
            "reason": "Special template treatment",
            "code_length": 1500
        },
        "Signal Width Modification": {
            "success": False,
            "reason": "Partial fixes only",
            "code_length": 800
        },
        "Port Addition": {
            "success": False,
            "reason": "Generic fallback only",
            "code_length": 500
        },
        "Reset Condition Change": {
            "success": False,
            "reason": "Generic fallback only",
            "code_length": 500
        },
        "Clock Domain Modification": {
            "success": False,
            "reason": "Generic fallback only",
            "code_length": 500
        }
    }
    
    print("🔍 Previous Biased System Behavior:")
    for name, behavior in previous_bias_patterns.items():
        status = "✅ Worked" if behavior["success"] else "❌ Failed"
        print(f"   {name}: {status}")
        print(f"      Reason: {behavior['reason']}")
        print(f"      Typical code length: {behavior['code_length']} chars")
    
    print("\\n🎯 Expected Unbiased System Behavior:")
    print("   - All transformations get equal treatment")
    print("   - Quality depends on RAG retrieval and LLM capability")
    print("   - No hard-coded favoritism")
    print("   - Consistent generation approach across all types")


def run_comprehensive_validation():
    """Run the comprehensive test suite with unbiased system"""
    
    print("\\n🔬 RUNNING COMPREHENSIVE UNBIASED TEST SUITE")
    print("=" * 60)
    
    try:
        tester = XformScenarioTester()
        results_dir, evaluations = tester.run_comprehensive_test()
        
        print(f"\\n📁 Test results saved to: {results_dir}")
        
        # Analyze results for bias patterns
        bias_analysis = analyze_test_results_for_bias(evaluations)
        
        return results_dir, evaluations, bias_analysis
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        return None, None, None


def analyze_test_results_for_bias(evaluations):
    """Analyze test results for remaining bias patterns"""
    
    bias_analysis = {
        "equal_treatment": True,
        "quality_variance": 0.0,
        "suspicious_patterns": [],
        "transformation_scores": {}
    }
    
    scores = []
    
    for eval_result in evaluations:
        scenario_name = eval_result.get("scenario", "Unknown")
        
        # Calculate quality score for this transformation
        quality_score = calculate_transformation_quality(eval_result)
        scores.append(quality_score)
        
        bias_analysis["transformation_scores"][scenario_name] = quality_score
        
        # Check for suspicious patterns indicating bias
        if quality_score > 0.8 and "wire" in scenario_name.lower():
            bias_analysis["suspicious_patterns"].append(f"High score for wire transformation: {quality_score}")
        
        if quality_score > 0.8 and "module" in scenario_name.lower():
            bias_analysis["suspicious_patterns"].append(f"High score for module transformation: {quality_score}")
    
    # Calculate variance in quality scores
    if scores:
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        bias_analysis["quality_variance"] = variance
        
        # High variance might indicate bias
        if variance > 0.1:  # Arbitrary threshold
            bias_analysis["equal_treatment"] = False
            bias_analysis["suspicious_patterns"].append(f"High quality variance: {variance:.3f}")
    
    return bias_analysis


def calculate_transformation_quality(eval_result):
    """Calculate quality score for a transformation result"""
    
    score = 0.0
    
    # Execution success (40%)
    if eval_result.get("execution", {}).get("success", False):
        score += 0.4
    
    # Syntax validity (30%)
    if eval_result.get("syntax", {}).get("valid", False):
        score += 0.3
    
    # Content transformation (30%)
    if eval_result.get("content_changed", False):
        score += 0.3
    
    return score


def save_validation_report(results, bias_analysis, output_file="unbiased_validation_report.json"):
    """Save comprehensive validation report"""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "unbiased_system_validation",
        "generation_results": results,
        "bias_analysis": bias_analysis,
        "summary": {
            "total_scenarios": len(results) if results else 0,
            "successful_generations": sum(1 for r in results if r.get("analysis", {}).get("has_code", False)) if results else 0,
            "average_quality": sum(r.get("analysis", {}).get("quality_score", 0) for r in results) / len(results) if results else 0,
            "bias_indicators_found": sum(len(r.get("analysis", {}).get("bias_indicators", [])) for r in results) if results else 0
        }
    }
    
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\\n📄 Validation report saved: {output_file}")
    
    return report


if __name__ == "__main__":
    print("🚀 UNBIASED SYSTEM VALIDATION")
    print("=" * 50)
    
    # Step 1: Test unbiased generation
    print("\\n1️⃣  Testing Unbiased Generation...")
    generation_results = test_unbiased_generation()
    
    # Step 2: Compare with previous bias
    compare_with_previous_bias()
    
    # Step 3: Run comprehensive validation
    print("\\n2️⃣  Running Comprehensive Test Suite...")
    results_dir, evaluations, bias_analysis = run_comprehensive_validation()
    
    # Step 4: Save validation report
    if generation_results and bias_analysis:
        report = save_validation_report(generation_results, bias_analysis)
        
        print("\\n🎯 VALIDATION SUMMARY")
        print("=" * 30)
        summary = report["summary"]
        print(f"✅ Scenarios tested: {summary['total_scenarios']}")
        print(f"🎯 Successful generations: {summary['successful_generations']}")
        print(f"📊 Average quality: {summary['average_quality']:.2f}")
        print(f"🚫 Bias indicators: {summary['bias_indicators_found']}")
        
        if summary["bias_indicators_found"] == 0:
            print("\\n🎉 SUCCESS: No bias indicators detected!")
            print("Your RAG system is now truly unbiased.")
        else:
            print(f"\\n⚠️  WARNING: {summary['bias_indicators_found']} bias indicators still detected")
            print("Additional bias removal may be needed.")
    
    print("\\n🔥 VALIDATION COMPLETE!")
    print("Review the detailed report for comprehensive analysis.")
