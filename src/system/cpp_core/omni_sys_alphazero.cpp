#include <cmath>

extern "C" {
    /// UCB1 selection for MCTS node.
    double omni_sys_alphazero_ucb1(double win_rate, int parent_visits, int child_visits, double c) {
        if (child_visits <= 0 || parent_visits <= 0) return 1e9;
        return win_rate + c * std::sqrt(std::log((double)parent_visits) / (double)child_visits);
    }

    /// Dirichlet noise injection for root exploration.
    float omni_sys_alphazero_add_noise(float prior, float noise, float epsilon) {
        return (1.0f - epsilon) * prior + epsilon * noise;
    }
}
