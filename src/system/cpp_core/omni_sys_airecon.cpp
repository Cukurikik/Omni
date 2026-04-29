#include <cstdint>
extern "C" {
    float omni_sys_airecon_threat_score(int num_indicators, int total_rules, float severity_avg) {
        if (total_rules <= 0) return 0.0f;
        float coverage = (float)num_indicators / (float)total_rules;
        return coverage * severity_avg;
    }
}
