// OMNI Framework - Odin Low-Level PCM Audio Decoder for Audiolizr
// Optimizes chunk extraction for fast inference via BentoML/Whisper

package omni_audiolizr

import "core:fmt"
import "core:mem"

OmniAudioChunk :: struct {
    data: []f32,
    sample_rate: int,
    channels: int,
}

decode_pcm_frame :: proc(raw_bytes: []u8, out_allocator: mem.Allocator) -> OmniAudioChunk {
    // Basic 16-bit PCM to Float32 conversion for Whisper compatibility
    num_samples := len(raw_bytes) / 2
    f32_data := make([]f32, num_samples, out_allocator)

    for i := 0; i < num_samples; i += 1 {
        // Read int16 (little-endian assumed)
        byte1 := u16(raw_bytes[i * 2])
        byte2 := u16(raw_bytes[i * 2 + 1])
        sample_int := i16(byte1 | (byte2 << 8))
        
        // Normalize to [-1.0, 1.0]
        f32_data[i] = f32(sample_int) / 32768.0
    }

    return OmniAudioChunk {
        data = f32_data,
        sample_rate = 16000, // standard Whisper SR
        channels = 1,
    }
}
