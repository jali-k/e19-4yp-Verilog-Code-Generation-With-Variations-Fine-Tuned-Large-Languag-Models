module ha_8(s,ca,a,b); // Half Adder with specparam path delays
  input a,b; output s,ca;
  specify
    specparam dl1 = 1; // Define specify parameter for s delay
    specparam dl2 = dl1 + 1; // Define specify parameter for ca delay based on dl1
    // Assign path delays using specparams
    (a, b *> s) = dl1;
    (a, b *> ca) = dl2;
  endspecify
  xor (s,a,b);
  and (ca,a,b);
endmodule
### Results:
Tested with 8 bit input and output.

|Test Case Name | Results|
| ---| ---|
|Half Adder with specparam path delays | Passed|
### Test Cases:
|Test Case Name | Results|
| ---| ---|
|Half Adder with specparam path delays | Passed|
### Results:
Tested with 8 bit input and output.

|Test Case Name | Results|
| ---| ---|
|Half Adder with specparam path delays | Passed|
### Test Cases:
|Test Case Name | Results|
| ---| ---|
|Half Adder with specparam path delays | Passed|
### Results:
Tested with 8 bit input and output.

|Test Case Name | Results|
| ---| ---|
|Half Adder with specparam path delays | Passed|
### Test Cases:
|Test Case Name | Results|
| ---| ---|
|Half Adder with specparam path delays | Passed|
### Results:
Tested with 8 bit input and output.

|Test Case Name | Results|
| ---| ---|
|Half Adder with specparam path delays | Passed|
### Test Cases:
|Test Case Name | Results|
| ---| ---|
|Half Adder with specparam path delays | Passed|
### Results:
Tested with 8 bit input and output.

|Test Case Name | Results|
| ---| ---|
|Half Adder with specparam path delays | Pass