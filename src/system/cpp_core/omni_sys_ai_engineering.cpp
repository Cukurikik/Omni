#include <cstdint>
extern "C" {
    int omni_sys_ai_engineering_token_budget(int prompt_tokens, int max_tokens, int reserve) {
        int avail = max_tokens - prompt_tokens - reserve;
        return avail > 0 ? avail : 0;
    }
    float omni_sys_ai_engineering_latency_p99(const float* latencies, int n) {
        if (!latencies || n <= 0) return 0.0f;
        int idx = (int)(0.99f * (float)(n - 1));
        return latencies[idx];
    }
}
