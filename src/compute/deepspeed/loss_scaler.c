#include <math.h>

// OMNI DEEPSPEED: FP16 Loss Scaler (C)
// Prevents underflow during mixed-precision training by scaling the loss up before backprop
// and scaling gradients down before optimizer update.
// Source: microsoft/DeepSpeed

typedef enum {
    SCALER_SUCCESS = 0,
    SCALER_ERR_NULL = 1
} scaler_err_t;

typedef struct {
    float scale;
    float growth_factor;
    float backoff_factor;
    int growth_interval;
    int successful_steps;
} LossScaler;

// Initialize the scaler
void scaler_init(LossScaler* s, float init_scale) {
    if (s) {
        s->scale = init_scale;
        s->growth_factor = 2.0f;
        s->backoff_factor = 0.5f;
        s->growth_interval = 2000;
        s->successful_steps = 0;
    }
}

// Scale the loss tensor (scalar value)
float scaler_scale_loss(LossScaler* s, float loss) {
    if (!s) return loss;
    return loss * s->scale;
}

// Unscale gradients. If inf/NaN detected, return 1 to trigger skip step.
int scaler_unscale_gradients(LossScaler* s, float* gradients, int num_elements) {
    if (!s || !gradients) return SCALER_ERR_NULL;
    
    int has_inf_nan = 0;
    float inv_scale = 1.0f / s->scale;

    for (int i = 0; i < num_elements; i++) {
        float g = gradients[i] * inv_scale;
        if (isnan(g) || isinf(g)) {
            has_inf_nan = 1;
        }
        gradients[i] = g;
    }

    return has_inf_nan;
}

// Update the scale based on step success (Dynamic Loss Scaling)
void scaler_update(LossScaler* s, int skipped_step) {
    if (!s) return;

    if (skipped_step) {
        // Overflow detected, reduce scale
        s->scale *= s->backoff_factor;
        s->successful_steps = 0;
    } else {
        s->successful_steps++;
        if (s->successful_steps == s->growth_interval) {
            // Stable for a long time, increase scale to retain more precision
            s->scale *= s->growth_factor;
            s->successful_steps = 0;
        }
    }
}
