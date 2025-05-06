#!/usr/bin/env python3
"""
Transform to rename a parameter in a Verilog module.
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


class RenameParameterXform(XformBase):
    """Transform to rename a parameter in a Verilog module."""

    def __init__(self, from_name, to_name, module_name=None):
        """
        Initialize the transformation.

        Args:
            from_name (str): Original parameter name
            to_name (str): New parameter name
            module_name (str, optional): Module name to target (if None, targets all modules)
        """
        super().__init__(
            f"rename_parameter_{from_name}_to_{to_name}",
            f"Rename parameter '{from_name}' to '{to_name}'"
            + (f" in module '{module_name}'" if module_name else ""),
        )
        self.from_name = from_name
        self.to_name = to_name
        self.module_name = module_name

    def apply(self, verilog_text, **kwargs):
        """
        Apply the transformation to rename a parameter.

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

        # Find and rename parameter declarations
        param_change_count = 0

        # Parameter declaration pattern
        if self.module_name:
            param_pattern = (
                rf"(\bmodule\s+{self.module_name}\s*\([^;]*\);.*?)"
                + rf"(\bparameter\s+)({self.from_name})\b(\s*=\s*[^;]+;)"
            )
        else:
            param_pattern = (
                rf"(\bmodule\s+\w+\s*\([^;]*\);.*?)"
                + rf"(\bparameter\s+)({self.from_name})\b(\s*=\s*[^;]+;)"
            )

        def replace_param_decl(match):
            nonlocal param_change_count
            prefix = match.group(1)
            param_keyword = match.group(2)
            param_name = match.group(3)
            value_part = match.group(4)

            param_change_count += 1
            return f"{prefix}{param_keyword}{self.to_name}{value_part}"

        transformed_text = re.sub(
            param_pattern, replace_param_decl, transformed_text, flags=re.DOTALL
        )

        # Also update all references to the parameter
        def replace_param_references(text):
            nonlocal param_change_count
            pattern = rf"\b{self.from_name}\b"
            if re.search(pattern, text):
                param_change_count += len(re.findall(pattern, text))
                return re.sub(pattern, self.to_name, text)
            return text

        # Find module boundaries
        if self.module_name:
            module_pattern = rf"module\s+{self.module_name}\s*\([^)]*\);(.*?)endmodule"
        else:
            module_pattern = r"module\s+\w+\s*\([^)]*\);(.*?)endmodule"

        for module_match in re.finditer(module_pattern, transformed_text, re.DOTALL):
            module_body = module_match.group(1)
            updated_body = replace_param_references(module_body)
            start, end = module_match.span(1)
            transformed_text = (
                transformed_text[:start] + updated_body + transformed_text[end:]
            )

        if param_change_count > 0:
            logger.info(f"Renamed parameter '{self.from_name}' to '{self.to_name}'")
            return transformed_text
        else:
            logger.warning(f"Parameter '{self.from_name}' not found")
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

    xform = RenameParameterXform(from_name, to_name, module_name)
    success = run_xform(xform, input_file, output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
