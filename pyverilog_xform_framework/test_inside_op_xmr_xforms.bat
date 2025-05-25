@echo off
setlocal

set INPUT_DIR=inputs
set OUTPUT_DIR=outputs

:: Create output directories if they don't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo Testing inside operator with XMR in different scenarios...

:: Test inside operator with module XMR
python xform_inside_op_xmr.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_module_xmr.v --signal mem_array --xmr-type module_xmr
echo Ran xform_inside_op_xmr.py with module_xmr

:: Test inside operator with interface XMR
python xform_inside_op_xmr.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_interface_xmr.v --signal mem_array --xmr-type interface_xmr
echo Ran xform_inside_op_xmr.py with interface_xmr

:: Test inside operator with class XMR
python xform_inside_op_xmr.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_class_xmr.v --signal mem_array --xmr-type class_xmr
echo Ran xform_inside_op_xmr.py with class_xmr

:: Test inside operator with virtual interface XMR
python xform_inside_op_xmr.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_virtual_interface_xmr.v --signal mem_array --xmr-type virtual_interface_xmr
echo Ran xform_inside_op_xmr.py with virtual_interface_xmr

:: Test inside operator with structure XMR
python xform_inside_op_xmr.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_structure_xmr.v --signal mem_array --xmr-type structure_xmr
echo Ran xform_inside_op_xmr.py with structure_xmr

:: Test inside operator with package XMR
python xform_inside_op_xmr.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_package_xmr.v --signal mem_array --xmr-type package_xmr
echo Ran xform_inside_op_xmr.py with package_xmr

:: Test inside operator with mix of different XMRs
python xform_inside_op_xmr.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\inside_mix_xmr.v --signal mem_array --xmr-type mix_xmr
echo Ran xform_inside_op_xmr.py with mix_xmr

echo All inside operator XMR transformations completed. Check the outputs directory for results.

endlocal