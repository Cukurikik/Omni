// moe_memory_mapped_weights.c — System / Storage
// Layer: System / OS — MoE Weight Loading
//
// Fast loading of MoE experts using mmap(). Allows the OS to page in
// expert weights directly from NVMe to memory bypassing standard read() calls,
// preventing RAM spikes and drastically speeding up cold-starts.

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

typedef enum {
    MMAP_OK = 0,
    MMAP_ERR_FILE = -1,
    MMAP_ERR_FSTAT = -2,
    MMAP_ERR_MAP = -3
} MmapResult;

typedef struct {
    void* data;
    size_t size;
    int fd;
} MappedExpert;

/**
 * Maps an expert's weight file directly into virtual memory.
 */
MmapResult omni_mmap_expert(const char* filepath, MappedExpert* out_expert) {
    if (!filepath || !out_expert) return MMAP_ERR_FILE;

    out_expert->fd = open(filepath, O_RDONLY);
    if (out_expert->fd < 0) {
        return MMAP_ERR_FILE;
    }

    struct stat sb;
    if (fstat(out_expert->fd, &sb) < 0) {
        close(out_expert->fd);
        return MMAP_ERR_FSTAT;
    }
    out_expert->size = sb.st_size;

    // Map file into memory. MAP_SHARED allows OS page cache usage.
    out_expert->data = mmap(NULL, out_expert->size, PROT_READ, MAP_SHARED, out_expert->fd, 0);
    if (out_expert->data == MAP_FAILED) {
        close(out_expert->fd);
        return MMAP_ERR_MAP;
    }

    // Advise the kernel that we will access this data sequentially or need it soon.
    madvise(out_expert->data, out_expert->size, MADV_WILLNEED);

    return MMAP_OK;
}

/**
 * Unmaps an expert from memory.
 */
void omni_munmap_expert(MappedExpert* expert) {
    if (!expert) return;

    if (expert->data && expert->data != MAP_FAILED) {
        // Advise kernel we are done to free up page cache
        madvise(expert->data, expert->size, MADV_DONTNEED);
        munmap(expert->data, expert->size);
    }

    if (expert->fd >= 0) {
        close(expert->fd);
    }

    expert->data = NULL;
    expert->size = 0;
    expert->fd = -1;
}

/**
 * Prefetches the mapped data into physical RAM.
 * Useful for hiding latency before the GPU attempts to transfer it.
 */
void omni_mmap_prefetch(MappedExpert* expert) {
    if (!expert || !expert->data) return;
    
    // Touching each page forces the OS to fault it into physical memory
    volatile char* ptr = (volatile char*)expert->data;
    size_t page_size = sysconf(_SC_PAGESIZE);
    
    for (size_t i = 0; i < expert->size; i += page_size) {
        char force_fault = ptr[i];
        (void)force_fault;
    }
}
