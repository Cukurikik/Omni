/*
 * omni_thread_pinner.c — OS-Level Thread Affinity
 * Layer: System / Kernel
 * Inspired by: DPDK / NGINX core
 *
 * Provides a cross-platform abstraction for pinning high-performance threads
 * to specific CPU cores. Prevents the OS scheduler from migrating threads,
 * drastically reducing L1/L2 cache misses in latency-critical loops. Zero mock.
 */

#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
#include <windows.h>
#else
#define _GNU_SOURCE
#include <sched.h>
#include <pthread.h>
#include <unistd.h>
#endif

/**
 * Pins the calling thread to the specified CPU core ID.
 * Returns 0 on success, non-zero on error.
 */
int omni_pin_thread_to_core(int core_id) {
#ifdef _WIN32
    HANDLE thread = GetCurrentThread();
    DWORD_PTR mask = (DWORD_PTR)1 << core_id;
    
    DWORD_PTR result = SetThreadAffinityMask(thread, mask);
    if (result == 0) {
        // Failure
        return -1;
    }
    return 0;

#else
    // Linux / POSIX
    int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (core_id < 0 || core_id >= num_cores) {
        return -1; // Invalid core ID
    }

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);

    pthread_t current_thread = pthread_self();    
    int result = pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);
    
    if (result != 0) {
        return result;
    }
    
    return 0;
#endif
}

/**
 * Retrieves the currently pinned core mask (if applicable).
 * For simplicity, returns the first core it finds it is permitted to run on.
 */
int omni_get_current_core() {
#ifdef _WIN32
    return (int)GetCurrentProcessorNumber();
#else
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    if (pthread_getaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) == 0) {
        for (int j = 0; j < CPU_SETSIZE; j++) {
            if (CPU_ISSET(j, &cpuset)) {
                return j;
            }
        }
    }
    return -1;
#endif
}
