#!/usr/bin/env python3
"""
Transformation to change reg variables to wire using PyVerilog and the xform framework.
"""

import sys
import os
import argparse
from xform_framework import XformBase, XformRunner
from pyverilog.vparser.ast import *


class RegToWireXform(XformBase):
    """Transformation to change reg variables to wire."""

    def __init__(self, target_variable=None):
        """
        Initialize the transformation.

        Args:
            target_variable (str, optional): If provided, only transform this variable
        """
        super().__init__("reg_to_wire", "Change reg variables to wire")
        self.target_variable = target_variable

    def visit(self, node):
        """
        Visit an AST node and apply the transformation.

        Args:
            node: The PyVerilog AST node to visit
        """
        if isinstance(node, Decl):
            # Check if this is a reg declaration
            for item in node.list:
                if isinstance(item, Reg):
                    # If targeting a specific variable, check the name
                    if self.target_variable is None or (
                        hasattr(item, "name") and item.name == self.target_variable
                    ):

                        # Replace Reg with Wire, preserving all other attributes
                        wire = Wire(
                            name=item.name, width=item.width, signed=item.signed
                        )
                        node.list[node.list.index(item)] = wire
                        self.changes_made.append(
                            f"Changed '{item.name}' from 'reg' to 'wire'"
                        )

        # Continue visiting all child nodes
        for child in node.children():
            self.visit(child)


def main():
    """Main function to parse command line arguments and process the file."""
    parser = argparse.ArgumentParser(
        description="Transform reg variables to wire using PyVerilog AST"
    )
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    parser.add_argument(
        "--variable",
        "-v",
        help="Specific variable to transform (default: all reg variables)",
    )

    args = parser.parse_args()

    # Ensure input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        return 1

    # Create and run the transformation
    xform = RegToWireXform(args.variable)
    success = XformRunner.run_xform(xform, args.input_file, args.output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
