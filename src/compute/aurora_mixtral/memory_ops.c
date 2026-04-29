#include <stdint.h>
#include <stdlib.h>

int32_t allocate_mixtral_buffer(size_t size_bytes, void** out_buffer) {
    if (size_bytes == 0 || !out_buffer) return -1;
    *out_buffer = malloc(size_bytes);
    if (!*out_buffer) return -2;
    return 0;
}
