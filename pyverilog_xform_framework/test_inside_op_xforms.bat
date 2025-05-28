@echo off
setlocal

set INPUT_DIR=inputs
set OUTPUT_DIR=outputs

:: Create output directories if they don't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo Testing inside operator variations...

:: Test array as a whole in inside operator
python xform_inside_op_array.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_array_whole.v --signal mem_array --test-type array_as_whole
echo Ran xform_inside_op_array.py with array_as_whole

:: Test array slice in inside operator
python xform_inside_op_array.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_array_slice.v --signal mem_array --test-type array_slice
echo Ran xform_inside_op_array.py with array_slice

:: Test part select in inside operator
python xform_inside_op_array.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_part_select.v --signal mem_array --test-type part_select
echo Ran xform_inside_op_array.py with part_select

:: Test array select for MDA in inside operator
python xform_inside_op_array.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_mda_select.v --signal mem_array --test-type array_select_mda
echo Ran xform_inside_op_array.py with array_select_mda

:: Test constant/variable index in inside operator
python xform_inside_op_array.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_const_var_index.v --signal mem_array --test-type constant_var_index
echo Ran xform_inside_op_array.py with constant_var_index

:: Test XMR in array index in inside operator
python xform_inside_op_array.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_xmr_index.v --signal mem_array --test-type xmr_index
echo Ran xform_inside_op_array.py with xmr_index

:: Test function call in array index in inside operator
python xform_inside_op_array.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_function_call_index.v --signal mem_array --test-type function_call_index
echo Ran xform_inside_op_array.py with function_call_index

echo All inside operator transformations completed. Check the outputs directory for results.

endlocal
