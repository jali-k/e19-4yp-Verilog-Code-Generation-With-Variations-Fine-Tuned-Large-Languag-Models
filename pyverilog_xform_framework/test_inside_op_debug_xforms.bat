@echo off
setlocal

set INPUT_DIR=inputs
set OUTPUT_DIR=outputs

:: Create output directories if they don't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo Testing inside operator debug and tool-specific cases...

:: Test value annotation in source window
python xform_inside_op_debug.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_debug_value_annotation.v --signal mem_array --debug-type value_annotation
echo Ran xform_inside_op_debug.py with value_annotation

:: Test trace driver and load
python xform_inside_op_debug.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_debug_trace_driver_load.v --signal mem_array --debug-type trace_driver_load
echo Ran xform_inside_op_debug.py with trace_driver_load

:: Test scountdriver functionality
python xform_inside_op_debug.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_debug_scountdriver.v --signal mem_array --debug-type scountdriver
echo Ran xform_inside_op_debug.py with scountdriver

:: Test SHDL XMR force
python xform_inside_op_debug.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_debug_shdl_xmr_force.v --signal mem_array --debug-type shdl_xmr_force
echo Ran xform_inside_op_debug.py with shdl_xmr_force

:: Test UCLI trace command
python xform_inside_op_debug.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_debug_ucli_trace.v --signal mem_array --debug-type ucli_trace
echo Ran xform_inside_op_debug.py with ucli_trace

:: Test UCLI/VPI walkers
python xform_inside_op_debug.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_debug_ucli_vpi_walkers.v --signal mem_array --debug-type ucli_vpi_walkers
echo Ran xform_inside_op_debug.py with ucli_vpi_walkers

echo All inside operator debug test transformations completed. Check the outputs directory for results.

endlocal