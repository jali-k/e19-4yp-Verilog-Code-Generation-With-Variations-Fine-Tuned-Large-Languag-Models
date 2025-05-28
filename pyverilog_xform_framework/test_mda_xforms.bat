@echo off
setlocal

set INPUT_DIR=inputs
set OUTPUT_DIR=outputs

:: Create output directories if they don't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%
if not exist outputs_old mkdir outputs_old

echo Testing MDA transformations...

:: Test fixed range MDA transformation
python xform_range_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\fixed_range_output.v --signal mem_array --ranges 7:0 0:15
echo Ran xform_range_mda.py with regular ranges

python xform_range_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\fixed_nonzero_output.v --signal mem_array --ranges 101:120
echo Ran xform_range_mda.py with non-zero ranges

python xform_range_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\fixed_negative_output.v --signal mem_array --ranges -10:-1
echo Ran xform_range_mda.py with negative ranges

python xform_range_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\fixed_reverse_output.v --signal mem_array --ranges 15:0
echo Ran xform_range_mda.py with reverse direction ranges

:: Test dynamic MDA transformation
python xform_dynamic_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\dynamic_output.v --signal mem_array --dimensions 2
echo Ran xform_dynamic_mda.py

:: Test queue MDA transformation
python xform_queue_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\queue_output.v --signal mem_array --dimensions 1
echo Ran xform_queue_mda.py for unbounded queue

python xform_queue_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\bounded_queue_output.v --signal mem_array --dimensions 1 --bounded --bound-size 10
echo Ran xform_queue_mda.py for bounded queue

:: Test associative array transformation
python xform_associative_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_string_output.v --signal mem_array --key-type string
echo Ran xform_associative_mda.py with string keys

python xform_associative_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_vector_output.v --signal mem_array --key-type vector
echo Ran xform_associative_mda.py with vector keys

python xform_associative_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_wildcard_output.v --signal mem_array --key-type wildcard
echo Ran xform_associative_mda.py with wildcard index

:: Test mixed MDA transformation
python xform_mixed_mda.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\mixed_output.v --signal mem_array --mda-spec fixed:7:0 assoc:string queue
echo Ran xform_mixed_mda.py

echo All transformations completed. Check the outputs directory for results.

endlocal