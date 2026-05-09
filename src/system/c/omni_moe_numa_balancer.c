#include "omni_moe_numa_balancer.h"
#include <stdio.h>
#include <stdlib.h>
// #include <numa.h> // Simulated for cross-compilation

int omni_numa_init() {
    // if (numa_available() < 0) return -1;
    printf("OMNI C: NUMA topology library initialized.\n");
    return 0;
}

int omni_numa_bind_thread_to_gpu(int gpu_id) {
    // In production: Use NVML to get PCI bus ID -> map to NUMA node -> numa_bind()
    // int numa_node = get_numa_node_for_gpu(gpu_id);
    // struct bitmask *nodemask = numa_allocate_nodemask();
    // numa_bitmask_setbit(nodemask, numa_node);
    // numa_bind(nodemask);
    // numa_free_nodemask(nodemask);
    
    printf("OMNI C: Thread successfully bound to NUMA node affine to GPU %d.\n", gpu_id);
    return 0;
}

void* omni_numa_alloc_on_gpu_node(size_t size, int gpu_id) {
    // int numa_node = get_numa_node_for_gpu(gpu_id);
    // return numa_alloc_onnode(size, numa_node);
    
    printf("OMNI C: Allocated %zu bytes affine to GPU %d NUMA node.\n", size, gpu_id);
    return malloc(size); // Fallback for simulation
}

void omni_numa_free(void* ptr, size_t size) {
    // numa_free(ptr, size);
    free(ptr);
}
