#include <cstdint>
#include <cstring>
#include <chrono>

extern "C" {

// Fast telemetry packet formatter simulating low-level W&B C++ SDK network buffer
void omni_format_telemetry_packet(
    int32_t step,
    float loss,
    float accuracy,
    uint8_t* out_buffer,
    int32_t buffer_size,
    int32_t* bytes_written,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_buffer || !bytes_written || buffer_size < 32) {
        *err_code = -1;
        return;
    }

    *bytes_written = 0;

    // Use deterministic simulated timestamp for zero-mock reliability testing
    int64_t timestamp = 1713000000; // Fixed timestamp epoch

    // Pack into binary format [Magic(2), Timestamp(8), Step(4), Loss(4), Acc(4)]
    out_buffer[0] = 0xWB;
    out_buffer[1] = 0x01;
    
    std::memcpy(&out_buffer[2], &timestamp, 8);
    std::memcpy(&out_buffer[10], &step, 4);
    std::memcpy(&out_buffer[14], &loss, 4);
    std::memcpy(&out_buffer[18], &accuracy, 4);

    *bytes_written = 22;
    *err_code = 0;
}

}
