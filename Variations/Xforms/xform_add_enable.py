#!/usr/bin/env python3
"""
Transform to add an enable signal to a counter or other logic in Verilog.
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


class AddEnableSignalXform(XformBase):
    """Transform to add an enable signal to a counter in Verilog."""

    def __init__(self, enable_name, counter_name):
        """
        Initialize the transformation.

        Args:
            enable_name (str): Name of the enable signal to add
            counter_name (str): Name of the counter to control with the enable signal
        """
        super().__init__(
            f"add_enable_{enable_name}_to_{counter_name}",
            f"Add enable signal '{enable_name}' to control counter '{counter_name}'",
        )
        self.enable_name = enable_name
        self.counter_name = counter_name

    def apply(self, verilog_text, **kwargs):
        """
        Apply the transformation to add an enable signal.

        Args:
            verilog_text (str): Verilog code to transform

        Returns:
            str: Transformed Verilog code
        """
        # Check if the counter exists
        counter_pattern = (
            rf"\b{self.counter_name}\s*<=\s*{self.counter_name}\s*\+\s*1\b"
        )
        if not re.search(counter_pattern, verilog_text):
            logger.warning(
                f"Counter increment pattern for '{self.counter_name}' not found"
            )
            return verilog_text

        # Check if the enable signal already exists as a port
        enable_port_pattern = (
            rf"\b(input|output|inout)\s+(\[\d+:\d+\]\s+)?{self.enable_name}\b"
        )
        enable_exists = re.search(enable_port_pattern, verilog_text)

        transformed_text = verilog_text

        # Step 1: Add the enable signal as an input port if it doesn't exist
        if not enable_exists:
            # Find the module definition
            module_pattern = r"module\s+(\w+)\s*\(([\s\S]*?)\);"

            def add_enable_port(match):
                module_name = match.group(1)
                port_list = match.group(2).strip()

                # Add the enable signal to the port list
                if port_list:
                    # Add to existing ports
                    new_port_list = port_list + f",\n    {self.enable_name}"
                else:
                    # Empty port list
                    new_port_list = self.enable_name

                return f"module {module_name}({new_port_list});"

            transformed_text = re.sub(module_pattern, add_enable_port, transformed_text)

            # Add the port declaration
            port_decl = f"input {self.enable_name};"

            # Find where to insert the port declaration (after other port declarations)
            port_decl_pattern = r"(input|output|inout)\s+[^;]*;"
            port_decls = list(re.finditer(port_decl_pattern, transformed_text))

            if port_decls:
                last_port_decl = port_decls[-1]
                pos = last_port_decl.end()
                transformed_text = (
                    transformed_text[:pos]
                    + f"\n    {port_decl}"
                    + transformed_text[pos:]
                )
            else:
                # No existing port declarations, try to insert after module definition
                module_end_pattern = r"module\s+\w+\s*\([^;]*\);"
                module_match = re.search(module_end_pattern, transformed_text)
                if module_match:
                    pos = module_match.end()
                    transformed_text = (
                        transformed_text[:pos]
                        + f"\n    {port_decl}"
                        + transformed_text[pos:]
                    )

            logger.info(f"Added enable signal '{self.enable_name}' as an input port")

        # Step 2: Modify counter increment logic to be conditional on the enable signal
        def add_enable_condition(match):
            counter_increment = match.group(0)
            # Add the enable condition
            return f"if ({self.enable_name}) begin\n            {counter_increment};\n        end"

        # Find and modify counter increment statements
        counter_modified = False

        # Look for different patterns of counter increment in always blocks
        always_pattern = r"(always\s*@[^)]+\)[^;]+?begin)([\s\S]*?)(end\b)"

        def modify_always_block(match):
            nonlocal counter_modified
            always_header = match.group(1)
            block_content = match.group(2)
            block_end = match.group(3)

            # Check if this block contains the counter increment
            if re.search(counter_pattern, block_content):
                modified_content = re.sub(
                    counter_pattern, add_enable_condition, block_content
                )
                counter_modified = True
                return always_header + modified_content + block_end
            else:
                return match.group(0)

        transformed_text = re.sub(always_pattern, modify_always_block, transformed_text)

        if counter_modified:
            logger.info(f"Added enable condition to counter '{self.counter_name}'")
            return transformed_text
        else:
            logger.warning(
                f"Counter increment not found in a suitable context for adding enable"
            )
            return transformed_text


def main():
    """Run the transformation from the command line."""
    if len(sys.argv) < 4:
        print(
            f"Usage: {sys.argv[0]} <input_file> <enable_name> <counter_name> [output_file]"
        )
        return 1

    input_file = sys.argv[1]
    enable_name = sys.argv[2]
    counter_name = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else None

    xform = AddEnableSignalXform(enable_name, counter_name)
    success = run_xform(xform, input_file, output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
