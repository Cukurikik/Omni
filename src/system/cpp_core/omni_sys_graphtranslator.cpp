#include <cstdint>

extern "C" {
    int omni_sys_graphtranslator_edge_count(const int* adj_matrix, int nodes) {
        if (!adj_matrix || nodes <= 0) return 0;
        
        int edges = 0;
        for (int i = 0; i < nodes * nodes; ++i) {
            if (adj_matrix[i] > 0) {
                edges++;
            }
        }
        // Assuming undirected graph, divide by 2
        return edges / 2;
    }
}
