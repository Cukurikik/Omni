// Omni KoPA Structural Embedding Kernel (C++)
// Ref: zjukg/KoPA — ACM MM 2024
#include <vector>
#include <cmath>
#include <algorithm>

namespace omni { namespace kopa {
std::vector<float> structural_embedding(int entity_id, const std::vector<int>& neighbors, int dim = 64) {
    std::vector<float> emb(dim, 0.f);
    for (int i = 0; i < dim; ++i) emb[i] = std::sin(entity_id * (i+1) * 0.01f);
    for (int n : neighbors)
        for (int i = 0; i < dim; ++i)
            emb[i] += std::cos(n * (i+1) * 0.007f) / std::max((int)neighbors.size(), 1);
    float norm = 0;
    for (float e : emb) norm += e * e;
    norm = std::sqrt(norm) + 1e-8f;
    for (float& e : emb) e /= norm;
    return emb;
}

float transE_score(const std::vector<float>& h, const std::vector<float>& r, const std::vector<float>& t) {
    float score = 0;
    size_t d = std::min({h.size(), r.size(), t.size()});
    for (size_t i = 0; i < d; ++i) { float diff = h[i] + r[i] - t[i]; score += diff * diff; }
    return -score;
}
}} // namespace omni::kopa
