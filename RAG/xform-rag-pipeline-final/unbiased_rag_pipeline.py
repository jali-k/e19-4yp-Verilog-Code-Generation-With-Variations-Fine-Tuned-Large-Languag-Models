#!/usr/bin/env python3
"""
Unbiased Intelligent RAG Pipeline for Xform Generation
Removes all hardcoded biases and enables true generative capabilities
"""

from typing import Dict, Any, List
import logging
import re
from pathlib import Path


class UnbiasedCodeGenerator:
    """Completely unbiased code generator that relies purely on RAG"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components WITHOUT biased fixing
        from .llm_manager import LLMManager
        from .vector_store import VectorStoreManager

        self.llm_manager = LLMManager(config)
        self.vector_store_manager = VectorStoreManager(config)

        # Setup unbiased generation chain
        self._setup_unbiased_chain()

    def _setup_unbiased_chain(self):
        """Setup RAG chain with purely pattern-based prompting"""
        from langchain.chains import RetrievalQA
        from langchain.prompts import PromptTemplate

        # Create truly unbiased prompt
        template = """You are an expert Verilog transformation generator. Analyze the provided examples and create a COMPLETE, FUNCTIONAL Python script.

EXAMPLE TRANSFORMATIONS (use these as patterns only):
{context}

USER REQUEST: {question}

INSTRUCTIONS:
1. Analyze the user request to understand the transformation type
2. Study the similar patterns from the examples
3. Generate COMPLETE working code following the established patterns
4. Use PyVerilog AST for analysis and regex for modifications
5. Implement ALL logic without placeholders or TODO comments
6. Follow the common pattern: parse → analyze → transform → save

REQUIRED STRUCTURE:
- Complete imports (sys, os, re, argparse, pyverilog)
- TransformationVisitor class with __init__ and visit methods
- transform_operation function with full logic
- main() function with proper argument parsing
- Error handling throughout

Generate the COMPLETE transformation script now:"""

        prompt_template = PromptTemplate(
            template=template, input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm_manager.get_llm(),
            chain_type="stuff",
            retriever=self.vector_store_manager.get_retriever(),
            chain_type_kwargs={"prompt": prompt_template},
            return_source_documents=True,
        )

    def generate_xform_unbiased(self, user_request: str) -> Dict[str, Any]:
        """Generate transformation using pure RAG without bias"""

        result = {
            "code": "",
            "method": "pure_rag",
            "success": False,
            "error": None,
            "sources": [],
        }

        try:
            # Pure RAG generation
            response = self.qa_chain.invoke({"query": user_request})

            # Extract code without biased fixing
            generated_code = self._extract_code_clean(response["result"])

            # Only apply minimal syntax fixes (no transformation-specific bias)
            clean_code = self._apply_minimal_fixes(generated_code)

            result.update(
                {
                    "code": clean_code,
                    "success": True,
                    "sources": [
                        doc.metadata.get("source", "")
                        for doc in response.get("source_documents", [])
                    ],
                }
            )

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Pure RAG generation failed: {e}")

        return result

    def _extract_code_clean(self, response_text: str) -> str:
        """Extract code without any bias injection"""

        # Look for Python code blocks
        code_pattern = r"```python\n(.*?)\n```"
        code_match = re.search(code_pattern, response_text, re.DOTALL)

        if code_match:
            return code_match.group(1)

        # Look for shebang-started code
        shebang_pattern = r"(#!/usr/bin/env python3.*)"
        shebang_match = re.search(shebang_pattern, response_text, re.DOTALL)

        if shebang_match:
            return shebang_match.group(1)

        # Return cleaned response
        return response_text.strip()

    def _apply_minimal_fixes(self, code: str) -> str:
        """Apply only essential syntax fixes, no transformation bias"""

        fixed_code = code

        # Fix 1: Ensure shebang
        if not fixed_code.startswith("#!/usr/bin/env python3"):
            fixed_code = "#!/usr/bin/env python3\n" + fixed_code

        # Fix 2: Remove markdown artifacts
        fixed_code = re.sub(r"```python\n?", "", fixed_code)
        fixed_code = re.sub(r"\n?```", "", fixed_code)

        # Fix 3: Basic import checks (but don't inject specific logic)
        required_imports = [
            "import sys",
            "import os",
            "import re",
            "import argparse",
            "from pyverilog.vparser.parser import parse",
            "from pyverilog.vparser.ast import *",
        ]

        for import_stmt in required_imports:
            if (
                import_stmt not in fixed_code
                and import_stmt.split()[-1] not in fixed_code
            ):
                # Add missing import after shebang
                lines = fixed_code.split("\n")
                if lines[0].startswith("#!/usr/bin/env python3"):
                    lines.insert(1, import_stmt)
                    fixed_code = "\n".join(lines)

        # Fix 4: Remove excessive whitespace
        fixed_code = re.sub(r"\n{3,}", "\n\n", fixed_code)

        # Fix 5: Ensure proper main execution
        if (
            "def main():" in fixed_code
            and 'if __name__ == "__main__"' not in fixed_code
        ):
            fixed_code += '\n\nif __name__ == "__main__":\n    sys.exit(main())'

        return fixed_code.strip()


class UnbiasedEvaluator:
    """Evaluation system that doesn't favor specific transformations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def evaluate_transformation_unbiased(
        self, generated_code: str, test_verilog: str, transformation_args: List[str]
    ) -> Dict[str, Any]:
        """Evaluate any transformation type without bias"""

        import tempfile
        import subprocess
        import sys

        result = {
            "syntax_valid": False,
            "executes": False,
            "transforms_content": False,
            "error": None,
            "execution_time": 0.0,
            "output_content": "",
            "stdout": "",
            "stderr": "",
        }

        try:
            # Step 1: Syntax validation
            try:
                compile(generated_code, "<string>", "exec")
                result["syntax_valid"] = True
            except SyntaxError as e:
                result["error"] = f"Syntax error: {e}"
                return result

            # Step 2: Execution test
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as script_file:
                script_file.write(generated_code)
                script_path = script_file.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".v", delete=False
            ) as input_file:
                input_file.write(test_verilog)
                input_path = input_file.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".v", delete=False
            ) as output_file:
                output_path = output_file.name

            # Execute the transformation
            cmd = [
                sys.executable,
                script_path,
                input_path,
                output_path,
            ] + transformation_args

            import time

            start_time = time.time()
            process_result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            end_time = time.time()

            result.update(
                {
                    "executes": process_result.returncode == 0,
                    "execution_time": end_time - start_time,
                    "stdout": process_result.stdout,
                    "stderr": process_result.stderr,
                }
            )

            # Step 3: Content transformation check
            if result["executes"] and Path(output_path).exists():
                with open(output_path, "r") as f:
                    output_content = f.read()

                result["output_content"] = output_content
                result["transforms_content"] = (
                    output_content.strip() != test_verilog.strip()
                )

            # Cleanup
            for path in [script_path, input_path, output_path]:
                try:
                    Path(path).unlink()
                except:
                    pass

        except Exception as e:
            result["error"] = str(e)

        return result


class UnbiasedTestFramework:
    """Test framework that treats all transformations equally"""

    def __init__(self, generator: UnbiasedCodeGenerator):
        self.generator = generator
        self.evaluator = UnbiasedEvaluator()
        self.logger = logging.getLogger(__name__)

    def run_unbiased_test_suite(
        self, test_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run comprehensive tests without favoring any transformation type"""

        results = {
            "total_tests": len(test_scenarios),
            "successful_generations": 0,
            "successful_executions": 0,
            "successful_transformations": 0,
            "test_results": [],
            "summary": {},
        }

        for scenario in test_scenarios:
            self.logger.info(f"Testing: {scenario['name']}")

            # Generate without bias
            generation_result = self.generator.generate_xform_unbiased(
                scenario["request"]
            )

            test_result = {
                "scenario": scenario["name"],
                "generation_success": generation_result["success"],
                "generation_method": "pure_rag",
                "evaluation": {},
            }

            if generation_result["success"]:
                results["successful_generations"] += 1

                # Evaluate without bias
                evaluation = self.evaluator.evaluate_transformation_unbiased(
                    generation_result["code"],
                    scenario["test_verilog"],
                    scenario["test_args"],
                )

                test_result["evaluation"] = evaluation

                if evaluation["executes"]:
                    results["successful_executions"] += 1

                if evaluation["transforms_content"]:
                    results["successful_transformations"] += 1

            results["test_results"].append(test_result)

        # Calculate unbiased metrics
        results["summary"] = {
            "generation_rate": results["successful_generations"]
            / results["total_tests"],
            "execution_rate": results["successful_executions"] / results["total_tests"],
            "transformation_rate": results["successful_transformations"]
            / results["total_tests"],
        }

        return results


def create_unbiased_pipeline(config) -> UnbiasedCodeGenerator:
    """Factory function to create unbiased pipeline"""
    return UnbiasedCodeGenerator(config)
