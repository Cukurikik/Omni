#include <cstdint>
#include <cmath>

extern "C" {

double omni_map_anndata(size_t num_cells, size_t num_genes, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (num_cells == 0 || num_genes == 0) {
        *err_code = -1;
        return 0.0;
    }

    // Deterministic simulation of memory-mapped AnnData matrix
    // 4 bytes per float32 expression value
    double memory_bytes = (double)num_cells * (double)num_genes * 4.0;
    
    // Simulate sparse optimization (approx 10% non-zero for scRNA-seq)
    double optimized_memory = memory_bytes * 0.1;
    
    *err_code = 0;
    return optimized_memory / (1024.0 * 1024.0); // Return MBs
}

}
