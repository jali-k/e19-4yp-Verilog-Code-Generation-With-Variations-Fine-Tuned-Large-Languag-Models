module Universal_Shift_Reg (Data_Out, MSB_Out, LSB_Out, Data_In, MSB_In, LSB_In,
s1, s0, clk, rst);
output reg [3: 0] Data_Out;
output reg MSB_Out, LSB_Out;
input [3: 0] Data_In;
input MSB_In, LSB_In;
reg [1: 0] control;
reg [1: 0] expected;
input s1, s0, clk, rst;
//inside `s1`, `s0` control signals
assign MSB_Out = Data_Out[3];
assign LSB_Out = Data_Out[0];
assign control = {s1, s0};
`ifdef RTL_SIM
packed array
`endif
always @ (posedge clk) begin
if (rst) Data_Out <= 0;
else case (control)
0: Data_Out <= Data_Out; // Idle
1: Data_Out <= {MSB_In, Data_Out[3:1]}; // Shift right
2: Data_Out <= {Data_Out[2:0], LSB_In}; // Shift Left
3: Data_Out <= Data_In; // Parallel Load
endcase
end
endmodule
/*
Test Plan
Verify initial reset
Verify idle
Verify shift right
Verify shift left
Verify parallel load
Verify reset-on-the-fly
*/
module t_Universal_Shift_Reg();
wire [3: 0] Data_Out;
reg [3: 0] Data_In;
wire MSB_Out, LSB_Out;
reg MSB_In, LSB_In;
reg s1, s0, rst;
defparam M2.half_cycle = 5;

Universal_Shift_Reg M1 (Data_Out, MSB_Out, LSB_Out, Data_In, MSB_In, LSB_In, s1,
s0, clk, rst);
Clock_Gen M2(clk);

initial #1000 $finish;
initial fork