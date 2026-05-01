//go:build ignore
// +build ignore

#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

// eBPF map for logging unauthorized syscall attempts to userspace
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); // 256 KB ring buffer
} audit_events SEC(".maps");

struct audit_event_t {
    __u32 pid;
    __u32 uid;
    __u32 syscall_id;
    char comm[16];
};

// OMNI MOTHER SYSTEM - Kernel Space Syscall Auditor
// Traces the sys_enter tracepoint. 
// Protects the Omni container environment from container escape attempts.

SEC("tracepoint/raw_syscalls/sys_enter")
int omni_audit_syscall(struct bpf_raw_tracepoint_args *ctx) {
    __u32 syscall_id = ctx->args[1];

    // Filter for sensitive syscalls indicating potential privilege escalation or escape
    // 101: ptrace
    // 164: setresuid
    // 322: execveat
    // 59: execve
    // 165: mount
    if (syscall_id != 101 && syscall_id != 164 && 
        syscall_id != 322 && syscall_id != 59 && syscall_id != 165) {
        return 0; // Ignore benign syscalls
    }

    // Capture context
    __u64 pid_tgid = bpf_get_current_pid_tgid();
    __u32 pid = pid_tgid >> 32;
    __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;

    // Reserve space in ring buffer
    struct audit_event_t *event = bpf_ringbuf_reserve(&audit_events, sizeof(*event), 0);
    if (!event) {
        return 0; // Ringbuffer full, fail open safely
    }

    event->pid = pid;
    event->uid = uid;
    event->syscall_id = syscall_id;
    bpf_get_current_comm(&event->comm, sizeof(event->comm));

    // Submit event to userspace (Go/Rust security monitor)
    bpf_ringbuf_submit(event, 0);

    return 0;
}

char _license[] SEC("license") = "GPL";
