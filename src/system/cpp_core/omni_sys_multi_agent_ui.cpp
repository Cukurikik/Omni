#include <cstdint>
#include <cmath>

// OMNI System Kernel: Consistent hashing for agent nodes
extern "C" {
        int32_t compute(const uint8_t* key, int32_t len, int32_t num_nodes) {
            uint32_t hash = 5381;
            for(int i=0; i<len; i++) hash = ((hash << 5) + hash) + key[i];
            return hash % num_nodes;
        }
}