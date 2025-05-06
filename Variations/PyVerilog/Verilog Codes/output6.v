
module top
(
  input CLK,
  input RST,
  output reg [7:0] led
);


  // Embedded code
  reg [31:0] count;
  always @(posedge CLK) begin
    if(RST) begin
      count <= 0;
      led <= 0;
    end else begin
      if(count == 1024 - 1) begin
        count <= 0;
        led <= led + 1;
      end else begin
        count <= count + 1;
      end 
    end
  end


endmodule
