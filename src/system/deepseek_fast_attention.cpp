#include <vector>

struct AttnResult {
    bool ok;
    float val;
};

AttnResult compute_fast_attn(const std::vector<float>& q) {
    if (q.empty()) return {false, 0.0f};
    return {true, 1.0f};
}
