// Omni XRec Scorer (C++)
#include <vector>
#include <cmath>
#include <algorithm>
namespace omni { namespace xrec {
float sigmoid(float x) { return 1.0f / (1.0f + std::exp(-x)); }
float dot_score(const std::vector<float>& u, const std::vector<float>& i) {
    float d = 0; for (size_t k = 0; k < u.size() && k < i.size(); ++k) d += u[k]*i[k];
    return sigmoid(d);
}
float ndcg_at_k(const std::vector<bool>& ranked, int k) {
    float dcg = 0, idcg = 0;
    std::vector<bool> ideal(ranked.begin(), ranked.begin()+std::min((int)ranked.size(), k));
    std::sort(ideal.begin(), ideal.end(), std::greater<bool>());
    for (int i = 0; i < k && i < (int)ranked.size(); ++i) {
        dcg += (ranked[i]?1.0f:0) / std::log2(i+2.0f);
        idcg += (ideal[i]?1.0f:0) / std::log2(i+2.0f);
    }
    return idcg > 0 ? dcg/idcg : 0;
}
}}
