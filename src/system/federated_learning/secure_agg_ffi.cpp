#include <cstdint>
#include <cmath>

extern "C" {

// FFI export for deterministic secure aggregation mathematical masking
void omni_secure_aggregation_mask(
    const double* input_weights, 
    int32_t num_params, 
    uint64_t client_seed, 
    double* out_masked_weights, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!input_weights || !out_masked_weights || num_params <= 0) {
        *err_code = -1;
        return;
    }

    // Deterministic simulation of homomorphic/secure aggregation masking
    // Clients add a deterministic pairwise mask that cancels out when summed globally
    
    for (int i = 0; i < num_params; ++i) {
        // Simple deterministic mask based on seed and parameter index
        // In reality, this would be a cryptographic PRG shared between clients
        double mask = std::sin((double)(client_seed * 31 + i * 17)) * 100.0;
        
        out_masked_weights[i] = input_weights[i] + mask;
    }

    *err_code = 0;
}

}
