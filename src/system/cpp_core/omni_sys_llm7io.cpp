#include <cstdint>

extern "C" {
    struct TokenBucket {
        int64_t tokens;
        int64_t capacity;
        int64_t last_refill;
        int32_t refill_rate; // tokens per second
    };

    int omni_sys_llm7io_consume(TokenBucket* bucket, int32_t amount, int64_t current_time) {
        if (bucket == nullptr || amount <= 0) return -1;

        int64_t time_diff = current_time - bucket->last_refill;
        int64_t new_tokens = time_diff * bucket->refill_rate;
        
        bucket->tokens += new_tokens;
        if (bucket->tokens > bucket->capacity) {
            bucket->tokens = bucket->capacity;
        }
        bucket->last_refill = current_time;

        if (bucket->tokens >= amount) {
            bucket->tokens -= amount;
            return 1; // Allowed
        }
        
        return 0; // Rate limited
    }
}
