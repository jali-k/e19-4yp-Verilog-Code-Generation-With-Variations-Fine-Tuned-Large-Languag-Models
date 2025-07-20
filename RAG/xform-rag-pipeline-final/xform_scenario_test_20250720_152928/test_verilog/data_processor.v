module processor(
    input wire clk,
    input wire [7:0] data_bus,
    output wire [7:0] result
);
    reg [7:0] buffer;
    wire [3:0] control_sig;
    
    always @(posedge clk) begin
        buffer <= data_bus ^ buffer;
    end
    
    assign result = buffer;
    assign control_sig = buffer[7:4];
endmodule