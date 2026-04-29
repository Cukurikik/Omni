// OMNI NUMA Memory Policy Engine — System Layer (C++)
// Absorbing linux-numa/numactl physical architecture
// Non-Uniform Memory Access spatial node distance assignment

#include <vector>
#include <string>
#include <unordered_map>
#include <cmath>

template<typename T>
struct NumaResult {
    bool ok;
    T value;
    std::string error;
};

struct PhysicalNode {
    int id;
    uint64_t available_bytes;
};

class OmniNumaMemoryPolicy {
private:
    uint64_t allocations_mapped = 0;
    std::vector<PhysicalNode> nodes;
    std::vector<std::vector<int>> distance_matrix; // Slit table representation

public:
    OmniNumaMemoryPolicy() = default;

    NumaResult<bool> initialize_topology(
        const std::vector<PhysicalNode>& physical_nodes,
        const std::vector<std::vector<int>>& distance_map) 
    {
        if (physical_nodes.size() != distance_map.size()) {
            return {false, false, "NumaError: Matrix mismatched bounds."};
        }

        nodes = physical_nodes;
        distance_matrix = distance_map;
        return {true, true, ""};
    }

    /**
     * Determines optimal memory bound physical attachment taking CPU locality into account.
     * Evaluates geometric lowest distance allocation policy.
     */
    NumaResult<int> evaluate_local_allocation(int executing_cpu_node, uint64_t required_bytes) {
        if (nodes.empty()) {
            return {false, -1, "NumaError: Uninitialized topology."};
        }
        
        if (executing_cpu_node < 0 || executing_cpu_node >= nodes.size()) {
            return {false, -1, "NumaError: Invalid CPU topology bound."};
        }

        this->allocations_mapped++;

        // Strict Local strategy: Check local node first
        if (nodes[executing_cpu_node].available_bytes >= required_bytes) {
            nodes[executing_cpu_node].available_bytes -= required_bytes;
            return {true, executing_cpu_node, ""};
        }

        // Fallback strategy: Nearest logical distance via ACPI SLIT mapping
        int best_node = -1;
        int min_distance = 10000;

        for (size_t i = 0; i < nodes.size(); ++i) {
            if (i == executing_cpu_node) continue;

            if (nodes[i].available_bytes >= required_bytes) {
                int dist = distance_matrix[executing_cpu_node][i];
                if (dist < min_distance) {
                    min_distance = dist;
                    best_node = static_cast<int>(i);
                }
            }
        }

        if (best_node != -1) {
            nodes[best_node].available_bytes -= required_bytes;
            return {true, best_node, ""};
        }

        // OOM Boundary limits
        return {false, -1, "NumaError: Out of available memory domains."};
    }

    std::unordered_map<std::string, std::string> diagnostics() const {
        return {
            {"engine", "OmniNumaMemoryPolicy"},
            {"topology_nodes", std::to_string(nodes.size())},
            {"allocations_routed", std::to_string(allocations_mapped)},
            {"status", "Operational"}
        };
    }
};
