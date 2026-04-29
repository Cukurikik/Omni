#include <stdint.h>
#include <stddef.h>

// Omni Fusion Bench Embedded (C)
// Bare-metal weight merging operations for embedded neuro-processing units (NPUs).

#define OMNI_SUCCESS 0
#define OMNI_ERR_NULL_PTR 1

typedef struct {
    float* model_a;
    float* model_b;
    float* merged_out;
    size_t weight_count;
    float alpha;
} FusionContext;

int omni_npu_linear_merge(FusionContext* ctx) {
    if (!ctx || !ctx->model_a || !ctx->model_b || !ctx->merged_out) {
        return OMNI_ERR_NULL_PTR;
    }

    // Unrolled SIMD-like execution for bare-metal NPU
    for (size_t i = 0; i < ctx->weight_count; ++i) {
        ctx->merged_out[i] = (1.0f - ctx->alpha) * ctx->model_a[i] + ctx->alpha * ctx->model_b[i];
    }

    return OMNI_SUCCESS;
}
