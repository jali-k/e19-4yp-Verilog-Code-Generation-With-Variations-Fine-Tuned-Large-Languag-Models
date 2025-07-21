#!/usr/bin/env python3
"""
Pattern Library for Verilog Transformation Generation
Extracts and organizes high-quality patterns from reference implementations
"""

import re
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CodePattern:
    """Represents a reusable code pattern"""

    name: str
    category: str
    template: str
    description: str
    example: str
    quality_attributes: List[str]


class PatternLibrary:
    """Manages reusable patterns for high-quality code generation"""

    def __init__(self):
        self.patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, CodePattern]:
        """Initialize the pattern library with high-quality templates"""
        patterns = {}

        # Constructor Patterns
        patterns["flexible_constructor"] = CodePattern(
            name="flexible_constructor",
            category="constructor",
            template="""def __init__(self, target_variable=None):
        self.target_variable = target_variable
        self.changes_made = []
        self.{type}_declarations = []""",
            description="Flexible constructor with optional targeting and comprehensive state tracking",
            example="def __init__(self, target_variable=None):",
            quality_attributes=["flexibility", "state_tracking", "optional_parameters"],
        )

        # AST Visitor Patterns
        patterns["defensive_ast_visitor"] = CodePattern(
            name="defensive_ast_visitor",
            category="ast_analysis",
            template="""def visit(self, node):
        \"\"\"Visit a node and identify {target} declarations.\"\"\"
        if isinstance(node, Node):
            if isinstance(node, Decl):
                for item in node.list:
                    if isinstance(item, {NodeType}):
                        # If targeting a specific variable, check the name
                        if self.target_variable is None or (
                            hasattr(item, "name") and item.name == self.target_variable
                        ):
                            # Store information about the {target} declaration
                            {pattern_specific_logic}
                            
            # Visit children
            for c in node.children():
                self.visit(c)""",
            description="Defensive AST visitor with null checks and flexible targeting",
            example="Handles optional targeting with hasattr checks",
            quality_attributes=[
                "defensive_programming",
                "null_safety",
                "flexible_targeting",
            ],
        )

        # Width Handling Pattern
        patterns["width_extraction"] = CodePattern(
            name="width_extraction",
            category="width_handling",
            template="""width = ""
            if item.width:
                msb = item.width.msb.value
                lsb = item.width.lsb.value
                width = f"[{msb}:{lsb}] \"""",
            description="Safe width extraction with proper formatting",
            example='width = "[7:0] " if item has width',
            quality_attributes=["safety", "formatting", "null_handling"],
        )

        # Regex Transformation Pattern
        patterns["sophisticated_regex"] = CodePattern(
            name="sophisticated_regex",
            category="text_transformation",
            template="""# Replace {source} declarations with {target} in the content
        modified_content = content
        for decl in visitor.{source}_declarations:
            # Match {source} declaration with the correct width
            pattern = (
                r"\\b{source}\\s+"
                + re.escape(decl["width"])
                + r"\\b"
                + re.escape(decl["name"])
                + r"\\b"
            )
            replacement = f'{target} {{decl["width"]}}{{decl["name"]}}'
            modified_content = re.sub(pattern, replacement, modified_content)""",
            description="Sophisticated regex with proper escaping and width handling",
            example="Uses re.escape for safety and preserves width formatting",
            quality_attributes=[
                "regex_safety",
                "width_preservation",
                "robust_matching",
            ],
        )

        # Error Handling Pattern
        patterns["comprehensive_error_handling"] = CodePattern(
            name="comprehensive_error_handling",
            category="error_handling",
            template="""try:
        # Main transformation logic here
        {main_logic}
        
        # Check if any changes were identified
        if not visitor.changes_made:
            if target_variable:
                print(f"Warning: Variable '{{target_variable}}' not found or not declared as '{source_type}'")
            else:
                print(f"Warning: No '{source_type}' variables found in file")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error processing file: {{e}}")
        import traceback
        traceback.print_exc()
        return False""",
            description="Comprehensive error handling with specific warning messages",
            example="Handles both targeted and general transformation failures",
            quality_attributes=["error_handling", "user_feedback", "debugging_support"],
        )

        # Argument Parser Pattern
        patterns["robust_argument_parser"] = CodePattern(
            name="robust_argument_parser",
            category="cli_interface",
            template="""def main():
    \"\"\"Main function to parse command line arguments and process the file.\"\"\"
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    parser.add_argument(
        "--variable", "-v",
        help="Specific variable to transform (default: all {type} variables)"
    )
    
    args = parser.parse_args()
    
    # Ensure input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{{args.input_file}}' not found")
        return 1
        
    # Process the file
    success = {function_name}(args.input_file, args.output_file, args.variable)
    
    return 0 if success else 1""",
            description="Robust argument parser with file validation",
            example="Includes input validation and proper exit codes",
            quality_attributes=["cli_robustness", "file_validation", "proper_exits"],
        )

        return patterns

    def get_patterns_for_transformation_type(
        self, transformation_type: str
    ) -> List[CodePattern]:
        """Get relevant patterns for a specific transformation type"""
        # All transformations need these core patterns
        core_patterns = [
            "flexible_constructor",
            "defensive_ast_visitor",
            "comprehensive_error_handling",
            "robust_argument_parser",
        ]

        # Add specific patterns based on transformation type
        type_specific = {
            "data_type": ["sophisticated_regex"],
            "width": ["width_extraction", "sophisticated_regex"],
            "port_direction": ["sophisticated_regex"],
            "module_name": ["sophisticated_regex"],
        }

        pattern_names = core_patterns + type_specific.get(transformation_type, [])
        return [self.patterns[name] for name in pattern_names if name in self.patterns]

    def get_quality_guidelines(self) -> Dict[str, str]:
        """Get quality guidelines for code generation"""
        return {
            "constructor": "MUST use flexible constructor with optional target_variable parameter",
            "state_tracking": "MUST track changes_made and declarations in separate lists",
            "ast_visitor": "MUST use defensive programming with hasattr checks and null validation",
            "regex": "MUST use re.escape for variable names and proper width preservation",
            "error_handling": "MUST provide specific error messages and handle edge cases",
            "cli": "MUST validate input files and provide proper exit codes",
            "code_structure": "MUST follow the exact structure: AST analysis + regex transformation",
        }

    def extract_anti_patterns(self) -> List[str]:
        """Get list of anti-patterns to avoid"""
        return [
            "AVOID: Simple list tracking like `self.wire_signals = []`",
            "AVOID: Basic type checking without null safety",
            "AVOID: Direct string replacement without regex escaping",
            "AVOID: Generic error messages without context",
            "AVOID: Rigid constructors without optional parameters",
            "AVOID: Missing width preservation in transformations",
        ]

    def format_pattern_for_prompt(self, pattern: CodePattern, **kwargs) -> str:
        """Format a pattern for inclusion in prompts"""
        formatted_template = pattern.template.format(**kwargs)

        return f"""
=== {pattern.name.upper()} PATTERN ===
Description: {pattern.description}
Quality Attributes: {', '.join(pattern.quality_attributes)}

Template:
{formatted_template}

Example: {pattern.example}
"""
