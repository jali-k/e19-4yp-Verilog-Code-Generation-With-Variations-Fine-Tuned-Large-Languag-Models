```verilog
module reg4(D, Clock, Resetn, Q);
input [3:0] D;
input Clock, Resetn;
output [3:0] Q;
reg [3:0] Q;
integer i;
always @(posedge Clock or negedge Resetn)
    if (Resetn == 0)
        Q <= 4'b0000;
    else begin
        Q <= D;
        for (i = 0; i <= 3; i = i + 1) begin
            $display("Q: %0b, D: %0b, index: %0d", Q[i], D[i], i);
        end
    end
endmodule
```

This modification introduces a loop to go through each bit of the 4-bit D register. On each clock cycle, all bits of D are also printed out. The index variable `i` is used to specify the bit of interest. 

Note: In this context, you are not assigning D to Q but instead, you are printing out D and Q for debugging purposes. Please replace it with your own assignments if needed.

Also, this code assumes a clock edge in the reset state. If you want it to be a clock edge in the set state then you need to modify the code as `if (!Resetn)` instead of `if (Resetn == 0)`. 

This code is written for ModelSim simulation. Please adjust the code based on your simulation tool if needed. 

Please also note that this code just prints out the D and Q values for debugging purposes and does not cover any actual functionality. This is just for illustration purposes. 

Lastly, note that using `always` blocks in a real design might lead to timing issues due to combinational loops and race conditions. Use it wisely. For example, in your actual design you might want to use a D-flip-flop which can handle both the clock edge and reset edge. This is what the `always` block does in the provided example and you shouldn't have any timing issues with this code. However, I've shown this for the sake of the question.###                            