@echo off
setlocal

set INPUT_DIR=inputs
set OUTPUT_DIR=outputs

:: Create output directories if they don't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo Testing inside operator negative test cases...

:: Test out of index access
python xform_inside_op_negative.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_negative_out_of_index.v --signal mem_array --test-type out_of_index
echo Ran xform_inside_op_negative.py with out_of_index

:: Test wildcard index with associative array
python xform_inside_op_negative.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_negative_wildcard_index.v --signal mem_array --test-type wildcard_index
echo Ran xform_inside_op_negative.py with wildcard_index

echo All inside operator negative test transformations completed. Check the outputs directory for results.

endlocal