# Generated by Ollama Llama 3
# Task: fsm_state_rename_minimal
# Attempt: 3
# Success: False
# Overall Score: 0.515

import argparse

from pyverilog.ast import *

def find_states(node):
    """Find all states in given node"""
    if isinstance(node, EnumDecl) and 'state' in node.name.lower():
        yield node
    else:
        for child in node.children():
            yield from find_states(child)

def rename_state(old_prefix, new_prefix, state_node):
    """Rename all occurences of a state enum/param"""
    # get state name
    name = state_node.name

    if old_prefix in name and not new_prefix in name:
        # update enum decl node
        new_name = name.replace(old_prefix, new_prefix)

        # add the new value to the end 
        new_value = str(len(state_node.values) + 1)
        new_values = []
        for i in state_node.values:
            if isinstance(i.value, ASTNumValue):
                old_val = int(i.value.value)
                new_val = old_val
                if old_prefix in str(old_val) and not new_prefix in str(new_val):
                    new_val += new_prefix + '0' * (len(str(old_val)) - len(str(new_val)))
            new_values.append(ASTNumValue(new_val))

        # update value list
        state_node.values = new_values

        # update name 
        state_node.name = ASTNameDecl(new_name)

def transform_ast(node, old_prefix, new_prefix):
    """Perform the actual transformation"""
    for state in find_states(node):
        rename_state(old_prefix, new_prefix, state)    

def main():
    parser = argparse.ArgumentParser(description='Systematically rename FSM states')
    parser.add_argument('input', help='Input verilog file path')
    parser.add_argument('--output', default='', help='Output Verilog file path')
    parser.add_argument('-o', '--old-prefix', required=True, type=str, help='Old prefix to search for in state names')
    parser.add_argument('-n', '--new-prefix', required=True, type=str, help='New prefix to append to state names')

    args = parser.parse_args()

    # parse input file
    ast = PyVerilogParser(args.input).parse()
    
    transform_ast(ast, args.old_prefix, args.new_prefix)

    if args.output:
        with open(args.output, 'w') as f:
            print(ast.to_verilog(), file=f)
    else:
        print(ast.to_verilog())

if __name__ == '__main__':
    main()