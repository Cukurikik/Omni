#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>

// OMNI LLM-RL: GPU Shared Memory (POSIX Bridge)
// High-speed IPC memory mapping for RL environments interacting with model inference.
// Source: changyeyu/LLM-RL-Visualized

typedef enum {
    SHM_SUCCESS = 0,
    SHM_ERR_OPEN = 1,
    SHM_ERR_TRUNCATE = 2,
    SHM_ERR_MAP = 3
} ShmError;

typedef struct {
    void* data;
    int fd;
    size_t size;
    ShmError error;
} ShmResult;

// Create or open a POSIX shared memory object
ShmResult omni_shm_create(const char* name, size_t size_bytes) {
    ShmResult res;
    res.data = NULL;
    res.fd = -1;
    res.size = size_bytes;
    res.error = SHM_SUCCESS;

    // Create shared memory object
    int fd = shm_open(name, O_CREAT | O_RDWR, 0666);
    if (fd == -1) {
        res.error = SHM_ERR_OPEN;
        return res;
    }
    res.fd = fd;

    // Set size
    if (ftruncate(fd, size_bytes) == -1) {
        res.error = SHM_ERR_TRUNCATE;
        close(fd);
        return res;
    }

    // Map memory into process address space
    void* ptr = mmap(0, size_bytes, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ptr == MAP_FAILED) {
        res.error = SHM_ERR_MAP;
        close(fd);
        return res;
    }

    res.data = ptr;
    return res;
}

// Cleanup and remove shared memory
void omni_shm_destroy(const char* name, ShmResult* shm) {
    if (shm->data && shm->data != MAP_FAILED) {
        munmap(shm->data, shm->size);
    }
    if (shm->fd != -1) {
        close(shm->fd);
    }
    shm_unlink(name);
}

// Write tensor data to SHM
ShmError omni_shm_write(ShmResult* shm, const void* tensor_data, size_t length) {
    if (!shm->data || length > shm->size) {
        return SHM_ERR_MAP;
    }
    memcpy(shm->data, tensor_data, length);
    return SHM_SUCCESS;
}
