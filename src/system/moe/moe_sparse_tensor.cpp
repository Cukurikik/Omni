// moe_sparse_tensor.cpp — System / Core
// Layer: System / Data Structures — Sparse MoE Tensors
//
// Represents the heavily sparse tensors generated during MoE routing.
// Standard dense tensors waste massive amounts of RAM storing zeros for un-routed 
// tokens. This provides a zero-mock representation of a CSR (Compressed Sparse Row)
// wrapper for MoE activations.

#include <iostream>
#include <vector>
#include <stdexcept>

namespace omni {
namespace moe {
namespace memory {

template <typename T>
class SparseMoETensor {
private:
    int num_experts;
    int hidden_dim;
    int total_tokens;
    
    // Values stored densely per expert
    std::vector<std::vector<T>> values;
    
    // Original sequence indices for gathering back to dense
    std::vector<std::vector<int>> sequence_indices;

public:
    SparseMoETensor(int num_experts, int hidden_dim, int total_tokens) 
        : num_experts(num_experts), hidden_dim(hidden_dim), total_tokens(total_tokens) {
        
        values.resize(num_experts);
        sequence_indices.resize(num_experts);
    }

    /**
     * Appends a token to a specific expert's bin.
     * This simulates the "Scatter" operation in MoE.
     */
    void add_token(int expert_id, int original_index, const std::vector<T>& token_data) {
        if (expert_id < 0 || expert_id >= num_experts) {
            throw std::out_of_range("Invalid expert ID");
        }
        if (token_data.size() != hidden_dim) {
            throw std::invalid_argument("Token dimension mismatch");
        }

        values[expert_id].insert(values[expert_id].end(), token_data.begin(), token_data.end());
        sequence_indices[expert_id].push_back(original_index);
    }

    /**
     * Simulates the "Gather" operation, returning a dense tensor (vector of vectors).
     */
    std::vector<std::vector<T>> to_dense() const {
        // Initialize dense buffer with zeros
        std::vector<std::vector<T>> dense(total_tokens, std::vector<T>(hidden_dim, T(0)));

        for (int e = 0; e < num_experts; ++e) {
            int tokens_in_expert = sequence_indices[e].size();
            for (int t = 0; t < tokens_in_expert; ++t) {
                int orig_idx = sequence_indices[e][t];
                
                // Copy the flat values back into the dense structure
                for (int d = 0; d < hidden_dim; ++d) {
                    dense[orig_idx][d] = values[e][t * hidden_dim + d];
                }
            }
        }

        return dense;
    }
};

} // namespace memory
} // namespace moe
} // namespace omni
