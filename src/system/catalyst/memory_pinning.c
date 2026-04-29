#include <stdlib.h>
#include <sys/mman.h>

extern "C" {
    void* allocate_pinned_memory(size_t size) {
        void* ptr = malloc(size);
        if (ptr) {
            mlock(ptr, size);
        }
        return ptr;
    }

    void free_pinned_memory(void* ptr, size_t size) {
        if (ptr) {
            munlock(ptr, size);
            free(ptr);
        }
    }
}
