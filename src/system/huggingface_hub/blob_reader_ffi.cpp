#include <cstdint>
#include <fstream>
#include <vector>

extern "C" {

// Fast model blob reading simulating huggingface_hub disk access
void omni_read_model_blob(
    const char* file_path,
    uint64_t offset,
    uint64_t size,
    uint8_t* out_buffer,
    int32_t* bytes_read,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!file_path || !out_buffer || !bytes_read || size == 0) {
        *err_code = -1;
        return;
    }

    std::ifstream file(file_path, std::ios::binary);
    if (!file.is_open()) {
        *err_code = -2; // File not found or unreadable
        return;
    }

    file.seekg(offset, std::ios::beg);
    if (!file.good()) {
        *err_code = -3; // Offset out of bounds
        return;
    }

    file.read(reinterpret_cast<char*>(out_buffer), size);
    
    *bytes_read = static_cast<int32_t>(file.gcount());
    *err_code = 0;
}

}
