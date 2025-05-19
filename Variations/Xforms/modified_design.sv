module test_module(
    input wire clk,
    input wire rst_n,
    output wire [31:0] data_out
);
    // Integer variables to be transformed
    shortint counter;
    shortint index, value;
    shortint array[10];
    
    // Function with shortint parameters
    function shortint calculate(shortint a, shortint b);
        shortint result;  // Local variable to transform
        
        result = a + b;
        return result;
    endfunction
    
    // Task with shortint parameters
    task process_data(shortint data_in);
        shortint temp;  // Local variable to transform
        
        temp = data_in * 2;
        counter = temp;
    endtask
    
    // Some implementation logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 0;
            index <= 0;
            value <= 0;
        end
        else begin
            counter <= counter + 1;
            
            if (counter % 10 == 0) begin
                index <= (index + 1) % 10;
                array[index] <= value;
                value <= calculate(value, 5);
            end
        end
    end
    
    assign data_out = array[index];

endmodule