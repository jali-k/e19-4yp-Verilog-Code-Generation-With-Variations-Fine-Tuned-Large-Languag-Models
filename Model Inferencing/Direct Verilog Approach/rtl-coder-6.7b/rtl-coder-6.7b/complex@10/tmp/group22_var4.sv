module tst_dffbehen;//test-bench
reg di,en;
wire do;
dffen d1(do,di,en); // Instantiate the D latch
int s_cnt = 5;
generate
if (s_cnt inside { 1, 2, 3, 4, 5 }) begin : behen
initial
begin
en=0; // Latch initially disabled (opaque)
di=1'b0; // Initial data
end
always #7 en =~en; // Toggle enable every 7 time units
always #4 di=~di; // Toggle data every 4 time units
initial
$monitor($time,"en=%b, di=%b, do=%b",en,di,do);
initial #50 $stop; // Stop simulation
end
endgenerate
endmodule