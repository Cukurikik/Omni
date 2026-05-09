//=============================================================================
// OMNI SYSTEM LAYER — eBPF TELEMETRY (C)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: eBPF kernel module to collect extremely low-overhead telemetry 
//              on network latency and packet drops, fed to the MLOps dashboard.
//=============================================================================

#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <bpf/bpf_helpers.h>

// BPF Map to store metrics
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(max_entries, 2); // 0 = packets processed, 1 = bytes processed
    __type(key, __u32);
    __type(value, __u64);
} omni_telemetry_map SEC(".maps");

SEC("xdp")
int omni_telemetry_filter(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    
    // Boundary check
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;

    __u32 key_pkts = 0;
    __u32 key_bytes = 1;
    
    __u64 *pkts = bpf_map_lookup_elem(&omni_telemetry_map, &key_pkts);
    __u64 *bytes = bpf_map_lookup_elem(&omni_telemetry_map, &key_bytes);

    if (pkts) {
        __sync_fetch_and_add(pkts, 1);
    }
    
    if (bytes) {
        __u64 pkt_len = (__u64)(data_end - data);
        __sync_fetch_and_add(bytes, pkt_len);
    }

    return XDP_PASS;
}

char _license[] SEC("license") = "Dual MIT/GPL";
