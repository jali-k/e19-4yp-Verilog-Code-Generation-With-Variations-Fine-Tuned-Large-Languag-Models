#!/usr/bin/env python3
"""
Transform to change a variable type in Verilog (e.g., from reg to wire).
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


class ChangeVarTypeXform(XformBase):
    """Transform to change a variable type in Verilog."""

    def __init__(self, var_name, from_type, to_type):
        """
        Initialize the transformation.

        Args:
            var_name (str): Name of the variable to change
            from_type (str): Original variable type (e.g., 'reg')
            to_type (str): New variable type (e.g., 'wire')
        """
        super().__init__(
            f"change_{var_name}_type_{from_type}_to_{to_type}",
            f"Change variable '{var_name}' type from '{from_type}' to '{to_type}'",
        )
        self.var_name = var_name
        self.from_type = from_type
        self.to_type = to_type

    def apply(self, verilog_text, **kwargs):
        """
        Apply the transformation to change a variable's type.

        Args:
            verilog_text (str): Verilog code to transform

        Returns:
            str: Transformed Verilog code
        """
        # Match variable declarations with the specified name and type
        # This handles both scalar and vector variables
        pattern = rf"\b{self.from_type}\s+(\[\d+:\d+\]\s+)?{self.var_name}\b"

        # Check if the pattern exists in the text
        if not re.search(pattern, verilog_text):
            logger.warning(
                f"Variable '{self.var_name}' of type '{self.from_type}' not found"
            )
            return verilog_text

        # Replace the variable type
        def replace_type(match):
            width_part = match.group(1) or ""
            return f"{self.to_type} {width_part}{self.var_name}"

        transformed_text = re.sub(pattern, replace_type, verilog_text)

        logger.info(
            f"Changed variable '{self.var_name}' type from '{self.from_type}' to '{self.to_type}'"
        )
        return transformed_text


def main():
    """Run the transformation from the command line."""
    if len(sys.argv) < 5:
        print(
            f"Usage: {sys.argv[0]} <input_file> <var_name> <from_type> <to_type> [output_file]"
        )
        return 1

    input_file = sys.argv[1]
    var_name = sys.argv[2]
    from_type = sys.argv[3]
    to_type = sys.argv[4]
    output_file = sys.argv[5] if len(sys.argv) > 5 else None

    xform = ChangeVarTypeXform(var_name, from_type, to_type)
    success = run_xform(xform, input_file, output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
