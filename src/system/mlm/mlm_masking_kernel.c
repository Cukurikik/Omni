// @omni-layer System | @omni-source lucidrains/mlm-pytorch
// @omni-description MLM token masking kernel in C: high-performance BERT-style masking.
// @omni-lang C | @omni-batch 16 | @omni-semester 16

#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    int *masked_ids;
    int *labels;
    int *mask_positions;
    int n_masked;
    int seq_len;
    int status; // 0=ok, -1=error
} MlmMaskResult;

typedef struct {
    float mask_prob;
    float replace_prob;
    float random_prob;
    int mask_token_id;
    int pad_token_id;
    int vocab_size;
} MlmConfig;

static unsigned int xorshift32(unsigned int *state) {
    unsigned int x = *state;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    *state = x;
    return x;
}

MlmMaskResult mlm_create_mask(const int *token_ids, int seq_len, const MlmConfig *cfg, unsigned int seed) {
    MlmMaskResult result;
    result.status = -1;
    if (!token_ids || seq_len <= 0 || !cfg) return result;

    result.masked_ids = (int*)malloc(seq_len * sizeof(int));
    result.labels = (int*)malloc(seq_len * sizeof(int));
    result.mask_positions = (int*)malloc(seq_len * sizeof(int));
    if (!result.masked_ids || !result.labels || !result.mask_positions) return result;

    memcpy(result.masked_ids, token_ids, seq_len * sizeof(int));
    result.seq_len = seq_len;
    result.n_masked = 0;

    unsigned int rng_state = seed ? seed : 42;
    float mask_thresh = cfg->mask_prob * 4294967296.0f;
    float replace_thresh = cfg->replace_prob;
    float random_thresh = cfg->replace_prob + cfg->random_prob;

    for (int i = 0; i < seq_len; i++) {
        result.labels[i] = cfg->pad_token_id;
        if (token_ids[i] == cfg->pad_token_id) continue;

        unsigned int r = xorshift32(&rng_state);
        float p = (float)r / 4294967296.0f;
        if (p < cfg->mask_prob) {
            result.labels[i] = token_ids[i];
            result.mask_positions[result.n_masked++] = i;
            float r2 = (float)xorshift32(&rng_state) / 4294967296.0f;
            if (r2 < replace_thresh) {
                result.masked_ids[i] = cfg->mask_token_id;
            } else if (r2 < random_thresh) {
                result.masked_ids[i] = (int)(xorshift32(&rng_state) % cfg->vocab_size);
            }
        }
    }
    result.status = 0;
    return result;
}

void mlm_free_result(MlmMaskResult *result) {
    if (result) {
        free(result->masked_ids); result->masked_ids = NULL;
        free(result->labels); result->labels = NULL;
        free(result->mask_positions); result->mask_positions = NULL;
    }
}

float mlm_compute_loss(const float *logits, const int *labels, int seq_len, int vocab_size, int pad_id) {
    if (!logits || !labels || seq_len <= 0) return -1.0f;
    float total_loss = 0.0f;
    int count = 0;
    for (int i = 0; i < seq_len; i++) {
        if (labels[i] == pad_id) continue;
        const float *row = logits + i * vocab_size;
        float max_val = row[0];
        for (int v = 1; v < vocab_size; v++) if (row[v] > max_val) max_val = row[v];
        float sum_exp = 0.0f;
        for (int v = 0; v < vocab_size; v++) sum_exp += expf(row[v] - max_val);
        float log_prob = row[labels[i]] - max_val - logf(sum_exp);
        total_loss -= log_prob;
        count++;
    }
    return count > 0 ? total_loss / count : 0.0f;
}
