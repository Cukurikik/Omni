// moe_memory_profiler.cpp — System / Telemetry
// Layer: System / Memory — VRAM Fragmentation Profiler
//
// A low-level C++ profiler that tracks VRAM allocations per expert.
// It detects memory fragmentation (e.g., when total free VRAM is large,
// but the largest contiguous block is too small for a new expert).

#include <iostream>
#include <vector>
#include <string>
#include <map>

namespace omni {
namespace moe {
namespace memory {

struct ExpertAllocation {
    int expert_id;
    size_t size_bytes;
    size_t start_address;
};

class VRAMProfiler {
private:
    size_t total_vram_capacity;
    std::map<int, ExpertAllocation> allocations;

public:
    VRAMProfiler(size_t capacity_bytes) : total_vram_capacity(capacity_bytes) {
        std::cout << "[MoE Profiler] Initialized VRAM tracking. Capacity: " 
                  << capacity_bytes / (1024 * 1024) << " MB." << std::endl;
    }

    void record_allocation(int expert_id, size_t start_addr, size_t size_bytes) {
        allocations[expert_id] = {expert_id, size_bytes, start_addr};
    }

    void record_free(int expert_id) {
        allocations.erase(expert_id);
    }

    /**
     * Calculates the fragmentation ratio. 
     * A high ratio (>0.5) indicates that the Zig Compactor should run.
     */
    double calculate_fragmentation_ratio() {
        if (allocations.empty()) return 0.0;

        size_t used_vram = 0;
        size_t max_end_addr = 0;

        for (const auto& pair : allocations) {
            used_vram += pair.second.size_bytes;
            size_t end_addr = pair.second.start_address + pair.second.size_bytes;
            if (end_addr > max_end_addr) {
                max_end_addr = end_addr;
            }
        }

        // The "fragmented" space is the difference between the highest address
        // occupied and the actual sum of allocations.
        size_t fragmentation_bytes = max_end_addr - used_vram;
        
        return static_cast<double>(fragmentation_bytes) / static_cast<double>(max_end_addr);
    }

    void print_report() {
        double frag_ratio = calculate_fragmentation_ratio();
        std::cout << "--- VRAM Profiler Report ---" << std::endl;
        std::cout << "Active Experts: " << allocations.size() << std::endl;
        std::cout << "Fragmentation Ratio: " << frag_ratio * 100.0 << "%" << std::endl;
        if (frag_ratio > 0.3) {
            std::cout << "WARNING: High fragmentation detected. Compaction recommended." << std::endl;
        }
        std::cout << "----------------------------" << std::endl;
    }
};

} // namespace memory
} // namespace moe
} // namespace omni
