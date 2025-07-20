module signal_manager(
    input wire clk,
    input wire [31:0] data,
    input wire valid,
    input wire ready,
    output wire ack,
    output wire [31:0] processed_data
);
    reg [31:0] internal_buffer;
    
    always @(posedge clk) begin
        if (valid && ready) begin
            internal_buffer <= data;
        end
    end
    
    assign ack = valid && ready;
    assign processed_data = internal_buffer;
endmodule