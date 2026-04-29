#include <cmath>

extern "C" {
    float omni_sys_reflexion_score(int trajectory_len, int error_count) {
        if (trajectory_len <= 0) return 0.0f;
        
        // Simple penalty scoring
        float base_score = 1.0f;
        float penalty = (float)error_count * 0.2f;
        float len_penalty = (trajectory_len > 1000) ? 0.1f : 0.0f;
        
        float final_score = base_score - penalty - len_penalty;
        if (final_score < 0.0f) final_score = 0.0f;
        return final_score;
    }
}
