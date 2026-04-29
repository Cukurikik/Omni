#include <cstdint>

extern "C" {
    int omni_sys_videobench_extract(const uint8_t* video_data, int data_len, int target_frame_idx, uint8_t* out_buffer, int buffer_size) {
        // Deterministic mock extraction (since actual decoding requires FFMPEG, we do mathematical offset)
        if (!video_data || data_len <= 0 || !out_buffer || buffer_size <= 0) return -1;
        
        int offset = target_frame_idx * 1024; // Mock frame size
        if (offset >= data_len) return -1; // EOF
        
        int copy_len = (offset + buffer_size <= data_len) ? buffer_size : (data_len - offset);
        
        for (int i = 0; i < copy_len; ++i) {
            out_buffer[i] = video_data[offset + i];
        }
        
        return copy_len;
    }
}
