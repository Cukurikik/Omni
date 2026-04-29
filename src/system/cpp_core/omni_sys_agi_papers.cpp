#include <cstdint>
extern "C" {
    float omni_sys_agi_papers_novelty_score(int ref_count, int self_cite, int total_refs) {
        if (total_refs <= 0) return 0.0f;
        float external = (float)(ref_count - self_cite) / (float)total_refs;
        return external > 0 ? external : 0.0f;
    }
}
