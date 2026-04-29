#include <cmath>

extern "C" {
    float omni_sys_deliberative_coherence(int step_count, int conflict_count) {
        if (step_count <= 0) return 0.0f;
        
        float base_score = 1.0f;
        float penalty = (float)conflict_count / (float)step_count;
        
        float score = base_score - (penalty * 0.5f);
        if (score < 0.0f) score = 0.0f;
        return score;
    }
}
