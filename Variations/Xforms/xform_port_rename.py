#!/usr/bin/env python3
"""
Transform to rename a port in a Verilog module.
"""

import re
import os
import sys
import logging
from verilog_xform_framework import XformBase, run_xform

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RenamePortXform(XformBase):
    """Transform to rename a port in a Verilog module."""

    def __init__(self, from_name, to_name, module_name=None):
        """
        Initialize the transformation.

        Args:
            from_name (str): Original port name
            to_name (str): New port name
            module_name (str, optional): Module name to target (if None, targets all modules)
        """
        super().__init__(
            f"rename_port_{from_name}_to_{to_name}",
            f"Rename port '{from_name}' to '{to_name}'"
            + (f" in module '{module_name}'" if module_name else ""),
        )
        self.from_name = from_name
        self.to_name = to_name
        self.module_name = module_name

    def apply(self, verilog_text, **kwargs):
        """
        Apply the transformation to rename a port.

        Args:
            verilog_text (str): Verilog code to transform

        Returns:
            str: Transformed Verilog code
        """
        transformed_text = verilog_text

        # If a module name is specified, make sure it exists
        if self.module_name:
            module_pattern = rf"\bmodule\s+{self.module_name}\b"
            if not re.search(module_pattern, verilog_text):
                logger.warning(f"Module '{self.module_name}' not found")
                return verilog_text

        # Find and modify port in module declaration
        port_change_count = 0

        # Pattern to match module declarations with port lists
        if self.module_name:
            module_pattern = (
                rf"module\s+{self.module_name}\s*\(([^)]*\b{self.from_name}\b[^)]*)\)"
            )
        else:
            module_pattern = rf"module\s+\w+\s*\(([^)]*\b{self.from_name}\b[^)]*)\)"

        def replace_port_in_list(match):
            nonlocal port_change_count
            port_list = match.group(1)
            module_header = match.group(0)[: match.start(1) - match.start(0)]
            closing_paren = ")"

            # Replace the port name but preserve whitespace and commas
            updated_port_list = re.sub(
                rf"(^|,|\s+)\s*({self.from_name})\s*($|,)",
                rf"\1 {self.to_name} \3",
                port_list,
            )

            port_change_count += 1
            return f"{module_header}{updated_port_list}{closing_paren}"

        transformed_text = re.sub(
            module_pattern, replace_port_in_list, transformed_text
        )

        # Also update port declarations (input, output, inout)
        port_decl_pattern = (
            rf"\b(input|output|inout)\s+(reg\s+)?(\[\d+:\d+\]\s+)?{self.from_name}\b"
        )

        def replace_port_decl(match):
            nonlocal port_change_count
            direction = match.group(1)
            reg_part = match.group(2) or ""
            width_part = match.group(3) or ""
            return f"{direction} {reg_part}{width_part}{self.to_name}"

        transformed_text = re.sub(
            port_decl_pattern, replace_port_decl, transformed_text
        )

        # Also update all other references to the port in the module body
        # This is trickier as we need to avoid variable names that might be substrings
        # or contain the port name as a substring
        def replace_port_references(text):
            return re.sub(rf"\b{self.from_name}\b", self.to_name, text)

        # Find module boundaries
        if self.module_name:
            module_match = re.search(
                rf"module\s+{self.module_name}\s*\([^)]*\);(.*?)endmodule",
                transformed_text,
                re.DOTALL,
            )
        else:
            module_match = re.search(
                r"module\s+\w+\s*\([^)]*\);(.*?)endmodule", transformed_text, re.DOTALL
            )

        if module_match:
            module_body = module_match.group(1)
            updated_body = replace_port_references(module_body)
            start, end = module_match.span(1)
            transformed_text = (
                transformed_text[:start] + updated_body + transformed_text[end:]
            )

        if port_change_count > 0:
            logger.info(f"Renamed port '{self.from_name}' to '{self.to_name}'")
            return transformed_text
        else:
            logger.warning(f"Port '{self.from_name}' not found")
            return verilog_text


def main():
    """Run the transformation from the command line."""
    if len(sys.argv) < 4:
        print(
            f"Usage: {sys.argv[0]} <input_file> <from_name> <to_name> [module_name] [output_file]"
        )
        return 1

    input_file = sys.argv[1]
    from_name = sys.argv[2]
    to_name = sys.argv[3]
    module_name = sys.argv[4] if len(sys.argv) > 4 else None
    output_file = sys.argv[5] if len(sys.argv) > 5 else None

    xform = RenamePortXform(from_name, to_name, module_name)
    success = run_xform(xform, input_file, output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
