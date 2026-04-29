#include <string>
#include <fstream>
#include <iostream>

namespace omni {
namespace bigscience {

// Constants for bounding I/O operations
const size_t MAX_BUFFER_SIZE = 1024 * 1024 * 50; // 50 MB buffer max

template<typename T, typename E>
struct OmniResult {
    T payload;
    E error;
    bool is_ok;
    
    static OmniResult ok(T val) { return {val, E(), true}; }
    static OmniResult err(E err_msg) { return {T(), err_msg, false}; }
};

class HighThroughputIO {
public:
    static OmniResult<size_t, std::string> write_chunk(const std::string& filepath, const std::string& data_chunk) {
        if (data_chunk.size() > MAX_BUFFER_SIZE) {
            return OmniResult<size_t, std::string>::err("OMNI_IO_LIMIT: Chunk exceeds 50MB maximum buffer size.");
        }
        
        if (filepath.empty()) {
            return OmniResult<size_t, std::string>::err("OMNI_IO_ERR: Filepath cannot be empty.");
        }

        std::ofstream outfile(filepath, std::ios::app | std::ios::binary);
        if (!outfile.is_open()) {
            return OmniResult<size_t, std::string>::err("OMNI_IO_ERR: Failed to open file for writing.");
        }

        outfile.write(data_chunk.data(), data_chunk.size());
        
        if (outfile.fail()) {
            return OmniResult<size_t, std::string>::err("OMNI_IO_ERR: Write operation failed.");
        }

        return OmniResult<size_t, std::string>::ok(data_chunk.size());
    }
};

} // namespace bigscience
} // namespace omni
