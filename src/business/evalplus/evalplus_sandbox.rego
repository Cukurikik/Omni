# EvalPlus execution sandbox policy
# Rego policy for sys-calls

package evalplus.sandbox

default allow = false

# Bound: Only allow specific safe syscalls
safe_syscalls = {"read", "write", "open", "close", "brk", "mmap", "munmap", "exit", "exit_group"}

allow {
    input.syscall == safe_syscalls[_]
}

deny {
    input.syscall == "execve" # Prevent shell breakouts
}
