#include <cstdint>
#include <cmath>

// OMNI System Kernel: Token bucket rate limiter logic
extern "C" {
        double compute(double current_tokens, double rate, double elapsed_sec, double capacity) {
            double new_tokens = current_tokens + (rate * elapsed_sec);
            return new_tokens > capacity ? capacity : new_tokens;
        }
}