/* kvpress — KV Cache Attention Scorer (NVIDIA)
 * C kernel for scoring attention token importance with O(n) memory */
#include <stdint.h>
#include <float.h>
#include <math.h>

#define MAX_SEQ_LEN 131072
#define MAX_HEADS   128

typedef struct { int is_ok; float value; const char* error; } OmniResult_f32;

typedef struct {
    float* scores;     /* [num_heads * seq_len] */
    uint32_t num_heads;
    uint32_t seq_len;
} KVScoreBuffer;

OmniResult_f32 kvpress_compute_knorm_score(
    const float* key_norms, uint32_t seq_len, uint32_t num_heads
) {
    if (!key_norms) return (OmniResult_f32){0, 0.0f, "Null key_norms pointer"};
    if (seq_len > MAX_SEQ_LEN) return (OmniResult_f32){0, 0.0f, "Seq exceeds 128K"};
    if (num_heads > MAX_HEADS) return (OmniResult_f32){0, 0.0f, "Heads exceed 128"};
    float total = 0.0f;
    uint32_t count = num_heads * seq_len;
    for (uint32_t i = 0; i < count; i++) {
        if (isnan(key_norms[i]) || isinf(key_norms[i]))
            return (OmniResult_f32){0, 0.0f, "NaN/Inf in key norms"};
        total += key_norms[i];
    }
    return (OmniResult_f32){1, total / (float)count, NULL};
}

OmniResult_f32 kvpress_expected_attention_score(
    const float* attn_weights, uint32_t seq_len, uint32_t query_len
) {
    if (!attn_weights) return (OmniResult_f32){0, 0.0f, "Null attention weights"};
    if (seq_len > MAX_SEQ_LEN) return (OmniResult_f32){0, 0.0f, "Seq exceeds 128K"};
    if (query_len == 0) return (OmniResult_f32){0, 0.0f, "Zero query length"};
    float sum = 0.0f;
    for (uint32_t i = 0; i < seq_len; i++) {
        float token_importance = 0.0f;
        for (uint32_t q = 0; q < query_len; q++)
            token_importance += attn_weights[q * seq_len + i];
        sum += token_importance / (float)query_len;
    }
    return (OmniResult_f32){1, sum / (float)seq_len, NULL};
}
