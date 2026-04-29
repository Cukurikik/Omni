#include <cstdint>

extern "C" {
    // CodeAgents DAG cycle detection matrix
    bool codeagents_has_cycle(const uint8_t* adjacency_matrix, uint32_t num_nodes) {
        // Simplified heuristic cycle check for small agent dependency graphs (N < 32)
        if (num_nodes == 0 || num_nodes > 32) return false;
        
        uint32_t in_degree[32] = {0};
        for (uint32_t i = 0; i < num_nodes; i++) {
            for (uint32_t j = 0; j < num_nodes; j++) {
                if (adjacency_matrix[i * num_nodes + j]) {
                    in_degree[j]++;
                }
            }
        }
        
        uint32_t processed = 0;
        bool changed = true;
        
        while (changed && processed < num_nodes) {
            changed = false;
            for (uint32_t i = 0; i < num_nodes; i++) {
                if (in_degree[i] == 0) {
                    in_degree[i] = 0xFFFFFFFF; // Mark processed
                    processed++;
                    changed = true;
                    // Remove outbound edges
                    for (uint32_t j = 0; j < num_nodes; j++) {
                        if (adjacency_matrix[i * num_nodes + j] && in_degree[j] != 0xFFFFFFFF) {
                            in_degree[j]--;
                        }
                    }
                }
            }
        }
        
        return processed < num_nodes;
    }
}
