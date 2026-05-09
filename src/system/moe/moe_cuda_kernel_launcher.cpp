/**
 * moe_cuda_kernel_launcher.cpp — CUDA Kernel Launcher for MoE Operations
 * Layer: System / GPU — MoE CUDA Kernels
 *
 * Host-side launcher for MoE CUDA kernels: grouped GEMM, expert routing
 * scatter/gather, and fused top-k softmax. Manages kernel grid configuration
 * and stream synchronization for multi-expert parallel execution.
 */

#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <cassert>
#include <vector>
#include <array>
#include <algorithm>
#include <numeric>
#include <stdexcept>
#include <string>
#include <memory>

namespace omni {
namespace moe {

/// GPU device properties relevant to MoE kernel configuration.
struct DeviceProps {
    int max_threads_per_block = 1024;
    int max_blocks_per_sm = 16;
    int sm_count = 80;
    int shared_memory_per_sm = 49152;
    int warp_size = 32;
    int max_shared_memory_per_block = 49152;
};

/// Configuration for a single grouped GEMM batch.
struct GroupedGemmConfig {
    int num_groups;
    int m;  // rows per group (tokens per expert)
    int n;  // output dim
    int k;  // input dim
    float alpha = 1.0f;
    float beta = 0.0f;
};

/// Routing metadata for scatter/gather operations.
struct RoutingMeta {
    std::vector<int32_t> expert_indices;   // (num_tokens, top_k)
    std::vector<float> expert_weights;      // (num_tokens, top_k)
    std::vector<int32_t> sorted_token_ids;  // tokens sorted by expert
    std::vector<int32_t> expert_offsets;     // cumulative token count per expert
    int num_tokens = 0;
    int top_k = 0;
    int num_experts = 0;
};

/// Compute optimal grid/block dimensions for MoE kernels.
struct KernelLaunchConfig {
    int grid_x, grid_y, grid_z;
    int block_x, block_y, block_z;
    int shared_mem_bytes;
    int stream_id;

    static KernelLaunchConfig for_scatter(
        int num_tokens, int dim, const DeviceProps& props
    ) {
        KernelLaunchConfig cfg{};
        cfg.block_x = std::min(256, ((dim + props.warp_size - 1) / props.warp_size) * props.warp_size);
        cfg.block_y = 1;
        cfg.block_z = 1;
        cfg.grid_x = (num_tokens + 3) / 4;  // 4 tokens per block
        cfg.grid_y = 1;
        cfg.grid_z = 1;
        cfg.shared_mem_bytes = 0;
        cfg.stream_id = 0;
        return cfg;
    }

    static KernelLaunchConfig for_grouped_gemm(
        const GroupedGemmConfig& gemm, const DeviceProps& props
    ) {
        KernelLaunchConfig cfg{};
        // Tile-based: 128x128 tiles for each expert's GEMM
        int tile_m = 128, tile_n = 128;
        cfg.block_x = 128;
        cfg.block_y = 1;
        cfg.block_z = 1;
        cfg.grid_x = (gemm.m + tile_m - 1) / tile_m;
        cfg.grid_y = (gemm.n + tile_n - 1) / tile_n;
        cfg.grid_z = gemm.num_groups;  // one group per expert
        cfg.shared_mem_bytes = std::min(
            2 * tile_m * tile_n * static_cast<int>(sizeof(float)),
            props.max_shared_memory_per_block
        );
        cfg.stream_id = 0;
        return cfg;
    }

    static KernelLaunchConfig for_topk_softmax(
        int num_tokens, int num_experts, const DeviceProps& props
    ) {
        KernelLaunchConfig cfg{};
        cfg.block_x = std::min(num_experts, props.max_threads_per_block);
        cfg.block_y = 1;
        cfg.block_z = 1;
        cfg.grid_x = num_tokens;
        cfg.grid_y = 1;
        cfg.grid_z = 1;
        cfg.shared_mem_bytes = num_experts * sizeof(float);
        cfg.stream_id = 0;
        return cfg;
    }
};

/// Build routing metadata from raw router outputs.
RoutingMeta build_routing_meta(
    const int32_t* expert_indices,
    const float* expert_weights,
    int num_tokens,
    int top_k,
    int num_experts
) {
    RoutingMeta meta;
    meta.num_tokens = num_tokens;
    meta.top_k = top_k;
    meta.num_experts = num_experts;

    int total = num_tokens * top_k;
    meta.expert_indices.assign(expert_indices, expert_indices + total);
    meta.expert_weights.assign(expert_weights, expert_weights + total);

    // Count tokens per expert
    std::vector<int> counts(num_experts, 0);
    for (int i = 0; i < total; ++i) {
        int eid = expert_indices[i];
        if (eid >= 0 && eid < num_experts) {
            counts[eid]++;
        }
    }

    // Compute offsets (exclusive prefix sum)
    meta.expert_offsets.resize(num_experts + 1, 0);
    for (int e = 0; e < num_experts; ++e) {
        meta.expert_offsets[e + 1] = meta.expert_offsets[e] + counts[e];
    }

    // Sort tokens by expert (stable)
    int total_assigned = meta.expert_offsets[num_experts];
    meta.sorted_token_ids.resize(total_assigned);
    std::vector<int> write_pos(num_experts, 0);
    for (int e = 0; e < num_experts; ++e) {
        write_pos[e] = meta.expert_offsets[e];
    }
    for (int i = 0; i < num_tokens; ++i) {
        for (int k = 0; k < top_k; ++k) {
            int eid = expert_indices[i * top_k + k];
            if (eid >= 0 && eid < num_experts) {
                meta.sorted_token_ids[write_pos[eid]++] = i;
            }
        }
    }

    return meta;
}

/// Compute load balance statistics from routing metadata.
struct LoadBalanceStats {
    float cv_squared;        // Coefficient of variation squared
    float max_utilization;   // Most-loaded expert's fraction
    float min_utilization;   // Least-loaded expert's fraction
    float entropy;           // Routing entropy

    static LoadBalanceStats compute(const RoutingMeta& meta) {
        LoadBalanceStats stats{};
        int ne = meta.num_experts;
        if (ne == 0) return stats;

        std::vector<float> fracs(ne, 0.0f);
        float total_tokens = static_cast<float>(meta.num_tokens * meta.top_k);
        for (int e = 0; e < ne; ++e) {
            int count = meta.expert_offsets[e + 1] - meta.expert_offsets[e];
            fracs[e] = static_cast<float>(count) / std::max(total_tokens, 1.0f);
        }

        float mean = 1.0f / ne;
        float var_sum = 0.0f;
        stats.max_utilization = 0.0f;
        stats.min_utilization = 1.0f;
        stats.entropy = 0.0f;

        for (int e = 0; e < ne; ++e) {
            float diff = fracs[e] - mean;
            var_sum += diff * diff;
            stats.max_utilization = std::max(stats.max_utilization, fracs[e]);
            stats.min_utilization = std::min(stats.min_utilization, fracs[e]);
            if (fracs[e] > 0) {
                stats.entropy -= fracs[e] * std::log(fracs[e]);
            }
        }

        float variance = var_sum / ne;
        stats.cv_squared = variance / (mean * mean + 1e-8f);
        return stats;
    }
};

/// Validate kernel launch configuration against device limits.
bool validate_launch_config(
    const KernelLaunchConfig& cfg,
    const DeviceProps& props
) {
    int total_threads = cfg.block_x * cfg.block_y * cfg.block_z;
    if (total_threads > props.max_threads_per_block) return false;
    if (cfg.shared_mem_bytes > props.max_shared_memory_per_block) return false;
    if (cfg.grid_x <= 0 || cfg.grid_y <= 0 || cfg.grid_z <= 0) return false;
    return true;
}

}  // namespace moe
}  // namespace omni
