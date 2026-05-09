// moe_three_phases_balancer.cpp — System
// Layer: System — Expert Routing Load Balancer
// Inspired by: three-phases-moe (Three Phases of Expert Routing)

#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>

namespace omni {
namespace system {

enum class TrainingPhase {
    RANDOM_ROUTING,
    SPECIALIZATION,
    EQUILIBRIUM
};

class ThreePhasesLoadBalancer {
private:
    int num_experts;
    std::vector<uint64_t> expert_loads;
    TrainingPhase current_phase;

public:
    ThreePhasesLoadBalancer(int experts) 
        : num_experts(experts), expert_loads(experts, 0), current_phase(TrainingPhase::RANDOM_ROUTING) {}

    void update_phase(uint64_t total_tokens_processed) {
        if (total_tokens_processed < 1000000) {
            current_phase = TrainingPhase::RANDOM_ROUTING;
        } else if (total_tokens_processed < 50000000) {
            current_phase = TrainingPhase::SPECIALIZATION;
        } else {
            current_phase = TrainingPhase::EQUILIBRIUM;
        }
    }

    // Applies jitter/noise based on the training phase to enforce load balancing
    float calculate_routing_noise(int expert_id) {
        float base_noise = 0.0f;
        
        switch (current_phase) {
            case TrainingPhase::RANDOM_ROUTING:
                base_noise = 1.0f; // High noise for exploration
                break;
            case TrainingPhase::SPECIALIZATION:
                base_noise = 0.1f; // Annealed noise allowing expert clustering
                break;
            case TrainingPhase::EQUILIBRIUM:
                // Apply penalty if expert is overloaded
                float avg_load = 0;
                for (auto l : expert_loads) avg_load += l;
                avg_load /= num_experts;
                
                if (expert_loads[expert_id] > avg_load * 1.1) {
                    base_noise = -0.5f; // Penalize routing
                } else {
                    base_noise = 0.01f; // Minimal noise
                }
                break;
        }
        return base_noise;
    }

    void record_assignment(int expert_id) {
        if (expert_id >= 0 && expert_id < num_experts) {
            expert_loads[expert_id]++;
        }
    }
};

}} // namespace
