// moe_numa_affinity.c — System / OS Integration
// Layer: System / OS — MoE Thread & Memory Pinning
//
// Binds MoE CPU worker threads and their associated memory allocations
// to specific NUMA nodes to prevent cross-socket latency when experts
// are offloaded to host memory.

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <numa.h>
#include <numaif.h>
#include <pthread.h>

// Monadic-style error codes for C
typedef enum {
    NUMA_OK = 0,
    NUMA_ERR_UNAVAILABLE = -1,
    NUMA_ERR_BIND_FAILED = -2,
    NUMA_ERR_MEM_ALLOC = -3
} NumaResult;

/**
 * Initializes NUMA capabilities.
 */
NumaResult omni_numa_init() {
    if (numa_available() == -1) {
        fprintf(stderr, "[MoE NUMA] NUMA is not available on this system.\n");
        return NUMA_ERR_UNAVAILABLE;
    }
    return NUMA_OK;
}

/**
 * Pins the calling thread to a specific NUMA node's CPUs.
 */
NumaResult omni_numa_pin_thread(int node_id) {
    if (node_id < 0 || node_id > numa_max_node()) {
        return NUMA_ERR_BIND_FAILED;
    }

    struct bitmask *cpus = numa_allocate_cpumask();
    if (numa_node_to_cpus(node_id, cpus) != 0) {
        numa_free_cpumask(cpus);
        return NUMA_ERR_BIND_FAILED;
    }

    // Convert NUMA bitmask to pthread CPU set
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    for (unsigned int i = 0; i < cpus->size; i++) {
        if (numa_bitmask_isbitset(cpus, i)) {
            CPU_SET(i, &cpuset);
        }
    }

    pthread_t thread = pthread_self();
    if (pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset) != 0) {
        numa_free_cpumask(cpus);
        return NUMA_ERR_BIND_FAILED;
    }

    numa_free_cpumask(cpus);
    return NUMA_OK;
}

/**
 * Allocates strict NUMA-bound memory for an expert's weights.
 * Prevents OS from migrating pages across sockets.
 */
void* omni_numa_alloc_expert_memory(int node_id, size_t size) {
    if (node_id < 0 || node_id > numa_max_node()) {
        return NULL;
    }
    
    // Allocate memory specifically on the requested node
    void *ptr = numa_alloc_onnode(size, node_id);
    if (ptr == NULL) {
        return NULL;
    }

    // Force strict binding (prevent future migration)
    unsigned long nodemask = (1UL << node_id);
    if (mbind(ptr, size, MPOL_BIND, &nodemask, sizeof(nodemask) * 8 + 1, MPOL_MF_STRICT) != 0) {
        numa_free(ptr, size);
        return NULL;
    }

    return ptr;
}

/**
 * Frees NUMA-bound memory.
 */
void omni_numa_free_expert_memory(void* ptr, size_t size) {
    if (ptr != NULL) {
        numa_free(ptr, size);
    }
}
