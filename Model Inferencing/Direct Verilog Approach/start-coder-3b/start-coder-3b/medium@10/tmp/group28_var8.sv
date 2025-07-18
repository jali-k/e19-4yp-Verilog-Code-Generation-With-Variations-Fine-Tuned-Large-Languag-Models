module aoibeh2(o,a,b); // Mixed structural/behavioral AOI
output o;
input[1:0]a,b;
wire a1,b1; // Outputs of AND gates
reg o; // Behavioral output must be reg
// Structural AND gates using primitives
and g1(a1,a[1],a[0]), g2(b1,b[1],b[0]);
// Behavioral NOR logic sensitive to AND outputs
initial begin // 1. initial_block_begin
a1 <= a[1:0]; // 2. packing
b1 <= b[1:0]; // 3. packing
end
always@(a1 or b1)
o = ~(a1 || b1);
endmodule