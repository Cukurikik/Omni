#include <stdint.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <stdatomic.h>
#endif

extern "C" {

// Fast FFI simulating Shared Memory Atomic Flag for lock-free cross-process Circuit Breaker state
// 0 = CLOSED, 1 = OPEN, 2 = HALF_OPEN
void omni_atomic_read_breaker_state(
    const volatile int32_t* state_ptr,
    int32_t* out_state,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!state_ptr || !out_state) {
        *err_code = -1;
        return;
    }

#ifdef _WIN32
    *out_state = InterlockedCompareExchange((volatile LONG*)state_ptr, 0, 0);
#else
    *out_state = atomic_load_explicit((const volatile _Atomic int32_t*)state_ptr, memory_order_acquire);
#endif

    *err_code = 0;
}

}
