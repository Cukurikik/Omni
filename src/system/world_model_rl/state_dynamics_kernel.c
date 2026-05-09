/* @omni-layer System | @omni-source lucidrains/improving-transformers-world-model-for-rl | @omni-lang C
 * @omni-description State dynamics kernel: optimized state transition matrix
 * multiply for model-based RL world model dynamics prediction.
 */
#include <math.h>
#include <string.h>

#define MAX_STATE_DIM 128

typedef struct {
    float state[MAX_STATE_DIM];
    int dim;
} OmniState;

typedef struct {
    float data[MAX_STATE_DIM * MAX_STATE_DIM];
    int rows;
    int cols;
} OmniTransitionMatrix;

typedef struct {
    int ok;
    OmniState result;
    const char *error;
} OmniStateResult;

void omni_init_state(OmniState *s, int dim) {
    s->dim = dim < MAX_STATE_DIM ? dim : MAX_STATE_DIM;
    memset(s->state, 0, sizeof(s->state));
}

OmniStateResult omni_apply_dynamics(const OmniTransitionMatrix *T, const OmniState *s, const float *action, int action_dim) {
    OmniStateResult result;
    result.ok = 1;
    result.error = NULL;
    result.result.dim = s->dim;
    if (s->dim <= 0 || s->dim > MAX_STATE_DIM) {
        result.ok = 0; result.error = "invalid dim"; return result;
    }
    /* s' = T * s + action_bias */
    int d = s->dim;
    for (int i = 0; i < d; i++) {
        float val = 0.0f;
        for (int j = 0; j < d; j++) {
            val += T->data[i * d + j] * s->state[j];
        }
        /* Add action influence */
        if (action && i < action_dim) {
            val += action[i] * 0.3f;
        }
        result.result.state[i] = tanhf(val);
    }
    return result;
}

float omni_compute_reward(const OmniState *s, const float *action, int action_dim) {
    float reward = 0.0f;
    int d = s->dim < action_dim ? s->dim : action_dim;
    for (int i = 0; i < d; i++) {
        reward += s->state[i] * action[i];
    }
    return tanhf(reward);
}

float omni_state_norm(const OmniState *s) {
    float norm = 0.0f;
    for (int i = 0; i < s->dim; i++) {
        norm += s->state[i] * s->state[i];
    }
    return sqrtf(norm);
}

void omni_state_blend(OmniState *out, const OmniState *a, const OmniState *b, float alpha) {
    int d = a->dim < b->dim ? a->dim : b->dim;
    out->dim = d;
    for (int i = 0; i < d; i++) {
        out->state[i] = alpha * a->state[i] + (1.0f - alpha) * b->state[i];
    }
}
