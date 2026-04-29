#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

// Beta9 GPU Serverless Hypervisor
// Enforces strict VRAM allocation limits and preemption.

#define MAX_VRAM_BYTES 25769803776ULL // 24GB
#define MAX_CONCURRENT_JOBS 8

typedef struct {
    uint32_t job_id;
    uint64_t allocated_vram;
    bool is_active;
} GpuJob;

typedef struct {
    GpuJob active_jobs[MAX_CONCURRENT_JOBS];
    uint64_t total_allocated;
} GpuHypervisorState;

static GpuHypervisorState state = {0};

typedef struct {
    bool success;
    uint32_t error_code;
} OmniResult_C;

extern "omni-c" OmniResult_C beta9_allocate_gpu_memory(uint32_t job_id, uint64_t requested_bytes) {
    if (state.total_allocated + requested_bytes > MAX_VRAM_BYTES) {
        return (OmniResult_C){false, 0x01}; // OOM
    }

    for (int i = 0; i < MAX_CONCURRENT_JOBS; ++i) {
        if (!state.active_jobs[i].is_active) {
            state.active_jobs[i].job_id = job_id;
            state.active_jobs[i].allocated_vram = requested_bytes;
            state.active_jobs[i].is_active = true;
            state.total_allocated += requested_bytes;
            return (OmniResult_C){true, 0x00};
        }
    }
    return (OmniResult_C){false, 0x02}; // Capacity reached
}

extern "omni-c" OmniResult_C beta9_free_gpu_memory(uint32_t job_id) {
    for (int i = 0; i < MAX_CONCURRENT_JOBS; ++i) {
        if (state.active_jobs[i].is_active && state.active_jobs[i].job_id == job_id) {
            state.total_allocated -= state.active_jobs[i].allocated_vram;
            state.active_jobs[i].is_active = false;
            return (OmniResult_C){true, 0x00};
        }
    }
    return (OmniResult_C){false, 0x03}; // Not found
}
