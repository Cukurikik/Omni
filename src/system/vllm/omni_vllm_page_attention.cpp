// OMNI vLLM Paged Attention Engine — System Layer (C++)
// Absorbing vLLM PageAttention physical memory routing logic
// LLM generation key-value caching mapping

#include <vector>
#include <string>
#include <unordered_map>
#include <cmath>

template<typename T>
struct PageResult {
    bool ok;
    T value;
    std::string error;
};

struct KVCacheBlock {
    int physical_block_id;
    int num_tokens;
    std::vector<std::vector<float>> keys; // Token x Dim
    std::vector<std::vector<float>> values; // Token x Dim
};

struct LogicalSequence {
    std::string seq_id;
    std::vector<int> logical_to_physical_table;
};

class OmniVllmPageAttention {
private:
    uint64_t attention_ops = 0;
    int block_size;
    int dim;
    std::unordered_map<int, KVCacheBlock> physical_memory;

public:
    OmniVllmPageAttention(int b_size = 16, int d = 128) : block_size(b_size), dim(d) {}

    /**
     * Reconstructs contiguous attention buffer using scattered physical memory block tables.
     */
    PageResult<std::vector<float>> compute_paged_attention(
        const LogicalSequence& seq,
        const std::vector<float>& query_vector) 
    {
        if (query_vector.size() != dim || seq.logical_to_physical_table.empty()) {
            return {false, {}, "PageError: Dimension mismatch or empty sequence"};
        }

        this->attention_ops++;

        std::vector<float> scores;
        
        // 1. Scatter/Gather Key matrix dot products
        for (int p_id : seq.logical_to_physical_table) {
            if (physical_memory.find(p_id) == physical_memory.end()) {
                return {false, {}, "PageError: Page fault, physical block missing"};
            }
            
            const KVCacheBlock& block = physical_memory.at(p_id);
            for (int t = 0; t < block.num_tokens; ++t) {
                float dot = 0.0f;
                for (int i = 0; i < dim; ++i) {
                    dot += query_vector[i] * block.keys[t][i];
                }
                scores.push_back(dot / std::sqrt((float)dim));
            }
        }

        // 2. Softmax
        float max_s = scores.empty() ? 0.0f : scores[0];
        for (float s : scores) if (s > max_s) max_s = s;
        
        float sum_exp = 0.0f;
        std::vector<float> exp_scores(scores.size(), 0.0f);
        for (size_t i = 0; i < scores.size(); ++i) {
            exp_scores[i] = std::exp(scores[i] - max_s);
            sum_exp += exp_scores[i];
        }

        // 3. Values projection over scattered memory
        std::vector<float> out_vec(dim, 0.0f);
        size_t token_idx = 0;

        for (int p_id : seq.logical_to_physical_table) {
            const KVCacheBlock& block = physical_memory.at(p_id);
            for (int t = 0; t < block.num_tokens; ++t) {
                float prob = exp_scores[token_idx++] / (sum_exp + 1e-9f);
                for (int i = 0; i < dim; ++i) {
                    out_vec[i] += prob * block.values[t][i];
                }
            }
        }

        return {true, out_vec, ""};
    }
    
    // Test mapping utility
    void allocate_mock_blockForVerification(int id, int tokens) {
        KVCacheBlock b;
        b.physical_block_id = id;
        b.num_tokens = tokens;
        b.keys = std::vector<std::vector<float>>(tokens, std::vector<float>(dim, 1.0f));
        b.values = std::vector<std::vector<float>>(tokens, std::vector<float>(dim, 0.5f));
        physical_memory[id] = b;
    }

    std::unordered_map<std::string, std::string> diagnostics() const {
        return {
            {"engine", "OmniVllmPageAttention"},
            {"attention_ops", std::to_string(attention_ops)},
            {"status", "Operational"}
        };
    }
};
