// Omni SystemVerilog Accelerator (SystemVerilog)
// Hardware & Silicon Layer
// Defines a custom hardware module (ASIC/FPGA) that accelerates 8-bit integer 
// matrix-vector multiplication (MAC operations) for hyper-fast inference.

module omni_mac_8bit (
    input logic clk,
    input logic rst_n,
    input logic enable,
    input logic signed [7:0] activation_in,
    input logic signed [7:0] weight_in,
    input logic clear_acc,
    output logic signed [31:0] accumulator_out
);

    // Internal 32-bit accumulator to prevent overflow
    logic signed [31:0] acc_reg;
    logic signed [15:0] product;

    // Combinational multiplier
    assign product = activation_in * weight_in;

    // Sequential Accumulator logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            acc_reg <= 32'sd0;
        end else if (enable) begin
            if (clear_acc) begin
                acc_reg <= product; // Start new accumulation
            end else begin
                acc_reg <= acc_reg + product; // MAC
            end
        end
    end

    // Output assignment
    assign accumulator_out = acc_reg;

endmodule
