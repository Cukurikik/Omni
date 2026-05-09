#ifndef OMNI_MOE_NVLINK_MONITOR_H
#define OMNI_MOE_NVLINK_MONITOR_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * OMNI Framework - NVLink Bandwidth Monitor
 * Monitors real-time NVLink Tx/Rx bandwidth to ensure MoE All-to-All 
 * communications are not bottlenecked by interconnect saturation.
 */

typedef struct {
    int gpu_id;
    double tx_bandwidth_gbps;
    double rx_bandwidth_gbps;
    int link_count;
    int is_bottlenecked;
} NVLinkStats;

// Initialize the NVML library
int omni_nvlink_init();

// Fetch statistics for a specific GPU
NVLinkStats omni_nvlink_get_stats(int gpu_id);

// Shutdown NVML
void omni_nvlink_shutdown();

#ifdef __cplusplus
}
#endif

#endif // OMNI_MOE_NVLINK_MONITOR_H
