#include <cstdint>
#include <cmath>

// OMNI System Kernel: DAG acyclic depth
extern "C" {
        int32_t compute(const int32_t* node_edges, int32_t num_nodes) {
            int max_depth = 0;
            for(int i=0; i<num_nodes; i++) {
                if(node_edges[i] > max_depth) max_depth = node_edges[i];
            }
            return max_depth + 1;
        }
}