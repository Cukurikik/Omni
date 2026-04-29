#include <cstdint>

extern "C" {
    int omni_sys_mlops_topsort(int* adjacency_matrix, int num_nodes, int* out_sorted) {
        if (num_nodes <= 0) return -1;
        
        int in_degree[1024] = {0};
        for (int i = 0; i < num_nodes; ++i) {
            for (int j = 0; j < num_nodes; ++j) {
                if (adjacency_matrix[i * num_nodes + j]) {
                    in_degree[j]++;
                }
            }
        }
        
        int head = 0, tail = 0;
        int queue[1024];
        
        for (int i = 0; i < num_nodes; ++i) {
            if (in_degree[i] == 0) {
                queue[tail++] = i;
            }
        }
        
        int count = 0;
        while (head < tail) {
            int u = queue[head++];
            out_sorted[count++] = u;
            
            for (int v = 0; v < num_nodes; ++v) {
                if (adjacency_matrix[u * num_nodes + v]) {
                    if (--in_degree[v] == 0) {
                        queue[tail++] = v;
                    }
                }
            }
        }
        
        return count == num_nodes ? 1 : 0; // 1 if DAG, 0 if cycle exists
    }
}
