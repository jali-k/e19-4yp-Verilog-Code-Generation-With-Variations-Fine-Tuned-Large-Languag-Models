module tst_dffbehen; // test-bench
reg di,en;
wire do;
dffen d1(do,di,en); // Instantiate the D latch
initial
begin
en = 0; // Latch initially disabled (opaque)
di = 1'b0; // Initial data
end
always #7 en = ~en; // Toggle enable every 7 time units
always #4 di = ~di; // Toggle data every 4 time units
initial
$monitor($time, "en=%b, di=%b, do=%b",en,di,do);
initial #50 $stop; // Stop simulation
endmodule
module dffen (d,di,en); // D latch with enable input
input di,en; // input data and enable
output reg d; // output register
parameter s_cnt = {3'b100,4'b0101}; // constant array
generate
    always @(*) begin
        if(en)
            d <= di;
    end
endgenerate
endmodule