#include <stdint.h>
#include <stdlib.h>

extern "C" {

// Fast FFI for contiguous memory pool allocation of Tree Nodes
// Used to manage large semantic search trees without GC pauses
void omni_allocate_thought_nodes(
    int32_t num_nodes,
    int32_t bytes_per_node,
    uint8_t** out_ptr,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_ptr || num_nodes <= 0 || bytes_per_node <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution
    // Allocates a massive contiguous block for MCTS tree structures
    size_t total_size = (size_t)num_nodes * (size_t)bytes_per_node;
    
    // In a real system, this would tie into the custom OMNI alloc (Section 15)
    *out_ptr = (uint8_t*)calloc(num_nodes, bytes_per_node);
    
    if (*out_ptr == NULL) {
        *err_code = -2; // OOM
    } else {
        *err_code = 0;
    }
}

// Memory cleanup
void omni_free_thought_nodes(uint8_t* ptr) {
    if (ptr) {
        free(ptr);
    }
}

}
