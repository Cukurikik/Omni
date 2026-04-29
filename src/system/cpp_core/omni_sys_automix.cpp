#include <cstdint>

extern "C" {
    int omni_sys_automix_routing_decision(float small_model_conf, float threshold) {
        // If small model is confident enough, return 0 (use small model)
        // Else return 1 (route to large model)
        if (small_model_conf >= threshold) {
            return 0;
        }
        return 1;
    }
}
