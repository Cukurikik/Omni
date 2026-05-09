// OMNI Hardware Layer: Verilog RTL
// Register-Transfer Level definition of a Pipelined Multiply-Accumulate (MAC) block.
// This is the fundamental building block synthesized for ASIC/FPGA inference acceleration.

module Omni_MAC_Pipelined (
    input wire clk,
    input wire rst_n,
    input wire signed [15:0] weight, // 16-bit INT quantization
    input wire signed [15:0] activation,
    input wire valid_in,
    output reg signed [31:0] accumulator,
    output reg valid_out
);

    // Pipeline Registers
    reg signed [15:0] reg_weight;
    reg signed [15:0] reg_activation;
    reg reg_valid_1;
    
    reg signed [31:0] multiplier_out;
    reg reg_valid_2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            reg_weight <= 16'd0;
            reg_activation <= 16'd0;
            reg_valid_1 <= 1'b0;
            
            multiplier_out <= 32'd0;
            reg_valid_2 <= 1'b0;
            
            accumulator <= 32'd0;
            valid_out <= 1'b0;
        end else begin
            // Stage 1: Register Inputs
            reg_weight <= weight;
            reg_activation <= activation;
            reg_valid_1 <= valid_in;
            
            // Stage 2: Multiply
            if (reg_valid_1) begin
                multiplier_out <= reg_weight * reg_activation;
            end else begin
                multiplier_out <= 32'd0;
            end
            reg_valid_2 <= reg_valid_1;
            
            // Stage 3: Accumulate
            if (reg_valid_2) begin
                accumulator <= accumulator + multiplier_out;
            end
            valid_out <= reg_valid_2;
        end
    end

endmodule
