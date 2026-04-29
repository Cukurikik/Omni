#include <cstdint>
#include <cmath>

// OMNI System Kernel: AST Depth
extern "C" {
        int32_t compute(const int32_t* node_depths, int32_t len) {
            int32_t max = 0;
            for(int i=0; i<len; i++) {
                if(node_depths[i] > max) max = node_depths[i];
            }
            return max;
        }
}