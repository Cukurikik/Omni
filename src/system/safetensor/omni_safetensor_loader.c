// omni_safetensor_loader.c — SafeTensors Binary Loader
// Inspired by: HuggingFace safetensors format for model weights
// Layer: System / C
//
// Zero-copy memory-mapped loader for .safetensors model files.
// Supports fp32, fp16, bf16, int8 tensor dtypes.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#endif

typedef enum {
    DTYPE_F32 = 0,
    DTYPE_F16 = 1,
    DTYPE_BF16 = 2,
    DTYPE_I8 = 3,
    DTYPE_I32 = 4,
    DTYPE_I64 = 5,
    DTYPE_BOOL = 6,
    DTYPE_UNKNOWN = 255
} OmniDType;

typedef struct {
    char name[256];
    OmniDType dtype;
    int64_t shape[8];
    int32_t ndim;
    int64_t data_offset;
    int64_t data_length;
    int64_t num_elements;
} TensorMeta;

typedef struct {
    TensorMeta* tensors;
    int32_t num_tensors;
    int32_t capacity;
    uint8_t* data_region;
    int64_t data_region_size;
    int64_t header_size;
    // Memory mapping handles
    void* file_mapping;
    int64_t file_size;
    bool is_mapped;
} SafeTensorFile;

static int64_t dtype_size(OmniDType dtype) {
    switch (dtype) {
        case DTYPE_F32:  return 4;
        case DTYPE_F16:  return 2;
        case DTYPE_BF16: return 2;
        case DTYPE_I8:   return 1;
        case DTYPE_I32:  return 4;
        case DTYPE_I64:  return 8;
        case DTYPE_BOOL: return 1;
        default:         return 0;
    }
}

static OmniDType parse_dtype(const char* dtype_str) {
    if (strcmp(dtype_str, "F32") == 0)  return DTYPE_F32;
    if (strcmp(dtype_str, "F16") == 0)  return DTYPE_F16;
    if (strcmp(dtype_str, "BF16") == 0) return DTYPE_BF16;
    if (strcmp(dtype_str, "I8") == 0)   return DTYPE_I8;
    if (strcmp(dtype_str, "I32") == 0)  return DTYPE_I32;
    if (strcmp(dtype_str, "I64") == 0)  return DTYPE_I64;
    if (strcmp(dtype_str, "BOOL") == 0) return DTYPE_BOOL;
    return DTYPE_UNKNOWN;
}

SafeTensorFile* omni_safetensor_create(void) {
    SafeTensorFile* sf = (SafeTensorFile*)calloc(1, sizeof(SafeTensorFile));
    if (!sf) return NULL;

    sf->capacity = 64;
    sf->tensors = (TensorMeta*)calloc(sf->capacity, sizeof(TensorMeta));
    if (!sf->tensors) { free(sf); return NULL; }

    sf->num_tensors = 0;
    sf->is_mapped = false;
    return sf;
}

static int add_tensor_meta(SafeTensorFile* sf, const TensorMeta* meta) {
    if (sf->num_tensors >= sf->capacity) {
        int new_cap = sf->capacity * 2;
        TensorMeta* new_tensors = (TensorMeta*)realloc(sf->tensors,
            new_cap * sizeof(TensorMeta));
        if (!new_tensors) return -1;
        sf->tensors = new_tensors;
        sf->capacity = new_cap;
    }
    sf->tensors[sf->num_tensors++] = *meta;
    return 0;
}

// Simple JSON-like header parser (production: use proper JSON parser)
int omni_safetensor_parse_header(SafeTensorFile* sf, const char* header, int64_t header_len) {
    const char* pos = header;
    const char* end = header + header_len;

    while (pos < end) {
        // Find tensor name (between quotes)
        const char* name_start = strchr(pos, '"');
        if (!name_start || name_start >= end) break;
        name_start++;

        const char* name_end = strchr(name_start, '"');
        if (!name_end || name_end >= end) break;

        TensorMeta meta;
        memset(&meta, 0, sizeof(meta));
        int name_len = (int)(name_end - name_start);
        if (name_len > 255) name_len = 255;
        strncpy(meta.name, name_start, name_len);
        meta.name[name_len] = '\0';

        // Skip metadata key "__metadata__"
        if (strcmp(meta.name, "__metadata__") == 0) {
            pos = name_end + 1;
            // Skip the value
            int brace_count = 0;
            while (pos < end) {
                if (*pos == '{') brace_count++;
                if (*pos == '}') {
                    brace_count--;
                    if (brace_count <= 0) { pos++; break; }
                }
                pos++;
            }
            continue;
        }

        // Find dtype
        const char* dtype_key = strstr(name_end, "\"dtype\"");
        if (!dtype_key || dtype_key >= end) { pos = name_end + 1; continue; }

        const char* dtype_val_start = strchr(dtype_key + 7, '"');
        if (!dtype_val_start) { pos = name_end + 1; continue; }
        dtype_val_start++;

        const char* dtype_val_end = strchr(dtype_val_start, '"');
        if (!dtype_val_end) { pos = name_end + 1; continue; }

        char dtype_str[16] = {0};
        int dtype_len = (int)(dtype_val_end - dtype_val_start);
        if (dtype_len > 15) dtype_len = 15;
        strncpy(dtype_str, dtype_val_start, dtype_len);
        meta.dtype = parse_dtype(dtype_str);

        // Find shape
        const char* shape_key = strstr(dtype_val_end, "\"shape\"");
        if (shape_key && shape_key < end) {
            const char* arr_start = strchr(shape_key, '[');
            const char* arr_end = strchr(shape_key, ']');
            if (arr_start && arr_end && arr_start < arr_end) {
                meta.ndim = 0;
                meta.num_elements = 1;
                const char* num_pos = arr_start + 1;
                while (num_pos < arr_end && meta.ndim < 8) {
                    while (num_pos < arr_end && (*num_pos == ' ' || *num_pos == ','))
                        num_pos++;
                    if (num_pos >= arr_end) break;
                    int64_t val = strtoll(num_pos, (char**)&num_pos, 10);
                    meta.shape[meta.ndim++] = val;
                    meta.num_elements *= val;
                }
            }
        }

        // Find data_offsets
        const char* offsets_key = strstr(dtype_val_end, "\"data_offsets\"");
        if (offsets_key && offsets_key < end) {
            const char* off_start = strchr(offsets_key, '[');
            if (off_start) {
                int64_t begin_off = strtoll(off_start + 1, NULL, 10);
                const char* comma = strchr(off_start, ',');
                int64_t end_off = comma ? strtoll(comma + 1, NULL, 10) : begin_off;
                meta.data_offset = begin_off;
                meta.data_length = end_off - begin_off;
            }
        }

        add_tensor_meta(sf, &meta);

        // Advance past this tensor's definition
        const char* next_brace = strchr(dtype_val_end, '}');
        pos = next_brace ? next_brace + 1 : dtype_val_end + 1;
    }

    return sf->num_tensors;
}

// Get a tensor's data pointer (zero-copy from mmap)
const void* omni_safetensor_get_data(const SafeTensorFile* sf, int32_t tensor_idx) {
    if (!sf || !sf->data_region || tensor_idx < 0 || tensor_idx >= sf->num_tensors)
        return NULL;

    const TensorMeta* meta = &sf->tensors[tensor_idx];
    if (meta->data_offset + meta->data_length > sf->data_region_size)
        return NULL;

    return sf->data_region + meta->data_offset;
}

// Find tensor by name
int32_t omni_safetensor_find(const SafeTensorFile* sf, const char* name) {
    if (!sf || !name) return -1;
    for (int32_t i = 0; i < sf->num_tensors; i++) {
        if (strcmp(sf->tensors[i].name, name) == 0)
            return i;
    }
    return -1;
}

// Get tensor metadata
const TensorMeta* omni_safetensor_meta(const SafeTensorFile* sf, int32_t idx) {
    if (!sf || idx < 0 || idx >= sf->num_tensors) return NULL;
    return &sf->tensors[idx];
}

void omni_safetensor_free(SafeTensorFile* sf) {
    if (!sf) return;
    if (sf->tensors) free(sf->tensors);

#ifdef _WIN32
    if (sf->is_mapped && sf->data_region) {
        UnmapViewOfFile((LPCVOID)((uint8_t*)sf->data_region - sf->header_size - 8));
    }
    if (sf->file_mapping) CloseHandle(sf->file_mapping);
#else
    if (sf->is_mapped && sf->data_region) {
        munmap((void*)((uint8_t*)sf->data_region - sf->header_size - 8), sf->file_size);
    }
#endif

    free(sf);
}
