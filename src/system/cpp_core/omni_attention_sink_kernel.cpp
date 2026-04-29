// Omni Attention Sink Kernel (C++)
// System Layer: High-perf attention weight thresholding for sink detection.
// Ref: sail-sg/Attention-Sink — ICLR 2025

#include <cstddef>
#include <cmath>
#include <algorithm>

struct SinkMetric { int layer; int pos; float magnitude; bool is_sink; };

int detect_sinks(const float* attn_weights, int num_layers, int seq_len,
                 float threshold, SinkMetric* out, int max_out) {
    int count = 0;
    for (int l = 0; l < num_layers && count < max_out; ++l) {
        const float* row = attn_weights + l * seq_len;
        int check = std::min(4, seq_len);
        for (int p = 0; p < check && count < max_out; ++p) {
            out[count] = {l, p, row[p], row[p] >= threshold};
            ++count;
        }
    }
    return count;
}
