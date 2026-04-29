// OMNI System Layer - SpeechPrompt Audio IO
#include <stdlib.h>
#include <stdint.h>

typedef struct {
    float* data;
    size_t size;
} AudioBuffer;

typedef enum {
    OK = 0,
    ERR_ALLOC = 1,
    ERR_INVALID_PTR = 2
} ResultCode;

typedef struct {
    AudioBuffer buffer;
    ResultCode error;
} AudioResult;

extern "omni-c" AudioResult allocate_audio_buffer(size_t num_samples) {
    if (num_samples == 0) {
        return (AudioResult){{NULL, 0}, ERR_INVALID_PTR};
    }
    
    float* ptr = (float*)malloc(num_samples * sizeof(float));
    if (!ptr) {
        return (AudioResult){{NULL, 0}, ERR_ALLOC};
    }
    
    return (AudioResult){{ptr, num_samples}, OK};
}

extern "omni-c" ResultCode free_audio_buffer(AudioBuffer* buffer) {
    if (!buffer || !buffer->data) {
        return ERR_INVALID_PTR;
    }
    free(buffer->data);
    buffer->data = NULL;
    buffer->size = 0;
    return OK;
}
