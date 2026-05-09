/**
 * moe_simd_router.c — SIMD-Optimized MoE Router for CPU Inference
 * Layer: System / CPU — MoE Routing
 *
 * AVX2/SSE4 optimized top-k router for CPU-based MoE inference.
 * Computes softmax over expert logits and selects top-k experts
 * per token using vectorized operations.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <float.h>

#ifdef __AVX2__
#include <immintrin.h>
#endif

typedef struct {
    int32_t expert_id;
    float weight;
} ExpertSelection;

typedef struct {
    int num_experts;
    int top_k;
    float noise_scale;
    float temperature;
} RouterConfig;

typedef struct {
    ExpertSelection* selections;  /* (num_tokens * top_k) */
    float* all_probs;             /* (num_tokens * num_experts) */
    float load_balance_loss;
    int num_tokens;
} RouterOutput;

/**
 * Compute softmax over a vector of logits.
 * Numerically stable: subtracts max before exponentiation.
 */
static void softmax_f32(const float* logits, float* probs, int n) {
    float max_val = -FLT_MAX;
    for (int i = 0; i < n; i++) {
        if (logits[i] > max_val) max_val = logits[i];
    }

    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        probs[i] = expf(logits[i] - max_val);
        sum += probs[i];
    }

    float inv_sum = 1.0f / (sum + 1e-8f);
    for (int i = 0; i < n; i++) {
        probs[i] *= inv_sum;
    }
}

#ifdef __AVX2__
/**
 * AVX2-optimized softmax for vectors aligned to 8 floats.
 */
static void softmax_f32_avx2(const float* logits, float* probs, int n) {
    /* Find max using AVX2 */
    __m256 vmax = _mm256_set1_ps(-FLT_MAX);
    int i;
    for (i = 0; i + 8 <= n; i += 8) {
        __m256 v = _mm256_loadu_ps(logits + i);
        vmax = _mm256_max_ps(vmax, v);
    }
    /* Horizontal max */
    float max_arr[8];
    _mm256_storeu_ps(max_arr, vmax);
    float max_val = max_arr[0];
    for (int j = 1; j < 8; j++) {
        if (max_arr[j] > max_val) max_val = max_arr[j];
    }
    for (; i < n; i++) {
        if (logits[i] > max_val) max_val = logits[i];
    }

    /* Compute exp and sum */
    __m256 vmax_bc = _mm256_set1_ps(max_val);
    __m256 vsum = _mm256_setzero_ps();
    for (i = 0; i + 8 <= n; i += 8) {
        __m256 v = _mm256_loadu_ps(logits + i);
        __m256 shifted = _mm256_sub_ps(v, vmax_bc);
        /* Approximation: use polynomial for exp is faster but less accurate */
        /* For production, use exact exp per element */
        float tmp[8];
        _mm256_storeu_ps(tmp, shifted);
        for (int j = 0; j < 8; j++) tmp[j] = expf(tmp[j]);
        __m256 exp_v = _mm256_loadu_ps(tmp);
        _mm256_storeu_ps(probs + i, exp_v);
        vsum = _mm256_add_ps(vsum, exp_v);
    }
    float sum_arr[8];
    _mm256_storeu_ps(sum_arr, vsum);
    float sum = 0.0f;
    for (int j = 0; j < 8; j++) sum += sum_arr[j];
    for (; i < n; i++) {
        probs[i] = expf(logits[i] - max_val);
        sum += probs[i];
    }

    /* Normalize */
    float inv_sum = 1.0f / (sum + 1e-8f);
    __m256 vinv = _mm256_set1_ps(inv_sum);
    for (i = 0; i + 8 <= n; i += 8) {
        __m256 v = _mm256_loadu_ps(probs + i);
        _mm256_storeu_ps(probs + i, _mm256_mul_ps(v, vinv));
    }
    for (; i < n; i++) {
        probs[i] *= inv_sum;
    }
}
#endif

/**
 * Select top-k experts from probability distribution.
 * Uses partial sort (selection algorithm) for O(n*k) complexity.
 */
static void topk_select(
    const float* probs, int num_experts, int top_k,
    ExpertSelection* out
) {
    /* Initialize with -inf */
    for (int k = 0; k < top_k; k++) {
        out[k].expert_id = -1;
        out[k].weight = -FLT_MAX;
    }

    for (int e = 0; e < num_experts; e++) {
        /* Find minimum in current top-k */
        int min_idx = 0;
        for (int k = 1; k < top_k; k++) {
            if (out[k].weight < out[min_idx].weight) {
                min_idx = k;
            }
        }
        if (probs[e] > out[min_idx].weight) {
            out[min_idx].expert_id = e;
            out[min_idx].weight = probs[e];
        }
    }

    /* Normalize top-k weights to sum to 1 */
    float wsum = 0.0f;
    for (int k = 0; k < top_k; k++) {
        wsum += out[k].weight;
    }
    if (wsum > 0.0f) {
        float inv = 1.0f / wsum;
        for (int k = 0; k < top_k; k++) {
            out[k].weight *= inv;
        }
    }
}

/**
 * Compute auxiliary load balance loss.
 * L_aux = N * sum_i(f_i * p_i)
 * where f_i = fraction of tokens routed to expert i
 *       p_i = average router probability for expert i
 */
static float compute_load_balance_loss(
    const RouterOutput* output,
    int num_experts
) {
    float* f = (float*)calloc(num_experts, sizeof(float));
    float* p = (float*)calloc(num_experts, sizeof(float));
    if (!f || !p) {
        free(f);
        free(p);
        return 0.0f;
    }

    int N = output->num_tokens;
    /* f_i: fraction of tokens assigned to expert i (using top-1) */
    for (int t = 0; t < N; t++) {
        int eid = output->selections[t * (output->num_tokens > 0 ? 1 : 0)].expert_id;
        if (eid >= 0 && eid < num_experts) {
            f[eid] += 1.0f;
        }
    }
    float inv_n = 1.0f / (float)(N > 0 ? N : 1);
    for (int e = 0; e < num_experts; e++) {
        f[e] *= inv_n;
    }

    /* p_i: average probability for expert i */
    for (int t = 0; t < N; t++) {
        for (int e = 0; e < num_experts; e++) {
            p[e] += output->all_probs[t * num_experts + e];
        }
    }
    for (int e = 0; e < num_experts; e++) {
        p[e] *= inv_n;
    }

    float loss = 0.0f;
    for (int e = 0; e < num_experts; e++) {
        loss += f[e] * p[e];
    }
    loss *= (float)num_experts;

    free(f);
    free(p);
    return loss;
}

/**
 * Route a batch of tokens to experts using SIMD-optimized softmax.
 *
 * @param logits       (num_tokens, num_experts) router logits
 * @param num_tokens   number of tokens in the batch
 * @param config       router configuration
 * @param output       pre-allocated output structure
 * @return 0 on success, -1 on error
 */
int moe_route_tokens(
    const float* logits,
    int num_tokens,
    const RouterConfig* config,
    RouterOutput* output
) {
    if (!logits || !config || !output) return -1;
    if (num_tokens <= 0 || config->num_experts <= 0) return -1;

    int ne = config->num_experts;
    int tk = config->top_k;

    output->num_tokens = num_tokens;
    output->selections = (ExpertSelection*)malloc(
        sizeof(ExpertSelection) * num_tokens * tk);
    output->all_probs = (float*)malloc(sizeof(float) * num_tokens * ne);
    if (!output->selections || !output->all_probs) {
        free(output->selections);
        free(output->all_probs);
        return -1;
    }

    float* scaled_logits = (float*)malloc(sizeof(float) * ne);
    if (!scaled_logits) {
        free(output->selections);
        free(output->all_probs);
        return -1;
    }

    for (int t = 0; t < num_tokens; t++) {
        const float* token_logits = logits + t * ne;

        /* Apply temperature scaling */
        float inv_temp = 1.0f / (config->temperature > 0 ? config->temperature : 1.0f);
        for (int e = 0; e < ne; e++) {
            scaled_logits[e] = token_logits[e] * inv_temp;
        }

        /* Softmax */
        float* probs = output->all_probs + t * ne;
#ifdef __AVX2__
        if (ne >= 8) {
            softmax_f32_avx2(scaled_logits, probs, ne);
        } else {
            softmax_f32(scaled_logits, probs, ne);
        }
#else
        softmax_f32(scaled_logits, probs, ne);
#endif

        /* Top-k selection */
        topk_select(probs, ne, tk, output->selections + t * tk);
    }

    output->load_balance_loss = compute_load_balance_loss(output, ne);

    free(scaled_logits);
    return 0;
}

/**
 * Free router output memory.
 */
void moe_free_router_output(RouterOutput* output) {
    if (output) {
        free(output->selections);
        free(output->all_probs);
        output->selections = NULL;
        output->all_probs = NULL;
    }
}
