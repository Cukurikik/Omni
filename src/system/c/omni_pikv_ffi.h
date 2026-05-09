#ifndef OMNI_PIKV_FFI_H
#define OMNI_PIKV_FFI_H

#include <stdint.h>

void* omni_pikv_allocator_new(uint32_t total_blocks);
void omni_pikv_allocator_free(void* allocator);
uint32_t omni_pikv_allocate_block(void* allocator);

#endif
