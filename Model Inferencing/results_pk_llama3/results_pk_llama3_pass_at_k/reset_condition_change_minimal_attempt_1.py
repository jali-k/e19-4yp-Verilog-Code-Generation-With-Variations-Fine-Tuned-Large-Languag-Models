# Generated by Ollama Llama 3
# Task: reset_condition_change_minimal
# Attempt: 1
# Success: False
# Overall Score: 0.418

Here is a Python module for transforming Verilog/SystemVerilog code to change the reset condition from active-high to active-low or vice versa:
```python
import pyverilog.ast as ast
import re
from argparse import ArgumentParser, RawTextHelpFormatter
from xforms.utils import AstVisitor, PatternFinder

class ResetConditionTransformer(AstVisitor):
    def __init__(self, direction):
        self.direction = direction  # 'high' or 'low'
        self.modified_code = ''

    def visit_if_stmt(self, node):
        if node.cond is not None and isinstance(node.cond, ast.expr) and \
           str(node.cond).startswith('rst'):
            if self.direction == 'low':
                new_cond = f'!({str(node.cond)[5:]})'
            else:
                new_cond = f'({str(node.cond)[5:]})'
            node.cond = ast.expr(new_cond)
            self.modified_code += f'{node}\n'

    def visit_sequence_stmt(self, node):
        for stmt in node.stmts:
            if isinstance(stmt, ast.if_stmt):
                self.visit_if_stmt(stmt)

class ResetConditionXform(PatternFinder):
    def __init__(self, direction):
        super().__init__()
        self.direction = direction

    def find_pattern(self, ast_node):
        return ast.IfStmt or ast.SequenceStmt

    def replace_pattern(self, node):
        visitor = ResetConditionTransformer(self.direction)
        visitor.visit(node)
        return visitor.modified_code

def main():
    parser = ArgumentParser(description='Reset Condition Transformer',
                             formatter_class=RawTextHelpFormatter)
    parser.add_argument('-d', '--direction', choices=['high', 'low'],
                         help='Direction of the reset condition (default: high)')
    parser.add_argument('input_file', type=str, help='Input Verilog/SystemVerilog file')
    parser.add_argument('output_file', type=str, help='Output Verilog/SystemVerilog file')

    args = parser.parse_args()
    direction = args.direction or 'high'

    try:
        with open(args.input_file, 'r') as f:
            ast_tree = pyverilog.parse(f.read())
        transformed_code = ResetConditionXform(direction).transform(ast_tree)
        if transformed_code:
            with open(args.output_file, 'w') as f:
                f.write(transformed_code)
            print(f'Transformation successful: {args.input_file} -> {args.output_file}')
        else:
            print(f'Error transforming: {args.input_file}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()
```
Here's a breakdown of the code:

1. The `ResetConditionTransformer` class is a custom visitor that inherits from `AstVisitor`. It has an initialization method that takes the direction of the reset condition (either 'high' or 'low') and stores it in an instance variable.
2. The `visit_if_stmt` method checks if the if statement has a condition that starts with 'rst'. If so, it changes the condition to either '!rst' (for low-to-high) or 'rst' (for high-to-low), depending on the direction.
3. The `visit_sequence_stmt` method recursively visits all if statements within a sequence statement and applies the transformation.
4. The `ResetConditionXform` class is a custom xform that inherits from `PatternFinder`. It has an initialization method that takes the direction of the reset condition and stores it in an instance variable.
5. The `find_pattern` method specifies the pattern to search for (in this case, if statements or sequence statements).
6. The `replace_pattern` method creates a new visitor instance and applies the transformation to the AST node.
7. The `main` function parses command-line arguments using `argparse`, reads the input file, applies the transformation, and writes the output file.

To use this module, simply run it from the command line with the following syntax:
```bash
python reset_condition_xform.py -d high|low input_file.v output_file.v
```
Replace `input_file.v` and `output_file.v` with your actual Verilog/SystemVerilog files. The `-d` option specifies the direction of the reset condition (either 'high' or 'low').