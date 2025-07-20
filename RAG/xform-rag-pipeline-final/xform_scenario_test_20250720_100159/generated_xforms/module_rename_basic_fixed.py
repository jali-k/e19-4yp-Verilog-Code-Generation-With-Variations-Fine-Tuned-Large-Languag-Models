#!/usr/bin/env python3
import sys
import os
import re
import argparse
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *

class TransformationVisitor:
    def __init__(self, old_name=None, new_name=None):
        self.old_name = old_name
        self.new_name = new_name
        self.changes_made = []
        self.found_modules = []

    def visit(self, node):
        if isinstance(node, ModuleDef):
            module_name = str(node.name)
            self.found_modules.append(module_name)
            if self.old_name and module_name == self.old_name:
                self.changes_made.append(f"Found module '{module_name}' to rename")
        
        if isinstance(node, Node):
            for child in node.children():
                self.visit(child)

def transform_operation(input_file, output_file, old_name=None, new_name=None):
    try:
        with open(input_file, "r") as f:
            content = f.read()
        
        ast, directives = parse([input_file])
        visitor = TransformationVisitor(old_name, new_name)
        visitor.visit(ast)
        
        if old_name and new_name:
            pattern = r'\bmodule\s+' + re.escape(old_name) + r'\b'
            replacement = f'module {new_name}'
            modified_content = re.sub(pattern, replacement, content)
            print(f"Renamed module '{old_name}' to '{new_name}'")
        else:
            modified_content = content
            print("No renaming parameters provided")
        
        with open(output_file, "w") as f:
            f.write(modified_content)
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Module renaming transformation")
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    parser.add_argument("--old-name", help="Old module name")
    parser.add_argument("--new-name", help="New module name")
    
    args = parser.parse_args()
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        return 1
    
    success = transform_operation(args.input_file, args.output_file, args.old_name, args.new_name)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())