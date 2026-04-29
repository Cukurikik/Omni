#include <cstdint>
extern "C" {
    int omni_sys_agentchain_topological_sort_check(int nodes, int edges) {
        return edges < nodes ? 1 : 0;
    }
    float omni_sys_agentchain_priority(float urgency, float importance, float w_u, float w_i) {
        return w_u * urgency + w_i * importance;
    }
}
