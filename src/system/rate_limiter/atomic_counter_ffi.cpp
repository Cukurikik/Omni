#include <stdint.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <stdatomic.h>
#endif

extern "C" {

// Fast FFI simulating lock-free atomic counter increment for high-speed rate limiting
void omni_atomic_increment(
    volatile int64_t* counter_ptr,
    int64_t increment_val,
    int64_t* out_new_val,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!counter_ptr || !out_new_val) {
        *err_code = -1;
        return;
    }

    // Hardware accelerated atomic fetch_add
#ifdef _WIN32
    *out_new_val = InterlockedExchangeAdd64((volatile LONG64*)counter_ptr, increment_val) + increment_val;
#else
    *out_new_val = atomic_fetch_add_explicit((_Atomic int64_t*)counter_ptr, increment_val, memory_order_seq_cst) + increment_val;
#endif

    *err_code = 0;
}

}
