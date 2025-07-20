module param_buffer #(
    parameter WIDTH = 8,
    parameter DEPTH = 16
)(
    input wire clk,
    input wire [WIDTH-1:0] data_in,
    output wire [WIDTH-1:0] data_out
);
    reg [WIDTH-1:0] buffer [0:DEPTH-1];
    reg [$clog2(DEPTH)-1:0] ptr;
    
    always @(posedge clk) begin
        buffer[ptr] <= data_in;
        ptr <= ptr + 1;
    end
    
    assign data_out = buffer[ptr];
endmodule