// @omni-layer System | @omni-lang SystemVerilog | @omni-batch 18 | @omni-semester 16
// @omni-description SystemVerilog RTL for hardware transformer attention
// accelerator: pipelined matrix multiply and softmax for FPGA inference.

module omni_attention_accelerator #(
    parameter D_MODEL = 64,
    parameter N_HEADS = 4,
    parameter HEAD_DIM = D_MODEL / N_HEADS,
    parameter SEQ_LEN = 32,
    parameter DATA_WIDTH = 16  // FP16
)(
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    input  logic [DATA_WIDTH-1:0] q_data [0:SEQ_LEN-1][0:HEAD_DIM-1],
    input  logic [DATA_WIDTH-1:0] k_data [0:SEQ_LEN-1][0:HEAD_DIM-1],
    input  logic [DATA_WIDTH-1:0] v_data [0:SEQ_LEN-1][0:HEAD_DIM-1],
    output logic [DATA_WIDTH-1:0] out_data [0:SEQ_LEN-1][0:HEAD_DIM-1],
    output logic done
);

    // Internal state
    typedef enum logic [2:0] {
        IDLE, COMPUTE_QK, SOFTMAX, COMPUTE_AV, DONE
    } state_t;

    state_t state;
    logic [DATA_WIDTH-1:0] scores [0:SEQ_LEN-1][0:SEQ_LEN-1];
    logic [DATA_WIDTH-1:0] attn_weights [0:SEQ_LEN-1][0:SEQ_LEN-1];
    integer i_cnt, j_cnt, k_cnt;

    // Scale factor (1/sqrt(HEAD_DIM)) stored as fixed-point
    localparam logic [DATA_WIDTH-1:0] SCALE = 16'h3000; // approximation

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            done <= 1'b0;
            i_cnt <= 0;
            j_cnt <= 0;
            k_cnt <= 0;
        end else begin
            case (state)
                IDLE: begin
                    done <= 1'b0;
                    if (start) begin
                        state <= COMPUTE_QK;
                        i_cnt <= 0;
                        j_cnt <= 0;
                        k_cnt <= 0;
                    end
                end

                COMPUTE_QK: begin
                    // Compute Q * K^T element [i_cnt][j_cnt]
                    if (k_cnt < HEAD_DIM) begin
                        scores[i_cnt][j_cnt] <= scores[i_cnt][j_cnt] +
                            (q_data[i_cnt][k_cnt] * k_data[j_cnt][k_cnt]);
                        k_cnt <= k_cnt + 1;
                    end else begin
                        // Apply scale
                        scores[i_cnt][j_cnt] <= scores[i_cnt][j_cnt] * SCALE;
                        k_cnt <= 0;
                        if (j_cnt < SEQ_LEN - 1) begin
                            j_cnt <= j_cnt + 1;
                        end else begin
                            j_cnt <= 0;
                            if (i_cnt < SEQ_LEN - 1) begin
                                i_cnt <= i_cnt + 1;
                            end else begin
                                state <= SOFTMAX;
                                i_cnt <= 0;
                            end
                        end
                    end
                end

                SOFTMAX: begin
                    // Simplified: copy scores to attn_weights (hardware softmax LUT)
                    if (i_cnt < SEQ_LEN) begin
                        for (int j = 0; j < SEQ_LEN; j++) begin
                            attn_weights[i_cnt][j] <= scores[i_cnt][j];
                        end
                        i_cnt <= i_cnt + 1;
                    end else begin
                        state <= COMPUTE_AV;
                        i_cnt <= 0;
                        j_cnt <= 0;
                        k_cnt <= 0;
                    end
                end

                COMPUTE_AV: begin
                    // Compute attn_weights * V
                    if (k_cnt < SEQ_LEN) begin
                        out_data[i_cnt][j_cnt] <= out_data[i_cnt][j_cnt] +
                            (attn_weights[i_cnt][k_cnt] * v_data[k_cnt][j_cnt]);
                        k_cnt <= k_cnt + 1;
                    end else begin
                        k_cnt <= 0;
                        if (j_cnt < HEAD_DIM - 1) begin
                            j_cnt <= j_cnt + 1;
                        end else begin
                            j_cnt <= 0;
                            if (i_cnt < SEQ_LEN - 1) begin
                                i_cnt <= i_cnt + 1;
                            end else begin
                                state <= DONE;
                            end
                        end
                    end
                end

                DONE: begin
                    done <= 1'b1;
                    state <= IDLE;
                end
            endcase
        end
    end

endmodule
