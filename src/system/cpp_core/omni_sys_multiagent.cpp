#include <cstring>

extern "C" {
    int omni_sys_multiagent_consensus(const int* agent_votes, int num_agents, int num_options) {
        if (!agent_votes || num_agents <= 0 || num_options <= 0) return -1;
        
        int counts[100] = {0}; // Assume max 100 options
        if (num_options > 100) return -1;
        
        for (int i = 0; i < num_agents; ++i) {
            int vote = agent_votes[i];
            if (vote >= 0 && vote < num_options) {
                counts[vote]++;
            }
        }
        
        int max_votes = -1;
        int best_option = -1;
        for (int i = 0; i < num_options; ++i) {
            if (counts[i] > max_votes) {
                max_votes = counts[i];
                best_option = i;
            }
        }
        return best_option;
    }
}
