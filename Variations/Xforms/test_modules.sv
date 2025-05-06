module test_module(
    input wire clk,
    input wire rst_n,
    output wire [31:0] data_out
);
    // Integer variables to be transformed
    int counter;
    int index, value;
    int array[10];
    
    // Function with int parameters
    function int calculate(int a, int b);
        int result;  // Local variable to transform
        
        result = a + b;
        return result;
    endfunction
    
    // Task with int parameters
    task process_data(int data_in);
        int temp;  // Local variable to transform
        
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