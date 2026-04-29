#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>

// OMNI Ploomber - Zombie Process Reaper
// C daemon logic for cleaning up dead DAG task subprocesses

typedef struct {
    int success;
    const char* error_msg;
    int reaped_count;
} reaper_result_t;

reaper_result_t reap_zombies() {
    reaper_result_t res = {0, NULL, 0};
    int status;
    pid_t child_pid;
    
    // WNOHANG ensures waitpid doesn't block if no children have exited
    while ((child_pid = waitpid(-1, &status, WNOHANG)) > 0) {
        res.reaped_count++;
        // In OMNI, telemetry would be emitted here regarding the exited PID
    }
    
    if (child_pid == -1 && errno != ECHILD) {
        res.error_msg = "waitpid failed with unexpected error";
        return res;
    }
    
    res.success = 1;
    return res;
}

// Function to forcefully terminate a hanging DAG task
reaper_result_t kill_task_group(pid_t pgid) {
    reaper_result_t res = {0, NULL, 0};
    
    if (kill(-pgid, SIGKILL) == -1) {
        res.error_msg = "Failed to kill process group";
        return res;
    }
    
    res.success = 1;
    return res;
}
