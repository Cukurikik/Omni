#include <cstdint>

extern "C" {
    int omni_sys_moe_balance(int32_t* loads, int32_t* capacities, int num_experts) {
        if (num_experts <= 0) return -1;
        
        int total_available = 0;
        for (int i = 0; i < num_experts; ++i) {
            int available = capacities[i] - loads[i];
            if (available < 0) return -2; // Overloaded state
            total_available += available;
        }
        return total_available;
    }
}
