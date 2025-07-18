# Generated by Ollama Llama 3
# Task: add_enable_signal_minimal
# Attempt: 9
# Success: False
# Overall Score: 0.478


"""


import argparse, re
from pyverilog import VerilogParser
from pyverilog.ast.verilog.moduledef import ModuleDef
# from pyverilog.ast.verilog.net import Net
from pyverilog.utils import verilogText2Py
from pyverilog.vparser.utils import name2port


class EnableCounterVisitor(VerilogParser):
    def __init__(self):
        super().__init__()
        self.module = None
        self._counter_stmt = []

    @property
    def counter_stmt(self):
        return [stmt for stmt in self._counter_stmt]

    def visit(self, module):
        self.module = module

        for m in module:
            if isinstance(m, ModuleDef) and 'counter' in m.name:
                self.visit_moduledef(m)


class EnableCounterTransformer():
    def __init__(self):
        pass

    @staticmethod
    def add_enable_port(module, name):
        newport = [p for p in module.get_ports() if not isinstance(p, str)]

        if len(newport) != 0:
            idx = max([port['idx'] for port in newport]) + 1
        else:
            idx = 32768

        module.add_port(name, 'logic', idx=idx)

    @staticmethod
    def create_enable_condition(module):
        enable = "always_ff @(posedge clk)"
        enable += "\n\t{"
        enable += "\n\t\tif (en) " + " ".join(["%s <= %s" %(p.name, p.name) for p in module.get_inputs()])
        enable += "\n\t\telse begin"

        return enable

    @staticmethod
    def add_enable_condition(module):
        if 'en' not in [port['name'] for port in module.get_ports()]:
            EnableCounterTransformer().add_enable_port(module, 'en')

            for stmt in module:
                if isinstance(stmt, str) and 'counter <= counter + 1' in stmt:
                    stmt += "; en = 0"
                else:
                    stmt += "\n\t\t\ten = 1"

                yield stmt

        elif [port['name'] for port in module.get_ports()]:
            for stmt in module:
                if isinstance(stmt, str) and 'counter <= counter + 1' in stmt:
                    stmt += "; en = 0"
                else:
                    stmt += "\n\t\t\ten = 1"

                yield stmt

    @staticmethod
    def wrap_with_enable_condition(module):
        enable_cond = EnableCounterTransformer().create_enable_condition(module)

        for stmt in module:
            if isinstance(stmt, str) and 'counter <= counter + 1' not in stmt \
                    or 'counter' not in name2port(stmt).keys():
                yield stmt

            elif isinstance(stmt, str):

                stmt += "\n" + enable_cond.replace('posedge', 'posedge').replace('en', 'counter')
                stmt = re.sub(';\s*', ";\n\t\t\t", stmt)

        yield from EnableCounterTransformer().add_enable_condition(module)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--inputfile', help='input Verilog file')
    parser.add_argument('-o', '--outputfile', help='output Verilog file')

    args = parser.parse_args()

    if not args.inputfile or not args.outputfile:
        print("Missing input/output file, please specify both files")

        return False

    try:
        with open(args.inputfile) as fp:
            text = verilogText2Py(fp.read())
    except FileNotFoundError as e:
        print('file does not exist')
        raise e

    if isinstance(text, list):
        text = "\n".join([stmt for stmt in text])

    parser = VerilogParser()
    parser.parse(text)

    module_list = EnableCounterVisitor().visit(parser)

    with open(args.outputfile, 'w+') as fp:
        for module in module_list:
            for stmt in EnableCounterTransformer().wrap_with_enable_condition(module):
                print(stmt + "\n", file=fp)


if __name__ == '__main__':
    main()
