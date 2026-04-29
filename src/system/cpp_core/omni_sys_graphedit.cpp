#include <cstdint>

extern "C" {
    int omni_sys_graphedit_update(int* adj_matrix, int num_nodes, int u, int v, int add_edge) {
        if (num_nodes <= 0 || u < 0 || u >= num_nodes || v < 0 || v >= num_nodes) {
            return -1; // Invalid bounds
        }
        
        adj_matrix[u * num_nodes + v] = add_edge ? 1 : 0;
        adj_matrix[v * num_nodes + u] = add_edge ? 1 : 0; // Undirected
        
        return 0; // Success
    }
}
