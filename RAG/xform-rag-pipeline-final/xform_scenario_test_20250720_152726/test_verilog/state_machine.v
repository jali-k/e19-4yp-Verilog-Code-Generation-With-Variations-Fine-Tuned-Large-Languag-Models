module fsm_controller(
    input wire clk,
    input wire reset,
    input wire start,
    output wire done
);
    typedef enum logic [1:0] {
        IDLE = 2'b00,
        ACTIVE = 2'b01,
        COMPLETE = 2'b10
    } state_t;
    
    state_t current_state, next_state;
    
    always @(posedge clk or posedge reset) begin
        if (reset)
            current_state <= IDLE;
        else
            current_state <= next_state;
    end
    
    always_comb begin
        case (current_state)
            IDLE: next_state = start ? ACTIVE : IDLE;
            ACTIVE: next_state = COMPLETE;
            COMPLETE: next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end
    
    assign done = (current_state == COMPLETE);
endmodule