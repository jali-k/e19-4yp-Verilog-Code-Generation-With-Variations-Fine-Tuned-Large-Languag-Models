# Generated by Ollama Llama 3
# Task: add_enable_signal_minimal
# Attempt: 8
# Success: False
# Overall Score: 0.465

import pyverilog
from pyverilog.ast import *

def add_enable_counter(xf):
    # Identify counter increment statements
    if not isinstance(xf, ASTStatement) or not xf.kind == 'assign' or len(xf.lvalue) != 1: 
        return False
    
    lvalue = xf.lvalue[0]
    
    if not isinstance(lvalue, ASTSignal) or lvalue.name != 'counter':
        return False

    # Add enable signal as new input port
    ports = [p for p in xf.portlist]
    if not any([isinstance(p, ASTInput) and p.name == 'enable' for p in ports]):
        ports.append(ASTInput(name='enable'))
    
    # Wrap counter increments with enable condition
    lvalue.assign_expr = ASTBinOp(op=ASTAnd(), lhs=lvalue.assign_expr, rhs=ASTLiteral(value=True))
    lvalue.assign_expr = ASTIfElse(cond=ASTBinaryExpr(lhs=lvalue.assign_expr, op=ASTOr(), rhs=ASTLiteral(value=False)), then_expr=lvalue.assign_expr)
    
    # Preserve existing sensitivity lists and reset logic
    reset_logic = [r for r in xf.portlist if isinstance(r, ASTInput) and r.name == 'reset']
    if len(reset_logic):
        lvalue.assign_expr = ASTIfElse(cond=ASTBinaryExpr(lhs=lvalue.assign_expr, op=ASTAnd(), rhs=ASTLiteral(value=True)), then_expr=lvalue.assign_expr)
    
    xf.portlist = ports
    return True

def main():
    parser = argparse.ArgumentParser(description='Add enable signal to control a counter')
    parser.add_argument('-v', '--verilog_file', help='Verilog source file path', required=True)
    args = parser.parse_args()
    
    with open(args.verilog_file, 'r') as f:
        text = f.read()
        
    ast = pyverilog.parse(text)
    xform_result = add_enable_counter(ast)
    if not xform_result:
        print('Transformation failed!')
        return
    
    text = str(ast)
    with open(args.verilog_file, 'w') as f:
        f.write(text)
    
if __name__ == '__main__':
    main()