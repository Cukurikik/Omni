#include <cmath>

extern "C" {
    /// Compute reward signal for agentic reinforcement step.
    float omni_sys_aeiva_reward(float task_progress, float penalty, float gamma) {
        return task_progress * gamma - penalty;
    }

    /// Bellman value update for state-action pair.
    float omni_sys_aeiva_bellman(float current_v, float reward, float next_v, float gamma, float alpha) {
        float target = reward + gamma * next_v;
        return current_v + alpha * (target - current_v);
    }
}
