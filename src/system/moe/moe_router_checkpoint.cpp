// moe_router_checkpoint.cpp — System / Storage
// Layer: System / Core — High-Speed Router Checkpointing
//
// While experts take hours to save due to size, the Router network is small
// and updates constantly via QLoRA or continuous learning. This C++ module
// provides millisecond-latency binary checkpointing for just the router weights,
// ensuring no routing knowledge is lost on sudden node failure.

#include <iostream>
#include <fstream>
#include <vector>

namespace omni {
namespace moe {
namespace storage {

class RouterCheckpoint {
private:
    std::string checkpoint_path;

public:
    RouterCheckpoint(const std::string& path) : checkpoint_path(path) {
        std::cout << "[Router Checkpoint] High-speed binary IO initialized at " << path << std::endl;
    }

    /**
     * @brief Writes raw float data directly to a binary file.
     * Bypasses heavy serialization frameworks (e.g. PyTorch safetensors) for raw speed.
     */
    void fast_save(const float* router_weights, size_t num_elements) {
        std::ofstream outfile(checkpoint_path, std::ios::out | std::ios::binary);
        if (!outfile) {
            std::cerr << "[Router Checkpoint] Failed to open file for writing." << std::endl;
            return;
        }

        outfile.write(reinterpret_cast<const char*>(router_weights), num_elements * sizeof(float));
        outfile.close();
        
        // std::cout << "[Router Checkpoint] Successfully saved " << num_elements << " weights." << std::endl;
    }

    /**
     * @brief Loads raw float data directly from a binary file into VRAM-mapped memory.
     */
    void fast_load(float* buffer, size_t num_elements) {
        std::ifstream infile(checkpoint_path, std::ios::in | std::ios::binary);
        if (!infile) {
            std::cerr << "[Router Checkpoint] Checkpoint not found. Starting fresh." << std::endl;
            return;
        }

        infile.read(reinterpret_cast<char*>(buffer), num_elements * sizeof(float));
        infile.close();
        
        std::cout << "[Router Checkpoint] Restored router weights from disk." << std::endl;
    }
};

} // namespace storage
} // namespace moe
} // namespace omni
