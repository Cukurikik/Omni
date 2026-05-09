#ifndef OMNI_MOE_NUMA_BALANCER_H
#define OMNI_MOE_NUMA_BALANCER_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * OMNI Framework - NUMA Memory Balancer
 * Ensures that CPU threads managing specific GPUs (and their MoE experts) 
 * are pinned to the correct NUMA node, minimizing PCIe cross-talk latency.
 */

// Initialize NUMA library and check availability
int omni_numa_init();

// Bind the current calling thread to the NUMA node closest to the given GPU
int omni_numa_bind_thread_to_gpu(int gpu_id);

// Allocate memory strictly on the NUMA node closest to the given GPU
void* omni_numa_alloc_on_gpu_node(size_t size, int gpu_id);

// Free NUMA-allocated memory
void omni_numa_free(void* ptr, size_t size);

#ifdef __cplusplus
}
#endif

#endif // OMNI_MOE_NUMA_BALANCER_H
