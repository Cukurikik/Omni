#ifndef OMNI_C_FFI_HEADER_H
#define OMNI_C_FFI_HEADER_H

/**
 * Omni C FFI Header
 * System Layer
 * The absolute master ABI boundary definition for the Omni Universal Binary.
 * Every language (Python, Java, Go, C#, Erlang, etc.) binds to these functions
 * to execute the zero-mock inference logic without duplicating memory.
 */

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Opaque handle representing a loaded Transformer model in VRAM
typedef void* OmniModelHandle;

// Result status codes
#define OMNI_OK 0
#define OMNI_ERR_OOM 1
#define OMNI_ERR_INVALID_MODEL 2
#define OMNI_ERR_HARDWARE 3

/**
 * Loads a model from disk or memory mapping.
 */
OmniModelHandle omni_load_model(const char* filepath);
OmniModelHandle omni_load_model_fd(int fd, size_t offset, size_t length);

/**
 * Unloads the model and frees all associated VRAM and KV Caches.
 */
void omni_free_model(OmniModelHandle handle);

/**
 * Executes a forward pass for generation.
 * Input and Output buffers must be pre-allocated by the caller.
 * 
 * @param handle The model instance
 * @param prompt Null-terminated UTF-8 string
 * @param output_buffer Pre-allocated char array to hold response
 * @param max_len Maximum bytes the output_buffer can hold
 * @return OMNI_OK on success
 */
int omni_generate(OmniModelHandle handle, const char* prompt, char* output_buffer, int max_len);

/**
 * Hardware metrics polling.
 */
int omni_get_vram_usage_mb(void);
int omni_get_gpu_temperature(void);

#ifdef __cplusplus
}
#endif

#endif // OMNI_C_FFI_HEADER_H
