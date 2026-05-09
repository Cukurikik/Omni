/*
 * omni_cpu_affinity.c — Thread Pinning and Core Affinity
 * Layer: System / C
 *
 * Provides cross-platform wrappers (primarily targeting POSIX/Linux) for 
 * pinning threads to specific CPU cores, bypassing OS scheduler migrations
 * to ensure maximum L1/L2 cache locality for inference loops. Zero mocks.
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <sched.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>

/**
 * Pins the current thread to a specific CPU core.
 * Returns 0 on success, or an error code on failure.
 */
int omni_pin_thread_to_core(int core_id) {
    int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (core_id < 0 || core_id >= num_cores) {
        fprintf(stderr, "OMNI Core Affinity: Invalid core ID %d (max %d)\n", core_id, num_cores - 1);
        return -1;
    }

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);

    pthread_t current_thread = pthread_self();
    
    int result = pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);
    if (result != 0) {
        fprintf(stderr, "OMNI Core Affinity: Failed to pin thread to core %d (error %d)\n", core_id, result);
        return result;
    }

    return 0;
}

/**
 * Retrieves the current CPU core ID the calling thread is executing on.
 */
int omni_get_current_core() {
    return sched_getcpu();
}

/**
 * Pins a thread to a range of cores (useful for I/O thread pools).
 */
int omni_pin_thread_to_core_range(int start_core, int end_core) {
    int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (start_core < 0 || end_core >= num_cores || start_core > end_core) {
        return -1;
    }

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    
    for (int i = start_core; i <= end_core; i++) {
        CPU_SET(i, &cpuset);
    }

    pthread_t current_thread = pthread_self();
    return pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);
}
