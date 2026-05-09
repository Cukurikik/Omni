#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

/*
 * OMNI MOTHER Production Zero-Mock mmap Tensor Loader
 * C Implementation for zero-copy loading of multi-gigabyte safetensor weights
 * directly from NVMe into unified memory space.
 */

typedef struct {
    void* data;
    size_t size;
    int fd;
} OmniMappedTensor;

OmniMappedTensor* omni_mmap_tensor_load(const char* filepath) {
    OmniMappedTensor* tensor = (OmniMappedTensor*)malloc(sizeof(OmniMappedTensor));
    if (!tensor) return NULL;

    tensor->fd = open(filepath, O_RDONLY);
    if (tensor->fd < 0) {
        perror("OMNI CRITICAL: Failed to open tensor file");
        free(tensor);
        return NULL;
    }

    struct stat st;
    if (fstat(tensor->fd, &st) < 0) {
        perror("OMNI CRITICAL: Failed to stat tensor file");
        close(tensor->fd);
        free(tensor);
        return NULL;
    }
    
    tensor->size = st.st_size;

    // MAP_SHARED | MAP_POPULATE ensures pages are prefetched for max throughput
    tensor->data = mmap(NULL, tensor->size, PROT_READ, MAP_SHARED | MAP_POPULATE, tensor->fd, 0);
    if (tensor->data == MAP_FAILED) {
        perror("OMNI CRITICAL: Failed to mmap tensor");
        close(tensor->fd);
        free(tensor);
        return NULL;
    }

    return tensor;
}

void omni_mmap_tensor_free(OmniMappedTensor* tensor) {
    if (tensor) {
        if (tensor->data && tensor->data != MAP_FAILED) {
            munmap(tensor->data, tensor->size);
        }
        if (tensor->fd >= 0) {
            close(tensor->fd);
        }
        free(tensor);
    }
}
