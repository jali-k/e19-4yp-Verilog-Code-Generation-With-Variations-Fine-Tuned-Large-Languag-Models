@echo off
setlocal

set INPUT_DIR=inputs
set OUTPUT_DIR=outputs

:: Create output directories if they don't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo Testing inside operator miscellaneous/edge cases...

:: Test x and z values
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_x_z_values.v --signal mem_array --misc-type x_z_values
echo Ran xform_inside_op_misc.py with x_z_values

:: Test [0:0] select on array
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_zero_select.v --signal mem_array --misc-type zero_select
echo Ran xform_inside_op_misc.py with zero_select

:: Test comparison result with x
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_comparison_result.v --signal mem_array --misc-type comparison_result
echo Ran xform_inside_op_misc.py with comparison_result

:: Test unsized literals
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_unsized_literal.v --signal mem_array --misc-type unsized_literal
echo Ran xform_inside_op_misc.py with unsized_literal

:: Test open range error
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_open_range_error.v --signal mem_array --misc-type open_range_error
echo Ran xform_inside_op_misc.py with open_range_error

:: Test array in initial block
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_initial_block.v --signal mem_array --misc-type initial_block
echo Ran xform_inside_op_misc.py with initial_block

:: Test empty VSA
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_empty_vsa.v --signal mem_array --misc-type empty_vsa
echo Ran xform_inside_op_misc.py with empty_vsa

:: Test array methods
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_array_methods.v --signal mem_array --misc-type array_methods
echo Ran xform_inside_op_misc.py with array_methods

:: Test generate loop
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_generate_loop.v --signal mem_array --misc-type generate_loop
echo Ran xform_inside_op_misc.py with generate_loop

:: Test case expression
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_case_expression.v --signal mem_array --misc-type case_expression
echo Ran xform_inside_op_misc.py with case_expression

:: Test always_comb
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_always_comb.v --signal mem_array --misc-type always_comb
echo Ran xform_inside_op_misc.py with always_comb

:: Test array method clause
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_array_method_clause.v --signal mem_array --misc-type array_method_clause
echo Ran xform_inside_op_misc.py with array_method_clause

:: Test function returning VSA
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_function_returning_vsa.v --signal mem_array --misc-type function_returning_vsa
echo Ran xform_inside_op_misc.py with function_returning_vsa

:: Test while loop with array slice
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_while_loop_array_slice.v --signal mem_array --misc-type while_loop_array_slice
echo Ran xform_inside_op_misc.py with while_loop_array_slice

:: Test upward XMR array
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_upward_xmr_array.v --signal mem_array --misc-type upward_xmr_array
echo Ran xform_inside_op_misc.py with upward_xmr_array

:: Test chained function
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_chained_function.v --signal mem_array --misc-type chained_function
echo Ran xform_inside_op_misc.py with chained_function

:: Test DPI function
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_dpi_function.v --signal mem_array --misc-type dpi_function
echo Ran xform_inside_op_misc.py with dpi_function

:: Test stress with large array
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_stress_large_array.v --signal mem_array --misc-type stress_large_array
echo Ran xform_inside_op_misc.py with stress_large_array

:: Test class static array
python xform_inside_op_misc.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_misc_class_static_array.v --signal mem_array --misc-type class_static_array
echo Ran xform_inside_op_misc.py with class_static_array

echo All inside operator miscellaneous test transformations completed. Check the outputs directory for results.

endlocal