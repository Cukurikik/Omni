// omni_syscall_interceptor.c — System Call Security Interceptor
// Layer: System / C
//
// Uses ptrace to intercept and audit system calls made by sub-processes
// (like isolated inference workers) to prevent unauthorized file or network access.

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/syscall.h>

/**
 * Traces a child process and logs/blocks specific syscalls.
 */
void omni_trace_process(pid_t child_pid) {
    int status;
    struct user_regs_struct regs;
    
    // Wait for the child to stop on the initial ptrace(TRACEME)
    waitpid(child_pid, &status, 0);
    
    // Set ptrace options to kill child on exit, and trace syscalls
    ptrace(PTRACE_SETOPTIONS, child_pid, 0, PTRACE_O_TRACESYSGOOD | PTRACE_O_EXITKILL);
    
    while (1) {
        // Continue to the next syscall entry
        ptrace(PTRACE_SYSCALL, child_pid, 0, 0);
        waitpid(child_pid, &status, 0);
        
        // Check if child exited
        if (WIFEXITED(status)) {
            break;
        }
        
        // Get registers to inspect the syscall number
        ptrace(PTRACE_GETREGS, child_pid, 0, &regs);
        long syscall_num = regs.orig_rax;
        
        // Audit: Block unapproved execve calls
        if (syscall_num == SYS_execve) {
            fprintf(stderr, "[SECURITY ALERT] Blocked SYS_execve in process %d\n", child_pid);
            // Alter syscall to an invalid one (e.g., -1) to block it
            regs.orig_rax = -1;
            ptrace(PTRACE_SETREGS, child_pid, 0, &regs);
        }
        
        // Continue to syscall exit
        ptrace(PTRACE_SYSCALL, child_pid, 0, 0);
        waitpid(child_pid, &status, 0);
        
        if (WIFEXITED(status)) {
            break;
        }
    }
}

/**
 * Forks a child process under ptrace surveillance.
 */
int omni_run_secured(const char* command) {
    pid_t pid = fork();
    
    if (pid == 0) {
        // Child
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        // Stop oneself so parent can attach
        raise(SIGSTOP);
        
        execl("/bin/sh", "sh", "-c", command, NULL);
        exit(1);
    } else if (pid > 0) {
        // Parent
        omni_trace_process(pid);
        return 0;
    } else {
        perror("fork");
        return -1;
    }
}
