#include "omni_c.h"

void* ggml_omni_alloc(size_t size) {
    return omni_zero_copy_malloc(size);
}
