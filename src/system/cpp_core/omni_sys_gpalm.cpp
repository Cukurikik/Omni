#include <cstdint>
#include <cmath>

extern "C" {
    // UCT (Upper Confidence Bound for Trees) calculation for Monte Carlo Tree Search
    float gpalm_compute_uct(float node_wins, uint32_t node_visits, uint32_t parent_visits, float exploration_param) {
        if (node_visits == 0) {
            return 999999.0f; // Infinite priority for unvisited nodes
        }
        float exploitation = node_wins / node_visits;
        float exploration = exploration_param * std::sqrt(std::log((float)parent_visits) / node_visits);
        return exploitation + exploration;
    }
}
