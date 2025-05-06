#!/usr/bin/env python3
"""
Transform to change a module name in Verilog.
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


class ChangeModuleNameXform(XformBase):
    """Transform to change a module name in Verilog."""

    def __init__(self, from_name, to_name):
        """
        Initialize the transformation.

        Args:
            from_name (str): Original module name
            to_name (str): New module name
        """
        super().__init__(
            f"change_module_name_{from_name}_to_{to_name}",
            f"Change module name from '{from_name}' to '{to_name}'",
        )
        self.from_name = from_name
        self.to_name = to_name

    def apply(self, verilog_text, **kwargs):
        """
        Apply the transformation to change a module's name.

        Args:
            verilog_text (str): Verilog code to transform

        Returns:
            str: Transformed Verilog code
        """
        # Match module declaration patterns
        pattern = rf"\bmodule\s+{self.from_name}\b"

        # Check if the pattern exists in the text
        if not re.search(pattern, verilog_text):
            logger.warning(f"Module '{self.from_name}' not found")
            return verilog_text

        # Replace the module name
        transformed_text = re.sub(pattern, f"module {self.to_name}", verilog_text)

        # Also replace endmodule comments if they reference the module name
        endmodule_pattern = rf"endmodule\s*//\s*{self.from_name}"
        transformed_text = re.sub(
            endmodule_pattern, f"endmodule // {self.to_name}", transformed_text
        )

        logger.info(f"Changed module name from '{self.from_name}' to '{self.to_name}'")
        return transformed_text


def main():
    """Run the transformation from the command line."""
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <input_file> <from_name> <to_name> [output_file]")
        return 1

    input_file = sys.argv[1]
    from_name = sys.argv[2]
    to_name = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else None

    xform = ChangeModuleNameXform(from_name, to_name)
    success = run_xform(xform, input_file, output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
