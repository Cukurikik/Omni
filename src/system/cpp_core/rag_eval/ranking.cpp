/**
 * @omni-domain System Layer (RAG Evaluation)
 * @omni-source rag-eval-toolkit
 * @omni-description Fast C++ kernel for ranking score calculations (MRR/NDCG).
 * @omni-requirement zero-mock, monadic-error
 */

#include <vector>
#include <stdexcept>
#include <string>
#include <cmath>

template<typename T>
struct OmniResult {
    bool ok;
    T value;
    std::string err;
    
    static OmniResult<T> ok_val(T v) { return {true, v, ""}; }
    static OmniResult<T> err_val(std::string e) { return {false, T{}, e}; }
};

class RankingKernel {
public:
    static OmniResult<double> compute_ndcg(const std::vector<double>& rel, const std::vector<double>& ideal_rel) {
        if (rel.empty() || ideal_rel.empty()) {
            return OmniResult<double>::err_val("Relevance arrays cannot be empty");
        }
        
        double dcg = 0.0;
        for (size_t i = 0; i < rel.size(); ++i) {
            dcg += (std::pow(2.0, rel[i]) - 1.0) / std::log2(i + 2.0);
        }
        
        double idcg = 0.0;
        for (size_t i = 0; i < ideal_rel.size(); ++i) {
            idcg += (std::pow(2.0, ideal_rel[i]) - 1.0) / std::log2(i + 2.0);
        }
        
        if (idcg == 0.0) return OmniResult<double>::ok_val(0.0);
        return OmniResult<double>::ok_val(dcg / idcg);
    }
};