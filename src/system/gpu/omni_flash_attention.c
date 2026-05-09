#include <stdint.h>
#include <math.h>
#include <stdlib.h>

/**
 * Omni Flash Attention (C)
 * CPU-bound emulation of FlashAttention logic (Dao et al.)
 * Evaluates attention while aggressively tiling to remain within L1/L2 Cache bounds,
 * mitigating main memory round-trips for the O(N^2) attention matrix.
 */

#define BLOCK_SIZE_M 32
#define BLOCK_SIZE_N 32

extern "C" {

// Helper: safe max
static inline float max_f32(float a, float b) {
    return a > b ? a : b;
}

void omni_flash_attention_forward(
    const float* Q, const float* K, const float* V, float* O,
    uint32_t seq_len, uint32_t head_dim) 
{
    // Initialize output and statistics blocks
    float* l = (float*)calloc(seq_len, sizeof(float));
    float* m = (float*)malloc(seq_len * sizeof(float));
    for (uint32_t i = 0; i < seq_len; ++i) {
        m[i] = -INFINITY;
    }

    float scale = 1.0f / sqrtf((float)head_dim);

    // Tiled execution over N dimension
    for (uint32_t j = 0; j < seq_len; j += BLOCK_SIZE_N) {
        uint32_t j_end = (j + BLOCK_SIZE_N > seq_len) ? seq_len : (j + BLOCK_SIZE_N);
        
        // Load Kj, Vj to SRAM (Conceptual in C)
        
        // Tiled execution over M dimension
        for (uint32_t i = 0; i < seq_len; i += BLOCK_SIZE_M) {
            uint32_t i_end = (i + BLOCK_SIZE_M > seq_len) ? seq_len : (i + BLOCK_SIZE_M);
            
            // For each query in block
            for (uint32_t ib = i; ib < i_end; ++ib) {
                float m_ij = -INFINITY;
                
                // Compute S_ij = Q_i * K_j^T
                float S[BLOCK_SIZE_N] = {0};
                for (uint32_t jb = j; jb < j_end; ++jb) {
                    float dot = 0.0f;
                    for (uint32_t d = 0; d < head_dim; ++d) {
                        dot += Q[ib * head_dim + d] * K[jb * head_dim + d];
                    }
                    dot *= scale;
                    S[jb - j] = dot;
                    m_ij = max_f32(m_ij, dot);
                }
                
                float m_i_new = max_f32(m[ib], m_ij);
                
                // Compute P_ij = exp(S_ij - m_i_new)
                float l_ij = 0.0f;
                float P[BLOCK_SIZE_N] = {0};
                for (uint32_t jb = j; jb < j_end; ++jb) {
                    P[jb - j] = expf(S[jb - j] - m_i_new);
                    l_ij += P[jb - j];
                }
                
                float l_i_new = expf(m[ib] - m_i_new) * l[ib] + l_ij;
                
                // Update O_i
                for (uint32_t d = 0; d < head_dim; ++d) {
                    float pv = 0.0f;
                    for (uint32_t jb = j; jb < j_end; ++jb) {
                        pv += P[jb - j] * V[jb * head_dim + d];
                    }
                    O[ib * head_dim + d] = 
                        (l[ib] * expf(m[ib] - m_i_new) * O[ib * head_dim + d] + pv) / l_i_new;
                }
                
                m[ib] = m_i_new;
                l[ib] = l_i_new;
            }
        }
    }

    free(l);
    free(m);
}

} // extern "C"
