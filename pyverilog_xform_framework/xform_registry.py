#!/usr/bin/env python3
"""
Registry for all available transformations.
This implementation allows using common argument names (--from, --to) across transformations
by using subcommands in argparse.
"""

import sys
import os
import argparse

# Import the transformation functions directly
from reg_to_wire_xform import transform_reg_to_wire
from module_name_xform import transform_module_name
from rename_port_xform import transform_rename_port
from change_reset_condition_xform import transform_reset_condition

# from change_signal_width_xform import transform_signal_width
# from add_enable_signal_xform import transform_add_enable
# from rename_clock_xform import transform_rename_clock

# Dictionary of all available transformations
AVAILABLE_XFORMS = {
    "reg_to_wire": {
        "description": "Change reg variables to wire",
        "function": transform_reg_to_wire,
        "args": {
            "target_variable": {
                "help": "Specific variable to transform (default: all reg variables)",
                "required": False,
                "arg_name": "variable",
            }
        },
    },
    "module_name": {
        "description": "Change module name",
        "function": transform_module_name,
        "args": {
            "from_name": {
                "help": "Original module name",
                "required": True,
                "arg_name": "from",
            },
            "to_name": {
                "help": "New module name",
                "required": True,
                "arg_name": "to",
            },
        },
    },
    "port_rename": {
        "description": "Rename ports in a module",
        "function": transform_rename_port,
        "args": {
            "from_name": {
                "help": "Original port name",
                "required": True,
                "arg_name": "from",
            },
            "to_name": {
                "help": "New port name",
                "required": True,
                "arg_name": "to",
            },
        },
    },
    "reset_condition": {
        "description": "Transform reset condition from active-high to active-low or vice versa",
        "function": transform_reset_condition,
        "args": {
            "reset_signal": {
                "help": "Name of the reset signal",
                "required": True,
                "arg_name": "signal",
            },
            "active_high_to_low": {
                "help": "Direction of change: high_to_low or low_to_high",
                "required": False,
                "arg_name": "direction",
            },
        },
    },
    # "signal_width": {
    #     "description": "Change a signal's width in a Verilog module",
    #     "function": transform_signal_width,
    #     "args": {
    #         "signal_name": {
    #             "help": "Name of the signal to modify",
    #             "required": True,
    #             "arg_name": "signal",
    #         },
    #         "new_width": {
    #             "help": "New width in the format 'msb:lsb' (e.g., '3:0')",
    #             "required": True,
    #             "arg_name": "width",
    #         },
    #     },
    # },
    # "add_enable": {
    #     "description": "Add an enable signal to a counter in a Verilog module",
    #     "function": transform_add_enable,
    #     "args": {
    #         "enable_name": {
    #             "help": "Name of the enable signal to add",
    #             "required": True,
    #             "arg_name": "enable",
    #         },
    #         "counter_name": {
    #             "help": "Name of the counter to control",
    #             "required": True,
    #             "arg_name": "counter",
    #         },
    #     },
    # },
    # "rename_clock": {
    #     "description": "Rename a clock signal in a Verilog module",
    #     "function": transform_rename_clock,
    #     "args": {
    #         "from_name": {
    #             "help": "Original clock signal name",
    #             "required": True,
    #             "arg_name": "from",
    #         },
    #         "to_name": {
    #             "help": "New clock signal name",
    #             "required": True,
    #             "arg_name": "to",
    #         },
    #     },
    # },
}


def list_xforms():
    """Print a list of all available transformations."""
    print("Available transformations:")
    for name, info in AVAILABLE_XFORMS.items():
        print(f"  {name}: {info['description']}")
        print("    Arguments:")
        for arg_name, arg_info in info["args"].items():
            required = "required" if arg_info.get("required", False) else "optional"
            cmd_arg = arg_info.get("arg_name", arg_name)
            print(f"      --{cmd_arg}: {arg_info['help']} ({required})")
        print()


def setup_parser():
    """Set up the argument parser with subcommands for each transformation."""
    parser = argparse.ArgumentParser(description="Run Verilog transformations")

    # Add common arguments
    parser.add_argument(
        "--list", action="store_true", help="List all available transformations"
    )

    # Add subparsers for each transformation
    subparsers = parser.add_subparsers(dest="xform", help="Transformation to apply")

    # Add a subparser for each transformation
    for xform_name, xform_info in AVAILABLE_XFORMS.items():
        subparser = subparsers.add_parser(xform_name, help=xform_info["description"])

        # Add input and output arguments to each subparser
        subparser.add_argument(
            "--input", "-i", required=True, help="Input Verilog file"
        )
        subparser.add_argument(
            "--output", "-o", required=True, help="Output Verilog file"
        )

        # Add transformation-specific arguments
        for param_name, param_info in xform_info["args"].items():
            cmd_arg = param_info.get("arg_name", param_name)
            required = param_info.get("required", False)
            subparser.add_argument(
                f"--{cmd_arg}",
                help=param_info["help"],
                required=required,
                dest=param_name,  # Use the internal parameter name as destination
            )

    return parser


def run_xform(xform_name, args):
    """
    Run a transformation based on the name and arguments.

    Args:
        xform_name (str): Name of the transformation
        args (Namespace): Command-line arguments namespace

    Returns:
        bool: True if successful, False otherwise
    """
    if xform_name not in AVAILABLE_XFORMS:
        print(f"Error: Unknown transformation '{xform_name}'")
        return False

    xform_info = AVAILABLE_XFORMS[xform_name]
    xform_function = xform_info["function"]

    # Get input and output files
    input_file = args.input
    output_file = args.output

    # Ensure input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return False

    # Create function arguments dictionary
    function_args = {}
    for param_name in xform_info["args"]:
        if hasattr(args, param_name) and getattr(args, param_name) is not None:
            value = getattr(args, param_name)

            # Special handling for specific transformations
            if (
                xform_name == "reset_condition"
                and param_name == "active_high_to_low"
                and value is not None
            ):
                # Convert string to boolean
                if value.lower() in ["high_to_low", "true", "1"]:
                    value = True
                else:
                    value = False

            function_args[param_name] = value

    # Call the transformation function
    try:
        print(f"Running transformation: {xform_name}")
        return xform_function(input_file, output_file, **function_args)
    except Exception as e:
        print(f"Error running transformation '{xform_name}': {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function to parse command line arguments and run transformations."""
    parser = setup_parser()
    args = parser.parse_args()

    # List available transformations
    if args.list:
        list_xforms()
        return 0

    # Check if a transformation was specified
    if not args.xform:
        parser.print_help()
        return 1

    # Run the transformation
    success = run_xform(args.xform, args)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
