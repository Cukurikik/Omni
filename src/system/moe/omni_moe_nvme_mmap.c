#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <stddef.h>

void* omni_moe_mmap_nvme(const char* filepath, size_t size) {
    int fd = open(filepath, O_RDONLY | O_DIRECT);
    if (fd < 0) return NULL;
    void* ptr = mmap(NULL, size, PROT_READ, MAP_PRIVATE | MAP_NORESERVE, fd, 0);
    close(fd);
    return (ptr == MAP_FAILED) ? NULL : ptr;
}
