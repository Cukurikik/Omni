/*
 * omni_numa_alloc.c — NUMA-Aware Memory Allocator
 * Layer: System / C
 *
 * Provides wrappers for allocating memory bound to specific NUMA nodes.
 * Extremely critical for preventing cross-socket memory access latency 
 * in multi-CPU inference servers. Requires libnuma (-lnuma). Zero mock.
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <numa.h>
#include <numaif.h>

/**
 * Checks if the system supports NUMA architecture.
 */
int omni_numa_available() {
    return (numa_available() != -1);
}

/**
 * Allocates memory specifically on the requested NUMA node.
 */
void* omni_numa_alloc_onnode(size_t size, int node_id) {
    if (!omni_numa_available()) {
        // Fallback to standard malloc if NUMA is disabled/unsupported
        return malloc(size);
    }
    
    int max_node = numa_max_node();
    if (node_id < 0 || node_id > max_node) {
        fprintf(stderr, "OMNI NUMA Alloc: Invalid node %d (max %d)\n", node_id, max_node);
        return NULL;
    }

    void* ptr = numa_alloc_onnode(size, node_id);
    return ptr;
}

/**
 * Allocates memory interleaved across all available NUMA nodes.
 * Useful for global data structures accessed uniformly by all threads.
 */
void* omni_numa_alloc_interleaved(size_t size) {
    if (!omni_numa_available()) {
        return malloc(size);
    }
    
    return numa_alloc_interleaved(size);
}

/**
 * Frees memory allocated by the NUMA routines.
 */
void omni_numa_free(void* ptr, size_t size) {
    if (!ptr) return;

    if (!omni_numa_available()) {
        free(ptr);
        return;
    }

    numa_free(ptr, size);
}

/**
 * Gets the NUMA node ID that a specific memory address is currently bound to.
 */
int omni_numa_get_node_from_ptr(void* ptr) {
    if (!omni_numa_available()) {
        return 0; // Assume node 0
    }

    int node = -1;
    int ret = get_mempolicy(&node, NULL, 0, ptr, MPOL_F_NODE | MPOL_F_ADDR);
    
    if (ret != 0) {
        return -1; // Failed to get policy
    }
    return node;
}
