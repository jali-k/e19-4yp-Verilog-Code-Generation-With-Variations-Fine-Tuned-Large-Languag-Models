#!/usr/bin/env python3
"""
Transform to change the width of a signal (port or variable) in Verilog.
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


class ChangeSignalWidthXform(XformBase):
    """Transform to change the width of a signal in Verilog."""

    def __init__(self, signal_name, new_width_str):
        """
        Initialize the transformation.

        Args:
            signal_name (str): Name of the signal to modify
            new_width_str (str): New width specification (e.g., "3:0" for a 4-bit signal)
        """
        super().__init__(
            f"change_{signal_name}_width_{new_width_str.replace(':', '_')}",
            f"Change signal '{signal_name}' width to [{new_width_str}]",
        )
        self.signal_name = signal_name

        # Parse the width string into MSB and LSB
        if ":" in new_width_str:
            msb_str, lsb_str = new_width_str.split(":")
            self.new_msb = int(msb_str.strip())
            self.new_lsb = int(lsb_str.strip())
        else:
            # Handle single-bit width
            self.new_msb = int(new_width_str.strip())
            self.new_lsb = 0

        self.new_width_str = f"{self.new_msb}:{self.new_lsb}"

    def apply(self, verilog_text, **kwargs):
        """
        Apply the transformation to change a signal's width.

        Args:
            verilog_text (str): Verilog code to transform

        Returns:
            str: Transformed Verilog code
        """
        transformed_text = verilog_text
        change_count = 0

        # First, check if the signal exists
        signal_pattern = (
            rf"\b(input|output|inout|reg|wire)\s+(\[\d+:\d+\]\s+)?{self.signal_name}\b"
        )
        signal_matches = re.findall(signal_pattern, verilog_text)

        if not signal_matches:
            logger.warning(f"Signal '{self.signal_name}' not found")
            return verilog_text

        # Change the width in port declarations
        port_pattern = rf"\b(input|output|inout)\s+(reg\s+)?(\[(\d+):(\d+)\]\s+)?{self.signal_name}\b"

        def replace_port_width(match):
            nonlocal change_count
            direction = match.group(1)
            reg_part = match.group(2) or ""
            has_width = match.group(3) is not None

            if has_width:
                change_count += 1
                return (
                    f"{direction} {reg_part}[{self.new_width_str}] {self.signal_name}"
                )
            else:
                change_count += 1
                return (
                    f"{direction} {reg_part}[{self.new_width_str}] {self.signal_name}"
                )

        transformed_text = re.sub(port_pattern, replace_port_width, transformed_text)

        # Change the width in variable declarations
        var_pattern = rf"\b(reg|wire)\s+(\[(\d+):(\d+)\]\s+)?{self.signal_name}\b"

        def replace_var_width(match):
            nonlocal change_count
            var_type = match.group(1)
            has_width = match.group(2) is not None

            if has_width:
                change_count += 1
                return f"{var_type} [{self.new_width_str}] {self.signal_name}"
            else:
                change_count += 1
                return f"{var_type} [{self.new_width_str}] {self.signal_name}"

        transformed_text = re.sub(var_pattern, replace_var_width, transformed_text)

        if change_count > 0:
            logger.info(
                f"Changed signal '{self.signal_name}' width to [{self.new_width_str}]"
            )
            return transformed_text
        else:
            logger.warning(f"No width changes were made to signal '{self.signal_name}'")
            return verilog_text


def main():
    """Run the transformation from the command line."""
    if len(sys.argv) < 4:
        print(
            f"Usage: {sys.argv[0]} <input_file> <signal_name> <new_width> [output_file]"
        )
        print("  new_width: format should be 'MSB:LSB', e.g., '3:0' for a 4-bit signal")
        return 1

    input_file = sys.argv[1]
    signal_name = sys.argv[2]
    new_width = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else None

    xform = ChangeSignalWidthXform(signal_name, new_width)
    success = run_xform(xform, input_file, output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
