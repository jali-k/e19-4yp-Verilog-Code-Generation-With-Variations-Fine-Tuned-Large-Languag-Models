#!/usr/bin/env python3
"""
Transformation to change a module name using PyVerilog and the xform framework.
"""

import sys
import os
import argparse
from xform_framework import XformBase, XformRunner
from pyverilog.vparser.ast import *


class ModuleNameXform(XformBase):
    """Transformation to change a module name."""

    def __init__(self, from_name, to_name):
        """
        Initialize the transformation.

        Args:
            from_name (str): Original module name
            to_name (str): New module name
        """
        super().__init__(
            f"module_name_{from_name}_to_{to_name}",
            f"Change module name from '{from_name}' to '{to_name}'",
        )
        self.from_name = from_name
        self.to_name = to_name

    def visit(self, node):
        """
        Visit an AST node and apply the transformation.

        Args:
            node: The PyVerilog AST node to visit
        """
        if isinstance(node, ModuleDef) and node.name == self.from_name:
            # Change the module name
            node.name = self.to_name
            self.changes_made.append(
                f"Changed module name from '{self.from_name}' to '{self.to_name}'"
            )

        # Continue visiting all child nodes
        for child in node.children():
            self.visit(child)


def main():
    """Main function to parse command line arguments and process the file."""
    parser = argparse.ArgumentParser(
        description="Change a module name using PyVerilog AST"
    )
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    parser.add_argument(
        "--from", dest="from_name", required=True, help="Original module name"
    )
    parser.add_argument("--to", dest="to_name", required=True, help="New module name")

    args = parser.parse_args()

    # Ensure input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        return 1

    # Create and run the transformation
    xform = ModuleNameXform(args.from_name, args.to_name)
    success = XformRunner.run_xform(xform, args.input_file, args.output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
