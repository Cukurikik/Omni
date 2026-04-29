#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct {
    void* ptr;
    const char* error;
    int is_ok;
} OmniResultPtr;

OmniResultPtr longmem_allocate_page(size_t size_bytes) {
    if (size_bytes == 0 || size_bytes > 1024L * 1024L * 1024L) { // Max 1GB per page
        return (OmniResultPtr){NULL, "Invalid allocation size", 0};
    }
    
    void* ptr = malloc(size_bytes);
    if (!ptr) {
        return (OmniResultPtr){NULL, "Out of memory", 0};
    }
    
    memset(ptr, 0, size_bytes);
    return (OmniResultPtr){ptr, NULL, 1};
}

OmniResultPtr longmem_free_page(void* ptr) {
    if (!ptr) {
        return (OmniResultPtr){NULL, "Null pointer free attempt", 0};
    }
    free(ptr);
    return (OmniResultPtr){NULL, NULL, 1};
}
