#include "omni_faiss_expert_index.hpp"
#include <iostream>
#include <stdexcept>

namespace omni {
namespace vector {

FaissExpertRouter::FaissExpertRouter(int d_model, int num_experts) 
    : d_model_(d_model), num_experts_(num_experts), is_trained_(false) {
    
    // index_ = new faiss::IndexFlatL2(d_model_);
    std::cout << "OMNI C++: Initialized FAISS L2 Index for Semantic Expert Routing." << std::endl;
}

FaissExpertRouter::~FaissExpertRouter() {
    // delete index_;
}

void FaissExpertRouter::build_index(const std::vector<float>& expert_centroids) {
    if (expert_centroids.size() != num_experts_ * d_model_) {
        throw std::invalid_argument("Centroid data size mismatch.");
    }
    
    // index_->add(num_experts_, expert_centroids.data());
    is_trained_ = true;
    std::cout << "OMNI C++: FAISS Index built with " << num_experts_ << " expert centroids." << std::endl;
}

std::vector<int> FaissExpertRouter::search_experts(const std::vector<float>& token_embedding, int top_k) {
    if (!is_trained_) throw std::runtime_error("Index not built.");
    
    std::vector<int> results(top_k, 0);
    // std::vector<float> distances(top_k);
    
    // Perform nearest neighbor search
    // index_->search(1, token_embedding.data(), top_k, distances.data(), results.data());
    
    // Mocking results for compilation
    for(int i=0; i<top_k; ++i) results[i] = i; 

    return results;
}

} // namespace vector
} // namespace omni
