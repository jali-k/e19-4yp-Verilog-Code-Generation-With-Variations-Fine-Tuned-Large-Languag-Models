@echo off
setlocal

set INPUT_DIR=inputs
set OUTPUT_DIR=outputs

:: Create output directories if they don't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo Testing inside operator in different contexts...

:: Test inside operator in if statement/nested if
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_if_statement.v --signal mem_array --context if_statement
echo Ran xform_inside_op_context.py with if_statement

:: Test inside operator in case statement
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_case.v --signal mem_array --context case
echo Ran xform_inside_op_context.py with case

:: Test inside operator in while/for loop
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_loop.v --signal mem_array --context loop
echo Ran xform_inside_op_context.py with loop

:: Test inside operator in continuous assign
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_continuous_assign.v --signal mem_array --context continuous_assign
echo Ran xform_inside_op_context.py with continuous_assign

:: Test inside operator in procedural continuous assign
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_procedural_continuous_assign.v --signal mem_array --context procedural_continuous_assign
echo Ran xform_inside_op_context.py with procedural_continuous_assign

:: Test inside operator in procedural assign inside initial/final
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_procedural_assign_initial_final.v --signal mem_array --context procedural_assign_initial_final
echo Ran xform_inside_op_context.py with procedural_assign_initial_final

:: Test inside operator in variable initialization
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_variable_initialization.v --signal mem_array --context variable_initialization
echo Ran xform_inside_op_context.py with variable_initialization

:: Test inside operator in always, always_comb
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_always_comb.v --signal mem_array --context always_comb
echo Ran xform_inside_op_context.py with always_comb

:: Test inside operator in initial and final blocks
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_initial_final_blocks.v --signal mem_array --context initial_final_blocks
echo Ran xform_inside_op_context.py with initial_final_blocks

:: Test inside operator in module high connections (negative scenario)
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_module_highconn.v --signal mem_array --context module_highconn
echo Ran xform_inside_op_context.py with module_highconn

:: Test case inside including unique/priority case
python xform_inside_op_context.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_case_inside.v --signal mem_array --context case_inside
echo Ran xform_inside_op_context.py with case_inside

echo All inside operator context transformations completed. Check the outputs directory for results.

endlocal