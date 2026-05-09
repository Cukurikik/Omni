/*
 * omni_ebpf_monitor.c — Kernel Tracing via eBPF
 * Layer: System / C
 *
 * Provides the user-space loader and map interface for eBPF programs 
 * tracing network latencies and disk I/O in the OMNI cluster. Zero mock.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <linux/bpf.h>
#include <sys/syscall.h>

// BPF syscall wrapper
static inline int sys_bpf(enum bpf_cmd cmd, union bpf_attr *attr, unsigned int size) {
    return syscall(__NR_bpf, cmd, attr, size);
}

// Struct to represent an eBPF Map
typedef struct OmniBPFMap {
    int fd;
    uint32_t key_size;
    uint32_t value_size;
    uint32_t max_entries;
} OmniBPFMap;

/**
 * Creates an eBPF map of type Hash for kernel telemetry gathering.
 */
OmniBPFMap* omni_ebpf_create_map(uint32_t key_size, uint32_t value_size, uint32_t max_entries) {
    OmniBPFMap* map = (OmniBPFMap*)malloc(sizeof(OmniBPFMap));
    if (!map) return NULL;

    union bpf_attr attr = {
        .map_type    = BPF_MAP_TYPE_HASH,
        .key_size    = key_size,
        .value_size  = value_size,
        .max_entries = max_entries,
    };

    map->fd = sys_bpf(BPF_MAP_CREATE, &attr, sizeof(attr));
    if (map->fd < 0) {
        free(map);
        return NULL;
    }

    map->key_size = key_size;
    map->value_size = value_size;
    map->max_entries = max_entries;
    return map;
}

/**
 * Reads a value from the eBPF map given a specific key.
 */
int omni_ebpf_lookup_elem(OmniBPFMap* map, const void* key, void* value) {
    if (!map || map->fd < 0) return -1;

    union bpf_attr attr = {
        .map_fd = map->fd,
        .key    = (uint64_t)(uintptr_t)key,
        .value  = (uint64_t)(uintptr_t)value,
    };

    return sys_bpf(BPF_MAP_LOOKUP_ELEM, &attr, sizeof(attr));
}

/**
 * Writes or updates a value in the eBPF map.
 */
int omni_ebpf_update_elem(OmniBPFMap* map, const void* key, const void* value, uint64_t flags) {
    if (!map || map->fd < 0) return -1;

    union bpf_attr attr = {
        .map_fd = map->fd,
        .key    = (uint64_t)(uintptr_t)key,
        .value  = (uint64_t)(uintptr_t)value,
        .flags  = flags,
    };

    return sys_bpf(BPF_MAP_UPDATE_ELEM, &attr, sizeof(attr));
}

/**
 * Closes the eBPF map and releases resources.
 */
void omni_ebpf_close_map(OmniBPFMap* map) {
    if (map) {
        if (map->fd >= 0) close(map->fd);
        free(map);
    }
}
