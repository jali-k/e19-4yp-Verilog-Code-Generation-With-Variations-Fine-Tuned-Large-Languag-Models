module Universal_Shift_Reg (Data_Out, MSB_Out, LSB_Out, Data_In,
MSB_In, LSB_In, s1, s0, clk, rst);
output [3: 0] Data_Out;
output MSB_Out, LSB_Out;
input [3: 0] Data_In;
input MSB_In, LSB_In;
reg [3: 0] Data_Out; // 10-12-2004
input s1, s0, clk, rst;
assign MSB_Out = Data_Out[3];
assign LSB_Out = Data_Out[0];
always @ (posedge clk) begin
if (rst) Data_Out <= 0;
else case ({s1, s0})
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

defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b1;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b1;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b1;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b1;

defparam t1.half_cycle = 5;

Universal_Shift_Reg M1 (Data_Out, MSB_Out, LSB_Out, Data_In, MSB_In, LSB_In, s1, s0, clk, rst);

initial #1000 $finish;

initial fork
begin #5 rst = 1; #20 rst = 0;end
begin #120 rst = 1; #20 rst = 0;end
begin #260 rst = 1; #20 rst = 0;end
begin #380 rst = 1; #20 rst = 0;end
join
initial fork
join
begin // Verify left shift
join
begin // Verify load
join
begin // reset
join

join
endmodule
### Final Code:
module Universal_Shift_Reg (Data_Out, MSB_Out, LSB_Out, Data_In,
MSB_In, LSB_In, s1, s0, clk, rst);
output [3: 0] Data_Out;
output MSB_Out, LSB_Out;
input [3: 0] Data_In;
input MSB_In, LSB_In;
reg [3: 0] Data_Out; // 10-12-2004
input s1, s0, clk, rst;
assign MSB_Out = Data_Out[3];
assign LSB_Out = Data_Out[0];
always @ (posedge clk) begin
if (rst) Data_Out <= 0;
else case ({s1, s0})
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

defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b1;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b1;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b1;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b1;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b0;
defparam M1.s1_mask = 1'b0;
defparam M1.s0_mask = 1'b1;

defparam t1.half_cycle = 5;

Universal_Shift_Reg M1 (Data_Out, MSB_Out, LSB_Out, Data_In, MSB_In, LSB_In, s1, s0, clk, rst);

initial #1000 $finish;

initial fork
begin #5 rst = 1; #20 rst = 0;end
begin #120 rst = 1; #