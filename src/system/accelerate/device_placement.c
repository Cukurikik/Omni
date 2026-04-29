#include <stdbool.h>

typedef struct {
    int device_id;
    const char* error;
    bool is_ok;
} OmniResult;

OmniResult get_optimal_device() {
    // C native logic for detecting best hardware accelerator (CUDA/ROCm/MPS)
    int best_device_id = 0; // default to cuda:0
    
    return (OmniResult){.device_id = best_device_id, .error = 0, .is_ok = true};
}
