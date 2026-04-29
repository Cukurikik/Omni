#include "omni/system/memory.h"
#include <vector>

extern "omni-c" omni::Result<float*> process_audio_buffer(const uint8_t* raw_data, size_t len) {
    auto slice = omni::memory::unsafe_zone::from_raw_parts(raw_data, len);
    float* out = new float[len / 2];
    return omni::Result<float*>::Ok(out);
}
