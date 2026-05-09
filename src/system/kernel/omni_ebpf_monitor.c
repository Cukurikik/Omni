// omni_ebpf_monitor.c — Kernel Network Latency Monitor
// Layer: System / eBPF
//
// Attaches to kernel tracepoints to monitor network packet latencies
// with zero overhead, feeding telemetry to the OMNI fault supervisor.

#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10240);
    __type(key, __u32); // Source IP
    __type(value, __u64); // Timestamp
} packet_timestamps SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(__u32));
    __uint(value_size, sizeof(__u32));
} events SEC(".maps");

struct event_t {
    __u32 src_ip;
    __u32 dst_ip;
    __u64 latency_ns;
};

SEC("tracepoint/net/netif_receive_skb")
int trace_packet_receive(struct pt_regs *ctx) {
    __u64 ts = bpf_ktime_get_ns();
    
    // Mock parsing of IP header (in practice requires skb parsing)
    __u32 src_ip = 0x0100007f; // 127.0.0.1
    __u32 dst_ip = 0x0100007f;
    
    bpf_map_update_elem(&packet_timestamps, &src_ip, &ts, BPF_ANY);
    
    return 0;
}

SEC("tracepoint/net/net_dev_queue")
int trace_packet_transmit(struct pt_regs *ctx) {
    __u32 src_ip = 0x0100007f;
    __u64 *start_ts = bpf_map_lookup_elem(&packet_timestamps, &src_ip);
    
    if (start_ts) {
        __u64 end_ts = bpf_ktime_get_ns();
        struct event_t event = {};
        event.src_ip = src_ip;
        event.dst_ip = 0;
        event.latency_ns = end_ts - *start_ts;
        
        bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU, &event, sizeof(event));
        bpf_map_delete_elem(&packet_timestamps, &src_ip);
    }
    
    return 0;
}

char _license[] SEC("license") = "GPL";
