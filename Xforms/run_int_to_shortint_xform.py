import re
import os
import sys
import argparse


class Variable:
    """Simple class to represent a variable in the code."""

    def __init__(self, name, var_type, is_param=False):
        self.name = name
        self.type = var_type
        self.is_param = is_param

    def __str__(self):
        return f"{self.type} {self.name}"


class Declaration:
    """Class to represent a declaration in the code."""

    def __init__(self, var_type, names):
        self.type = var_type
        self.names = names  # List of variable names in this declaration

    def __str__(self):
        return f"{self.type} {', '.join(self.names)};"


class Function:
    """Simple class to represent a function in the code."""

    def __init__(self, name, params=None):
        self.name = name
        self.params = params or []

    def get_params(self):
        return self.params


class Method:
    """Simple class to represent a method in the code."""

    def __init__(self, name, params=None):
        self.name = name
        self.params = params or []

    def get_params(self):
        return self.params


class Design:
    """Simple class to represent a design with variable declarations and functions."""

    def __init__(self):
        self.declarations = []
        self.functions = []
        self.methods = []
        self.all_objects = []

    def add_declaration(self, declaration):
        self.declarations.append(declaration)
        self.all_objects.append(declaration)

    def add_function(self, function):
        self.functions.append(function)
        self.all_objects.append(function)

    def add_method(self, method):
        self.methods.append(method)
        self.all_objects.append(method)

    def get_all_objs(self, obj_type):
        return [obj for obj in self.all_objects if isinstance(obj, obj_type)]

    def find_variable(self, name):
        for decl in self.declarations:
            if name in decl.names:
                return Variable(name, decl.type)
        return None

    def __iter__(self):
        """Return an iterator that yields all declarations."""

        class DesignIterator:
            def __init__(self, declarations):
                self.declarations = declarations
                self.index = 0

            def __next__(self):
                if self.index >= len(self.declarations):
                    raise StopIteration
                result = self.declarations[self.index]
                self.index += 1
                return result

        return iter([self.declarations])


def parse_verilog_file(file_path):
    """
    Simple parser to extract variable declarations and functions from a Verilog file.
    This is a basic implementation and doesn't handle all Verilog syntax.
    """
    design = Design()

    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Find variable declarations (very simplified)
        var_pattern = r"(int)\s+([a-zA-Z0-9_,\s]+);"
        for match in re.finditer(var_pattern, content):
            var_type = match.group(1)
            var_names = [name.strip() for name in match.group(2).split(",")]
            design.add_declaration(Declaration(var_type, var_names))

        # Find function declarations (very simplified)
        func_pattern = r"function\s+\w+\s+([a-zA-Z0-9_]+)\s*\((.*?)\)"
        for match in re.finditer(func_pattern, content, re.DOTALL):
            func_name = match.group(1)
            params_str = match.group(2)

            # Parse parameters (very simplified)
            params = []
            for param in params_str.split(","):
                param = param.strip()
                if param:
                    parts = param.split()
                    if len(parts) >= 2 and parts[0] == "int":
                        param_type = parts[0]
                        param_name = parts[1]
                        params.append(Variable(param_name, param_type, is_param=True))

            design.add_function(Function(func_name, params))

        return design

    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return None


def write_transformed_verilog(design, input_file, output_file):
    """
    Write the transformed design back to a Verilog file.
    This is a simple implementation that replaces 'int' with 'shortint'.
    """
    try:
        with open(input_file, "r") as f:
            content = f.read()

        # Replace 'int' declarations with 'shortint'
        # This is a simplified approach and might not handle all cases correctly
        transformed_content = re.sub(r"\bint\b", "shortint", content)

        with open(output_file, "w") as f:
            f.write(transformed_content)

        print(f"Transformed file written to {output_file}")

    except Exception as e:
        print(f"Error writing transformed file: {e}")


def int_to_shortint_xform(design, xform_to_all=False, xform_target=None):
    """
    Transform int variables to shortint.

    Input:
        - design: The design object that we will be transforming.
        - xform_to_all: If this switch is enable, we will do the transformation wherever possible. Default is False.
        - xform_target: Specific target to transform if not transforming all.

    Note:
        - It will only transform variables with type 'int' to 'shortint'.
        - It will not transform parameter types or struct field types.
    """

    def is_target(obj):
        if not isinstance(obj, Declaration):
            return False
        if xform_target:
            # If we have a specific target, check if any of the declaration's names match
            if isinstance(xform_target, str):
                return xform_target in obj.names
            elif hasattr(xform_target, "name"):
                return xform_target.name in obj.names
            else:
                return False
        return True

    transformations_made = False

    # Process variable declarations
    for decls in design:
        for decl in decls:
            if not is_target(decl):
                if xform_to_all and decl.type == "int":
                    # Transform all int declarations
                    print(f"Transforming declaration {decl} from 'int' to 'shortint'")
                    decl.type = "shortint"
                    transformations_made = True
                continue

            # Check if variable is of type 'int'
            if decl.type == "int":
                print(f"Transforming declaration {decl} from 'int' to 'shortint'")
                decl.type = "shortint"
                transformations_made = True

    # Process function parameters
    for func in design.get_all_objs(Function):
        for param in func.get_params():
            should_transform = xform_to_all or (
                xform_target
                and (
                    (isinstance(xform_target, str) and param.name == xform_target)
                    or (
                        hasattr(xform_target, "name")
                        and param.name == xform_target.name
                    )
                )
            )

            if should_transform and param.type == "int":
                print(
                    f"Transforming parameter {param.name} from 'int' to 'shortint' in function {func.name}"
                )
                param.type = "shortint"
                transformations_made = True

    return transformations_made


def main():
    parser = argparse.ArgumentParser(
        description="Transform int variables to shortint in Verilog files"
    )
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: <input>_transformed.sv)",
        default=None,
    )
    parser.add_argument(
        "--target", "-t", help="Specific variable to transform", default=None
    )
    parser.add_argument(
        "--all", "-a", action="store_true", help="Transform all int variables"
    )

    args = parser.parse_args()

    # Determine output file name
    if args.output:
        output_file = args.output
    else:
        base, ext = os.path.splitext(args.input_file)
        output_file = f"{base}_transformed{ext}"

    # Parse the input file
    print(f"Parsing {args.input_file}...")
    design = parse_verilog_file(args.input_file)

    if not design:
        print("Failed to parse input file.")
        return 1

    # Run the transformation
    print("Running int_to_shortint transformation...")
    transformations_made = int_to_shortint_xform(
        design, xform_to_all=args.all, xform_target=args.target
    )

    if not transformations_made:
        print("No transformations made.")
        return 0

    # Write the transformed file
    write_transformed_verilog(design, args.input_file, output_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
