// omni_posix_utils.c — POSIX Thread and System Utilities
// Layer: System / C
//
// Wrappers around POSIX APIs for pinning threads to specific CPU cores 
// (CPU Affinity) and adjusting scheduling policies to reduce latency jitter.

#define _GNU_SOURCE
#include <sched.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

/**
 * Pins the calling thread to a specific CPU core.
 * Crucial for networking threads (like io_uring) to avoid cache misses.
 */
int omni_pin_thread_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    
    pthread_t current_thread = pthread_self();
    
    int result = pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);
    if (result != 0) {
        fprintf(stderr, "Failed to set thread affinity to core %d\n", core_id);
        return -1;
    }
    return 0;
}

/**
 * Sets the scheduling policy of the calling thread to real-time (FIFO).
 * Requires root/CAP_SYS_NICE capabilities.
 */
int omni_set_realtime_priority(int priority_level) {
    struct sched_param param;
    param.sched_priority = priority_level; // Usually 1 to 99
    
    // SCHED_FIFO provides first-in, first-out real-time execution
    int result = sched_setscheduler(0, SCHED_FIFO, &param);
    if (result != 0) {
        // Fallback to normal priority if not permitted
        fprintf(stderr, "Warning: Failed to set SCHED_FIFO (Check capabilities)\n");
        return -1;
    }
    return 0;
}
