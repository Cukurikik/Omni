#ifndef OMNI_KERNEL_BRIDGE_H
#define OMNI_KERNEL_BRIDGE_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// OMNI MOTHER: Low-level C headers (Production Grade)
void* omni_sys_malloc(size_t size);
void omni_sys_free(void* ptr);
int omni_fast_memory_copy(void* dest, const void* src, size_t n);

#ifdef __cplusplus
}
#endif

#endif // OMNI_KERNEL_BRIDGE_H
