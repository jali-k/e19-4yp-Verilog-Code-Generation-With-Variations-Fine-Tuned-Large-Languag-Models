#!/usr/bin/env python3
"""
Transform to rename a clock signal in a Verilog module.
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


class RenameClockXform(XformBase):
    """Transform to rename a clock signal in a Verilog module."""

    def __init__(self, from_name, to_name):
        """
        Initialize the transformation.

        Args:
            from_name (str): Original clock signal name
            to_name (str): New clock signal name
        """
        super().__init__(
            f"rename_clock_{from_name}_to_{to_name}",
            f"Rename clock signal from '{from_name}' to '{to_name}'",
        )
        self.from_name = from_name
        self.to_name = to_name

    def apply(self, verilog_text, **kwargs):
        """
        Apply the transformation to rename a clock signal.

        Args:
            verilog_text (str): Verilog code to transform

        Returns:
            str: Transformed Verilog code
        """
        transformed_text = verilog_text
        change_count = 0

        # Check if the clock signal exists as a port
        clock_port_pattern = rf"\b(input)\s+(\[\d+:\d+\]\s+)?{self.from_name}\b"

        if not re.search(clock_port_pattern, verilog_text):
            logger.warning(
                f"Clock signal '{self.from_name}' not found as an input port"
            )
            return verilog_text

        # First, rename it in the port list
        port_list_pattern = rf"\bmodule\s+\w+\s*\(([^)]*\b{self.from_name}\b[^)]*)\)"

        def replace_port_in_list(match):
            nonlocal change_count
            port_list = match.group(1)
            module_header = match.group(0)[: match.start(1) - match.start(0)]
            closing_paren = ")"

            # Replace the port name but preserve whitespace and commas
            updated_port_list = re.sub(
                rf"(^|,|\s+)\s*({self.from_name})\s*($|,)",
                rf"\1 {self.to_name} \3",
                port_list,
            )

            change_count += 1
            return f"{module_header}{updated_port_list}{closing_paren}"

        transformed_text = re.sub(
            port_list_pattern, replace_port_in_list, transformed_text
        )

        # Rename in port declarations
        port_decl_pattern = rf"\b(input)\s+(\[\d+:\d+\]\s+)?{self.from_name}\b"

        def replace_port_decl(match):
            nonlocal change_count
            direction = match.group(1)
            width_part = match.group(2) or ""

            change_count += 1
            return f"{direction} {width_part}{self.to_name}"

        transformed_text = re.sub(
            port_decl_pattern, replace_port_decl, transformed_text
        )

        # Rename in clock sensitivity lists (posedge/negedge)
        sens_pattern = rf"(posedge|negedge)\s+{self.from_name}"

        def replace_sens_list(match):
            nonlocal change_count
            edge = match.group(1)

            change_count += 1
            return f"{edge} {self.to_name}"

        transformed_text = re.sub(sens_pattern, replace_sens_list, transformed_text)

        # Rename all other occurrences of the clock signal
        def replace_signal_name(text):
            nonlocal change_count
            pattern = rf"\b{self.from_name}\b"
            matches = list(re.finditer(pattern, text))
            if matches:
                change_count += len(matches)
                return re.sub(pattern, self.to_name, text)
            return text

        # Apply to the entire text
        transformed_text = replace_signal_name(transformed_text)

        if change_count > 0:
            logger.info(
                f"Renamed clock signal from '{self.from_name}' to '{self.to_name}', {change_count} occurrences"
            )
            return transformed_text
        else:
            logger.warning(
                f"No occurrences of clock signal '{self.from_name}' found to rename"
            )
            return verilog_text


def main():
    """Run the transformation from the command line."""
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <input_file> <from_name> <to_name> [output_file]")
        return 1

    input_file = sys.argv[1]
    from_name = sys.argv[2]
    to_name = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else None

    xform = RenameClockXform(from_name, to_name)
    success = run_xform(xform, input_file, output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
