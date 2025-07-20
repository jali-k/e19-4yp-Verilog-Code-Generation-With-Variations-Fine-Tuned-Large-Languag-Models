#!/usr/bin/env python3
"""
Transformation to change reset condition from active-high to active-low or vice versa.
"""

import sys
import os
import re
import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *


class ResetConditionVisitor:
    """
    AST visitor that identifies reset conditions.
    """

    def __init__(self, reset_signal, active_high_to_low=True):
        self.reset_signal = reset_signal
        self.active_high_to_low = active_high_to_low
        self.changes_made = []
        self.reset_conditions_found = []
        self.reset_edges_found = []

    def visit(self, node):
        """Visit a node and identify reset conditions."""
        if isinstance(node, Node):
            # Check for if statements with reset conditions
            if isinstance(node, IfStatement):
                cond = node.cond

                # Check for active-high reset: if(RST)
                if (
                    self.active_high_to_low
                    and isinstance(cond, Identifier)
                    and cond.name == self.reset_signal
                ):
                    self.reset_conditions_found.append(
                        {
                            "type": "active_high",
                            "line": cond.lineno if hasattr(cond, "lineno") else None,
                        }
                    )

                # Check for active-low reset: if(!RST)
                elif (
                    not self.active_high_to_low
                    and isinstance(cond, Unot)
                    and isinstance(cond.right, Identifier)
                    and cond.right.name == self.reset_signal
                ):
                    self.reset_conditions_found.append(
                        {
                            "type": "active_low",
                            "line": cond.lineno if hasattr(cond, "lineno") else None,
                        }
                    )

            # Check for sensitivity lists with reset edges
            if isinstance(node, Sens):
                if (
                    node.type == "posedge"
                    and isinstance(node.sig, Identifier)
                    and node.sig.name == self.reset_signal
                ):
                    self.reset_edges_found.append(
                        {
                            "type": "posedge",
                            "line": node.lineno if hasattr(node, "lineno") else None,
                        }
                    )
                elif (
                    node.type == "negedge"
                    and isinstance(node.sig, Identifier)
                    and node.sig.name == self.reset_signal
                ):
                    self.reset_edges_found.append(
                        {
                            "type": "negedge",
                            "line": node.lineno if hasattr(node, "lineno") else None,
                        }
                    )

            # Continue visiting all child nodes
            for child in node.children():
                self.visit(child)

            # After analyzing, record changes
            if self.reset_conditions_found or self.reset_edges_found:
                direction = "high to low" if self.active_high_to_low else "low to high"
                self.changes_made.append(
                    f"Changed reset condition for '{self.reset_signal}' from active-{direction}"
                )


def transform_reset_condition(
    input_file, output_file, reset_signal, active_high_to_low=True
):
    """
    Transform reset condition from active-high to active-low or vice versa.

    Args:
        input_file (str): Path to input Verilog file
        output_file (str): Path to output Verilog file
        reset_signal (str): Name of the reset signal
        active_high_to_low (bool): True to change from active-high to active-low,
                                  False to change from active-low to active-high

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the input file
        with open(input_file, "r") as f:
            content = f.read()

        # Parse the Verilog file to get the AST
        ast, directives = parse([input_file])

        # Create and apply the visitor to identify reset conditions
        visitor = ResetConditionVisitor(reset_signal, active_high_to_low)
        visitor.visit(ast)

        # Check if reset conditions were found
        if not visitor.reset_conditions_found and not visitor.reset_edges_found:
            high_low_str = "high" if active_high_to_low else "low"
            print(
                f"Warning: No active-{high_low_str} reset conditions found for '{reset_signal}'"
            )
            return False

        # Print summary of changes
        for change in visitor.changes_made:
            print(change)

        # Perform the transformations using regex
        modified_content = content

        # 1. Transform reset conditions in if statements
        if active_high_to_low:
            # Change from if(RST) to if(!RST)
            pattern = r"if\s*\(\s*" + re.escape(reset_signal) + r"\s*\)"
            replacement = f"if(!{reset_signal})"
            modified_content = re.sub(pattern, replacement, modified_content)
        else:
            # Change from if(!RST) to if(RST)
            pattern = r"if\s*\(\s*!\s*" + re.escape(reset_signal) + r"\s*\)"
            replacement = f"if({reset_signal})"
            modified_content = re.sub(pattern, replacement, modified_content)

        # 2. Transform reset edges in sensitivity lists
        if active_high_to_low:
            # Change from posedge RST to negedge RST
            pattern = r"posedge\s+" + re.escape(reset_signal)
            replacement = f"negedge {reset_signal}"
            modified_content = re.sub(pattern, replacement, modified_content)
        else:
            # Change from negedge RST to posedge RST
            pattern = r"negedge\s+" + re.escape(reset_signal)
            replacement = f"posedge {reset_signal}"
            modified_content = re.sub(pattern, replacement, modified_content)

        # Write the modified content to the output file
        with open(output_file, "w") as f:
            f.write(modified_content)

        print(f"Output written to {output_file}")
        return True

    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function to parse command line arguments and process the file."""
    parser = argparse.ArgumentParser(
        description="Change reset condition from active-high to active-low or vice versa"
    )
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    parser.add_argument("--signal", required=True, help="Name of the reset signal")
    parser.add_argument(
        "--direction",
        choices=["high_to_low", "low_to_high"],
        default="high_to_low",
        help="Direction of change: high_to_low (default) or low_to_high",
    )

    args = parser.parse_args()

    # Ensure input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        return 1

    # Process the file
    active_high_to_low = args.direction == "high_to_low"
    success = transform_reset_condition(
        args.input_file, args.output_file, args.signal, active_high_to_low
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
