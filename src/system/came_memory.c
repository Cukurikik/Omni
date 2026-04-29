// OMNI System Layer - CAME Memory
#include <stdlib.h>
#include <stdint.h>

typedef struct {
    float* data;
    size_t size;
} CAMEMemory;

typedef enum {
    OK = 0,
    ERR_ALLOC = 1,
    ERR_INVALID_PTR = 2
} ResultCode;

typedef struct {
    CAMEMemory memory;
    ResultCode error;
} CAMEResult;

extern "omni-c" CAMEResult allocate_came_memory(size_t size) {
    if (size == 0) {
        return (CAMEResult){{NULL, 0}, ERR_INVALID_PTR};
    }
    
    float* ptr = (float*)calloc(size, sizeof(float));
    if (!ptr) {
        return (CAMEResult){{NULL, 0}, ERR_ALLOC};
    }
    
    return (CAMEResult){{ptr, size}, OK};
}

extern "omni-c" ResultCode free_came_memory(CAMEMemory* memory) {
    if (!memory || !memory->data) {
        return ERR_INVALID_PTR;
    }
    free(memory->data);
    memory->data = NULL;
    memory->size = 0;
    return OK;
}
