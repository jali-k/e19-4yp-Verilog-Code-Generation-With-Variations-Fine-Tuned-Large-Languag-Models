#!/usr/bin/env python3
"""
Transformation to convert individual signals to SystemVerilog interfaces for better modularity.
"""

import sys
import os
import re
import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *

class TransformationVisitor:
    def __init__(self, target_param=None):
        self.target_param = target_param
        self.changes_made = []
        self.target_elements = []

    def visit(self, node):
        if isinstance(node, Node):
            # ANALYZE based on transformation type:
            # Wire/Reg: Check isinstance(node, Decl) and look for Wire/Reg items
            # Renaming: Check isinstance(node, Identifier) for target names
            # Modules: Check isinstance(node, ModuleDef) for module operations
            # Ports: Check isinstance(node, Ioport) for port modifications
            
            # ALWAYS visit children
            for child in node.children():
                self.visit(child)

def transform_operation(input_file, output_file, target_param=None):
    try:
        with open(input_file, "r") as f:
            content = f.read()
        
        ast, directives = parse([input_file])
        visitor = TransformationVisitor(target_param)
        visitor.visit(ast)
        
        if not visitor.changes_made:
            print("Warning: No targets found for transformation")
            return False
        
        modified_content = content
        # Apply regex transformations based on visitor findings
        for target in visitor.target_elements:
            signal_name = target[0]
            new_type = target[1]
            if new_type == "wire":
                pattern = r'\bwire\s+' + re.escape(signal_name) + r'\b'
                replacement = 'wire ' + signal_name
            elif new_type == "reg":
                pattern = r'\bwire\s+' + re.escape(signal_name) + r'\b'
                replacement = 'reg ' + signal_name
            else:
                print("Error: Unsupported type for transformation")
                return False
            
            modified_content = re.sub(pattern, replacement, modified_content)
        
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
    
    success = transform_operation(args.input_file, args.output_file, args.target)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())