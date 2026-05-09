#ifndef OMNI_FAISS_EXPERT_INDEX_HPP
#define OMNI_FAISS_EXPERT_INDEX_HPP

#include <vector>
// #include <faiss/IndexFlat.h> // Simulated FAISS import

namespace omni {
namespace vector {

/**
 * OMNI Framework - FAISS Expert Indexer
 * Uses Meta's FAISS library to map prompt embeddings to the semantic centroids
 * of available experts. This is an alternative routing mechanism to MLP routers.
 */
class FaissExpertRouter {
public:
    FaissExpertRouter(int d_model, int num_experts);
    ~FaissExpertRouter();

    // Initialize the index with the semantic centroids of each expert
    void build_index(const std::vector<float>& expert_centroids);

    // Given a token embedding, return the Top-K expert indices
    std::vector<int> search_experts(const std::vector<float>& token_embedding, int top_k);

private:
    int d_model_;
    int num_experts_;
    bool is_trained_;
    
    // faiss::IndexFlatL2* index_;
};

} // namespace vector
} // namespace omni

#endif // OMNI_FAISS_EXPERT_INDEX_HPP
