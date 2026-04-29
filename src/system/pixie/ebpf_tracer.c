#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>

SEC("kprobe/sys_clone")
int bpf_prog1(struct pt_regs *ctx) {
    char fmt[] = "sys_clone called\n";
    bpf_trace_printk(fmt, sizeof(fmt));
    return 0;
}

char _license[] SEC("license") = "GPL";
