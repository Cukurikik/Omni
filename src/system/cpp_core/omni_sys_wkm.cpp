#include <cstdint>

extern "C" {
    // WKM fast graph transition state lookup
    int32_t wkm_find_next_state(const int32_t* transition_matrix, uint32_t num_states, int32_t current_state, int32_t action_id) {
        if (current_state < 0 || current_state >= (int32_t)num_states) return -1;
        if (action_id < 0 || action_id >= (int32_t)num_states) return -1;
        
        // Assumes matrix is num_states x num_actions
        return transition_matrix[current_state * num_states + action_id];
    }
}
