#include <stdlib.h>

typedef struct {
    void* ptr;
    size_t size;
} OmniAllocResult;

OmniAllocResult allocate_opengpt_memory(size_t size) {
    OmniAllocResult res;
    if (size == 0) {
        res.ptr = NULL;
        res.size = 0;
        return res;
    }
    res.ptr = malloc(size);
    res.size = size;
    return res;
}
