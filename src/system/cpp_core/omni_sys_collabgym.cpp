#include <cstdint>

extern "C" {
    int omni_sys_collabgym_reward(int agent_effort, int human_effort) {
        if (agent_effort < 0) agent_effort = 0;
        if (human_effort < 0) human_effort = 0;
        
        // Collaborative synergy formula
        int base_score = agent_effort + human_effort;
        int synergy = (agent_effort > 0 && human_effort > 0) ? 5 : 0;
        
        return base_score + synergy;
    }
}
