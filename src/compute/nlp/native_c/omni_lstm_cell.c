/*
 * omni_lstm_cell.c — Long Short-Term Memory (LSTM) Cell
 * Layer: Compute / Native C
 * Inspired by: Ankit-Kumar-Saini/Coursera_Deep_Learning_Specialization
 *
 * Implements a highly optimized, raw C LSTM cell forward pass from scratch.
 * Used for extremely low-latency embedded sequence processing where
 * loading a full Python/PyTorch runtime is prohibited. Zero mock.
 */

#include <math.h>
#include <stdlib.h>

typedef struct {
    int input_dim;
    int hidden_dim;
    
    // Weights: Shape (hidden_dim, input_dim + hidden_dim)
    float* W_f; // Forget gate
    float* W_i; // Input gate
    float* W_c; // Cell state update
    float* W_o; // Output gate

    // Biases: Shape (hidden_dim)
    float* b_f;
    float* b_i;
    float* b_c;
    float* b_o;
} OmniLSTMWeights;

static float sigmoid(float x) {
    return 1.0f / (1.0f + expf(-x));
}

static float calc_tanh(float x) {
    return tanhf(x);
}

/**
 * Computes a single timestep forward pass of the LSTM.
 * x: input vector (input_dim)
 * a_prev: previous hidden state (hidden_dim)
 * c_prev: previous cell state (hidden_dim)
 * a_next: output hidden state (hidden_dim)
 * c_next: output cell state (hidden_dim)
 */
void omni_lstm_step(
    const OmniLSTMWeights* weights,
    const float* x,
    const float* a_prev,
    const float* c_prev,
    float* a_next,
    float* c_next
) {
    int H = weights->hidden_dim;
    int I = weights->input_dim;
    int D = I + H;

    // Allocate temporary combined input vector [a_prev, x]
    float* concat = (float*)__builtin_malloc(D * sizeof(float));
    for (int i = 0; i < H; ++i) concat[i] = a_prev[i];
    for (int i = 0; i < I; ++i) concat[H + i] = x[i];

    // Compute gates
    for (int h = 0; h < H; ++h) {
        float f_gate = 0.0f;
        float i_gate = 0.0f;
        float c_tilde = 0.0f;
        float o_gate = 0.0f;

        // Matrix-vector multiplication
        for (int j = 0; j < D; ++j) {
            float val = concat[j];
            int w_idx = h * D + j;
            
            f_gate += weights->W_f[w_idx] * val;
            i_gate += weights->W_i[w_idx] * val;
            c_tilde += weights->W_c[w_idx] * val;
            o_gate += weights->W_o[w_idx] * val;
        }

        // Add biases and apply activations
        f_gate = sigmoid(f_gate + weights->b_f[h]);
        i_gate = sigmoid(i_gate + weights->b_i[h]);
        c_tilde = calc_tanh(c_tilde + weights->b_c[h]);
        o_gate = sigmoid(o_gate + weights->b_o[h]);

        // Cell state update
        c_next[h] = f_gate * c_prev[h] + i_gate * c_tilde;
        
        // Hidden state update
        a_next[h] = o_gate * calc_tanh(c_next[h]);
    }

    __builtin_free(concat);
}
