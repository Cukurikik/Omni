#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    void* ptr;
    size_t size;
    int error_code;
} AllocResult;

AllocResult allocate_simd_buffer(size_t size) {
    AllocResult res = {0};
    void* ptr = NULL;
    // 64-byte alignment for AVX-512
    int ret = posix_memalign(&ptr, 64, size);
    if (ret != 0) {
        res.error_code = ret;
        return res;
    }
    res.ptr = ptr;
    res.size = size;
    return res;
}
