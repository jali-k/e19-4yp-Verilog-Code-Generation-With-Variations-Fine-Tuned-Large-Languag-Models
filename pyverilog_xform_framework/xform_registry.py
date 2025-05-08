#!/usr/bin/env python3
"""
Registry for all available transformations.
This file allows central registration and discovery of transformations.
"""

import sys
import os
import argparse
from xform_framework import XformRunner
from reg_to_wire_xform import RegToWireXform
from module_name_xform import ModuleNameXform

# Dictionary of all available transformations
AVAILABLE_XFORMS = {
    "reg_to_wire": {
        "description": "Change reg variables to wire",
        "class": RegToWireXform,
        "args": {
            "variable": {
                "help": "Specific variable to transform (default: all reg variables)",
                "required": False,
            }
        },
    },
    "module_name": {
        "description": "Change module name",
        "class": ModuleNameXform,
        "args": {
            "from_name": {"help": "Original module name", "required": True},
            "to_name": {"help": "New module name", "required": True},
        },
    },
}


def list_xforms():
    """Print a list of all available transformations."""
    print("Available transformations:")
    for name, info in AVAILABLE_XFORMS.items():
        print(f"  {name}: {info['description']}")
        print("    Arguments:")
        for arg_name, arg_info in info["args"].items():
            required = "required" if arg_info.get("required", False) else "optional"
            print(f"      --{arg_name}: {arg_info['help']} ({required})")
        print()


def create_xform(xform_name, args):
    """
    Create a transformation instance based on the name and arguments.

    Args:
        xform_name (str): Name of the transformation
        args (dict): Dictionary of arguments for the transformation

    Returns:
        XformBase: Instance of the transformation, or None if not found
    """
    if xform_name not in AVAILABLE_XFORMS:
        print(f"Error: Unknown transformation '{xform_name}'")
        return None

    xform_info = AVAILABLE_XFORMS[xform_name]
    xform_class = xform_info["class"]

    # Check for required arguments
    for arg_name, arg_info in xform_info["args"].items():
        if arg_info.get("required", False) and arg_name not in args:
            print(
                f"Error: Required argument '{arg_name}' not provided for '{xform_name}'"
            )
            return None

    # Create the transformation instance with the provided arguments
    try:
        if xform_name == "reg_to_wire":
            return xform_class(args.get("variable"))
        elif xform_name == "module_name":
            return xform_class(args.get("from_name"), args.get("to_name"))
        else:
            print(f"Error: Creation of '{xform_name}' not implemented in registry")
            return None
    except Exception as e:
        print(f"Error creating transformation '{xform_name}': {e}")
        return None


def main():
    """Main function to parse command line arguments and run transformations."""
    parser = argparse.ArgumentParser(
        description="Run Verilog transformations using PyVerilog AST"
    )

    parser.add_argument(
        "--list", action="store_true", help="List all available transformations"
    )
    parser.add_argument("--input", "-i", help="Input Verilog file")
    parser.add_argument("--output", "-o", help="Output Verilog file")
    parser.add_argument("--xform", "-x", help="Transformation to apply")

    # Add dynamic arguments for transformations
    for xform_name, xform_info in AVAILABLE_XFORMS.items():
        for arg_name, arg_info in xform_info["args"].items():
            parser.add_argument(f"--{arg_name}", help=arg_info["help"], required=False)

    args = parser.parse_args()

    # List available transformations
    if args.list:
        list_xforms()
        return 0

    # Check for required arguments
    if not args.input:
        print("Error: Input file is required")
        return 1

    if not args.output:
        print("Error: Output file is required")
        return 1

    if not args.xform:
        print("Error: Transformation is required")
        return 1

    # Ensure input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        return 1

    # Create arguments dictionary for the transformation
    xform_args = {
        arg_name: getattr(args, arg_name, None)
        for xform_info in AVAILABLE_XFORMS.values()
        for arg_name in xform_info["args"]
    }

    # Create the transformation
    xform = create_xform(args.xform, xform_args)
    if not xform:
        return 1

    # Run the transformation
    success = XformRunner.run_xform(xform, args.input, args.output)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
