#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>

// OMNI Ploomber - System Layer CGroup Limiter
// Enforces hard memory limits on DAG tasks using cgroups v2

typedef struct {
    int success;
    const char* error;
} cgroup_result_t;

cgroup_result_t enforce_memory_limit(const char* cgroup_name, pid_t pid, size_t memory_limit_bytes) {
    cgroup_result_t res = {0, NULL};
    char path[256];
    
    // Create cgroup directory
    snprintf(path, sizeof(path), "/sys/fs/cgroup/%s", cgroup_name);
    if (mkdir(path, 0755) != 0) {
        // If it exists, we can still use it, otherwise check error.
        // Simplifying for brevity, assuming existence or creation.
    }

    // Write memory limit
    char mem_limit_path[256];
    snprintf(mem_limit_path, sizeof(mem_limit_path), "%s/memory.max", path);
    FILE* f_mem = fopen(mem_limit_path, "w");
    if (!f_mem) {
        res.error = "Failed to open memory.max";
        return res;
    }
    fprintf(f_mem, "%zu\n", memory_limit_bytes);
    fclose(f_mem);

    // Assign PID
    char cgroup_procs_path[256];
    snprintf(cgroup_procs_path, sizeof(cgroup_procs_path), "%s/cgroup.procs", path);
    FILE* f_procs = fopen(cgroup_procs_path, "w");
    if (!f_procs) {
        res.error = "Failed to open cgroup.procs";
        return res;
    }
    fprintf(f_procs, "%d\n", pid);
    fclose(f_procs);

    res.success = 1;
    return res;
}
