#!/bin/bash

INPUT_DIR="inputs"
OUTPUT_DIR="outputs"

# Create input and output directories if they don't exist
mkdir -p $INPUT_DIR
mkdir -p $OUTPUT_DIR

# Copy sample files to input directory if not already there
if [ ! -f "$INPUT_DIR/simple_array_example.v" ]; then
    cp simple_array_example.v $INPUT_DIR/
fi

# Test fixed range MDA transformation
python range_mda_xform.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/fixed_range_output.v --signal mem_array --ranges 7:0 0:15
python range_mda_xform.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/fixed_nonzero_output.v --signal mem_array --ranges 101:120
python range_mda_xform.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/fixed_negative_output.v --signal mem_array --ranges -10:-1
python range_mda_xform.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/fixed_reverse_output.v --signal mem_array --ranges 15:0

# Test dynamic MDA transformation
python xform_dynamic_mda.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/dynamic_output.v --signal mem_array --dimensions 2

# Test queue MDA transformation
python xform_queue_mda.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/queue_output.v --signal mem_array --dimensions 1
python xform_queue_mda.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/bounded_queue_output.v --signal mem_array --dimensions 1 --bounded --bound-size 10

# Test associative array transformation
python xform_associative_mda.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/assoc_string_output.v --signal mem_array --key-type string
python xform_associative_mda.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/assoc_vector_output.v --signal mem_array --key-type vector
python xform_associative_mda.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/assoc_wildcard_output.v --signal mem_array --key-type wildcard

# Test mixed MDA transformation
python xform_mixed_mda.py $INPUT_DIR/simple_array_example.v $OUTPUT_DIR/mixed_output.v --signal mem_array --mda-spec fixed:7:0 assoc:string queue

echo "All transformations completed. Check the outputs directory for results."