#include <stdatomic.h>
#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// OMNI System Layer: Memory barriers for cross-process shared memory (e.g. Plasma Store in Ray)
// Enforces strict memory ordering for lock-free IPC data structures

typedef struct {
    int is_success;
    uint64_t value;
    int error_code; // 1 = null pointer
} BarrierResult;

BarrierResult read_with_acquire_barrier(const _Atomic(uint64_t)* ptr) {
    BarrierResult res = {0, 0, 0};
    if (!ptr) {
        res.error_code = 1;
        return res;
    }
    
    // Acquire barrier ensures all subsequent reads/writes happen AFTER this load
    res.value = atomic_load_explicit(ptr, memory_order_acquire);
    res.is_success = 1;
    return res;
}

BarrierResult write_with_release_barrier(_Atomic(uint64_t)* ptr, uint64_t val) {
    BarrierResult res = {0, 0, 0};
    if (!ptr) {
        res.error_code = 1;
        return res;
    }
    
    // Release barrier ensures all prior reads/writes happen BEFORE this store
    atomic_store_explicit(ptr, val, memory_order_release);
    res.value = val;
    res.is_success = 1;
    return res;
}

// Full sequential consistency barrier
void strict_memory_fence() {
    atomic_thread_fence(memory_order_seq_cst);
}

#ifdef __cplusplus
}
#endif
