// OMNI Divine Memory Integration: Inspired by Baichuan-7B
// System Layer - C Header for FFI Boundary

#ifndef OMNI_BAICHUAN_FFI_H
#define OMNI_BAICHUAN_FFI_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int code;
    const char* message;
} OmniError;

typedef struct {
    int is_ok;
    void* ptr;
    OmniError error;
} OmniResult_Ptr;

// Bounded physical FFI initialization for model parameters mapping
OmniResult_Ptr omni_baichuan_init_weights(const char* model_path);

#ifdef __cplusplus
}
#endif

#endif // OMNI_BAICHUAN_FFI_H
