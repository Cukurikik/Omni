#include <cstdint>

struct MedicalOntologyNode {
    uint32_t id;
    uint32_t parent_id;
    uint32_t risk_level;
};

extern "C" {
    // Me-LLaMA fast hierarchical risk escalation
    uint32_t mellama_calculate_max_risk_path(const MedicalOntologyNode* nodes, uint32_t count, uint32_t start_node_id) {
        uint32_t max_risk = 0;
        uint32_t current_id = start_node_id;
        
        // Prevent infinite loops with max depth
        for (uint32_t depth = 0; depth < 256; ++depth) {
            bool found = false;
            for (uint32_t i = 0; i < count; ++i) {
                if (nodes[i].id == current_id) {
                    if (nodes[i].risk_level > max_risk) {
                        max_risk = nodes[i].risk_level;
                    }
                    if (nodes[i].parent_id == 0 || nodes[i].parent_id == current_id) {
                        return max_risk; // Reached root
                    }
                    current_id = nodes[i].parent_id;
                    found = true;
                    break;
                }
            }
            if (!found) break; // Path broken
        }
        return max_risk;
    }
}
