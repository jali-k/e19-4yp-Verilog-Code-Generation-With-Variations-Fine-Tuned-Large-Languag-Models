@echo off
setlocal

set INPUT_DIR=inputs
set OUTPUT_DIR=outputs

:: Create output directories if they don't exist
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%
if not exist outputs_old mkdir outputs_old

echo Testing all MDA transformations...

:: Test standard MDA transformations
echo Testing standard MDA transformations...

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

:: Test new transformations for different key types
echo Testing associative array with various key types...

python xform_associative_mda_key_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_int_output.v --signal mem_array --key-type int
echo Ran xform_associative_mda_key_type.py with int key

python xform_associative_mda_key_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_longint_output.v --signal mem_array --key-type longint
echo Ran xform_associative_mda_key_type.py with longint key

python xform_associative_mda_key_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_byte_output.v --signal mem_array --key-type byte
echo Ran xform_associative_mda_key_type.py with byte key

python xform_associative_mda_key_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_bit_vector_output.v --signal mem_array --key-type bit-vector
echo Ran xform_associative_mda_key_type.py with bit-vector key

python xform_associative_mda_key_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_logic_vector_output.v --signal mem_array --key-type logic-vector
echo Ran xform_associative_mda_key_type.py with logic-vector key

python xform_associative_mda_key_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_enum_output.v --signal mem_array --key-type enum
echo Ran xform_associative_mda_key_type.py with enum key

python xform_associative_mda_key_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_class_output.v --signal mem_array --key-type class
echo Ran xform_associative_mda_key_type.py with class key

python xform_associative_mda_key_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_union_output.v --signal mem_array --key-type union
echo Ran xform_associative_mda_key_type.py with union key

python xform_associative_mda_key_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\assoc_struct_output.v --signal mem_array --key-type struct
echo Ran xform_associative_mda_key_type.py with struct key

:: Test array base type transformations
echo Testing array base type transformations...

python xform_array_base_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\base_int_output.v --signal mem_array --base-type int
echo Ran xform_array_base_type.py with int base type

python xform_array_base_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\base_logic_output.v --signal mem_array --base-type logic
echo Ran xform_array_base_type.py with logic base type

python xform_array_base_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\base_bit_output.v --signal mem_array --base-type bit
echo Ran xform_array_base_type.py with bit base type

python xform_array_base_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\base_longint_output.v --signal mem_array --base-type longint
echo Ran xform_array_base_type.py with longint base type

python xform_array_base_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\base_shortint_output.v --signal mem_array --base-type shortint
echo Ran xform_array_base_type.py with shortint base type

python xform_array_base_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\base_enum_output.v --signal mem_array --base-type enum
echo Ran xform_array_base_type.py with enum base type

python xform_array_base_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\base_struct_output.v --signal mem_array --base-type struct
echo Ran xform_array_base_type.py with struct base type

python xform_array_base_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\base_union_output.v --signal mem_array --base-type union
echo Ran xform_array_base_type.py with union base type

:: Test structure type transformations
echo Testing structure type transformations...

python xform_structure_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\struct_packed_output.v --signal mem_array --struct-type packed
echo Ran xform_structure_type.py with packed structure

python xform_structure_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\struct_unpacked_output.v --signal mem_array --struct-type unpacked
echo Ran xform_structure_type.py with unpacked structure

python xform_structure_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\struct_nested_output.v --signal mem_array --struct-type nested
echo Ran xform_structure_type.py with nested structure

python xform_structure_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\struct_hybrid_output.v --signal mem_array --struct-type hybrid
echo Ran xform_structure_type.py with hybrid structure

python xform_structure_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\struct_union_output.v --signal mem_array --struct-type union
echo Ran xform_structure_type.py with union structure

python xform_structure_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\struct_blasted_output.v --signal mem_array --struct-type blasted
echo Ran xform_structure_type.py with blasted structure

python xform_structure_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\struct_native_output.v --signal mem_array --struct-type native
echo Ran xform_structure_type.py with native structure

python xform_structure_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\struct_extended_class_output.v --signal mem_array --struct-type extended_class
echo Ran xform_structure_type.py with extended class

python xform_structure_type.py %INPUT_DIR%\simple_array_example.v %OUTPUT_DIR%\struct_rand_members_output.v --signal mem_array --struct-type rand_members
echo Ran xform_structure_type.py with rand members

echo All transformations completed. Check the outputs directory for results.

endlocal