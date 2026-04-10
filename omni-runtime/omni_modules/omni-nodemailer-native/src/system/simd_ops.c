#include <string.h>
#include <stdlib.h>

void omni_nodemailer_native_memcpy_avx(void* dst, const void* src, size_t n) {
    memcpy(dst, src, n);
}

int omni_nodemailer_native_memcmp_fast(const void* a, const void* b, size_t n) {
    return memcmp(a, b, n);
}

void omni_nodemailer_native_memset_zero(void* ptr, size_t n) { memset(ptr, 0, n); }

size_t omni_nodemailer_native_strlen_simd(const char* s) { return strlen(s); }

void* omni_nodemailer_native_aligned_alloc(size_t alignment, size_t size) {
    void* ptr = NULL;
    #ifdef _WIN32
    ptr = _aligned_malloc(size, alignment);
    #else
    posix_memalign(&ptr, alignment, size);
    #endif
    return ptr;
}

void omni_nodemailer_native_aligned_free(void* ptr) {
    #ifdef _WIN32
    _aligned_free(ptr);
    #else
    free(ptr);
    #endif
}