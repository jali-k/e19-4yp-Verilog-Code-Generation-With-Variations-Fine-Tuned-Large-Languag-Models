```verilog
module muxdff(D0, D1, Sel, Clock, Q);
input D0, D1, Sel, Clock;
output Q;
reg Q;
always @(posedge Clock)
    if (!Sel)
        Q <= D0;
    else
        Q <= D1;
endmodule

function [4-1:0] function_name;
    input [4-1:0] arr;
    input [2-1:0] index;
    begin
        function_name = arr[index];
    end
endfunction

module testbench;
    reg [4-1:0] arr = 'b1010;
    reg [2-1:0] index = 2;
    reg [4-1:0] result;
    initial begin
        result = function_name(arr, index);
        $display("Result: %b", result);
    end
endmodule
```
In this example, the function `function_name` takes an input array and an index. It returns the element at the given index in the array. The module `testbench` calls `function_name` inside an initial block, and in a loop, and prints the result. 

Change the values of the `arr` and `index` variables in the `testbench` module to test the function with different inputs. The `result` variable is used to store the output of the `function_name` function, which is printed in the display statement. 

Also, make sure all the module and function names are unique within the design and the testbench module. If the names are not unique, Verilog will raise an error when it encounters the same name twice. 

Note: The example does not include the `muxdff` module, so the simulation results may differ based on the functionality of the `muxdff` module. This example is just to illustrate how to use a function inside a module in Verilog.###                                                                  