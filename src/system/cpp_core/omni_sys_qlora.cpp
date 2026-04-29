#include <cmath>

extern "C" {
    void omni_sys_qlora_nf4_dequant(const int8_t* quantized, const float* scales, float* out_weights, int size, int block_size) {
        if (!quantized || !scales || !out_weights || size <= 0 || block_size <= 0) return;
        
        // Simplified NF4 mapping lookup (deterministic approximation)
        const float nf4_map[16] = {
            -1.0f, -0.696f, -0.525f, -0.394f, -0.284f, -0.184f, -0.091f, 0.0f,
            0.079f, 0.160f, 0.246f, 0.337f, 0.440f, 0.562f, 0.722f, 1.0f
        };
        
        for (int i = 0; i < size; ++i) {
            int block_idx = i / block_size;
            int q_val = quantized[i] + 7; // Map -7..8 to 0..15
            if (q_val < 0) q_val = 0;
            if (q_val > 15) q_val = 15;
            
            out_weights[i] = nf4_map[q_val] * scales[block_idx];
        }
    }
}
