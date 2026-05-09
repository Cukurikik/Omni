// moe_expert_parallelism.cpp — System / Hardware
// Layer: System / GPU — Expert Parallelism (EP) + Tensor Parallelism (TP)
//
// Implements 2D Parallelism for MoE models. Large experts that don't fit on a 
// single GPU are sharded via Tensor Parallelism (TP), while different experts 
// are placed on different GPUs via Expert Parallelism (EP).

#include <iostream>
#include <vector>

namespace omni {
namespace moe {
namespace parallelism {

struct ParallelConfig {
    int ep_degree; // Expert Parallelism degree
    int tp_degree; // Tensor Parallelism degree
    int pp_degree; // Pipeline Parallelism degree
};

class HybridParallelismMapper {
private:
    ParallelConfig config;
    int total_gpus;

public:
    HybridParallelismMapper(ParallelConfig cfg, int total_gpus) 
        : config(cfg), total_gpus(total_gpus) {
        
        if (cfg.ep_degree * cfg.tp_degree * cfg.pp_degree > total_gpus) {
            std::cerr << "[MoE Parallelism] Error: Required GPUs exceed available topology." << std::endl;
        } else {
            std::cout << "[MoE Parallelism] 2D/3D Hybrid Mapping Initialized. (EP=" 
                      << cfg.ep_degree << ", TP=" << cfg.tp_degree << ")" << std::endl;
        }
    }

    /**
     * Given an expert ID, returns the physical GPU IDs holding that expert's shards.
     */
    std::vector<int> get_gpu_placement_for_expert(int expert_id) {
        std::vector<int> placement;
        
        // EP assigns experts to specific TP groups
        int ep_group = expert_id % config.ep_degree;
        
        // Find which GPUs make up this TP group
        int start_gpu = ep_group * config.tp_degree;
        
        for (int i = 0; i < config.tp_degree; ++i) {
            placement.push_back(start_gpu + i);
        }
        
        return placement;
    }
};

} // namespace parallelism
} // namespace moe
} // namespace omni
