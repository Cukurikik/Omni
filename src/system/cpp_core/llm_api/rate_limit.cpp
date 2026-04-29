#include <cstdint>
#include <algorithm>

extern "C" {
    // OMNI System Layer - Atomic-free token bucket calculation for single threaded hot paths
    bool compute_token_bucket(double* current_tokens, double capacity, double fill_rate, double elapsed_sec, double requested) {
        if (!current_tokens) return false;
        
        *current_tokens = std::min(capacity, *current_tokens + (elapsed_sec * fill_rate));
        if (*current_tokens >= requested) {
            *current_tokens -= requested;
            return true;
        }
        return false;
    }
}
