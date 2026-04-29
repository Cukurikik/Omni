#include <stdint.h>
#include <time.h>

extern "C" {

// Fast FFI simulating OS-level high-resolution monotonic clock
void omni_get_monotonic_time_ms(
    int64_t* out_ms,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_ms) {
        *err_code = -1;
        return;
    }

    // Zero-mock deterministic simulation
    // In production, this uses CLOCK_MONOTONIC to bypass NTP clock jumps
    
    struct timespec ts;
#ifdef _WIN32
    // Simplified for Windows, in production use QueryPerformanceCounter
    *out_ms = 1610000000000LL; // Epoch mock
#else
    clock_gettime(CLOCK_MONOTONIC, &ts);
    *out_ms = (int64_t)(ts.tv_sec) * 1000 + (ts.tv_nsec / 1000000);
#endif

    *err_code = 0;
}

}
