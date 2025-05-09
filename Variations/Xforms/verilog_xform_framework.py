#!/usr/bin/env python3
"""
Base framework for Verilog code transformations.
This provides the common utilities and base classes needed for all transformations.
"""

import re
import os
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("verilog_xform")


class VerilogParser:
    """Parser for Verilog code."""

    @staticmethod
    def parse_file(file_path):
        """Parse a Verilog file and return its content."""
        try:
            with open(file_path, "r") as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            raise


class XformBase(ABC):
    """Base class for Verilog transformations."""

    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def apply(self, verilog_text, **kwargs):
        """
        Apply the transformation to the Verilog text.

        Args:
            verilog_text (str): The Verilog code to transform
            **kwargs: Additional arguments specific to the transformation

        Returns:
            str: The transformed Verilog code
        """
        pass

    def __str__(self):
        return f"{self.name}: {self.description}"


def run_xform(xform, input_path, output_path=None, **kwargs):
    """Run a transformation on a Verilog file."""
    # Determine output path if not provided
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_transformed{ext}"

    try:
        # Parse the input file
        verilog_text = VerilogParser.parse_file(input_path)

        # Apply the transformation
        transformed_text = xform.apply(verilog_text, **kwargs)

        # Write the transformed text
        with open(output_path, "w") as f:
            f.write(transformed_text)

        logger.info(f"Transformation {xform.name} applied successfully")
        logger.info(f"Output written to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error applying transformation {xform.name}: {e}")
        return False


def run_xform_chain(xforms, input_path, output_path=None, **kwargs):
    """Run a chain of transformations on a Verilog file."""
    # Determine output path if not provided
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_transformed{ext}"

    try:
        # Parse the input file
        verilog_text = VerilogParser.parse_file(input_path)

        # Apply each transformation in sequence
        for xform in xforms:
            verilog_text = xform.apply(verilog_text, **kwargs)

        # Write the transformed text
        with open(output_path, "w") as f:
            f.write(verilog_text)

        logger.info(f"Transformation chain applied successfully")
        logger.info(f"Output written to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error applying transformation chain: {e}")
        return False
