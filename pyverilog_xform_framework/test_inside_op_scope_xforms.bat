@echo off
setlocal

set INPUT_DIR=inputs
set OUTPUT_DIR=outputs

:: Create output directories if they don't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo Testing inside operator in different scopes...

:: Test inside operator in module scope
python xform_inside_op_scope.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_module_scope.v --signal mem_array --scope module
echo Ran xform_inside_op_scope.py with module scope

:: Test inside operator in interface scope
python xform_inside_op_scope.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_interface_scope.v --signal mem_array --scope interface
echo Ran xform_inside_op_scope.py with interface scope

:: Test inside operator in package scope
python xform_inside_op_scope.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_package_scope.v --signal mem_array --scope package
echo Ran xform_inside_op_scope.py with package scope

:: Test inside operator in SystemVerilog class scope
python xform_inside_op_scope.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_sv_class_scope.v --signal mem_array --scope sv_class
echo Ran xform_inside_op_scope.py with sv_class scope

:: Test inside operator in $unit scope
python xform_inside_op_scope.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_dollar_unit_scope.v --signal mem_array --scope dollar_unit
echo Ran xform_inside_op_scope.py with dollar_unit scope

:: Test inside operator in generate block scope with escape names
python xform_inside_op_scope.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_generate_block_scope.v --signal mem_array --scope generate_block
echo Ran xform_inside_op_scope.py with generate_block scope

echo All inside operator scope transformations completed. Check the outputs directory for results.

endlocal