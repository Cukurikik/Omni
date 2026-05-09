/*
 * omni_futex_lock.c — Fast Userspace Mutex (Futex)
 * Layer: System / C
 *
 * Implements a hyper-fast, low-overhead mutex leveraging the Linux futex 
 * syscall directly. Spins briefly in userspace before sleeping in the kernel,
 * outperforming standard pthreads for short critical sections. Zero mock.
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdint.h>
#include <stdatomic.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>
#include <limits.h>
#include <time.h>

typedef struct OmniFutexLock {
    atomic_int state; // 0 = unlocked, 1 = locked/no waiters, 2 = locked/waiters
} OmniFutexLock;

static inline int sys_futex(atomic_int *uaddr, int futex_op, int val, 
                            const struct timespec *timeout, int *uaddr2, int val3) {
    return syscall(__NR_futex, uaddr, futex_op, val, timeout, uaddr2, val3);
}

void omni_futex_init(OmniFutexLock *lock) {
    atomic_init(&lock->state, 0);
}

void omni_futex_lock(OmniFutexLock *lock) {
    int expected = 0;
    
    // Fast path: try to lock if currently unlocked
    if (atomic_compare_exchange_strong_explicit(&lock->state, &expected, 1, 
                                                memory_order_acquire, memory_order_relaxed)) {
        return; // Acquired lock
    }

    // Slow path: spin a few times before going to sleep
    for (int spin = 0; spin < 100; ++spin) {
        expected = 0;
        if (atomic_compare_exchange_strong_explicit(&lock->state, &expected, 1, 
                                                    memory_order_acquire, memory_order_relaxed)) {
            return;
        }
        __asm__ volatile("pause" ::: "memory"); // Hint to CPU that we are spinning
    }

    // Really slow path: Wait via kernel
    while (1) {
        // Assume state is 2 (waiters exist) or set it to 2 if it was 1
        expected = atomic_exchange_explicit(&lock->state, 2, memory_order_acquire);
        
        if (expected == 0) {
            return; // Acquired lock!
        }
        
        // Wait until the state changes from 2
        sys_futex(&lock->state, FUTEX_WAIT_PRIVATE, 2, NULL, NULL, 0);
    }
}

void omni_futex_unlock(OmniFutexLock *lock) {
    // Fast path: Try to release if there are no waiters (state transitions 1 -> 0)
    int expected = 1;
    if (atomic_compare_exchange_strong_explicit(&lock->state, &expected, 0, 
                                                memory_order_release, memory_order_relaxed)) {
        return; // Unlocked, nobody was waiting
    }

    // Slow path: There are waiters (state was 2). Set to 0 and wake one up.
    atomic_store_explicit(&lock->state, 0, memory_order_release);
    sys_futex(&lock->state, FUTEX_WAKE_PRIVATE, 1, NULL, NULL, 0);
}
