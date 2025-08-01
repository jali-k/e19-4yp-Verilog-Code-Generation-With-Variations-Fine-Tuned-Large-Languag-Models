from __future__ import absolute_import
from __future__ import print_function
import pyverilog.vparser.ast as vast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

def main():
    # Define parameter
    width_param = vast.Parameter('WIDTH', vast.Rvalue(vast.IntConst('8')))
    params = vast.Paramlist([width_param])

    # Define ports with parameterized width
    width = vast.Width(vast.Minus(vast.Identifier('WIDTH'), vast.IntConst('1')), vast.IntConst('0'))
    a = vast.Ioport(vast.Input('A', width=width))
    b = vast.Ioport(vast.Input('B', width=width))
    sel = vast.Ioport(vast.Input('SEL'))
    y = vast.Ioport(vast.Output('Y', width=width))
    ports = vast.Portlist([a, b, sel, y])

    # Define continuous assignment: Y = SEL ? A : B
    assign = vast.Assign(
        vast.Lvalue(vast.Identifier('Y')),
        vast.Rvalue(vast.Cond(vast.Identifier('SEL'), vast.Identifier('A'), vast.Identifier('B')))
    )

    # Module items
    items = [assign]

    # Module definition
    ast = vast.ModuleDef("mux_2to1_param", params, ports, items)

    # Generate Verilog code
    codegen = ASTCodeGenerator()
    rslt = codegen.visit(ast)
    with open("mux_2to1_param.v", "w") as f:
        f.write(rslt)

if __name__ == '__main__':
    main()


# Prompt:
# Generate a Python script using Pyverilog to create a Verilog module for a 2:1 multiplexer with parameterized input/output widths. Modify the base mux_2to1.py to:

# Add a WIDTH parameter set to 8 using vast.Parameter and vast.Paramlist.
# Define ports A, B, and Y as [WIDTH-1:0] using vast.Width with vast.Minus. Keep SEL as a single bit.
# Retain the continuous assignment Y = SEL ? A : B with vast.Cond.
# Name the module mux_2to1_param and write to mux_2to1_param.v.
# Align with the test plan’s “array as a whole” and “continuous assign” themes.