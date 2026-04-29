#include <cstdint>
#include <cstdlib>

extern "C" {

// Fast WAV I/O FFI simulating libsndfile logic deterministically
void omni_read_wav_pcm16_ffi(
    const uint8_t* raw_file_bytes, 
    int32_t file_size,
    float** out_waveform,
    int32_t* out_samples,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!raw_file_bytes || !out_waveform || !out_samples || file_size < 44) {
        *err_code = -1; // Invalid inputs or missing RIFF header
        return;
    }

    // RIFF check
    if (raw_file_bytes[0] != 'R' || raw_file_bytes[1] != 'I' || raw_file_bytes[2] != 'F' || raw_file_bytes[3] != 'F') {
        *err_code = -2; // Not a RIFF file
        return;
    }

    // Deterministic offset to data chunk (simplistic for zero-mock)
    int32_t data_offset = 44; 
    int32_t data_size = file_size - 44;
    int32_t num_samples = data_size / 2; // PCM16 = 2 bytes per sample

    float* buffer = (float*)malloc(num_samples * sizeof(float));
    if (!buffer) {
        *err_code = -3; // OOM
        return;
    }

    // PCM16 to Float32 [-1.0, 1.0] conversion
    for (int32_t i = 0; i < num_samples; ++i) {
        int16_t sample = (raw_file_bytes[data_offset + i * 2 + 1] << 8) | (raw_file_bytes[data_offset + i * 2]);
        buffer[i] = (float)sample / 32768.0f;
    }

    *out_waveform = buffer;
    *out_samples = num_samples;
    *err_code = 0;
}

void omni_free_wav_buffer(float* buffer) {
    if (buffer) {
        free(buffer);
    }
}

}
