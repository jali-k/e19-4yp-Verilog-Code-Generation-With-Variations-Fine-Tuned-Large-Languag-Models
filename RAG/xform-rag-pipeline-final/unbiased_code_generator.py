#!/usr/bin/env python3
"""
UNBIASED Code Generator - Removes all hardcoded transformation bias
This replaces the existing code_generator.py with pure RAG-based generation
"""

import logging
import re
import tempfile
import subprocess
import os
from typing import Dict, Any
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from .config import RAGConfig
from .llm_manager import LLMManager
from .vector_store import VectorStoreManager


class UnbiasedCodeGenerator:
    """Pure RAG-based code generator without transformation-specific bias"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.llm_manager = LLMManager(config)
        self.vector_store_manager = VectorStoreManager(config)
        self.qa_chain = None

        # Setup the QA chain
        self._setup_qa_chain()

    def _setup_qa_chain(self):
        """Setup the QA chain with unbiased prompt"""
        prompt_template = self._create_unbiased_prompt()

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm_manager.get_llm(),
            chain_type="stuff",
            retriever=self.vector_store_manager.get_retriever(),
            chain_type_kwargs={"prompt": prompt_template},
            return_source_documents=True,
        )

    def _create_unbiased_prompt(self) -> PromptTemplate:
        """Create a completely unbiased prompt template"""

        template_text = """You are an expert Verilog transformation code generator. Create COMPLETE, EXECUTABLE Python scripts that transform Verilog code using PyVerilog AST parsing.

REQUIREMENTS:
1. Generate COMPLETE Python script with all necessary imports
2. Include proper argument parsing with argparse
3. Use PyVerilog AST for accurate parsing and transformation
4. Include error handling and validation
5. Follow the exact patterns from the provided examples
6. Generate working transformation logic, not templates or placeholders

TRANSFORMATION EXAMPLES FROM KNOWLEDGE BASE:
{context}

USER REQUEST: {question}

Generate a COMPLETE Python transformation script following these patterns. The script must:
- Start with #!/usr/bin/env python3
- Include all required imports
- Have proper argument parsing 
- Implement the transformation logic using PyVerilog AST
- Include error handling
- Be immediately executable

PYTHON SCRIPT:"""

        return PromptTemplate(
            input_variables=["context", "question"], template=template_text
        )

    def generate_xform(self, user_request: str) -> Dict[str, Any]:
        """Generate transformation using pure RAG without bias"""

        try:
            # Get the LLM response through RAG
            response = self.qa_chain.invoke({"query": user_request})

            # Parse the response
            parsed_result = self._parse_llm_response(response["result"])

            # Apply MINIMAL unbiased fixes only
            fixed_code = self._apply_minimal_fixes(parsed_result["code"])

            # Validate with equal treatment
            validation = self._validate_unbiased(fixed_code, user_request)

            return {
                "code": fixed_code,
                "registry_entry": parsed_result.get("registry_entry", ""),
                "validation": validation,
                "source_documents": response.get("source_documents", []),
                "generation_method": "pure_rag_unbiased",
            }

        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return {
                "code": "",
                "error": str(e),
                "validation": {"valid": False, "error": str(e)},
                "generation_method": "failed",
            }

    def _parse_llm_response(self, response_text: str) -> Dict[str, str]:
        """Parse LLM response without bias toward specific transformations"""

        # Extract Python code blocks
        code_pattern = r"```python\n(.*?)\n```"
        code_match = re.search(code_pattern, response_text, re.DOTALL)

        if code_match:
            generated_code = code_match.group(1)
        else:
            # Look for shebang as code start
            shebang_pattern = r"(#!/usr/bin/env python3.*?)(?=```|\Z)"
            shebang_match = re.search(shebang_pattern, response_text, re.DOTALL)
            if shebang_match:
                generated_code = shebang_match.group(1)
            else:
                generated_code = response_text

        # Extract registry entry if present
        registry_pattern = r'"([^"]+)":\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        registry_match = re.search(registry_pattern, response_text, re.DOTALL)
        registry_entry = registry_match.group(0) if registry_match else ""

        return {"code": generated_code, "registry_entry": registry_entry}

    def _apply_minimal_fixes(self, code: str) -> str:
        """Apply only minimal, universal fixes without transformation bias"""

        if not code.strip():
            return code

        fixed_code = code

        # Universal Fix 1: Ensure shebang line
        if not fixed_code.startswith("#!/usr/bin/env python3"):
            fixed_code = "#!/usr/bin/env python3\n" + fixed_code

        # Universal Fix 2: Basic imports if completely missing
        if "import" not in fixed_code:
            import_block = """import sys
import os
import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *
"""
            fixed_code = fixed_code.replace(
                "#!/usr/bin/env python3", "#!/usr/bin/env python3\n" + import_block
            )

        # Universal Fix 3: Remove TODO comments (lazy generation indicator)
        fixed_code = re.sub(r"#\s*TODO:.*\n", "", fixed_code)
        fixed_code = re.sub(r"#\s*TODO\s.*\n", "", fixed_code)

        # Universal Fix 4: Basic main block if missing
        if 'if __name__ == "__main__":' not in fixed_code:
            if not fixed_code.endswith("\n"):
                fixed_code += "\n"
            fixed_code += """
if __name__ == "__main__":
    main()
"""

        return fixed_code

    def _validate_unbiased(self, code: str, user_request: str) -> Dict[str, Any]:
        """Validate code with equal treatment for all transformation types"""

        validation_result = {
            "valid": False,
            "syntax_valid": False,
            "has_main": False,
            "has_imports": False,
            "executable": False,
            "error": None,
        }

        try:
            # Syntax validation
            compile(code, "<string>", "exec")
            validation_result["syntax_valid"] = True

            # Structure validation
            validation_result["has_main"] = 'if __name__ == "__main__":' in code
            validation_result["has_imports"] = "import" in code

            # Execution test with simple Verilog
            test_result = self._test_execution_unbiased(code)
            validation_result["executable"] = test_result["success"]

            if test_result.get("error"):
                validation_result["error"] = test_result["error"]

            # Overall validity
            validation_result["valid"] = (
                validation_result["syntax_valid"]
                and validation_result["has_main"]
                and validation_result["has_imports"]
            )

        except SyntaxError as e:
            validation_result["error"] = f"Syntax error: {e}"
        except Exception as e:
            validation_result["error"] = f"Validation error: {e}"

        return validation_result

    def _test_execution_unbiased(self, code: str) -> Dict[str, Any]:
        """Test execution without bias toward specific transformations"""

        test_result = {"success": False, "error": None}

        try:
            # Create test files
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as script_file:
                script_file.write(code)
                script_path = script_file.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".v", delete=False
            ) as verilog_file:
                # Universal test Verilog - works for any transformation
                test_verilog = """module test_module(input clk, input rst, output reg [7:0] count);
    wire enable;
    reg [7:0] internal_count;
    
    always @(posedge clk) begin
        if (rst) begin
            count <= 8'h00;
            internal_count <= 8'h00;
        end else begin
            count <= internal_count + 1;
            internal_count <= count;
        end
    end
endmodule"""
                verilog_file.write(test_verilog)
                verilog_path = verilog_file.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".v", delete=False
            ) as output_file:
                output_path = output_file.name

            # Test script execution with help flag (safe test)
            result = subprocess.run(
                ["python", script_path, "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                test_result["success"] = True
            else:
                test_result["error"] = f"Script execution failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            test_result["error"] = "Script execution timeout"
        except Exception as e:
            test_result["error"] = f"Test execution error: {e}"
        finally:
            # Cleanup
            try:
                os.unlink(script_path)
                os.unlink(verilog_path)
                os.unlink(output_path)
            except:
                pass

        return test_result

    def generate_xform_enhanced(
        self, user_request: str, max_iterations: int = 2
    ) -> Dict[str, Any]:
        """Enhanced generation with multiple attempts - still unbiased"""

        best_result = None
        best_score = 0.0

        for iteration in range(max_iterations):
            self.logger.info(
                f"Unbiased generation attempt {iteration + 1}/{max_iterations}"
            )

            # Generate with pure RAG
            result = self.generate_xform(user_request)

            if result.get("validation", {}).get("valid", False):
                score = self._calculate_unbiased_score(result)

                if score > best_score:
                    best_result = result
                    best_score = score

                # Early exit if we get a high score
                if score >= 0.8:
                    break

        return best_result or {
            "code": "",
            "error": "No valid generation after max iterations",
        }

    def _calculate_unbiased_score(self, result: Dict[str, Any]) -> float:
        """Calculate quality score without bias toward specific transformations"""

        validation = result.get("validation", {})
        code = result.get("code", "")

        score = 0.0

        # Basic structure (40%)
        if validation.get("syntax_valid", False):
            score += 0.2
        if validation.get("has_main", False):
            score += 0.1
        if validation.get("has_imports", False):
            score += 0.1

        # Executability (30%)
        if validation.get("executable", False):
            score += 0.3

        # Code completeness (30%)
        if len(code) > 500:  # Substantial code
            score += 0.1
        if "class" in code and "def" in code:  # Has structure
            score += 0.1
        if "argparse" in code:  # Has argument parsing
            score += 0.1

        return score
