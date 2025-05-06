#!/usr/bin/env python3
"""
Transform to change a reset condition in Verilog (e.g., from active-high to active-low).
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


class ChangeResetConditionXform(XformBase):
    """Transform to change a reset condition in Verilog."""

    def __init__(self, reset_signal, active_high_to_low=True):
        """
        Initialize the transformation.

        Args:
            reset_signal (str): Name of the reset signal
            active_high_to_low (bool): True to change from active-high to active-low,
                                       False to change from active-low to active-high
        """
        if active_high_to_low:
            super().__init__(
                f"change_reset_{reset_signal}_high_to_low",
                f"Change reset '{reset_signal}' from active-high to active-low",
            )
        else:
            super().__init__(
                f"change_reset_{reset_signal}_low_to_high",
                f"Change reset '{reset_signal}' from active-low to active-high",
            )

        self.reset_signal = reset_signal
        self.active_high_to_low = active_high_to_low

    def apply(self, verilog_text, **kwargs):
        """
        Apply the transformation to change a reset condition.

        Args:
            verilog_text (str): Verilog code to transform

        Returns:
            str: Transformed Verilog code
        """
        transformed_text = verilog_text
        change_count = 0

        if self.active_high_to_low:
            # Change from if(RST) to if(!RST)
            pattern = rf"if\s*\(\s*{self.reset_signal}\s*\)"
            replacement = f"if(!{self.reset_signal})"

            if not re.search(pattern, verilog_text):
                logger.warning(
                    f"Active-high reset condition using '{self.reset_signal}' not found"
                )
                return verilog_text

            transformed_text = re.sub(pattern, replacement, verilog_text)
            change_count += len(re.findall(pattern, verilog_text))

            # Also check for reset conditions in sensitivity lists (posedge RST -> negedge RST)
            sens_pattern = rf"posedge\s+{self.reset_signal}"
            sens_replacement = f"negedge {self.reset_signal}"

            if re.search(sens_pattern, transformed_text):
                transformed_text = re.sub(
                    sens_pattern, sens_replacement, transformed_text
                )
                change_count += len(re.findall(sens_pattern, verilog_text))
        else:
            # Change from if(!RST) to if(RST)
            pattern = rf"if\s*\(\s*!\s*{self.reset_signal}\s*\)"
            replacement = f"if({self.reset_signal})"

            if not re.search(pattern, verilog_text):
                logger.warning(
                    f"Active-low reset condition using '{self.reset_signal}' not found"
                )
                return verilog_text

            transformed_text = re.sub(pattern, replacement, verilog_text)
            change_count += len(re.findall(pattern, verilog_text))

            # Also check for reset conditions in sensitivity lists (negedge RST -> posedge RST)
            sens_pattern = rf"negedge\s+{self.reset_signal}"
            sens_replacement = f"posedge {self.reset_signal}"

            if re.search(sens_pattern, transformed_text):
                transformed_text = re.sub(
                    sens_pattern, sens_replacement, transformed_text
                )
                change_count += len(re.findall(sens_pattern, verilog_text))

        if change_count > 0:
            high_low_str = "high to low" if self.active_high_to_low else "low to high"
            logger.info(
                f"Changed reset condition for '{self.reset_signal}' from active-{high_low_str}"
            )
            return transformed_text
        else:
            logger.warning(f"No reset conditions changed")
            return verilog_text


def main():
    """Run the transformation from the command line."""
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} <input_file> <reset_signal> [high_to_low] [output_file]"
        )
        print(
            "  high_to_low: 1 (default) to change from active-high to active-low, 0 for the opposite"
        )
        return 1

    input_file = sys.argv[1]
    reset_signal = sys.argv[2]
    active_high_to_low = True

    if len(sys.argv) > 3:
        if sys.argv[3].lower() in ("0", "false", "no"):
            active_high_to_low = False

    output_file = sys.argv[4] if len(sys.argv) > 4 else None

    xform = ChangeResetConditionXform(reset_signal, active_high_to_low)
    success = run_xform(xform, input_file, output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
