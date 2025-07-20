#!/usr/bin/env python3

import sys
import os
import re
import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *

class SignalWidthVisitor(NodeVisitor):
    def __init__(self, signal_name, new_width):
        self.signal_name = signal_name
        # Parse the new width as [msb:lsb]
        if isinstance(new_width, str) and ":" in new_width:
            msb, lsb = new_width.strip("[]").split(":")
            self.new_msb = msb.strip()
            self.new_lsb = lsb.strip()
        else:
            raise ValueError("New width must be in the format 'msb:lsb' (e.g., '3:0')")

        self.changes_made = []
        self.signals_found = []
        self.current_width = None

    def visit(self, node):
        if isinstance(node, Node):
            # Check various types of signals (ports, wires, regs, etc.)
            if (
                hasattr(node, "name")
                and node.name == self.signal_name
                and hasattr(node, "width")
                and node.width
            ):
                # Found the signal with a width
                if isinstance(node.width, Width):
                    msb = node.width.msb
                    lsb = node.width.lsb
                    if hasattr(msb, "value") and hasattr(lsb, "value"):
                        old_msb = msb.value
                        old_lsb = lsb.value
                        self.current_width = f"[{old_msb}:{old_lsb}]"

                        # Identify the node type (Input, Output, Reg, Wire, etc.)
                        node_type = type(node).__name__

                        if node_type in ["input", "output", "inout"]:
                            # For ports
                            pattern = rf"\b{node_type}\s+{self.current_width}\s+{self.signal_name}\b"
                            replacement = f"{node_type} {self.new_msb}:{self.new_lsb} {self.signal_name}"
                        else:
                            # For other signals (reg, wire, etc.)
                            pattern = rf"\b{node_type}\s+{self.current_width}\s+{self.signal_name}\b"
                            replacement = f"{node_type} {self.new_msb}:{self.new_lsb} {self.signal_name}"

                        modified_content = re.sub(pattern, replacement, content)
                        self.changes_made.append((node, pattern, replacement))
                        self.signals_found.append({"type": node_type, "old_width": self.current_width, "new_width": f"{self.new_msb}:{self.new_lsb}"})

def transform_signal_width(input_file, output_file, signal_name, new_width):
    try:
        # Read the input file
        with open(input_file, "r") as f:
            content = f.read()

        # Parse the Verilog file to get the AST
        ast, directives = parse([input_file])

        # Create and apply the visitor to identify signals to modify
        visitor = SignalWidthVisitor(signal_name, new_width)
        visitor.visit(ast)

        # Check if signals were found
        if not visitor.signals_found:
            print("Warning: No targets found for transformation")
            return False

        # Apply regex transformations based on visitor findings
        with open(output_file, "w") as f:
            f.write(modified_content)
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Verilog transformation tool")
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    parser.add_argument("--target", help="Target parameter for transformation")
    
    args = parser.parse_args()
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        return 1
    
    success = transform_signal_width(args.input_file, args.output_file, args.target)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())