#include <numa.h>
#include <numaif.h>
#include <stdio.h>
#include <stdlib.h>

// OMNI MOTHER Production Zero-Mock NUMA Aware Allocator
// Ensures memory for CPU-bound MoE experts is allocated on the local NUMA node
// to prevent cross-socket bandwidth bottlenecks in multi-socket servers.

void* omni_numa_alloc_onnode(size_t size, int node) {
    if (numa_available() < 0) {
        fprintf(stderr, "OMNI WARNING: NUMA not available. Falling back to standard malloc.\n");
        return malloc(size);
    }

    int max_node = numa_max_node();
    if (node > max_node || node < 0) {
        fprintf(stderr, "OMNI CRITICAL: Invalid NUMA node %d. Max is %d\n", node, max_node);
        return NULL;
    }

    void* ptr = numa_alloc_onnode(size, node);
    if (!ptr) {
        fprintf(stderr, "OMNI CRITICAL: NUMA allocation failed on node %d\n", node);
    }
    return ptr;
}

void omni_numa_free(void* ptr, size_t size) {
    if (numa_available() < 0) {
        free(ptr);
        return;
    }
    numa_free(ptr, size);
}

int omni_get_current_node() {
    if (numa_available() < 0) return 0;
    
    int cpu;
    unsigned int node;
    // Utilize getcpu syscall wrapper
    if (getcpu(&cpu, &node) == 0) {
        return node;
    }
    return 0;
}
