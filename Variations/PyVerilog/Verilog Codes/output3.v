// Rename the output port from `led` to `led_out`.
module top #
(
  parameter DATAWID = 32
)
(
  input CLK,
  input RST,
  output [7:0] led_out
);

  reg [DATAWID-1:0] count;
  assign led_out = count[DATAWID-1:DATAWID-8];

  always @(posedge CLK) begin
    if(RST) begin
      count <= 0;
    end else begin
      count <= count + 1;
    end
  end


endmodule
