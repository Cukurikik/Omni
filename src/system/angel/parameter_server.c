/* @omni-domain System Layer (Parameter Server)
   @omni-source angel-ml/angel
   @omni-description Angel Parameter Server mimicking distributed gradient aggregation in C.
   @omni-requirement zero-mock, monadic-error */

#include <stdlib.h>
#include <string.h>

typedef struct { void* data; char* error; int is_ok; } OmniResult;

typedef struct {
    double* weights;
    int num_params;
    int num_workers;
} ParameterServer;

OmniResult ps_init(ParameterServer* ps, int num_params, int num_workers) {
    OmniResult r;
    if (num_params <= 0 || num_workers <= 0) {
        r.data = NULL; r.error = "Invalid params."; r.is_ok = 0; return r;
    }
    ps->num_params = num_params;
    ps->num_workers = num_workers;
    ps->weights = (double*)calloc(num_params, sizeof(double));
    if (!ps->weights) { r.data = NULL; r.error = "Allocation failed."; r.is_ok = 0; return r; }
    r.data = ps; r.error = NULL; r.is_ok = 1; return r;
}

OmniResult ps_push_gradients(ParameterServer* ps, double* gradients, int len, double learning_rate) {
    OmniResult r;
    if (!ps || !gradients || len != ps->num_params) {
        r.data = NULL; r.error = "Invalid gradient push."; r.is_ok = 0; return r;
    }
    for (int i = 0; i < ps->num_params; i++) {
        ps->weights[i] -= learning_rate * gradients[i] / ps->num_workers;
    }
    r.data = ps->weights; r.error = NULL; r.is_ok = 1; return r;
}

OmniResult ps_pull_weights(ParameterServer* ps, double* buffer, int len) {
    OmniResult r;
    if (!ps || !buffer || len != ps->num_params) {
        r.data = NULL; r.error = "Invalid weight pull."; r.is_ok = 0; return r;
    }
    memcpy(buffer, ps->weights, ps->num_params * sizeof(double));
    r.data = buffer; r.error = NULL; r.is_ok = 1; return r;
}

void ps_free(ParameterServer* ps) {
    if (ps && ps->weights) { free(ps->weights); ps->weights = NULL; }
}
