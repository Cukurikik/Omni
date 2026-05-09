#ifndef OMNI_NVLINK_MONITOR_H
#define OMNI_NVLINK_MONITOR_H

#include <stdint.h>

// OMNI MOTHER: NVLink Telemetry API
// Zero-mock hardware abstraction for fetching real-time NVLink bandwidth.
// Used by the Go router to determine if expert offloading is viable.

typedef struct {
    uint32_t device_id;
    uint32_t link_id;
    uint64_t tx_bytes;
    uint64_t rx_bytes;
    uint32_t link_status; // 1 = Active, 0 = Down
} OmniNVLinkMetrics;

typedef void* OmniNVMLContext;

#ifdef __cplusplus
extern "C" {
#endif

OmniNVMLContext omni_nvlink_init();
int omni_nvlink_get_metrics(OmniNVMLContext ctx, uint32_t device_idx, uint32_t link_idx, OmniNVLinkMetrics* out_metrics);
void omni_nvlink_shutdown(OmniNVMLContext ctx);

#ifdef __cplusplus
}
#endif

#endif // OMNI_NVLINK_MONITOR_H
