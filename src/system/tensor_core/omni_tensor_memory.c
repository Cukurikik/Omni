// OMNI System Layer — C Bare-Metal Tensor Memory Manager
// Direct memory management for transformer weight buffers.
// Zero-copy mmap-based weight loading for inference.

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <sys/types.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#endif

// Alignment for SIMD operations (AVX-512 = 64 bytes)
#define OMNI_TENSOR_ALIGN 64
#define OMNI_PAGE_SIZE 4096

typedef enum {
    OMNI_DTYPE_F32 = 0,
    OMNI_DTYPE_F16 = 1,
    OMNI_DTYPE_BF16 = 2,
    OMNI_DTYPE_INT8 = 3,
    OMNI_DTYPE_INT4 = 4,
} omni_dtype_t;

typedef struct {
    void*       data;
    size_t      size_bytes;
    size_t      numel;
    int         ndim;
    int64_t     shape[8];
    int64_t     strides[8];
    omni_dtype_t dtype;
    int         is_mmap;
    int         ref_count;
} omni_tensor_t;

static size_t omni_dtype_size(omni_dtype_t dtype) {
    switch (dtype) {
        case OMNI_DTYPE_F32:  return 4;
        case OMNI_DTYPE_F16:  return 2;
        case OMNI_DTYPE_BF16: return 2;
        case OMNI_DTYPE_INT8: return 1;
        case OMNI_DTYPE_INT4: return 1; // packed 2 per byte
        default: return 4;
    }
}

// Allocate aligned tensor buffer
omni_tensor_t* omni_tensor_alloc(const int64_t* shape, int ndim, omni_dtype_t dtype) {
    if (ndim <= 0 || ndim > 8) return NULL;

    omni_tensor_t* t = (omni_tensor_t*)calloc(1, sizeof(omni_tensor_t));
    if (!t) return NULL;

    t->ndim = ndim;
    t->dtype = dtype;
    t->numel = 1;
    for (int i = 0; i < ndim; i++) {
        t->shape[i] = shape[i];
        t->numel *= (size_t)shape[i];
    }

    // Compute strides (row-major)
    t->strides[ndim - 1] = 1;
    for (int i = ndim - 2; i >= 0; i--) {
        t->strides[i] = t->strides[i + 1] * shape[i + 1];
    }

    t->size_bytes = t->numel * omni_dtype_size(dtype);

    // Aligned allocation
#ifdef _WIN32
    t->data = _aligned_malloc(t->size_bytes, OMNI_TENSOR_ALIGN);
#else
    if (posix_memalign(&t->data, OMNI_TENSOR_ALIGN, t->size_bytes) != 0) {
        free(t);
        return NULL;
    }
#endif

    if (!t->data) {
        free(t);
        return NULL;
    }

    memset(t->data, 0, t->size_bytes);
    t->is_mmap = 0;
    t->ref_count = 1;
    return t;
}

// Memory-mapped tensor loading (zero-copy from disk)
omni_tensor_t* omni_tensor_mmap(const char* filepath, const int64_t* shape,
                                 int ndim, omni_dtype_t dtype, size_t offset) {
    omni_tensor_t* t = (omni_tensor_t*)calloc(1, sizeof(omni_tensor_t));
    if (!t) return NULL;

    t->ndim = ndim;
    t->dtype = dtype;
    t->numel = 1;
    for (int i = 0; i < ndim; i++) {
        t->shape[i] = shape[i];
        t->numel *= (size_t)shape[i];
    }
    t->strides[ndim - 1] = 1;
    for (int i = ndim - 2; i >= 0; i--) {
        t->strides[i] = t->strides[i + 1] * shape[i + 1];
    }
    t->size_bytes = t->numel * omni_dtype_size(dtype);

#ifdef _WIN32
    HANDLE hFile = CreateFileA(filepath, GENERIC_READ, FILE_SHARE_READ,
                               NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) { free(t); return NULL; }
    HANDLE hMap = CreateFileMappingA(hFile, NULL, PAGE_READONLY, 0, 0, NULL);
    if (!hMap) { CloseHandle(hFile); free(t); return NULL; }
    t->data = (char*)MapViewOfFile(hMap, FILE_MAP_READ, 0, (DWORD)offset, t->size_bytes) ;
    CloseHandle(hMap);
    CloseHandle(hFile);
#else
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) { free(t); return NULL; }
    t->data = mmap(NULL, t->size_bytes + offset, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    if (t->data == MAP_FAILED) { free(t); return NULL; }
    t->data = (char*)t->data + offset;
#endif

    if (!t->data) { free(t); return NULL; }
    t->is_mmap = 1;
    t->ref_count = 1;
    return t;
}

// Free tensor
void omni_tensor_free(omni_tensor_t* t) {
    if (!t) return;
    t->ref_count--;
    if (t->ref_count > 0) return;

    if (t->data) {
        if (t->is_mmap) {
#ifdef _WIN32
            UnmapViewOfFile(t->data);
#else
            munmap(t->data, t->size_bytes);
#endif
        } else {
#ifdef _WIN32
            _aligned_free(t->data);
#else
            free(t->data);
#endif
        }
    }
    free(t);
}

// F32 softmax in-place
void omni_softmax_f32(float* data, int n) {
    float max_val = data[0];
    for (int i = 1; i < n; i++) {
        if (data[i] > max_val) max_val = data[i];
    }
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        data[i] = expf(data[i] - max_val);
        sum += data[i];
    }
    float inv = 1.0f / sum;
    for (int i = 0; i < n; i++) {
        data[i] *= inv;
    }
}

// F32 RMS normalization in-place
void omni_rmsnorm_f32(float* out, const float* x, const float* weight, int n, float eps) {
    float ss = 0.0f;
    for (int i = 0; i < n; i++) {
        ss += x[i] * x[i];
    }
    ss = 1.0f / sqrtf(ss / (float)n + eps);
    for (int i = 0; i < n; i++) {
        out[i] = x[i] * ss * weight[i];
    }
}

// Quantize f32 -> int8 (per-tensor symmetric)
void omni_quantize_f32_i8(const float* src, int8_t* dst, int n, float* scale) {
    float amax = 0.0f;
    for (int i = 0; i < n; i++) {
        float v = fabsf(src[i]);
        if (v > amax) amax = v;
    }
    *scale = amax / 127.0f;
    float inv = (*scale > 0.0f) ? 127.0f / amax : 0.0f;
    for (int i = 0; i < n; i++) {
        int v = (int)roundf(src[i] * inv);
        if (v > 127) v = 127;
        if (v < -127) v = -127;
        dst[i] = (int8_t)v;
    }
}
