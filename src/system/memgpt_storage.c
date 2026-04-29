#include <stdlib.h>

typedef struct {
    int ok;
    void* block;
} MemResult;

MemResult alloc_storage(int size) {
    if (size <= 0) return (MemResult){0, NULL};
    return (MemResult){1, malloc(size)};
}
