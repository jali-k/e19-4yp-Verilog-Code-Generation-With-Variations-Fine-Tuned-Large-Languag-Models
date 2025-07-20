module dual_clock_fifo(
    input wire clk_a,
    input wire clk_b, 
    input wire reset,
    input wire [7:0] data_in,
    output wire [7:0] data_out
);
    reg [7:0] memory [0:15];
    reg [3:0] wr_ptr, rd_ptr;
    
    always @(posedge clk_a) begin
        if (reset) wr_ptr <= 0;
        else wr_ptr <= wr_ptr + 1;
    end
    
    always @(posedge clk_b) begin
        if (reset) rd_ptr <= 0;
        else rd_ptr <= rd_ptr + 1;
    end
endmodule