#include <cstdint>
#include <vector>

extern "C" {

void omni_partition_data_hash(
    const int32_t* keys, 
    int32_t num_keys, 
    int32_t num_partitions, 
    int32_t* out_partition_ids, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!keys || !out_partition_ids || num_keys <= 0 || num_partitions <= 0) {
        *err_code = -1;
        return;
    }

    // Deterministic murmur3-like simple hash for partitioning logic
    for (int32_t i = 0; i < num_keys; ++i) {
        uint32_t k = (uint32_t)keys[i];
        k ^= k >> 16;
        k *= 0x85ebca6b;
        k ^= k >> 13;
        k *= 0xc2b2ae35;
        k ^= k >> 16;
        
        out_partition_ids[i] = (int32_t)(k % (uint32_t)num_partitions);
    }

    *err_code = 0;
}

}
