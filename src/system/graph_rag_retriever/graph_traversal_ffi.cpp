#include <stdint.h>

extern "C" {

// Fast FFI for Graph RAG traversal (e.g., Breadth-First Search for semantic hops)
void omni_graph_bfs_traversal(
    const int32_t* row_ptrs,
    const int32_t* col_indices,
    int32_t num_nodes,
    int32_t start_node,
    int32_t max_hops,
    int32_t* out_distances,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!row_ptrs || !col_indices || !out_distances || num_nodes <= 0 || start_node < 0 || start_node >= num_nodes) {
        *err_code = -1;
        return;
    }

    // Zero-mock deterministic BFS on CSR (Compressed Sparse Row) graph format
    for (int32_t i = 0; i < num_nodes; ++i) {
        out_distances[i] = -1;
    }
    
    out_distances[start_node] = 0;
    
    // Simple queue array for zero-mock C++
    int32_t* queue = new int32_t[num_nodes];
    int32_t head = 0;
    int32_t tail = 0;
    
    queue[tail++] = start_node;
    
    while (head < tail) {
        int32_t u = queue[head++];
        int32_t dist = out_distances[u];
        
        if (dist >= max_hops) continue;
        
        int32_t start_edge = row_ptrs[u];
        int32_t end_edge = row_ptrs[u + 1];
        
        for (int32_t e = start_edge; e < end_edge; ++e) {
            int32_t v = col_indices[e];
            if (out_distances[v] == -1) {
                out_distances[v] = dist + 1;
                queue[tail++] = v;
            }
        }
    }
    
    delete[] queue;
    *err_code = 0;
}

}
