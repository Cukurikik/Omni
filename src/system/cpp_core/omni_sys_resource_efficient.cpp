#include <cstdint>

extern "C" {
    // Hardware utilization ratio calculator
    float resource_efficient_calculate_utilization(uint64_t allocated_bytes, uint64_t max_bytes, float throughput) {
        if (max_bytes == 0) return 0.0f;
        float mem_ratio = (float)allocated_bytes / (float)max_bytes;
        // A synthetic metric combining memory footprint and throughput
        return mem_ratio > 0 ? (throughput / mem_ratio) : 0.0f;
    }
}
