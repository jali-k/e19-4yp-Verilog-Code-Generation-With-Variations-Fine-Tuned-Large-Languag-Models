#!/usr/bin/env python3
"""
Main script to run Verilog transformations.
This script provides a command-line interface to run single transformations
or chains of transformations on Verilog code.
"""

import os
import sys
import argparse
import importlib
import logging
from verilog_xform_framework import run_xform, run_xform_chain

# Import all transformations
from xform_var_type import ChangeVarTypeXform
from xform_module_name import ChangeModuleNameXform
from xform_port_rename import RenamePortXform
from xform_reset_condition import ChangeResetConditionXform
from xform_signal_width import ChangeSignalWidthXform
from xform_add_enable import AddEnableSignalXform
from xform_rename_parameter import RenameParameterXform
from xform_rename_clock import RenameClockXform

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("xform_runner")


def list_transformations():
    """Print a list of available transformations."""
    print("Available transformations:")
    print("1. Change variable type (e.g., reg to wire)")
    print("   Usage: --type var_type --var VAR_NAME --from FROM_TYPE --to TO_TYPE")
    print()
    print("2. Change module name")
    print("   Usage: --type module_name --from FROM_NAME --to TO_NAME")
    print()
    print("3. Rename port")
    print(
        "   Usage: --type port_rename --from FROM_NAME --to TO_NAME [--module MODULE_NAME]"
    )
    print()
    print("4. Change reset condition (active-high to active-low or vice versa)")
    print("   Usage: --type reset_condition --signal RESET_SIGNAL [--high-to-low 0/1]")
    print()
    print("5. Change signal width")
    print("   Usage: --type signal_width --signal SIGNAL_NAME --width NEW_WIDTH")
    print()
    print("6. Add enable signal to counter")
    print("   Usage: --type add_enable --enable ENABLE_NAME --counter COUNTER_NAME")
    print()
    print("7. Rename parameter")
    print(
        "   Usage: --type param_rename --from FROM_NAME --to TO_NAME [--module MODULE_NAME]"
    )
    print()
    print("8. Rename clock signal")
    print("   Usage: --type clock_rename --from FROM_NAME --to TO_NAME")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run Verilog transformations")

    parser.add_argument(
        "--list", action="store_true", help="List available transformations"
    )
    parser.add_argument("--input", "-i", help="Input Verilog file")
    parser.add_argument(
        "--output", "-o", help="Output file (default: input_transformed.v)"
    )

    # Transformation type selection
    parser.add_argument(
        "--type",
        "-t",
        choices=[
            "var_type",
            "module_name",
            "port_rename",
            "reset_condition",
            "signal_width",
            "add_enable",
            "param_rename",
            "clock_rename",
        ],
        help="Type of transformation to apply",
    )

    # Parameters for different transformation types
    parser.add_argument("--var", help="Variable name for var_type transformation")
    parser.add_argument("--from", dest="from_val", help="From value (type, name, etc.)")
    parser.add_argument("--to", dest="to_val", help="To value (type, name, etc.)")
    parser.add_argument(
        "--module", help="Module name for transformations that target a specific module"
    )
    parser.add_argument(
        "--signal",
        help="Signal name for signal_width or reset_condition transformations",
    )
    parser.add_argument("--width", help="New width for signal_width transformation")
    parser.add_argument(
        "--high-to-low",
        type=int,
        default=1,
        help="1 for high-to-low, 0 for low-to-high",
    )
    parser.add_argument(
        "--enable", help="Enable signal name for add_enable transformation"
    )
    parser.add_argument("--counter", help="Counter name for add_enable transformation")

    # Run a chain of transformations from a config file
    parser.add_argument(
        "--chain", help="Run a chain of transformations defined in a file"
    )

    return parser.parse_args()


def create_transformation(args):
    """Create a transformation object based on command-line arguments."""
    if args.type == "var_type":
        if not all([args.var, args.from_val, args.to_val]):
            logger.error("Missing required arguments for var_type transformation")
            return None
        return ChangeVarTypeXform(args.var, args.from_val, args.to_val)

    elif args.type == "module_name":
        if not all([args.from_val, args.to_val]):
            logger.error("Missing required arguments for module_name transformation")
            return None
        return ChangeModuleNameXform(args.from_val, args.to_val)

    elif args.type == "port_rename":
        if not all([args.from_val, args.to_val]):
            logger.error("Missing required arguments for port_rename transformation")
            return None
        return RenamePortXform(args.from_val, args.to_val, args.module)

    elif args.type == "reset_condition":
        if not args.signal:
            logger.error(
                "Missing required arguments for reset_condition transformation"
            )
            return None
        return ChangeResetConditionXform(args.signal, bool(args.high_to_low))

    elif args.type == "signal_width":
        if not all([args.signal, args.width]):
            logger.error("Missing required arguments for signal_width transformation")
            return None
        return ChangeSignalWidthXform(args.signal, args.width)

    elif args.type == "add_enable":
        if not all([args.enable, args.counter]):
            logger.error("Missing required arguments for add_enable transformation")
            return None
        return AddEnableSignalXform(args.enable, args.counter)

    elif args.type == "param_rename":
        if not all([args.from_val, args.to_val]):
            logger.error("Missing required arguments for param_rename transformation")
            return None
        return RenameParameterXform(args.from_val, args.to_val, args.module)

    elif args.type == "clock_rename":
        if not all([args.from_val, args.to_val]):
            logger.error("Missing required arguments for clock_rename transformation")
            return None
        return RenameClockXform(args.from_val, args.to_val)

    else:
        logger.error(f"Unknown transformation type: {args.type}")
        return None


def parse_chain_file(chain_file):
    """Parse a chain file and create a list of transformations."""
    import json

    try:
        with open(chain_file, "r") as f:
            chain_config = json.load(f)

        transformations = []

        for xform_config in chain_config:
            xform_type = xform_config.get("type")

            if xform_type == "var_type":
                var_name = xform_config.get("var")
                from_type = xform_config.get("from")
                to_type = xform_config.get("to")
                if all([var_name, from_type, to_type]):
                    transformations.append(
                        ChangeVarTypeXform(var_name, from_type, to_type)
                    )

            elif xform_type == "module_name":
                from_name = xform_config.get("from")
                to_name = xform_config.get("to")
                if all([from_name, to_name]):
                    transformations.append(ChangeModuleNameXform(from_name, to_name))

            elif xform_type == "port_rename":
                from_name = xform_config.get("from")
                to_name = xform_config.get("to")
                module_name = xform_config.get("module")
                if all([from_name, to_name]):
                    transformations.append(
                        RenamePortXform(from_name, to_name, module_name)
                    )

            elif xform_type == "reset_condition":
                signal = xform_config.get("signal")
                high_to_low = xform_config.get("high_to_low", True)
                if signal:
                    transformations.append(
                        ChangeResetConditionXform(signal, high_to_low)
                    )

            elif xform_type == "signal_width":
                signal = xform_config.get("signal")
                width = xform_config.get("width")
                if all([signal, width]):
                    transformations.append(ChangeSignalWidthXform(signal, width))

            elif xform_type == "add_enable":
                enable = xform_config.get("enable")
                counter = xform_config.get("counter")
                if all([enable, counter]):
                    transformations.append(AddEnableSignalXform(enable, counter))

            elif xform_type == "param_rename":
                from_name = xform_config.get("from")
                to_name = xform_config.get("to")
                module_name = xform_config.get("module")
                if all([from_name, to_name]):
                    transformations.append(
                        RenameParameterXform(from_name, to_name, module_name)
                    )

            elif xform_type == "clock_rename":
                from_name = xform_config.get("from")
                to_name = xform_config.get("to")
                if all([from_name, to_name]):
                    transformations.append(RenameClockXform(from_name, to_name))

            else:
                logger.warning(
                    f"Unknown transformation type in chain file: {xform_type}"
                )

        return transformations

    except Exception as e:
        logger.error(f"Error parsing chain file {chain_file}: {e}")
        return None


def main():
    """Main entry point."""
    args = parse_args()

    if args.list:
        list_transformations()
        return 0

    if not args.input:
        logger.error("Input file is required")
        return 1

    if not os.path.exists(args.input):
        logger.error(f"Input file {args.input} does not exist")
        return 1

    output_file = args.output
    if not output_file:
        base, ext = os.path.splitext(args.input)
        output_file = f"{base}_transformed{ext}"

    if args.chain:
        # Run a chain of transformations
        transformations = parse_chain_file(args.chain)
        if transformations:
            logger.info(f"Running chain of {len(transformations)} transformations")
            success = run_xform_chain(transformations, args.input, output_file)
            return 0 if success else 1
        else:
            logger.error("Failed to parse chain file")
            return 1

    # Run a single transformation
    if not args.type:
        logger.error("Transformation type is required")
        return 1

    transformation = create_transformation(args)
    if not transformation:
        return 1

    logger.info(f"Running transformation: {transformation.description}")
    success = run_xform(transformation, args.input, output_file)

    return 0 if success else 1
