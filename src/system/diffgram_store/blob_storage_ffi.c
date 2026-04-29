#include <stdint.h>

extern "C" {

// FFI export simulating low-level continuous byte block packing for blobs
void omni_pack_blob_stream(
    const uint8_t* raw_blob, 
    int32_t blob_len, 
    uint8_t* disk_page_buffer, 
    int32_t page_capacity, 
    int32_t* bytes_written, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!raw_blob || !disk_page_buffer || !bytes_written || blob_len <= 0 || page_capacity <= 0) {
        *err_code = -1;
        return;
    }

    *bytes_written = 0;

    // Mathematical header formulation for blob storage
    // 4 bytes: Magic Number (0xDF 0xGR 0xAM 0x01)
    // 4 bytes: Length
    
    if (page_capacity < 8 + blob_len) {
        *err_code = -2; // Insufficient page capacity for mathematical struct
        return;
    }

    // Write header
    disk_page_buffer[0] = 0xDF;
    disk_page_buffer[1] = 0xGR;
    disk_page_buffer[2] = 0xAM;
    disk_page_buffer[3] = 0x01;

    disk_page_buffer[4] = (blob_len >> 24) & 0xFF;
    disk_page_buffer[5] = (blob_len >> 16) & 0xFF;
    disk_page_buffer[6] = (blob_len >> 8) & 0xFF;
    disk_page_buffer[7] = blob_len & 0xFF;

    // Fast deterministic memory copy
    for (int32_t i = 0; i < blob_len; ++i) {
        disk_page_buffer[8 + i] = raw_blob[i];
    }

    *bytes_written = 8 + blob_len;
    *err_code = 0;
}

}
