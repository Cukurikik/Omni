#include <cmath>

extern "C" {
    float omni_sys_dialop_compute_utility(float agent1_pref, float agent2_pref) {
        // Collaborative utility function
        if (agent1_pref < 0.0f || agent2_pref < 0.0f) return 0.0f;
        
        // Nash bargaining product mock
        return std::sqrt(agent1_pref * agent2_pref);
    }
}
