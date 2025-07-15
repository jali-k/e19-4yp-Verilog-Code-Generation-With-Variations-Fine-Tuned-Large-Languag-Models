#!/usr/bin/env python3
"""
Code generation engine for the Xform RAG Pipeline
Handles the core RAG logic for generating transformations
"""

import logging
import re
from typing import Dict, Any
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from .config import RAGConfig
from .llm_manager import LLMManager
from .vector_store import VectorStoreManager


class CodeGenerator:
    """Generates xform code using RAG pipeline"""

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
        """Setup the QA chain with custom prompt"""
        prompt_template = self._create_prompt_template()

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm_manager.get_llm(),
            chain_type="stuff",
            retriever=self.vector_store_manager.get_retriever(),
            chain_type_kwargs={"prompt": prompt_template},
            return_source_documents=True,
        )

    def _create_prompt_template(self) -> PromptTemplate:
        """Create a balanced, flexible prompt template for any xform generation"""
        template_text = """
        You are an expert Verilog transformation code generator. You must create COMPLETE, EXECUTABLE Python scripts that transform Verilog code using PyVerilog AST parsing and regex-based modifications.

        CONTEXT: Here are examples of existing working transformations:
        {context}

        USER REQUEST: {question}

        CRITICAL REQUIREMENTS - FOLLOW EXACTLY:
        1. START with proper shebang: #!/usr/bin/env python3
        2. CREATE a visitor class that inherits from no base class (plain Python class)
        3. IMPLEMENT a complete transform function with signature: transform_[name](input_file, output_file, ...)
        4. INCLUDE complete main() function with argparse
        5. USE PyVerilog AST for ANALYSIS ONLY - identify what to change
        6. USE regex for ACTUAL TRANSFORMATIONS - modify the text directly
        7. HANDLE all errors with try/except blocks
        8. RETURN True/False for success/failure
        9. ABSOLUTELY NO TODO COMMENTS - implement everything completely
        10. NO PLACEHOLDER CODE - all logic must be functional

        MANDATORY STRUCTURE PATTERN:
        ```python
        #!/usr/bin/env python3
        \"\"\"
        [Brief description of what this transformation does]
        \"\"\"

        import sys
        import os
        import re
        import argparse
        from pyverilog.vparser.parser import parse
        from pyverilog.vparser.ast import *

        class [TransformationName]Visitor:
            \"\"\"AST visitor that identifies elements to transform.\"\"\"

            def __init__(self, [required_params]):
                self.[required_params] = [required_params]
                self.changes_made = []
                self.target_elements = []

            def visit(self, node):
                \"\"\"Visit AST nodes and identify transformation targets.\"\"\"
                if isinstance(node, Node):
                    # ANALYZE what needs to be transformed based on user request
                    # Examples:
                    # - For wire/reg changes: check isinstance(node, Decl) and item types
                    # - For signal renaming: check isinstance(node, Identifier) 
                    # - For module changes: check isinstance(node, ModuleDef)
                    # - For port changes: check isinstance(node, Ioport)
                    # - For width changes: check node.width attributes
                    # - For counter/enable: check isinstance(node, NonblockingSubstitution)
                    
                    # STORE information about what was found
                    # Always append to self.target_elements and self.changes_made
                    
                    # ALWAYS visit children
                    for child in node.children():
                        self.visit(child)

        def transform_[name](input_file, output_file, [required_params]):
            \"\"\"
            Main transformation function.
            
            Returns:
                bool: True if successful, False otherwise
            \"\"\"
            try:
                # Read input file
                with open(input_file, "r") as f:
                    content = f.read()

                # Parse with PyVerilog to analyze structure
                ast, directives = parse([input_file])

                # Use visitor to identify what needs to be changed
                visitor = [TransformationName]Visitor([params])
                visitor.visit(ast)

                # Check if anything was found to transform
                if not visitor.changes_made:
                    print("Warning: No targets found for transformation")
                    return False

                # Apply transformations using regex on the original text
                modified_content = content
                for element in visitor.target_elements:
                    # Use regex to make the actual text changes
                    # Pattern depends on transformation type:
                    # - Wire to reg: rf"\\bwire\\s+{name}\\b" -> f"reg {name}"
                    # - Signal rename: rf"\\b{old_name}\\b" -> f"{new_name}"
                    # - Width change: rf"\\[{old_width}\\]" -> f"[{new_width}]"
                    # - Add ports: insert into module declaration
                    # - Enable logic: wrap statements with if conditions
                    pass  # Implement specific regex transformations here

                # Write output
                with open(output_file, "w") as f:
                    f.write(modified_content)

                print(f"Transformation completed. Output: {output_file}")
                return True

            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
                return False

        def main():
            \"\"\"Command line interface.\"\"\"
            parser = argparse.ArgumentParser(description="[Description]")
            parser.add_argument("input_file", help="Input Verilog file")
            parser.add_argument("output_file", help="Output Verilog file")
            # Add transformation-specific arguments here
            
            args = parser.parse_args()

            if not os.path.exists(args.input_file):
                print(f"Error: Input file '{args.input_file}' not found")
                return 1

            success = transform_[name](args.input_file, args.output_file, [args])
            return 0 if success else 1

        if __name__ == "__main__":
            sys.exit(main())
        ```

        ANALYSIS PATTERNS FOR DIFFERENT TRANSFORMATIONS:
        - Wire/Reg conversions: Look for Decl nodes containing Wire or Reg items
        - Signal renaming: Look for Identifier nodes with target name
        - Module modifications: Look for ModuleDef nodes  
        - Port changes: Look for Ioport nodes in portlist
        - Width changes: Look for nodes with width attributes
        - Enable/control logic: Look for assignment statements (NonblockingSubstitution)
        - Reset condition changes: Look for if statements with reset conditions

        REGEX TRANSFORMATION PATTERNS:
        - Simple replacements: Use re.sub() with word boundaries \\b
        - Structured changes: Use capturing groups and replacement functions
        - Multi-line patterns: Use re.DOTALL flag for module declarations
        - Preserve formatting: Match and preserve indentation patterns

        GENERATE code that implements the SPECIFIC transformation requested.
        DO NOT use the hardcoded examples above - adapt the pattern to the user's request.
        ENSURE every function is complete and executable.
        """

        return PromptTemplate(
            template=template_text, input_variables=["context", "question"]
        )

    def generate_xform(self, user_request: str) -> Dict[str, Any]:
        """
        Generate a new transformation based on user request
        This method now uses the enhanced generation with validation

        Args:
            user_request: Description of the desired transformation

        Returns:
            Dictionary containing generated code and metadata
        """
        return self.generate_xform_enhanced(user_request, max_iterations=2)

    def _parse_llm_response(self, response_text: str) -> Dict[str, str]:
        """Parse the LLM response to extract code and registry entry"""
        # Extract the main code block from python code blocks
        code_pattern = r"```python\n(#!/usr/bin/env python3.*?)\n```"
        code_match = re.search(code_pattern, response_text, re.DOTALL)

        if code_match:
            generated_code = code_match.group(1)
        else:
            # Fallback: look for shebang line as start of code
            shebang_pattern = r"(#!/usr/bin/env python3.*?)(?=```|\n```|\Z)"
            shebang_match = re.search(shebang_pattern, response_text, re.DOTALL)
            if shebang_match:
                generated_code = shebang_match.group(1)
            else:
                # Last resort: use the whole response
                generated_code = response_text

        # Extract registry entry with better pattern matching
        registry_pattern = r'"([^"]+)":\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        registry_match = re.search(registry_pattern, response_text, re.DOTALL)
        registry_entry = registry_match.group(0) if registry_match else ""

        # Clean up the code more thoroughly
        generated_code = self._clean_generated_code(generated_code)

        # Additional validation and fixing
        generated_code = self._fix_common_issues(generated_code)

        # If code is still incomplete, inject template structure
        # (This will be passed the user_request when available)

        return {"code": generated_code, "registry_entry": registry_entry}

    def _fix_common_issues(self, code: str) -> str:
        """Fix common issues in generated code and eliminate ALL TODO sections"""

        # AGGRESSIVELY remove ANY TODO comments
        if "TODO" in code or "# TODO" in code:
            self.logger.warning("Found TODO comments in generated code, removing them")

            lines = code.split("\n")
            filtered_lines = []

            for line in lines:
                if "TODO" in line or "# TODO" in line:
                    # Skip TODO lines entirely
                    self.logger.warning(f"Removed TODO line: {line.strip()}")
                    continue
                else:
                    filtered_lines.append(line)

            code = "\n".join(filtered_lines)

        # Ensure proper imports are present
        required_imports = [
            "import sys",
            "import os",
            "import re",
            "import argparse",
            "from pyverilog.vparser.parser import parse",
            "from pyverilog.vparser.ast import *",
        ]

        # Check if imports are missing and add them after shebang/docstring
        for import_stmt in required_imports:
            if import_stmt not in code:
                # Find insertion point (after docstring if present)
                docstring_end = code.find('"""', code.find('"""') + 3)
                if docstring_end != -1:
                    docstring_end += 3
                    while docstring_end < len(code) and code[docstring_end] in " \n":
                        docstring_end += 1
                    code = (
                        code[:docstring_end] + import_stmt + "\n" + code[docstring_end:]
                    )
                else:
                    # No docstring, add after shebang
                    shebang_end = code.find("\n") + 1
                    code = code[:shebang_end] + import_stmt + "\n" + code[shebang_end:]

        # Ensure proper main execution
        if "def main():" in code and "sys.exit(main())" not in code:
            if not code.strip().endswith("sys.exit(main())"):
                code = (
                    code.rstrip()
                    + '\n\nif __name__ == "__main__":\n    sys.exit(main())\n'
                )

        # Ensure visitor classes have proper node checking
        if "def visit(self, node):" in code and "isinstance(node, Node)" not in code:
            # Add proper node type checking to visit methods
            visit_pattern = (
                r"(def visit\(self, node\):\s*\n)(.*?)(\n.*?for.*?node\.children)"
            )

            def add_node_check(match):
                method_def = match.group(1)
                docstring = match.group(2) if '"""' in match.group(2) else ""
                children_visit = match.group(3)

                node_check = "        if isinstance(node, Node):\n            # Process the node based on its type\n"
                return method_def + docstring + node_check + children_visit

            code = re.sub(visit_pattern, add_node_check, code, flags=re.DOTALL)

        return code

    def _clean_generated_code(self, code: str) -> str:
        """Clean up generated code"""
        # Remove any extra markdown formatting
        code = re.sub(r"^```python\n?", "", code)
        code = re.sub(r"\n?```$", "", code)

        # Ensure proper shebang
        if not code.startswith("#!/usr/bin/env python3"):
            code = "#!/usr/bin/env python3\n" + code

        # Remove excessive blank lines
        code = re.sub(r"\n{3,}", "\n\n", code)

        return code.strip()

    def _generate_filename(self, user_request: str) -> str:
        """Generate appropriate filename from user request"""
        # Clean and create filename
        clean_request = re.sub(r"[^a-zA-Z0-9\s]", "", user_request.lower())
        words = clean_request.split()[:4]  # Take first 4 words
        filename = f"xform_{'_'.join(words)}.py"

        # Ensure it's a valid filename
        filename = re.sub(r"[^a-zA-Z0-9_.]", "_", filename)

        return filename

    def validate_generated_code(self, code: str) -> Dict[str, Any]:
        """Comprehensive validation of the generated code"""
        validation_result = {
            "is_valid": True,
            "syntax_errors": [],
            "warnings": [],
            "missing_components": [],
            "has_main": False,
            "has_docstring": False,
            "has_visitor": False,
            "has_transform_function": False,
            "has_proper_imports": False,
            "has_error_handling": False,
            "has_argparse": False,
            "completeness_score": 0.0,
        }

        try:
            # Check syntax
            compile(code, "<generated>", "exec")
        except SyntaxError as e:
            validation_result["is_valid"] = False
            validation_result["syntax_errors"].append(f"Line {e.lineno}: {e.msg}")
            return validation_result  # Return early if syntax is broken
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["syntax_errors"].append(f"Compilation error: {e}")
            return validation_result

        # Check for required components
        components_found = 0
        total_components = 7

        # 1. Check for main function
        if "def main(" in code:
            validation_result["has_main"] = True
            components_found += 1
        else:
            validation_result["missing_components"].append("main() function")

        # 2. Check for docstring
        if '"""' in code or "'''" in code:
            validation_result["has_docstring"] = True
            components_found += 1
        else:
            validation_result["missing_components"].append("module docstring")

        # 3. Check for visitor class
        if "class" in code and "Visitor" in code:
            validation_result["has_visitor"] = True
            components_found += 1
        else:
            validation_result["missing_components"].append("visitor class")

        # 4. Check for transform function
        if "def transform_" in code:
            validation_result["has_transform_function"] = True
            components_found += 1
        else:
            validation_result["missing_components"].append("transform function")

        # 5. Check for proper imports
        required_imports = [
            "from pyverilog.vparser.parser import parse",
            "from pyverilog.vparser.ast import",
            "import argparse",
        ]
        import_count = sum(1 for imp in required_imports if imp in code)
        if import_count >= 2:  # At least pyverilog imports
            validation_result["has_proper_imports"] = True
            components_found += 1
        else:
            validation_result["missing_components"].append("required imports")

        # 6. Check for error handling
        if "try:" in code and "except" in code:
            validation_result["has_error_handling"] = True
            components_found += 1
        else:
            validation_result["missing_components"].append("error handling")

        # 7. Check for argument parsing
        if "argparse.ArgumentParser" in code or "parser.add_argument" in code:
            validation_result["has_argparse"] = True
            components_found += 1
        else:
            validation_result["missing_components"].append("argument parsing")

        # Calculate completeness score
        validation_result["completeness_score"] = components_found / total_components

        # Additional warnings for quality
        if "def visit(self, node):" in code and "isinstance(node, Node)" not in code:
            validation_result["warnings"].append(
                "Visitor method missing proper node type checking"
            )

        if "return True" not in code or "return False" not in code:
            validation_result["warnings"].append(
                "Transform function missing proper return values"
            )

        if "changes_made" not in code:
            validation_result["warnings"].append("No tracking of changes made")

        # Check for TODO comments - this should fail validation
        if "TODO" in code or "# TODO" in code:
            validation_result["is_valid"] = False
            validation_result["warnings"].append(
                "Code contains TODO comments - must be complete"
            )

        if validation_result["completeness_score"] < 0.6:
            validation_result["is_valid"] = False

        return validation_result

    def test_connection(self) -> bool:
        """Test if the code generator is working"""
        try:
            # Test LLM connection
            if not self.llm_manager.test_connection():
                return False

            # Test vector store
            docs = self.vector_store_manager.search_similar("test", k=1)
            if not docs:
                self.logger.warning("No documents found in vector store")
                return False

            self.logger.info("Code generator test successful")
            return True

        except Exception as e:
            self.logger.error(f"Code generator test failed: {e}")
            return False

    def generate_xform_enhanced(
        self, user_request: str, max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a new transformation with iterative improvement

        Args:
            user_request: Description of the desired transformation
            max_iterations: Maximum number of improvement iterations

        Returns:
            Dictionary containing generated code and metadata
        """
        self.logger.info(f"Generating enhanced xform for request: {user_request}")

        best_result = None
        best_score = 0.0

        for iteration in range(max_iterations):
            self.logger.info(f"Iteration {iteration + 1}/{max_iterations}")

            try:
                # Modify the request for subsequent iterations
                if iteration > 0 and best_result:
                    # Add feedback from previous iteration
                    validation = best_result.get("validation", {})
                    missing_components = validation.get("missing_components", [])

                    if missing_components:
                        enhanced_request = f"""
                        {user_request}
                        
                        IMPORTANT: The previous attempt was missing these critical components:
                        {', '.join(missing_components)}
                        
                        Ensure the generated code includes ALL required components:
                        - Complete visitor class with proper AST traversal
                        - Main transform function with correct signature  
                        - Proper error handling with try/except blocks
                        - Complete argument parsing with argparse
                        - All required imports (pyverilog, sys, os, re, argparse)
                        - Executable main() function that calls sys.exit()
                        """
                    else:
                        enhanced_request = user_request
                else:
                    enhanced_request = user_request

                # Query the RAG system
                result = self.qa_chain.invoke({"query": enhanced_request})

                # Parse the response
                parsed_result = self._parse_llm_response(result["result"])

                # Apply template injection if needed
                parsed_result["code"] = self._inject_template_structure(
                    parsed_result["code"], user_request
                )

                # Validate the generated code
                validation_result = self.validate_generated_code(parsed_result["code"])

                # Generate filename
                filename = self._generate_filename(user_request)

                current_result = {
                    "filename": filename,
                    "code": parsed_result["code"],
                    "registry_entry": parsed_result["registry_entry"],
                    "source_documents": [
                        doc.metadata.get("filename")
                        for doc in result["source_documents"]
                    ],
                    "user_request": user_request,
                    "llm_response": result["result"],
                    "validation": validation_result,
                    "iteration": iteration + 1,
                    "completeness_score": validation_result.get(
                        "completeness_score", 0.0
                    ),
                }

                # Check if this is the best result so far
                current_score = validation_result.get("completeness_score", 0.0)
                if current_score > best_score:
                    best_score = current_score
                    best_result = current_result

                # If we achieved high quality, stop early
                if validation_result.get("is_valid", False) and current_score >= 0.85:
                    self.logger.info(
                        f"High quality result achieved in iteration {iteration + 1}"
                    )
                    break

            except Exception as e:
                self.logger.error(f"Error in iteration {iteration + 1}: {e}")
                if best_result is None:
                    return {"error": str(e), "user_request": user_request}

        if best_result:
            self.logger.info(
                f"Best result: score {best_score:.2f} from iteration {best_result['iteration']}"
            )
            return best_result
        else:
            return {
                "error": "Failed to generate valid code after all iterations",
                "user_request": user_request,
            }

    def _inject_template_structure(self, code: str, user_request: str) -> str:
        """Inject minimal template structure if the generated code is incomplete"""

        # Only inject if code is severely incomplete (missing basic structure)
        if not code.strip() or len(code.strip()) < 100:
            # Generate a minimal template based on user request
            transform_name = self._generate_transform_name(user_request)

            template = f'''#!/usr/bin/env python3
"""
{user_request}
"""

import sys
import os
import re
import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *

class {transform_name.title()}Visitor:
    """AST visitor for transformation analysis."""
    
    def __init__(self):
        self.changes_made = []
        self.target_elements = []
    
    def visit(self, node):
        """Visit AST nodes and identify transformation targets."""
        if isinstance(node, Node):
            # Analysis logic will be generated by LLM
            for child in node.children():
                self.visit(child)

def transform_{transform_name}(input_file, output_file):
    """Main transformation function."""
    try:
        with open(input_file, "r") as f:
            content = f.read()
        
        ast, directives = parse([input_file])
        visitor = {transform_name.title()}Visitor()
        visitor.visit(ast)
        
        # Transformation logic will be generated by LLM
        modified_content = content
        
        with open(output_file, "w") as f:
            f.write(modified_content)
        
        return True
    except Exception as e:
        print(f"Error: {{e}}")
        return False

def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(description="{user_request}")
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found")
        return 1
    
    success = transform_{transform_name}(args.input_file, args.output_file)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
'''
            return template

        return code

    def _generate_transform_name(self, user_request: str) -> str:
        """Generate a transform name from user request"""
        # Extract key words and create a name
        words = re.findall(r"\b\w+\b", user_request.lower())
        # Filter out common words
        filtered_words = [
            w
            for w in words
            if w
            not in [
                "a",
                "an",
                "the",
                "to",
                "from",
                "and",
                "or",
                "with",
                "in",
                "on",
                "for",
            ]
        ]
        # Take first few meaningful words
        name_words = filtered_words[:3] if len(filtered_words) >= 3 else filtered_words
        return "_".join(name_words) if name_words else "custom_transform"
        template = f'''#!/usr/bin/env python3
"""
{description}
"""

import sys
import os
import re
import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *


class FindCounterVisitor:
    """
    AST visitor that identifies counter increment statements.
    """

    def __init__(self, counter_name):
        self.counter_name = counter_name
        self.changes_made = []
        self.counter_increments = []
        self.module_name = None
        self.ports = []

    def visit(self, node):
        """Visit a node and identify counter increments."""
        if isinstance(node, Node):
            # Get the module name
            if isinstance(node, ModuleDef):
                self.module_name = node.name
                # Collect ports to check if enable signal already exists
                for item in node.portlist.ports:
                    if isinstance(item, Ioport) and hasattr(item.first, "name"):
                        self.ports.append(item.first.name)

            # Find counter increments (x <= x + 1)
            if isinstance(node, NonblockingSubstitution):
                # Check if left side is the counter
                lhs = node.left
                if isinstance(lhs, Identifier) and lhs.name == self.counter_name:
                    # Check if right side is counter + 1
                    rhs = node.right
                    if (
                        isinstance(rhs, Plus)
                        and isinstance(rhs.left, Identifier)
                        and rhs.left.name == self.counter_name
                    ):
                        if isinstance(rhs.right, IntConst) and rhs.right.value == "1":
                            # Found a counter increment
                            self.counter_increments.append({{
                                "statement": node,
                                "line": getattr(node, "lineno", None),
                            }})
                            self.changes_made.append(
                                f"Added enable condition to '{{self.counter_name}}' increment"
                            )

            # Continue visiting all child nodes
            for child in node.children():
                self.visit(child)


def transform_{transform_name}(input_file, output_file, enable_name, counter_name):
    """
    Add an enable signal to a counter.

    Args:
        input_file (str): Path to input Verilog file
        output_file (str): Path to output Verilog file
        enable_name (str): Name of the enable signal to add
        counter_name (str): Name of the counter to control

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the input file
        with open(input_file, "r") as f:
            content = f.read()

        # Parse the Verilog file to get the AST
        ast, directives = parse([input_file])

        # Create and apply the visitor to identify counter increments
        visitor = FindCounterVisitor(counter_name)
        visitor.visit(ast)

        # Check if counter increments were found
        if not visitor.counter_increments:
            print(f"Warning: No increment statements found for counter '{{counter_name}}'")
            return False

        # Check if enable signal already exists
        if enable_name in visitor.ports:
            print(f"Warning: Enable signal '{{enable_name}}' already exists in module ports")
            return False

        # Print summary of changes
        for change in visitor.changes_made:
            print(change)

        # Apply transformations using regex
        modified_content = content

        # 1. Add enable signal to port list
        port_pattern = r"(module\\s+\\w+\\s*\\()(.*?)(\\);)"
        def add_enable_port(match):
            module_decl = match.group(1)
            ports = match.group(2).strip()
            module_end = match.group(3)
            
            if ports:
                return f"{{module_decl}}{{ports}},\\n    input {{enable_name}}{{module_end}}"
            else:
                return f"{{module_decl}}input {{enable_name}}{{module_end}}"

        modified_content = re.sub(port_pattern, add_enable_port, modified_content, flags=re.DOTALL)

        # 2. Wrap counter increments with enable condition
        increment_pattern = rf"(\\s*)({{counter_name}}\\s*<=\\s*{{counter_name}}\\s*\\+\\s*1\\s*;)"
        def wrap_with_enable(match):
            indent = match.group(1)
            statement = match.group(2)
            return f"{{indent}}if ({{enable_name}})\\n{{indent}}    {{statement}}"

        modified_content = re.sub(increment_pattern, wrap_with_enable, modified_content)

        # Write the modified content to the output file
        with open(output_file, "w") as f:
            f.write(modified_content)

        print(f"Output written to {{output_file}}")
        return True

    except Exception as e:
        print(f"Error processing file: {{e}}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to parse command line arguments and process the file."""
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    parser.add_argument("enable_name", help="Name of the enable signal to add")
    parser.add_argument("counter_name", help="Name of the counter to control")

    args = parser.parse_args()

    # Ensure input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{{args.input_file}}' not found")
        return 1

    # Process the file
    success = transform_{transform_name}(args.input_file, args.output_file, args.enable_name, args.counter_name)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
'''
        return template

    def _get_generic_template(self, transform_name: str, description: str) -> str:
        """Get generic template for other transformations"""
        template = f'''#!/usr/bin/env python3
"""
{description}
"""

import sys
import os
import re
import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *


class {transform_name.title().replace('_', '')}Visitor:
    """
    AST visitor that identifies elements to transform.
    """

    def __init__(self, target_param=None):
        self.target_param = target_param
        self.changes_made = []
        self.target_elements = []

    def visit(self, node):
        """Visit a node and identify transformation targets."""
        if isinstance(node, Node):
            # Check for declarations and identifiers
            if isinstance(node, Decl):
                for item in node.list:
                    if hasattr(item, "name"):
                        self.target_elements.append({{"name": item.name, "type": type(item).__name__.lower()}})
                        self.changes_made.append(f"Found {{type(item).__name__.lower()}} '{{item.name}}'")
            
            elif isinstance(node, Identifier) and self.target_param:
                if node.name == self.target_param:
                    self.target_elements.append({{"type": "identifier", "name": node.name}})
                    self.changes_made.append(f"Found identifier '{{node.name}}'")
            
            elif isinstance(node, ModuleDef):
                self.target_elements.append({{"type": "module", "name": node.name}})
                self.changes_made.append(f"Found module '{{node.name}}'")
            
            # Visit children
            for child in node.children():
                self.visit(child)


def transform_{transform_name}(input_file, output_file, target_param=None):
    """
    Main transformation function.

    Args:
        input_file (str): Path to input Verilog file
        output_file (str): Path to output Verilog file
        target_param: Target parameter for transformation

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the input file
        with open(input_file, "r") as f:
            content = f.read()

        # Parse the Verilog file to get the AST
        ast, directives = parse([input_file])

        # Create and apply the visitor
        visitor = {transform_name.title().replace('_', '')}Visitor(target_param)
        visitor.visit(ast)

        # Check if any changes were identified
        if not visitor.changes_made:
            print("Warning: No changes identified")
            return False

        # Print summary of changes
        for change in visitor.changes_made:
            print(change)

        # Apply transformations using regex
        modified_content = content
        
        # Generic transformation logic - customize based on specific needs
        for element in visitor.target_elements:
            name = element["name"]
            element_type = element.get("type", "")
            
            # Example transformation pattern
            print(f"Processing {{element_type}} '{{name}}'")

        # Write the modified content to the output file
        with open(output_file, "w") as f:
            f.write(modified_content)

        print(f"Output written to {{output_file}}")
        return True

    except Exception as e:
        print(f"Error processing file: {{e}}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to parse command line arguments and process the file."""
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    parser.add_argument("--target", help="Target parameter for transformation")

    args = parser.parse_args()

    # Ensure input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{{args.input_file}}' not found")
        return 1

    # Process the file
    success = transform_{transform_name}(args.input_file, args.output_file, args.target)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
'''
        return template

    def _inject_template_structure(self, generated_code: str, user_request: str) -> str:
        """Inject proper template structure if the generated code is incomplete"""
        # Extract transformation name from user request
        transform_name = self._generate_transform_name(user_request)

        # If the code is too short or missing key components, use template
        if (
            len(generated_code) < 500
            or "def main(" not in generated_code
            or "class" not in generated_code
        ):
            self.logger.warning(
                "Generated code appears incomplete, using template structure"
            )
            template = self._get_code_template(transform_name, user_request)

            # Try to extract any useful logic from the generated code
            visitor_logic = self._extract_visitor_logic(generated_code)
            transform_logic = self._extract_transform_logic(generated_code)

            # Inject the extracted logic into the template
            if visitor_logic:
                template = template.replace(
                    "# Check for wire declarations to transform", visitor_logic
                )
            if transform_logic:
                template = template.replace(
                    "# Transform each identified element", transform_logic
                )

            return template

        return generated_code

    def _generate_transform_name(self, user_request: str) -> str:
        """Generate a proper transform function name from user request"""
        # Clean and create name
        clean_request = re.sub(r"[^a-zA-Z0-9\s]", "", user_request.lower())
        words = clean_request.split()[:3]  # Take first 3 words
        return "_".join(words)

    def _extract_visitor_logic(self, code: str) -> str:
        """Extract visitor logic from partially generated code"""
        # Look for AST-related code patterns
        patterns = [
            r"if isinstance\(.*?Node.*?\):.*?$",
            r"elif isinstance\(.*?\):.*?$",
            r"node\..*?=.*?$",
            r"self\..*?\.append.*?$",
        ]

        extracted_lines = []
        for line in code.split("\n"):
            for pattern in patterns:
                if re.search(pattern, line.strip(), re.MULTILINE):
                    extracted_lines.append(line)
                    break

        return "\n".join(extracted_lines) if extracted_lines else ""

    def _extract_transform_logic(self, code: str) -> str:
        """Extract transformation logic from partially generated code"""
        # Look for regex transformation patterns
        patterns = [
            r"re\.sub\(.*?\)",
            r"re\.search\(.*?\)",
            r"modified_content\s*=.*?$",
            r"pattern\s*=.*?$",
            r"replacement\s*=.*?$",
        ]

        extracted_lines = []
        for line in code.split("\n"):
            for pattern in patterns:
                if re.search(pattern, line.strip(), re.MULTILINE):
                    extracted_lines.append(line)
                    break

        return "\n".join(extracted_lines) if extracted_lines else ""

    # ...existing code...
