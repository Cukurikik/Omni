#include <cstdint>

extern "C" {
    int omni_sys_chatllama_ratelimit_check(int message_count, int time_window_sec) {
        // Simple deterministic rate limiter math
        // Allow 5 messages per 10 seconds
        if (time_window_sec <= 0) return 1; // Allow
        
        float rate = (float)message_count / time_window_sec;
        if (rate > 0.5f) {
            return 0; // Block
        }
        return 1; // Allow
    }
}
