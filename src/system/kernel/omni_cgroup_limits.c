// omni_cgroup_limits.c — Cgroups v2 Resource Manager
// Layer: System / C
//
// Interacts with the Linux cgroup v2 filesystem to dynamically apply
// CPU and memory limits to isolated OMNI inference worker containers.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

#define CGROUP_BASE "/sys/fs/cgroup/omni_nexus"

/**
 * Ensures the base OMNI cgroup directory exists.
 */
int omni_init_cgroup() {
    struct stat st = {0};
    if (stat(CGROUP_BASE, &st) == -1) {
        if (mkdir(CGROUP_BASE, 0755) != 0) {
            perror("Failed to create base cgroup");
            return -1;
        }
    }
    return 0;
}

/**
 * Creates a cgroup for a specific worker process and limits its memory.
 */
int omni_set_worker_limits(pid_t pid, const char* worker_id, size_t max_memory_mb) {
    char path[256];
    char value[64];
    int fd;

    // 1. Create worker directory
    snprintf(path, sizeof(path), "%s/worker_%s", CGROUP_BASE, worker_id);
    mkdir(path, 0755); // Ignore if exists

    // 2. Set memory limit (cgroup v2: memory.max)
    snprintf(path, sizeof(path), "%s/worker_%s/memory.max", CGROUP_BASE, worker_id);
    fd = open(path, O_WRONLY);
    if (fd >= 0) {
        snprintf(value, sizeof(value), "%zu", max_memory_mb * 1024 * 1024);
        write(fd, value, strlen(value));
        close(fd);
    } else {
        perror("Failed to open memory.max");
        return -1;
    }

    // 3. Attach process to the cgroup
    snprintf(path, sizeof(path), "%s/worker_%s/cgroup.procs", CGROUP_BASE, worker_id);
    fd = open(path, O_WRONLY);
    if (fd >= 0) {
        snprintf(value, sizeof(value), "%d", pid);
        write(fd, value, strlen(value));
        close(fd);
    } else {
        perror("Failed to attach process to cgroup");
        return -1;
    }

    return 0;
}

/**
 * Cleans up a worker's cgroup after it exits.
 */
void omni_cleanup_worker(const char* worker_id) {
    char path[256];
    snprintf(path, sizeof(path), "%s/worker_%s", CGROUP_BASE, worker_id);
    rmdir(path); // Only works if no processes are attached and no child cgroups exist
}
